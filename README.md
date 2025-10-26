<p align="left">
  <img src="Logo.png" alt="EconoSphere Dashboard" width="250">
</p>

# EconoSphere - Macroeconomic Simulator

### Watch the economy ripple with every decision.

Simulates entire economies with autonomous agents (consumers, firms, policies, central bank) to test economic outcomes or business strategies.
Takes into account the impact of tariffs, current trends and news, government crypto-currency reserves and relationships between different markets. 

## Visit the App: [EconoSphere](https://econosphere.azurewebsites.net)

## 🌟 Features

### Core Simulation
- **Agent-Based Modeling**: Autonomous consumers, firms, government, and central bank
- **Financial Markets**: Stock market with P/E ratios & cryptocurrency with macro-driven dynamics
- **Multi-Country Trade**: International trade with tariffs, retaliation, and exchange rates
- **Policy Sandbox**: Test fiscal and monetary policies in real-time
- **Real-World Calibration**: ML-powered parameter fitting from World Bank data

### Multi-Page Dashboard
- **Simulation Page**: Main economic simulator with policy controls
- **Financial Markets**: Stock & cryptocurrency markets with policy responsiveness
- **News Insights**: AI-powered analysis of economic news with one-click policy simulation
- **Validation Page**: Compare simulation output to real-world economic data
- **International Trade**: Multi-country trade simulation with tariffs and FX dynamics

### Advanced Features
- **News Simulation System**: Real world news fetching and simulating the policies suggested/being considered by the government, with AI summarization
- **AI Narrative System**: Real-time economic news generation powered by Azure OpenAI
- **Crypto-Macro Integration**: First simulator to model cryptocurrency's unique macro-policy relationships
- **Government Crypto Reserve**: Strategic reserve functionality like US Treasury proposals
- **Consumer Investment Portfolios**: Agents invest in stocks and crypto based on macro conditions
- **Capital Flows**: Financial account balancing and currency intervention
- **Central Bank FX Intervention**: Automatic exchange rate stabilization
- **Crisis Scenarios**: Pre-configured economic shocks (recession, inflation, trade wars, market crashes)

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/sanjithdevineni/EconoSphere.git
cd EconoSphere

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys
```

### Running the Simulator

```bash
python main.py
```

Then open http://localhost:8050 in your browser.

### Optional: Real-World Calibration

```bash
# Calibrate using World Bank data
python scripts/calibrate_economy.py --country USA --year 2023

# Use calibrated parameters
export ECON_CALIBRATION_FILE=config/calibrated/usa_2023.json
python main.py
```

## 📊 Dashboard Pages

### 1. Simulation
Main economic simulator with:
- **Policy Controls**: Tax rates, interest rates, government spending, welfare
- **Real-time Charts**: GDP, unemployment, inflation, inequality
- **Scenario Triggers**: Recession, inflation shocks, policy presets
- **Auto-Policy Mode**: Taylor Rule for automatic monetary policy

### 2. News Insights
AI-powered economic news analysis and **SIMULATION**:
- Fetch latest economic policy news (NewsAPI)
- AI analysis of policy impacts (Azure OpenAI)
- **One-click policy simulation from news articles**
- Impact predictions for GDP, inflation, unemployment

### 3. Validation
Compare simulation to real-world data:
- Time-series validation against actual economic data
- Trend forecasting with ML models
- Diagnostic metrics (R², MAE, RMSE)
- Historical scenario replay

### 4. Financial Markets
Stock and cryptocurrency markets that respond to macro policy:
- **Stock Market**: P/E ratio-based pricing, Fear & Greed index, sentiment tracking
- **Cryptocurrency**: Inflation hedge narrative, interest rate sensitivity, network effects
- **Consumer Investments**: Agents allocate savings to stocks/crypto based on risk and macro conditions
- **Government Crypto Reserve**: Enable strategic reserve purchases (like US Treasury proposals)
- **Policy Responsiveness**: Watch markets react to interest rate changes, government spending
- **Market Scenarios**: Stock crashes, crypto rallies, regulatory crackdowns
- **AI Insights Button**: Manual analysis of market conditions using Azure OpenAI

### 5. International Trade
Multi-country trade simulation:
- **Trading Partners**: China, EU, Rest of World
- **Tariff Policies**: Set import tariffs, watch retaliation
- **Exchange Rates**: PPP, interest rate parity, trade balance effects
- **Capital Flows**: Financial account balancing
- **FX Intervention**: Central bank currency stabilization
- **Trade Scenarios**: Trade wars, free trade agreements

## 🏗️ Project Structure

```
EconoSphere/
├── agents/                      # Agent classes
│   ├── consumer.py             # Consumer agents (workers + investors)
│   ├── firm.py                 # Firm agents (businesses)
│   ├── government.py           # Fiscal policy + crypto reserve
│   ├── central_bank.py         # Monetary policy authority
│   ├── stock_market.py         # Stock exchange (NEW!)
│   ├── crypto_market.py        # Cryptocurrency market (NEW!)
│   └── foreign_sector.py       # Trading partner countries
│
├── simulation/                  # Core simulation engine
│   ├── economy_model.py        # Base economy simulation
│   ├── financial_markets_model.py  # Extended with stocks & crypto (NEW!)
│   ├── trade_economy_model.py  # Extended model with trade
│   ├── markets.py              # Labor & goods markets
│   └── metrics.py              # Economic indicators
│
├── dashboard/                   # Multi-page web interface
│   ├── app.py                  # Main Dash application
│   └── pages/                  # Individual pages
│       ├── simulation.py       # Main simulator
│       ├── markets.py          # Financial markets (NEW!)
│       ├── news_insights.py    # News analysis
│       ├── validation.py       # Data validation
│       └── trade.py            # International trade
│
├── data/                        # Data integration
│   ├── world_bank.py           # World Bank API client
│   ├── news_client.py          # NewsAPI integration
│   ├── news_analyzer.py        # AI news analysis
│   └── calibration/            # ML parameter fitting
│       ├── world_bank_client.py
│       ├── parameter_fit.py
│       └── scenarios.py
│
├── narrative/                   # AI narrative generation
│   └── ai_narrator.py          # Economic news generator
│
├── scripts/                     # Utility scripts
│   └── calibrate_economy.py    # Calibration tool
│
├── config.py                    # Configuration parameters
├── main.py                     # Entry point
└── requirements.txt            # Dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# NewsAPI (optional - for real-time news)
NEWS_API_KEY=your_newsapi_key

