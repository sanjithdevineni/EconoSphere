# MacroEcon Simulator - Technical Architecture

## Project Structure

```
macroecon/
│
├── agents/                      # Agent-based models
│   ├── consumer.py             # Consumer agents (workers, spenders)
│   ├── firm.py                 # Firm agents (employers, producers)
│   ├── government.py           # Fiscal policy authority
│   └── central_bank.py         # Monetary policy authority
│
├── simulation/                  # Core simulation engine
│   ├── economy_model.py        # Main simulation orchestrator
│   ├── markets.py              # Labor & goods market mechanisms
│   └── metrics.py              # Economic indicators calculator
│
├── dashboard/                   # Web interface
│   └── app.py                  # Plotly Dash application
│
├── data/                        # External data integration
│   └── world_bank.py           # World Bank API client
│
├── utils/                       # Utilities
│   └── scenarios.py            # Pre-configured scenarios
│
├── config.py                   # Configuration parameters
├── main.py                     # Entry point
└── test_simulation.py          # Test script

```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD LAYER (Dash)                    │
│  - Policy Controls (sliders for tax, interest rate, etc.)   │
│  - Real-time Charts (GDP, unemployment, inflation, Gini)    │
│  - Scenario Buttons (recession, inflation, reset)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ User interactions trigger policy changes
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   SIMULATION ENGINE                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  EconomyModel (Mesa-based)                             │ │
│  │  - Manages all agents                                  │ │
│  │  - Executes time steps                                 │ │
│  │  - Applies policy changes                              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐  ┌───▼────┐  ┌──────▼────────┐
│ LABOR MARKET │  │ AGENTS │  │ GOODS MARKET  │
│              │  │        │  │               │
│ - Match      │  │ 100+   │  │ - Production  │
│   workers    │  │ Consum │  │ - Pricing     │
│   to firms   │  │ ers    │  │ - Supply/     │
│ - Wage       │  │        │  │   Demand      │
│   discovery  │  │ 10     │  │   matching    │
│              │  │ Firms  │  │               │
└──────────────┘  │        │  └───────────────┘
                  │ 1 Govt │
                  │        │
                  │ 1 CB   │
                  └────┬───┘
                       │
                       │ Generate metrics
                       │
              ┌────────▼────────┐
              │ METRICS CALC    │
              │ - GDP           │
              │ - Unemployment  │
              │ - Inflation     │
              │ - Gini          │
              └─────────────────┘
```

## Agent Interactions

### Time Step Flow

Each simulation step executes in this order:

```
1. LABOR DEMAND
   Firms → Central Bank: "What's the interest rate?"
   Firms calculate: "How many workers can we afford?"

2. LABOR MARKET CLEARING
   LaborMarket matches unemployed workers to firms
   Result: Employment rate, market wage

3. FISCAL POLICY
   Government → Consumers: "Pay taxes"
   Government → Unemployed: "Here's welfare"

4. CONSUMPTION
   Consumers → GoodsMarket: "I want to buy X goods at price P"

5. PRODUCTION
   Firms → GoodsMarket: "I'm producing Y goods"

6. GOODS MARKET CLEARING
   Match supply/demand, adjust prices
   Result: GDP, inflation, price level

7. PAYMENTS
   Firms → Workers: "Here's your wage"
   Firms calculate profit/loss

8. INVESTMENT
   Firms → Central Bank: "If rates are low, I'll invest"

9. POLICY ADJUSTMENT
   Central Bank (if auto-policy): Adjust rates based on inflation
   Government: Calculate budget balance/debt

10. METRICS
    Calculate and record all economic indicators
