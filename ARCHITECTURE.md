# EconoSphere - Technical Architecture

## System Overview

EconoSphere is a multi-page, agent-based macroeconomic simulator with international trade, AI-powered news analysis, and real-world calibration capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  MULTI-PAGE DASHBOARD (Dash)                    │
│  ┌────────────┬─────────────┬─────────────┬──────────────────┐ │
│  │ Simulation │ News        │ Validation  │ International    │ │
│  │ (/)        │ Insights    │ (/validate) │ Trade (/trade)   │ │
│  │            │ (/news)     │             │                  │ │
│  └────────────┴─────────────┴─────────────┴──────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
  ┌───────▼────────┐          ┌─────────▼──────────┐
  │ EconomyModel   │          │TradeEconomyModel   │
  │ (Domestic)     │          │(Multi-Country)     │
  └────────┬───────┘          └──────────┬─────────┘
           │                             │
    ┌──────┴──────┐         ┌────────────┴──────────────┐
    │             │         │                           │
┌───▼──────┐  ┌──▼────┐ ┌──▼────────┐    ┌──────────────▼─────┐
│Consumers │  │Firms  │ │Government │    │ Foreign Sectors    │
│(100+)    │  │(10+)  │ │Central    │    │  - China           │
│          │  │       │ │Bank       │    │  - EU              │
└──────────┘  └───────┘ └───────────┘    │  - Rest of World   │
                                         └────────────────────┘
           │
    ┌──────┴────────────┐
    │                   │
┌───▼──────────┐  ┌─────▼────────────┐
│ Markets      │  │ Economic Metrics │
│ - Labor      │  │ - GDP            │
│ - Goods      │  │ - Unemployment   │
│ - Capital    │  │ - Inflation      │
│ - FX         │  │ - Gini           │
└──────────────┘  └──────────────────┘

