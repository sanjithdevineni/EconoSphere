"""
Helpers for building counterfactual scenarios before calibration.
"""

from __future__ import annotations

import pandas as pd


def apply_growth_shock(dataset: pd.DataFrame, gdp_growth_pct: float) -> pd.DataFrame:
    """Scale GDP by a growth percentage."""
    frame = dataset.copy()
    frame["gdp"] *= 1 + gdp_growth_pct / 100.0
    return frame


def apply_unemployment_shock(dataset: pd.DataFrame, delta_pct_points: float) -> pd.DataFrame:
    """Adjust unemployment rate by a number of percentage points."""
    frame = dataset.copy()
    frame["unemployment"] = frame["unemployment"] + delta_pct_points
    return frame


def apply_consumption_shift(dataset: pd.DataFrame, delta_pct_points: float) -> pd.DataFrame:
    """Tweak household consumption expenditure share."""
    frame = dataset.copy()
    frame["consumption_share"] = frame["consumption_share"] + delta_pct_points
    return frame