```

## Agent Behaviors

### Consumer
**State**: wealth, income, employed, employer
**Decisions**:
- How much to consume (based on propensity to consume)
- Seeks employment when unemployed

**Interactions**:
- Sells labor → Firms
- Pays taxes → Government
- Receives welfare → Government (if unemployed)
- Buys goods → Firms

### Firm
**State**: capital, employees, inventory, price, wage
**Decisions**:
- How many workers to hire (based on expected demand, interest rates)
- What price to charge (based on supply/demand)
- Whether to invest (based on profitability, interest rates)

**Interactions**:
- Hires labor → Consumers
- Pays wages → Consumers
- Sells goods → Consumers
- Checks borrowing cost → Central Bank

### Government
**State**: tax_rate, welfare_payment, govt_spending, debt
**Decisions**:
- Fiscal policy settings (controlled by user/dashboard)

**Interactions**:
- Collects taxes → Consumers
- Distributes welfare → Unemployed Consumers
- Injects spending → Economy (adds to aggregate demand)

### Central Bank
**State**: interest_rate, money_supply, inflation_target
**Decisions**:
- Interest rate (user-controlled or Taylor Rule auto-policy)
- Quantitative easing (emergency policy)

**Interactions**:
- Sets borrowing cost → Firms
- Optionally: Auto-adjusts rates based on inflation/unemployment

## Market Mechanisms

### Labor Market
**Purpose**: Match workers to jobs, determine wages

**Algorithm**:
1. Firms post job openings (labor_demand)
2. Unemployed workers apply
3. Random matching until jobs filled
4. Calculate unemployment rate
5. Adjust wages based on labor market tightness

**Key Dynamics**:
- Low unemployment → Wages rise (tight labor market)
- High unemployment → Wages fall (slack labor market)

### Goods Market
**Purpose**: Match production to consumption, determine prices

**Algorithm**:
1. Consumers state quantity demanded at current price
2. Firms produce based on workforce
3. Market clearing: min(demand, supply)
4. Price adjustment:
   - Demand > Supply → Prices rise
   - Supply > Demand → Prices fall
5. Calculate inflation rate

**Key Dynamics**:
- Excess demand → Inflation
- Excess supply → Deflation

## Economic Metrics

### GDP (Gross Domestic Product)
**Formula**: Sum of firm revenues
**Interpretation**: Total economic output

### Unemployment Rate
**Formula**: (Unemployed / Total Labor Force) × 100
**Interpretation**: % of workers without jobs

### Inflation Rate
**Formula**: (Current Price - Previous Price) / Previous Price × 100
**Interpretation**: Rate of price increase

### Gini Coefficient
**Formula**: Wealth distribution inequality measure (0-1)
**Interpretation**:
- 0 = Perfect equality
- 1 = Perfect inequality

## Policy Transmission Mechanisms

### Fiscal Policy (Government)

**Tax Rate** ↑:
```
Higher taxes
  → Consumers have less disposable income
  → Lower consumption
  → Lower demand for goods
  → Firms produce less
  → GDP ↓, Unemployment ↑
```

**Welfare Payments** ↑:
```
Higher welfare
  → Unemployed have more income
  → Higher consumption
  → Higher demand
  → Firms produce more
  → GDP ↑, Unemployment ↓
  (But also: Government debt ↑)
```

**Government Spending** ↑:
```
More govt spending
  → Direct demand injection
  → Firms produce more
  → Hire more workers
  → GDP ↑, Unemployment ↓
  (But also: Budget deficit ↑)
```

### Monetary Policy (Central Bank)

**Interest Rate** ↑:
```
Higher rates
  → Firms face higher borrowing costs
  → Less investment
  → Hire fewer workers
  → Unemployment ↑
  → Lower consumer spending
  → Lower demand → Lower inflation
```

**Interest Rate** ↓:
```
Lower rates
  → Cheaper borrowing
  → Firms invest more
  → Hire more workers
  → Unemployment ↓
  → More consumer spending
  → Higher demand → Higher inflation (risk)
