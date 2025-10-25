"""
Configuration parameters for the economic simulation
"""

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
INITIAL_WELFARE_PAYMENT = 500
INITIAL_GOVT_SPENDING = 10000

# Central Bank Parameters
INITIAL_INTEREST_RATE = 0.05  # 5%
INFLATION_TARGET = 0.02  # 2%
RESERVE_RATIO = 0.10  # 10%

# Market Parameters
INITIAL_WAGE = 1000
INITIAL_PRICE_LEVEL = 10
CONSUMER_PROPENSITY_TO_CONSUME = 0.7  # Marginal propensity to consume (MPC)

# Firm Production Parameters
FIRM_PRODUCTIVITY = 2.0  # Total factor productivity (TFP)
FIRM_GAMMA = 0.7  # Returns to scale parameter (0.6-0.8 typical)
FIRM_DEPRECIATION_RATE = 0.05  # Capital depreciation rate per period (5%)
FIRM_INVESTMENT_SHARE = 0.1  # Share of profit invested (xi)
FIRM_PRODUCTIVITY_GROWTH_COEFF = 0.1  # Productivity growth coefficient (kappa)

# Price Adjustment Parameters
PRICE_DEMAND_SENSITIVITY = 0.1  # theta_d: sensitivity to excess demand
PRICE_COST_SENSITIVITY = 0.1  # theta_c: sensitivity to cost changes

# Dashboard Settings
UPDATE_INTERVAL = 1000  # milliseconds
PORT = 8050
DEBUG_MODE = True
