"""
Utilities for fetching macroeconomic indicators from the World Bank API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests

BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"


@dataclass(frozen=True)
class IndicatorRequest:
    """Descriptor for a World Bank indicator."""

    name: str
    indicator_code: str


def fetch_indicator_series(
    country: str,
    indicator: IndicatorRequest,
    start_year: int,
    end_year: int,
) -> pd.Series:
    """
    Fetch a time series for a single indicator and country.
    Handles pagination and cases where payload[1] is missing/None.
    """
    session = requests.Session()
    params = {
        "format": "json",
        "per_page": 20000,                 # pull everything
        "date": f"{start_year}:{end_year}",
        "page": 1,
    }

    all_rows = []
    while True:
        resp = session.get(
            BASE_URL.format(country=country, indicator=indicator.indicator_code),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()

        # World Bank returns [meta, rows]; rows can be None or payload can be shorter
        if not isinstance(payload, list) or len(payload) == 0:
            break

        rows = payload[1] if len(payload) > 1 and payload[1] is not None else []
        all_rows.extend([r for r in rows if r.get("value") is not None])

        meta = payload[0] if isinstance(payload[0], dict) else {}
        page = int(meta.get("page", params["page"]))
        pages = int(meta.get("pages", 1))
        if page >= pages:
            break
        params["page"] = page + 1

    if not all_rows:
        raise RuntimeError(f"No data returned for {indicator.indicator_code} ({country})")

    frame = (
        pd.DataFrame.from_records(all_rows)[["date", "value"]]
        .assign(date=lambda df: df["date"].astype(int))
        .set_index("date")
        .sort_index()
    )
    return frame["value"].rename(indicator.name)


def build_country_macro_dataset(
    country: str,
    indicators: Iterable[IndicatorRequest],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """Fetch and combine multiple indicators for a single country (tolerant)."""
    series_list = []
    missing = []

    for indicator in indicators:
        try:
            s = fetch_indicator_series(country, indicator, start_year, end_year)
        except RuntimeError:
            missing.append(indicator.indicator_code)
            continue
        if not s.empty:
            series_list.append(s)

    # If nothing at all was fetched for this country, give up
    if not series_list:
        raise RuntimeError(f"No usable indicators for {country}; missing={missing}")

    # Outer-join to keep years that exist for at least one indicator
    dataset = pd.concat(series_list, axis=1, join="outer").sort_index()
    dataset.index.name = "year"
    dataset["country"] = country.upper()
    dataset = dataset.reset_index().set_index(["country", "year"]).sort_index()

    # (Optional) drop rows where *all* indicators are NaN
    dataset = dataset.dropna(how="all")

    return dataset

def build_training_dataset(
    countries: Iterable[str],
    indicators: Iterable[IndicatorRequest],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """
    Construct a combined dataset across multiple countries.

    Countries with insufficient data are skipped.
    """
    frames = []
    for country in countries:
        try:
            frame = build_country_macro_dataset(country, indicators, start_year, end_year)
        except RuntimeError:
            continue
        frames.append(frame)

    if not frames:
        raise RuntimeError("Could not retrieve data for any training country")

    combined = pd.concat(frames).sort_index()
    return combined.dropna()
