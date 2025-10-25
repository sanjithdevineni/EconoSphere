"""
Machine-learning based calibration for simulation parameters.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class CalibrationResult:
    """Container for calibrated parameters and diagnostics."""

    year: int
    country: str
    parameters: dict[str, float]
    diagnostics: dict[str, dict[str, float]]

    def to_json(self) -> str:
        return json.dumps(
            {
                "country": self.country,
                "year": self.year,
                "parameters": self.parameters,
                "diagnostics": self.diagnostics,
            },
            indent=2,
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")


def engineer_features(dataset: pd.DataFrame) -> pd.DataFrame:
    """Derive model features from macroeconomic indicators."""
    features = dataset.copy()
    features["gdp_per_capita"] = features["gdp"] / features["population"]
    features["consumption_ratio"] = features["consumption_share"] / 100.0
    features["investment_ratio"] = features["capital_formation"] / 100.0
    features["unemployment_ratio"] = features["unemployment"] / 100.0
    features["productivity_proxy"] = features["gdp_per_capita"] * (
        1 - features["unemployment_ratio"]
    )
    return features[
        [
            "gdp_per_capita",
            "consumption_ratio",
            "investment_ratio",
            "unemployment_ratio",
            "productivity_proxy",
        ]
    ]


def derive_training_labels(features: pd.DataFrame) -> pd.DataFrame:
    """
    Generate pseudo labels for MPC, productivity, returns to scale, and depreciation.

    These heuristics bootstrap ML fitting without curated labelled data.
    """
    labels = pd.DataFrame(index=features.index)
    labels["mpc"] = np.clip(features["consumption_ratio"], 0.45, 0.95)
    labels["tfp_a"] = np.clip(features["productivity_proxy"] / 60000.0, 0.1, 5.0)
    labels["gamma"] = np.clip(0.55 + features["investment_ratio"] * 0.0035, 0.45, 0.9)
    labels["depreciation"] = np.clip(
        0.02 + features["investment_ratio"] * 0.0008,
        0.02,
        0.12,
    )
    return labels


def fit_regressor(X: pd.DataFrame, y: pd.Series) -> tuple[GradientBoostingRegressor, dict[str, float]]:
    """Train a gradient boosting regressor with evaluation metrics."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=13
    )

    model = GradientBoostingRegressor(
        n_estimators=350,
        learning_rate=0.05,
        max_depth=3,
        random_state=13,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    metrics = {
        "r2": float(r2_score(y_test, predictions)),
        "mae": float(mean_absolute_error(y_test, predictions)),
    }
    return model, metrics


def calibrate_parameters(
    dataset: pd.DataFrame,
    target_country: str,
    target_year: int,
    baseline_parameters: Iterable[str] = ("mpc", "tfp_a", "gamma", "depreciation"),
) -> CalibrationResult:
    """
    Fit ML models for macro parameters and return target-year estimates.
    """
    features = engineer_features(dataset)
    labels = derive_training_labels(features)

    index_key = (target_country.upper(), target_year)
    if index_key not in features.index:
        raise ValueError("Target country/year not present in dataset")

    target_row = features.loc[index_key]

    fitted: dict[str, float] = {}
    diagnostics: dict[str, dict[str, float]] = {}

    for param in baseline_parameters:
        model, metrics = fit_regressor(features, labels[param])
        fitted[param] = float(model.predict(target_row.to_frame().T)[0])
        diagnostics[param] = metrics

    fitted["unemployment_rate"] = float(features.loc[target_year, "unemployment_ratio"])
    fitted["gdp_per_capita"] = float(features.loc[target_year, "gdp_per_capita"])

    return CalibrationResult(
        year=target_year,
        country=target_country.upper(),
        parameters=fitted,
        diagnostics=diagnostics,
    )
