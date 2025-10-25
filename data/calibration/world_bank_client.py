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

    Returns a pandas Series indexed by year with float values.
    """
    params = {
        "format": "json",
        "per_page": 1000,
        "date": f"{start_year}:{end_year}",
    }
    response = requests.get(
        BASE_URL.format(country=country, indicator=indicator.indicator_code),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if len(payload) < 2:
        raise RuntimeError(f"No data returned for {indicator.indicator_code} ({country})")
    rows = payload[1]
    frame = (
        pd.DataFrame.from_records(rows)[["date", "value"]]
        .dropna()
        .assign(date=lambda df: df["date"].astype(int))
        .set_index("date")
        .sort_index()
    )
    series = frame["value"].rename(indicator.name)
    return series


def build_country_macro_dataset(
    country: str,
    indicators: Iterable[IndicatorRequest],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """Fetch and combine multiple indicators for a single country."""
    series_list = []
    for indicator in indicators:
        series = fetch_indicator_series(country, indicator, start_year, end_year)
        series_list.append(series)

    dataset = pd.concat(series_list, axis=1).sort_index()
    dataset.index.name = "year"
    dataset["country"] = country.upper()
    dataset = dataset.reset_index().set_index(["country", "year"]).sort_index()
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