┌─────────────────────────────────────┐
│     EXTERNAL INTEGRATIONS           │
│  - World Bank API (data/calibrate)  │
│  - NewsAPI (real-time news)         │
│  - Azure OpenAI (AI analysis)       │
└─────────────────────────────────────┘
```

## Project Structure

```
EconoSphere/
├── agents/                          # Agent implementations
│   ├── consumer.py                 # Worker/household agents
│   ├── firm.py                     # Business agents
│   ├── government.py               # Fiscal authority
│   ├── central_bank.py             # Monetary authority
│   └── foreign_sector.py           # Trading partner countries
│
├── simulation/                      # Core simulation logic
│   ├── economy_model.py            # Base economic model
│   ├── trade_economy_model.py      # Extended with trade/FX
│   ├── markets.py                  # Market clearing algorithms
│   └── metrics.py                  # Economic indicator calculation
│
├── dashboard/                       # Multi-page web UI
│   ├── app.py                      # Main Dash application
│   └── pages/                      # Individual dashboard pages
│       ├── simulation.py           # Main simulator (/)
│       ├── news_insights.py        # AI news analysis (/news)
│       ├── validation.py           # Data validation (/validate)
│       └── trade.py                # Trade simulation (/trade)
│
├── data/                            # Data integration layer
│   ├── world_bank.py               # World Bank API client
│   ├── news_client.py              # NewsAPI integration
│   ├── news_analyzer.py            # AI-powered news analysis
│   └── calibration/                # ML calibration system
│       ├── world_bank_client.py    # Enhanced WB client
│       ├── parameter_fit.py        # ML parameter fitting
│       └── scenarios.py            # Scenario generation
│
├── narrative/                       # AI narrative generation
│   └── ai_narrator.py              # Real-time news generation
│
├── scripts/                         # Utility scripts
│   └── calibrate_economy.py        # Calibration CLI tool
│
├── config.py                        # Global configuration
├── main.py                         # Application entry point
└── requirements.txt                # Python dependencies
```

## Agent Types & Behaviors

### Consumer Agent

**Purpose**: Represents workers/households in the economy

**State Variables**:
- `wealth`: Current financial assets
- `income`: Wage from employment
- `employed`: Employment status (boolean)
- `employer`: Reference to employing firm

**Decision Logic**:
1. **Job Seeking**: Unemployed consumers apply to firms with openings
2. **Consumption**: Spend portion of wealth (MPC ≈ 0.9)
3. **Tax Payment**: Pay income taxes to government
4. **Welfare Receipt**: Receive transfers if unemployed

**Key Parameters**:
- `CONSUMER_WEALTH_SPEND_RATE`: Marginal propensity to consume
- `INITIAL_WEALTH`: Starting wealth endowment

### Firm Agent

**Purpose**: Represents businesses that hire, produce, and invest

**State Variables**:
- `capital`: Physical capital stock
- `cash`: Liquid financial assets
- `employees`: List of hired consumers
- `production`: Current output level
- `price`: Product price
- `inventory`: Unsold goods
- `labor_demand`: Desired workforce size

**Decision Logic**:
1. **Labor Demand**: Calculate workers needed based on expected demand, interest rates
2. **Production**: Output = A × K^α × L^γ (Cobb-Douglas)
3. **Pricing**: Adjust based on excess demand/supply
4. **Investment**: Expand capital when profitable and rates are low
5. **Hiring/Firing**: Adjust workforce gradually based on demand

**Key Parameters**:
- `productivity` (A): Total factor productivity
- `gamma` (γ): Returns to scale (0.7 typical)
- `depreciation_rate` (δ): Capital decay (5% per period)

### Government Agent

**Purpose**: Fiscal policy authority

**State Variables**:
- `tax_revenue`: Collected taxes (VAT, payroll, corporate)
- `total_spending`: Government expenditure
- `debt`: Accumulated deficits

**Decision Logic**:
1. **Tax Collection**: VAT on consumption, payroll on wages, corporate on profits
2. **Welfare Transfers**: Payments to unemployed
3. **Government Spending**: Direct demand injection
4. **Budget Accounting**: debt_t+1 = debt_t + (spending - revenue)

**Policy Levers** (user-controlled):
- `vat_rate`: 0-50%
- `payroll_rate`: 0-50%
- `corporate_rate`: 0-50%
- `welfare_payment`: $0-$2000
- `govt_spending`: $0-$50,000

### Central Bank Agent

**Purpose**: Monetary policy authority

**State Variables**:
- `interest_rate`: Lending rate to firms
- `inflation_target`: Desired inflation (2%)
- `auto_policy`: Taylor Rule enabled/disabled

**Decision Logic**:
1. **Manual Mode**: User sets interest rate
2. **Auto Mode (Taylor Rule)**:
   ```
   r_t = r* + 1.5(π_t - π*) - 0.5(u_t - u*)
   ```
   Where:
   - r* = neutral rate (3%)
   - π_t = current inflation
   - π* = target inflation (2%)
   - u_t = unemployment
   - u* = natural rate (5%)

**Policy Transmission**:
- Higher rates → Firms invest less → Lower demand → Lower inflation

### Foreign Sector Agent (NEW)

**Purpose**: Represents trading partner country

**State Variables**:
- `gdp`: Foreign economy size
- `price_level`: Foreign price level
- `exchange_rate`: E = Foreign Currency / Domestic Currency
- `tariff_rate_on_imports`: Retaliatory tariff
- `import_propensity`: Share of domestic demand from this country
- `exports_to_domestic`: Value sold to domestic economy
- `imports_from_domestic`: Value bought from domestic economy

**Decision Logic**:
1. **Supply Imports**: Provide goods based on competitiveness and tariffs
2. **Demand Exports**: Buy domestic goods based on prices and foreign GDP
3. **Retaliate**: Gradually adjust tariffs in response to domestic tariffs
4. **Exchange Rate Dynamics**:
   ```
   ΔE = -0.5(π_dom - π_for) + 0.3(r_dom - r_for) + 0.1(TB/GDP)
   ```
5. **Economic Evolution**: GDP and price level grow/evolve over time

**Countries**:
- **China**: GDP=$500k, import_propensity=12%, E₀=7.0 (Yuan/$)
- **EU**: GDP=$600k, import_propensity=8%, E₀=0.9 (€/$)
- **ROW**: GDP=$400k, import_propensity=6%, E₀=1.0

## Market Mechanisms

### Labor Market

**Clearing Algorithm**:
1. Firms post `labor_demand`
2. Unemployed consumers apply randomly
3. Match until all openings filled or no applicants remain
4. Calculate unemployment rate
5. Adjust wages based on tightness:
   ```
   wage_t+1 = wage_t × (1 + 0.1 × (labor_demand - labor_supply) / labor_supply)
   ```

**Dynamics**:
- Tight market (low unemployment) → Wages rise
- Slack market (high unemployment) → Wages fall

### Goods Market

**Clearing Algorithm**:
1. Consumers demand quantity based on wealth × MPC
2. Firms supply based on production + inventory
3. Trade + Imports add to supply, Exports subtract
4. Market clears at min(demand, supply)
5. Price adjustment:
   ```
   price_t+1 = price_t × [1 + θ_d × excess_demand + θ_c × cost_change]
   ```
   - θ_d = 0.1 (demand sensitivity)
   - θ_c = 0.1 (cost sensitivity)

**Dynamics**:
- Excess demand → Prices rise (inflation)
- Excess supply → Prices fall (deflation)

### Capital Market (Trade Model)

**Purpose**: Balance trade deficits/surpluses via financial flows

**Mechanism**:
```
Capital Inflow = -Trade Balance + Interest Differential Effect
```

**Dynamics**:
- Trade deficit → Capital inflows (foreign investment finances imports)
- Higher domestic rates → Attract more capital
- Capital flows affect exchange rates and foreign reserves

### FX Market (Trade Model)

**Central Bank Intervention**:
- Monitors exchange rate deviations from baseline
- Intervention threshold: ±15%
- Actions:
  - E too high (weak currency) → Sell reserves, buy domestic currency
  - E too low (strong currency) → Buy reserves, sell domestic currency
- Limited by foreign reserve availability

**Effects**:
- Stabilizes exchange rates
- Prevents catastrophic currency collapses
- Mimics real central bank behavior

## Economic Models

### Base Economy Model (economy_model.py)

**Closed economy** with:
- Consumers, Firms, Government, Central Bank
- Labor and Goods markets
- Fiscal and Monetary policy
- No international trade

**Step Sequence**:
1. Firms determine labor demand
2. Labor market clears
3. Firms produce
4. Consumers demand goods
5. Goods market clears
6. Payments (wages, profits)
7. Firms invest
8. Government collects taxes, pays welfare
9. Central Bank adjusts policy (if auto)
10. Calculate metrics

### Trade Economy Model (trade_economy_model.py)

**Extends base model** with:
- Multiple foreign sector agents
- Import/export flows
- Tariff policies
- Exchange rate dynamics
- Capital account balancing
- Central bank FX intervention

**Additional Steps**:
1. Calculate trade flows (imports, exports, tariffs)
2. Apply capital flows
3. Central bank FX intervention
4. Update export capacity
5. Track trade history

**Key Features**:
- Realistic import propensities (26% total)
- Dynamic export capacity growth
- Trade deficit dampening feedback
- Gradual tariff retaliation

## Dashboard Pages

### 1. Simulation Page (/)

**Components**:
- Policy control sliders (taxes, rates, spending)
- Real-time charts (GDP, unemployment, inflation, Gini)
- Scenario buttons (recession, inflation)
- Current metrics display
- AI narrative feed (if enabled)

**State Management**:
- dcc.Interval for auto-updates
- dcc.Store for simulation state
- Callbacks for user interactions

### 2. News Insights Page (/news)

**Components**:
- News article cards with AI analysis
- Timeframe selector
- Refresh button
- "Simulate This Policy" buttons

**AI Analysis Pipeline**:
1. Fetch articles from NewsAPI
2. Send to Azure OpenAI for analysis
3. Extract policy type, sentiment, impacts
4. Generate parameter suggestions
5. Display with confidence scores

**Fallback**: Heuristic analysis if AI unavailable

### 3. Validation Page (/validate)

**Components**:
- Simulation vs Actual data charts
- Trend forecasting
- Diagnostic metrics (R², MAE)
- Calibrated parameters display

**Data Flow**:
1. Fetch real data from World Bank API
2. Run simulation
3. Compare trajectories
4. Calculate validation metrics
5. Display ML-fitted parameters

### 4. International Trade Page (/trade)

**Components**:
- Tariff rate slider
- Trade scenario buttons (war, FTAs)
- 5 trade-specific charts:
  - Trade balance over time
  - Imports/Exports/Tariff revenue
  - Exchange rates (3 currencies)
  - Country-specific flows
  - Retaliation tariff tracking
- Trading partner status cards

**Real-Time Simulation**:
- Separate TradeEconomyModel instance
- Independent controls
- Full trade dynamics

## Data Integration

### World Bank API

**Purpose**: Real economic data for calibration and validation

**Fetched Indicators**:
- GDP (`NY.GDP.MKTP.CD`)
- Unemployment (`SL.UEM.TOTL.ZS`)
- Inflation (`FP.CPI.TOTL.ZG`)
- Tax revenue (`GC.TAX.TOTL.GD.ZS`)
- Government debt (`GC.DOD.TOTL.GD.ZS`)

**Usage**:
1. `scripts/calibrate_economy.py` fetches historical data
2. ML models fit parameters to match real trends
3. Output JSON with calibrated values
4. Load via `ECON_CALIBRATION_FILE` environment variable

### NewsAPI

**Purpose**: Real-time economic policy news

**Query**: `"federal reserve" OR "interest rates" OR "tariffs" OR "economic policy"`

**Rate Limits**: 100 requests/day (free tier)

**Fallback**: Sample news articles if API key missing

### Azure OpenAI

**Purpose**: AI-powered analysis and narrative generation

**Models Used**:
- GPT-4 for news analysis
- GPT-3.5 for narrative generation

**Features**:
1. **News Analysis**: Extract policy impacts from articles
2. **Narrative Generation**: Create economic news from simulation events
3. **Parameter Extraction**: Suggest simulation settings from news

**Fallback**: Heuristic rule-based analysis if API unavailable

## ML Calibration System

### Parameter Fitting (parameter_fit.py)

**Purpose**: Fit model parameters to match real economic data

**Algorithm**:
1. Fetch historical time series (15+ years)
2. For each parameter:
   - Train regression model on data
   - Predict parameter value
   - Validate with R², MAE
3. Output calibrated parameters

**Fitted Parameters**:
- `mpc`: Marginal propensity to consume
- `tfp_a`: Total factor productivity
- `gamma`: Returns to scale
- `depreciation`: Capital depreciation rate
- `unemployment_rate`: Baseline unemployment
- `gdp_per_capita`: Per-capita output

**Validation Metrics**:
- R² (coefficient of determination)
- MAE (mean absolute error)
- RMSE (root mean squared error)

## Advanced Features

### Capital Flows

**Formula**:
```
K_t = -TB_t + 0.5 × (r_dom - r_for) × GDP
```

Where:
- K_t = capital inflow (positive = inflow)
- TB_t = trade balance
- r_dom, r_for = domestic and foreign interest rates

**Purpose**: Model financial account balancing current account

### FX Intervention

**Trigger**: |E_t - E_baseline| / E_baseline > 0.15

**Action**:
```
If E too high (weak currency):
  Sell reserves = 0.1 × reserves × intervention_strength
  E_new = E × (1 - 0.5 × intervention_strength)