```

## Data Integration

### World Bank API
**Purpose**: Calibrate simulation with real-world data

**Indicators Fetched**:
- GDP
- Unemployment rate
- Inflation rate
- Gini coefficient
- Tax revenue (% GDP)
- Government debt (% GDP)

**Usage**:
1. Fetch current US economic indicators
2. Use to set initial simulation parameters
3. Validate simulation output against real data

## Technology Stack

### Core Simulation
- **Mesa**: Agent-based modeling framework
  - Provides Agent base class
  - Scheduler for agent activation
  - Model structure
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation (for World Bank API)

### Dashboard
- **Plotly Dash**: Web dashboard framework
  - React-based UI components
  - Real-time chart updates
  - Callback-based interactivity
- **Dash Bootstrap Components**: UI styling

### Data
- **wbgapi**: World Bank API client
- **requests**: HTTP client for any additional APIs

### Development
- **Python 3.8+**
- Standard library: random, typing, etc.

## Performance Considerations

### Scalability
- **Current**: 100 consumers, 10 firms runs smoothly
- **Bottleneck**: Agent.step() calls in each time step
- **Optimization strategies**:
  1. Reduce agent count for faster simulation
  2. Batch operations where possible
  3. Use NumPy arrays instead of loops
  4. Pre-compute market clearing instead of iterative

### Update Frequency
- **Dashboard refresh**: 1000ms (1 second) by default
- **Simulation step**: ~50-100ms with current agent count
- **Trade-off**: More agents = realism, Fewer = speed

## Extension Points

### Adding New Agent Types
1. Create new class inheriting from `mesa.Agent`
2. Implement `__init__` and `step` methods
3. Add to `EconomyModel._create_agents()`
4. Update market mechanisms if needed

### Adding New Policies
1. Add parameter to `config.py`
2. Create setter method in `EconomyModel`
3. Add slider in dashboard `app.py` layout
4. Wire callback to update policy

### Adding New Markets
1. Create new market class in `simulation/markets.py`
2. Implement `clear_market()` method
3. Add to `EconomyModel.__init__()`
4. Call in `EconomyModel.step()`

### Adding New Metrics
1. Add calculation method to `MetricsCalculator`
2. Add to history dict
3. Call in `get_all_metrics()`
4. Create chart in dashboard

## Known Limitations

1. **Simplified markets**: No price stickiness, perfect information
2. **No money explicitly**: Money is implicit in wealth/capital
3. **No banking sector**: No fractional reserve, no credit creation
4. **No international trade**: Closed economy
5. **Homogeneous agents**: All consumers/firms similar (could add heterogeneity)
6. **Deterministic (mostly)**: Random matching but predictable behavior

## Future Enhancements

### High Priority
- [ ] Add scenario presets to dashboard dropdown
- [ ] Export simulation data to CSV
- [ ] Simple ML prediction overlay (ARIMA)
- [ ] Parameter calibration from World Bank data

### Medium Priority
- [ ] Banking sector with credit creation
- [ ] Heterogeneous agents (different skills, productivities)
- [ ] International trade (import/export)
- [ ] More sophisticated price/wage dynamics

### Low Priority
- [ ] Multi-player mode (different users control policies)
- [ ] Historical scenario replay (2008, 2020, etc.)
- [ ] Agent genealogy visualization
- [ ] Sound effects for crises

## Testing

### Unit Tests (Future)
- Test individual agent behaviors
- Test market clearing algorithms
- Test metrics calculations

### Integration Tests
- `test_simulation.py`: Basic end-to-end test
- Verify simulation runs without crashes
- Check metrics are reasonable ranges

### Manual Testing Checklist
- [ ] Start simulation runs smoothly
- [ ] All sliders update policies
- [ ] Charts update in real-time
- [ ] Reset clears history
- [ ] Crisis buttons trigger events
- [ ] Auto-policy adjusts rates

## Hackathon Success Tips

### What Judges Love
1. **Live demo**: Real-time interaction is impressive
2. **Clear impact**: Show before/after policy changes
3. **Technical depth**: Explain agent-based modeling
4. **Practical use**: Business strategy testing, education

### Demo Script
1. "This simulates a real economy with autonomous agents"
2. Show baseline → Adjust tax → Watch impact
3. Trigger recession → Implement response → Show recovery
4. "Use cases: Policy testing, business strategy, education"

### Potential Questions & Answers

**Q: How is this different from a spreadsheet model?**
A: Agent-based models capture emergent behavior - the interactions between agents create realistic dynamics you can't get from equations alone.

**Q: How accurate is it?**
A: It captures qualitative dynamics well (higher taxes → lower growth). For quantitative accuracy, you'd calibrate against real data using our World Bank integration.

**Q: What's the business application?**
A: Test pricing strategies, market entry scenarios, competitive dynamics in a simulated market before risking real capital.

**Q: Could this scale to millions of agents?**
A: Current Python implementation wouldn't scale that far, but the architecture could be ported to a distributed system (Spark, Ray) for large-scale simulation.

Good luck!