# Azure OpenAI (required for AI features)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

# Optional: Custom calibration file
ECON_CALIBRATION_FILE=config/calibrated/usa_2023.json
```

### Simulation Parameters

Edit `config.py` to adjust:
- Number of agents (consumers, firms)
- Initial economic conditions
- Policy defaults
- Market parameters
- Update frequency

## 📈 Policy Controls

### Fiscal Policy (Government)
- **VAT Rate**: Value-added tax (0-50%)
- **Payroll Tax**: Tax on wages (0-50%)
- **Corporate Tax**: Tax on profits (0-50%)
- **Welfare Payments**: Unemployment benefits ($0-$2000)
- **Government Spending**: Direct expenditure ($0-$50,000)

### Monetary Policy (Central Bank)
- **Interest Rate**: Borrowing cost (0-10%)
- **Auto Policy**: Enable Taylor Rule for automatic rate adjustment

### Trade Policy (International)
- **Import Tariffs**: Tariff rate on all imports (0-100%)
- **Trade Scenarios**: Trigger trade wars or sign FTAs

## 🧪 Crisis Scenarios

Pre-configured economic shocks:
- **Recession**: Demand shock simulation (2008-style)
- **Inflation Shock**: Supply-side price surge
- **Trade War**: Multi-country tariff conflict
- **Free Trade Agreements**: Remove trade barriers

## 📐 Architecture

```
┌─────────────────────────────────────────────────────┐
│            Multi-Page Dashboard (Dash)              │
│  ┌──────────┬────────────┬────────────┬──────────┐  │
│  │Simulation│News Insights│ Validation │  Trade  │  │
│  └──────────┴────────────┴────────────┴──────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼───────┐           ┌─────────▼──────────┐
│ Economy Model │           │ Trade Economy Model│
│  (Domestic)   │           │  (Multi-Country)   │
└───────┬───────┘           └─────────┬──────────┘
        │                             │
        │  ┌──────────────────────────┤
        │  │                          │
┌───────▼──▼─────────────────┐   ┌────▼────────┐
│   Agent Ecosystem           │  │Foreign Sects│
│  - Consumers (100+)         │  │ - China     │
│  - Firms (10+)              │  │ - EU        │
│  - Government (1)           │  │ - ROW       │
│  - Central Bank (1)         │  └─────────────┘
└──────────┬──────────────────┘
           │
┌──────────▼──────────────────┐
│   Market Mechanisms         │
│  - Labor Market             │
│  - Goods Market             │
│  - Capital Flows            │
│  - FX Market                │
└─────────────────────────────┘
```

## 🛠️ Tech Stack

- **Simulation**: Python, Mesa (ABM framework), NumPy, Pandas
- **Visualization**: Plotly Dash, Dash Bootstrap Components
- **Data**: World Bank API (wbgapi), NewsAPI
- **ML**: Scikit-learn (parameter calibration, trend forecasting)
- **AI**: Azure OpenAI (news analysis, narrative generation)

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Setup and usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical architecture details
- **[FINANCIAL_MARKETS.md](FINANCIAL_MARKETS.md)**: Financial markets feature guide 
- **[INTERNATIONAL_TRADE.md](INTERNATIONAL_TRADE.md)**: Trade model documentation
- **[NEWS_INSIGHTS_README.md](NEWS_INSIGHTS_README.md)**: News feature guide

## 🔬 Advanced Features

### Real-World Calibration
Uses machine learning to fit model parameters from actual economic data:
- Fetches historical data from World Bank
- Trains regression models on time-series data
- Outputs calibrated parameters for realistic simulation
- Supports scenario generation (growth, recession)

### Capital Flows & FX Intervention
Realistic international finance:
- Trade deficits financed by capital inflows
- Interest rate differentials affect capital flows
- Central bank intervenes to stabilize exchange rates
- Foreign reserve management

### AI Narrative System
Real-time economic news generation:
- Monitors simulation for significant events
- Generates news articles with Azure OpenAI
- Provides economic context and analysis
- Appears in dashboard feed


## 🏆 Unique Differentiator

**FIRST economic simulator with integrated crypto-macro dynamics!** No other ABM simulator models how cryptocurrency responds to monetary policy:
- Government reserves → legitimacy boost (like US Treasury HOLDING major crypto-currency reserves from July 2025)
- Interest rate hikes → crypto crashes (like 2022)
- Inflation surges → crypto adoption (like 2020-2021)


Perfect for:
- **Policy Testing**: Government agencies analyzing crypto regulation
- **Business Strategy**: Investment firms modeling macro-market correlations
- **Education**: Teaching how monetary policy affects asset prices
- **Research**: Testing crypto-as-inflation-hedge hypothesis