If E too low (strong currency):
  Buy reserves = 0.1 × reserves × intervention_strength
  E_new = E × (1 + 0.5 × intervention_strength)
```

**Limits**: Bounded by available foreign reserves

### Export Capacity

**Growth Formula**:
```
capacity_t+1 = capacity_t × (1 + 0.015 + balance_effect)
```

Where:
- 0.015 = 1.5% baseline growth
- balance_effect ∈ [-0.005, +0.005]

**Cap**: Maximum 5,000 units to prevent explosions

### Trade Deficit Dampening

**Trigger**: 8 out of last 10 periods in deficit

**Action**: Reduce all import_propensity by 10%

**Purpose**: Natural market feedback to persistent imbalances

## Performance & Scalability

**Current Configuration**:
- 100 consumers + 10 firms = 110+ agents
- ~50-100ms per simulation step
- Dashboard updates every 1000ms

**Bottlenecks**:
1. Agent.step() calls (O(n))
2. Market clearing algorithms
3. Metric calculations

**Optimization Strategies**:
- Reduce agent count for speed
- Use NumPy vectorization
- Pre-compute market equilibria
- Batch database operations

## Extension Points

### Adding New Agent Types

Example: Banking sector

```python
from mesa import Agent

class Bank(Agent):
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.deposits = 0
        self.loans = 0
        self.reserves = 0

    def step(self):
        # Accept deposits from consumers
        # Make loans to firms
        # Manage reserve requirements
        pass
