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
ENABLE_AI_NARRATIVE = True
NARRATIVE_COOLDOWN_STEPS = 2  # Steps to emit AI headlines after a trigger

INFLATION_TARGET = 0.02  # 2%
RESERVE_RATIO = 0.10  # 10%

# Market Parameters
INITIAL_WAGE = 1000
INITIAL_PRICE_LEVEL = 10
CONSUMER_PROPENSITY_TO_CONSUME = 0.58  # Marginal propensity to consume (MPC)
CONSUMER_WEALTH_SPEND_RATE = 0.025  # Share of wealth households spend each step

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

_calibration_path = Path(CALIBRATION_FILE)
if _calibration_path.exists():
    try:
        calibration_payload = json.loads(_calibration_path.read_text(encoding="utf-8"))
        calibration_params = calibration_payload.get("parameters", {})
        CALIBRATION_SOURCE = {
            "country": calibration_payload.get("country"),
            "year": calibration_payload.get("year"),
            "path": str(_calibration_path),
        }

        CONSUMER_PROPENSITY_TO_CONSUME = calibration_params.get(
            "mpc",
            CONSUMER_PROPENSITY_TO_CONSUME,
        )
        FIRM_PRODUCTIVITY = calibration_params.get(
            "tfp_a",
            FIRM_PRODUCTIVITY,
        )
        FIRM_GAMMA = calibration_params.get("gamma", FIRM_GAMMA)
        FIRM_DEPRECIATION_RATE = calibration_params.get(
            "depreciation",
            FIRM_DEPRECIATION_RATE,
        )
        CALIBRATED_UNEMPLOYMENT_RATE = calibration_params.get("unemployment_rate")
        CALIBRATED_GDP_PER_CAPITA = calibration_params.get("gdp_per_capita")
    except (OSError, ValueError, json.JSONDecodeError):
        CALIBRATION_SOURCE = {"error": "failed_to_load", "path": str(_calibration_path)}
