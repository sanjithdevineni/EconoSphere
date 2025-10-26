"""
Configuration parameters for the economic simulation
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Simulation Parameters
NUM_CONSUMERS = 100
NUM_FIRMS = 10
SIMULATION_STEPS = 100
TIME_STEP_DURATION = 1  # Each step = 1 quarter (3 months)

# Initial Economic Conditions
INITIAL_MONEY_SUPPLY = 1_000_000
INITIAL_CONSUMER_WEALTH_MEAN = 5000
INITIAL_CONSUMER_WEALTH_STD = 2000
INITIAL_FIRM_CAPITAL_MEAN = 50000
INITIAL_FIRM_CAPITAL_STD = 20000

# Government Parameters
INITIAL_VAT_RATE = 0.15  # 15% Value Added Tax
INITIAL_PAYROLL_RATE = 0.10  # 10% Payroll tax
INITIAL_CORPORATE_RATE = 0.20  # 20% Corporate tax
INITIAL_WELFARE_PAYMENT = 350
INITIAL_GOVT_SPENDING = 3000

# Central Bank Parameters
INITIAL_INTEREST_RATE = 0.05  # 5%

# Demo & AI Features
ENABLE_AI_NARRATIVE = True  # Disabled - use manual "AI Insights" button instead
NARRATIVE_COOLDOWN_STEPS = 2  # Steps to emit AI headlines after a trigger

INFLATION_TARGET = 0.02  # 2%
RESERVE_RATIO = 0.10  # 10%

# Market Parameters
INITIAL_WAGE = 1000
INITIAL_PRICE_LEVEL = 10
CONSUMER_PROPENSITY_TO_CONSUME = 0.58  # Marginal propensity to consume (MPC)
CONSUMER_WEALTH_SPEND_RATE = 0.025  # Share of wealth households spend each step

# Investment & Financial Markets Parameters
CONSUMER_RISK_TOLERANCE = 0.3  # Risk tolerance (0-1): affects crypto vs stock allocation

# Labor Adjustment Parameters
LABOR_ADJUSTMENT_RATE = 0.25  # Max fractional change in firm workforce per period
MIN_EXPECTED_DEMAND_PER_FIRM = 2  # Floor on expected demand to prevent collapse

# Firm Production Parameters
FIRM_PRODUCTIVITY = 2.0  # Total factor productivity (TFP)
FIRM_GAMMA = 0.7  # Returns to scale parameter (0.6-0.8 typical)
FIRM_DEPRECIATION_RATE = 0.05  # Capital depreciation rate per period (5%)
FIRM_INVESTMENT_SHARE = 0.1  # Share of profit invested (xi)
FIRM_PRODUCTIVITY_GROWTH_COEFF = 0.1  # Productivity growth coefficient (kappa)

# Price Adjustment Parameters
PRICE_DEMAND_SENSITIVITY = 0.02  # theta_d: sensitivity to excess demand (0.05-0.2 typical)
PRICE_COST_SENSITIVITY = 0.05  # theta_c: sensitivity to cost changes (0.05-0.2 typical)
MAX_EXCESS_DEMAND_RATIO = 0.8  # Cap on demand vs supply used in pricing
MAX_PRICE_ADJUSTMENT = 0.02  # Maximum fractional price change per step
DEMAND_BALANCE_TOLERANCE = 0.02  # Range within which demand vs supply is treated as balanced
DEMAND_ADJUSTMENT_ALPHA = 0.35  # Speed at which firms update expected demand after shortages

# Wage Adjustment Parameters
WAGE_ADJUSTMENT_SPEED = 0.05  # eta: wage response to labor shortage (0.05-0.15 typical)

# Dashboard Settings
UPDATE_INTERVAL = 1000  # milliseconds
PORT = 8050
DEBUG_MODE = True

# Calibration Overrides
CALIBRATION_FILE = os.environ.get(
    "ECON_CALIBRATION_FILE",
    "config/calibrated/latest.json",
)
CALIBRATION_SOURCE = None
CALIBRATED_UNEMPLOYMENT_RATE = None
CALIBRATED_GDP_PER_CAPITA = None
CALIBRATED_PARAMETERS = None
CALIBRATION_DIAGNOSTICS = None

_DEFAULT_PARAMETERS = {
    "CONSUMER_PROPENSITY_TO_CONSUME": CONSUMER_PROPENSITY_TO_CONSUME,
    "FIRM_PRODUCTIVITY": FIRM_PRODUCTIVITY,
    "FIRM_GAMMA": FIRM_GAMMA,
    "FIRM_DEPRECIATION_RATE": FIRM_DEPRECIATION_RATE,
}

def _apply_calibration_payload(payload: dict[str, object], path: Path | None) -> None:
    global CONSUMER_PROPENSITY_TO_CONSUME, FIRM_PRODUCTIVITY, FIRM_GAMMA, FIRM_DEPRECIATION_RATE
    global CALIBRATION_SOURCE, CALIBRATED_UNEMPLOYMENT_RATE, CALIBRATED_GDP_PER_CAPITA
    global CALIBRATED_PARAMETERS, CALIBRATION_DIAGNOSTICS

    calibration_params = payload.get("parameters", {}) if payload else {}

    CONSUMER_PROPENSITY_TO_CONSUME = calibration_params.get(
        "mpc",
        _DEFAULT_PARAMETERS["CONSUMER_PROPENSITY_TO_CONSUME"],
    )
    FIRM_PRODUCTIVITY = calibration_params.get(
        "tfp_a",
        _DEFAULT_PARAMETERS["FIRM_PRODUCTIVITY"],
    )
    FIRM_GAMMA = calibration_params.get("gamma", _DEFAULT_PARAMETERS["FIRM_GAMMA"])
    FIRM_DEPRECIATION_RATE = calibration_params.get(
        "depreciation",
        _DEFAULT_PARAMETERS["FIRM_DEPRECIATION_RATE"],
    )

    CALIBRATED_UNEMPLOYMENT_RATE = calibration_params.get("unemployment_rate") if calibration_params else None
    CALIBRATED_GDP_PER_CAPITA = calibration_params.get("gdp_per_capita") if calibration_params else None
    CALIBRATED_PARAMETERS = dict(calibration_params) if calibration_params else None
    CALIBRATION_DIAGNOSTICS = payload.get("diagnostics", {}) if payload else {}

    if payload:
        CALIBRATION_SOURCE = {
            "country": payload.get("country"),
            "year": payload.get("year"),
            "path": str(path) if path else None,
        }
    elif path:
        CALIBRATION_SOURCE = {"error": "failed_to_load", "path": str(path)}
    else:
        CALIBRATION_SOURCE = None


def apply_calibration(calibration_path: str | Path | None) -> None:
    """Load calibration from the given path, or reset to defaults if None."""
    if calibration_path is None:
        _apply_calibration_payload({}, None)
        return

    path = Path(calibration_path)
    if not path.exists():
        _apply_calibration_payload({}, path)
        return

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        payload = None
    _apply_calibration_payload(payload or {}, path)


def list_calibration_files(directory: str | Path = "config/calibrated") -> list[Path]:
    """Return available calibration JSON files sorted alphabetically."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    return sorted(p for p in dir_path.glob("*.json") if p.is_file())


_calibration_path = Path(CALIBRATION_FILE)
if _calibration_path.exists():
    apply_calibration(_calibration_path)
else:
    apply_calibration(None)
