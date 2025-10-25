"""
CLI for calibrating simulation parameters against World Bank data.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

from data.calibration.parameter_fit import calibrate_parameters
from data.calibration.world_bank_client import (
    IndicatorRequest,
    build_country_macro_dataset,
    build_training_dataset,
)
from data.calibration.scenarios import (
    apply_growth_shock,
    apply_unemployment_shock,
    apply_consumption_shift,
)

DEFAULT_COUNTRY = "usa"
TRAINING_COUNTRIES = [
    "usa",
    "can",
    "gbr",
    "deu",
    "fra",
    "jpn",
    "aus",
    "chn",
    "ind",
    "bra",
]

INDICATORS = [
    IndicatorRequest("gdp", "NY.GDP.MKTP.CD"),
    IndicatorRequest("consumption_share", "NE.CON.PETC.ZS"),
    IndicatorRequest("unemployment", "SL.UEM.TOTL.ZS"),
    IndicatorRequest("capital_formation", "NE.GDI.TOTL.ZS"),
    IndicatorRequest("population", "SP.POP.TOTL"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate simulation parameters from macro data")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="ISO2/3 country code (e.g. usa)")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--years-back", type=int, default=15, help="Years of training history to use")
    parser.add_argument(
        "--training-countries",
        nargs="*",
        default=TRAINING_COUNTRIES,
        help="Countries used for model fitting",
    )
    parser.add_argument(
        "--scenario",
        choices=["baseline", "growth", "recession"],
        default="baseline",
        help="Optional macro scenario applied before calibration",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("config/calibrated/latest.json"),
        help="Path to write calibrated parameters JSON",
    )
    return parser.parse_args()


def apply_scenario(dataset: pd.DataFrame, scenario: str) -> pd.DataFrame:
    if scenario == "growth":
        return apply_unemployment_shock(
            apply_growth_shock(dataset, gdp_growth_pct=2.5),
            delta_pct_points=-1.5,
        )
    if scenario == "recession":
        return apply_consumption_shift(
            apply_unemployment_shock(dataset, delta_pct_points=3.0),
            delta_pct_points=-2.0,
        )
    return dataset


def main() -> None:
    args = parse_args()
    start_year = args.year - args.years_back

    training = build_training_dataset(
        args.training_countries,
        INDICATORS,
        start_year,
        args.year,
    )
    target = build_country_macro_dataset(args.country, INDICATORS, start_year, args.year)
    combined = pd.concat([training, target])
    combined = combined[combined.index <= args.year]
    combined = apply_scenario(combined, args.scenario)

    result = calibrate_parameters(combined, args.country, args.year)
    result.write(args.output)

    print(f"Calibration saved to {args.output}")
    for name, value in result.parameters.items():
        if name in {"gdp_per_capita", "unemployment_rate"}:
            continue
        diag = result.diagnostics.get(name, {})
        print(f"{name:<12} {value:.3f}  (r2={diag.get('r2', float('nan')):.2f}, mae={diag.get('mae', float('nan')):.3f})")


if __name__ == "__main__":
    main()