```

Then add to `EconomyModel._create_agents()`

### Adding New Markets

Example: Asset market

```python
class AssetMarket:
    def clear_market(self, buyers, sellers):
        # Match asset buyers/sellers
        # Determine equilibrium price
        # Execute trades
        pass
```

Then call in `EconomyModel.step()`

### Adding New Metrics

Example: Capacity utilization

```python
# In metrics.py
def get_capacity_utilization(self, firms):
    total_capacity = sum(f.capital for f in firms)
    total_production = sum(f.production for f in firms)
    return total_production / max(total_capacity, 1)
```

## Testing

### Manual Testing Checklist

- [ ] All 4 pages load without errors
- [ ] Policy sliders update simulation
- [ ] Charts update in real-time
- [ ] Reset button works
- [ ] Scenario buttons trigger correct shocks
- [ ] News page fetches and displays articles
- [ ] AI analysis appears (or fallback)
- [ ] Validation shows actual data
- [ ] Trade page simulates properly
- [ ] FX intervention activates
- [ ] Calibration loads correctly

### Known Limitations

1. **Production Scaling**: Firm production doesn't scale with GDP growth due to labor constraints
2. **Trade Balance**: May be structurally imbalanced in long simulations
3. **Calibration Accuracy**: ML fits capture trends, not exact values
4. **AI Dependency**: Some features require Azure OpenAI access
5. **Agent Homogeneity**: All consumers/firms have similar parameters

## Technology Stack

**Core**:
- Python 3.8+
- Mesa (agent-based modeling)
- NumPy, Pandas

**Web**:
- Plotly Dash
- Dash Bootstrap Components

**Data**:
- wbgapi (World Bank)
- requests (NewsAPI)

**AI/ML**:
- scikit-learn (calibration)
- Azure OpenAI (analysis, narratives)

**Development**:
- Git (version control)
- dotenv (environment management)

## References

**Economic Theory**:
- Mankiw, N. Gregory. *Principles of Macroeconomics*
- Blanchard, O. *Macroeconomics*

**Agent-Based Modeling**:
- Mesa Documentation: https://mesa.readthedocs.io

**APIs**:
- World Bank API: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589
- NewsAPI: https://newsapi.org/docs
- Azure OpenAI: https://learn.microsoft.com/azure/ai-services/openai/

---

For more details, see:
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [INTERNATIONAL_TRADE.md](INTERNATIONAL_TRADE.md) - Trade model documentation
- [NEWS_INSIGHTS_README.md](NEWS_INSIGHTS_README.md) - AI features guide
