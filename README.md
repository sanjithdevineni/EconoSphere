# MacroEcon Simulator

An agent-based economic simulation with real-time visualization and policy sandbox capabilities.

## Features

- **Agent-Based Modeling**: Simulates autonomous consumers, firms, government, and central bank
- **Policy Sandbox**: Test economic policies in real-time (taxes, interest rates, welfare, etc.)
- **Real-Time Dashboard**: Live visualization of economic indicators
- **Data-Driven**: Integrates real economic data from World Bank API
- **Crisis Scenarios**: Pre-configured scenarios (2008 recession, COVID crash, etc.)

## Project Structure

```
macroecon/
├── agents/              # Agent classes (Consumer, Firm, Government, CentralBank)
├── simulation/          # Core simulation engine
├── dashboard/           # Plotly Dash UI
├── data/               # Data integration and storage
├── utils/              # Helper functions
├── config.py           # Configuration parameters
├── requirements.txt    # Dependencies
└── main.py            # Entry point
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run simulation
python main.py
```

Then open http://localhost:8050 in your browser.

## Policy Controls

- **Tax Rate**: Adjust government tax rate (0-50%)
- **Interest Rate**: Set central bank interest rate (0-10%)
- **Welfare Payments**: Universal basic income amount
- **Government Spending**: Direct government expenditure

## Architecture

```
Dashboard (Dash) → Simulation Engine → Agents (Consumers, Firms, Gov, Central Bank)
                        ↓
                   Market Mechanisms (Labor, Goods)
                        ↓
                   Metrics Calculator (GDP, Unemployment, Inflation)
```

## Tech Stack

- **Simulation**: Python, Mesa (ABM framework), NumPy, Pandas
- **Visualization**: Plotly Dash
- **Data**: World Bank API
- **ML**: Scikit-learn (trend forecasting)
