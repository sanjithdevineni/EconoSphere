# Financial Markets Feature - Technical Documentation

## Overview

EconoSphere includes a sophisticated **Financial Markets** system that integrates stock and cryptocurrency markets into the agent-based macroeconomic simulation. This is **the first economic simulator to model cryptocurrency's unique relationships with monetary policy**.

## 🎯 Unique Differentiator

**No other ABM simulator does this:** We model how cryptocurrency responds to macroeconomic policy in realistic ways:

- **Interest Rate Hikes** → Crypto crashes (like 2022 when Fed hiked rates, Bitcoin fell 70%)
- **Inflation Surges** → Crypto adoption rises (like 2020-2021 stimulus, Bitcoin rallied 800%)
- **Government Reserves** → Legitimacy boost & price pump (like US Treasury crypto proposals)

This creates a playground for testing:
- Crypto-as-inflation-hedge hypothesis
- Impact of government crypto adoption
- Monetary policy transmission to digital assets
- Consumer portfolio allocation under macro uncertainty

## 📊 Architecture

### Components

```
Financial Markets System
│
├── Stock Market (agents/stock_market.py)
│   ├── P/E Ratio Pricing
│   ├── Fear & Greed Index (0-100)
│   ├── Sentiment Tracking
│   └── Dividend Modeling
│
├── Crypto Market (agents/crypto_market.py)
│   ├── Inflation Hedge Dynamics
│   ├── Interest Rate Sensitivity
│   ├── Network Effects (Metcalfe's Law)
│   ├── Government Legitimacy Boost
│   └── Regulatory Sentiment
│
├── Consumer Investments (agents/consumer.py)
│   ├── Investment Portfolios
│   ├── Risk Tolerance
│   ├── Macro-Responsive Allocation
│   └── Rebalancing Logic
│
├── Government Crypto Reserve (agents/government.py)
│   ├── Strategic Purchases
│   ├── Reserve Management
│   └── Market Impact
│
└── Financial Markets Model (simulation/financial_markets_model.py)
    ├── Extends Base Economy
    ├── Market Updates
    ├── Consumer Investment Processing
    └── AI Insights Integration
```

## 🏛️ Stock Market

### Pricing Model

Stock prices use **P/E ratio approach** (realistic financial modeling):

```python
# P/E ratio depends on interest rates
base_pe = 15
rate_adjustment = -(interest_rate - 0.03) * 100
pe_ratio = max(5, base_pe + rate_adjustment)

# Price = Earnings × P/E
fundamental_value = firm.profit * pe_ratio
```

**Key Dynamics:**
- **Low rates** → High P/E multiples → Higher stock prices
- **High rates** → P/E compression → Stock prices fall
- **Strong earnings** → Higher stock prices
- **Sentiment** → ±20% price variation

### Fear & Greed Index

Tracks market psychology (0-100 scale):

- **0-25**: Extreme Fear (crash territory)
- **25-45**: Fear (bearish)
- **45-55**: Neutral
- **55-75**: Greed (bullish)
- **75-100**: Extreme Greed (bubble risk)

**Calculation:**
```python
# Based on multiple factors
price_momentum = recent_returns * 50
volatility_factor = (1 - current_volatility) * 20
sentiment_factor = market_sentiment * 30

fear_greed = price_momentum + volatility_factor + sentiment_factor
fear_greed = max(0, min(100, fear_greed))
```

### Crash Scenarios

Trigger via button: `-30% instant drop`

Effects:
- Sentiment crashes to -0.9
- Fear & Greed → Extreme Fear
- Consumers sell stocks, hold cash
- Economic confidence falls

## 💎 Cryptocurrency Market

### Core Innovation: Macro-Driven Dynamics

This is the **hackathon differentiator!** Crypto price responds to:

#### 1. Inflation Hedge Narrative

```python
# When inflation rises above 2%, people flee to crypto
inflation_excess = max(0, inflation - 0.02)
inflation_boost = inflation_excess * 5.0 * inflation_hedge_belief
```

- **2% inflation (target)** → No effect
- **4% inflation** → Crypto adoption rises
- **6%+ inflation** → Strong crypto demand (digital gold narrative)
- **Belief strengthens** when crypto rises during high inflation

**Real Example:** 2020-2021 stimulus → 8% inflation → Bitcoin $69k

#### 2. Interest Rate Sensitivity

```python
# High rates make crypto less attractive (opportunity cost)
rate_excess = interest_rate - 0.03
rate_drag = rate_excess * -8.0  # Strong negative effect
```

- **Low rates (0-2%)** → Crypto bullish (no alternative yield)
- **Neutral rates (3%)** → Balanced
- **High rates (5%+)** → Crypto bearish (can earn yield elsewhere)

**Real Example:** 2022 Fed hikes to 5% → Bitcoin crashed $69k → $16k

#### 3. Risk-On / Risk-Off

```python
# Crypto is 2x levered to stocks
risk_sentiment = stock_market_return * 2.0
```

- **Stocks rally** → Crypto rallies harder
- **Stocks crash** → Crypto crashes harder
- Captures "risk appetite" transmission

#### 4. Government Legitimacy Effect

```python
if government_holdings > 0:
    legitimacy_boost = log10(government_holdings + 1) * 0.05
    adoption_rate *= 1.1  # People follow government
```

**This is the BIG narrative moment!**
- Government buys crypto → Immediate price pump
- Regulatory sentiment improves
- Mainstream adoption accelerates
- Network effects amplify

**Real-World Inspiration:** US Treasury crypto reserve debates, El Salvador Bitcoin law

#### 5. Network Effects

```python
# Metcalfe's Law: Value ~ n² (but with diminishing returns)
network_effect = log(1 + adoption_rate * 100) * 0.02
```

- More adopters → More valuable
- Logarithmic scaling prevents explosion
- Baseline "true believers" provide price floor

### Price Stabilization Mechanisms

To prevent unrealistic behavior:

```python
# Mean reversion to fundamental value ($50k)
price_deviation = (price - 50000) / 50000
mean_reversion = -price_deviation * 0.01  # 1% pull

# Hard bounds
price = max(5000, min(500000, price))  # $5k - $500k

# Max daily change
max_daily_change = 0.10  # 10% per step
```

### Crypto Scenarios

**💥 Crypto Crash** (-50%):
- Regulatory crackdown, exchange failure
- Sentiment → Extreme Fear
- Regulatory sentiment falls

**🚀 Crypto Rally** (+30%):
- ETF approval, institutional adoption
- Sentiment → Greed
- Adoption surge

**🏦 Government Reserve**:
- Strategic crypto purchases
- Massive legitimacy boost
- Price pump based on % of market cap
- Ongoing accumulation

## 👥 Consumer Investment Behavior

Consumers invest savings in stocks and crypto based on:

### Portfolio Allocation

```python
# Base allocation
base_stock_allocation = 0.7  # 70% stocks
base_crypto_allocation = 0.3  # 30% crypto

# Adjust for inflation
if inflation > 0.04:  # 4% inflation
    crypto_allocation = 0.5  # Shift to crypto hedge
if inflation > 0.06:  # 6% inflation
    crypto_allocation = 0.7  # Heavy crypto allocation
```

### Investment Logic

1. **Calculate investable amount**:
   ```python
   disposable_income = income - essential_spending
   investment_amount = disposable_income * investment_propensity
   ```

2. **Allocate based on macro**:
   - High inflation → More crypto (inflation hedge)
   - Low inflation → More stocks (growth)
   - Risk tolerance varies by consumer

3. **Rebalance when needed**:
   - If cash < 20% of wealth → Sell investments
   - Prevents liquidity crises

## 🏛️ Government Crypto Reserve

Like US Treasury Bitcoin proposals!

### How It Works

1. **Enable Reserve**:
   ```python
   model.enable_government_crypto_reserve(annual_budget=500000)
   ```

2. **Initial Purchase**:
   - Large one-time buy (10x annual budget)
   - Creates dramatic market impact
   - Signals serious commitment

3. **Ongoing Accumulation**:
   - Government buys crypto periodically
   - Dollar-cost averaging approach
   - Builds strategic reserve over time

### Market Impact

```python
# Calculate purchase as % of market cap
market_cap = crypto_price * circulating_supply
purchase_pct = purchase_amount / market_cap

# Price impact with power function (non-linear)
price_pump = (purchase_pct ** 0.5) * 3.0
price_pump = min(0.50, price_pump)  # Cap at 50%
```

**Example:**
- Market cap: $4.5 billion
- Purchase: $1 million
- % of market: 0.022%
- Price pump: ~9.5%

Plus secondary effects:
- Regulatory sentiment +0.2
- Adoption rate +10%
- Belief in legitimacy strengthens

## 📈 Dashboard Features

### Charts (7 total)

1. **Stock Market Index**
   - Tracks composite index of all firms
   - Shows market trends

2. **Cryptocurrency Price**
   - Real-time crypto price
   - Shows macro policy impacts

3. **Fear & Greed Index**
   - Market psychology indicator
   - Helps predict crashes/rallies

4. **Market Capitalizations**
   - Total value of stocks
   - Total value of crypto
   - Comparison view

5. **Consumer Holdings**
   - How much consumers own in stocks
   - How much in crypto
   - Portfolio allocation

6. **Government Crypto Reserve**
   - Reserve size (coins)
   - Reserve value ($)
   - Tracks accumulation

7. **Crypto Adoption Rate**
   - % of population holding crypto
   - Network effect tracking

### Interactive Controls

**Interest Rate Slider** (0-10%):
- Real-time policy changes
- Watch markets respond instantly

**Government Spending** ($0-$50k):
- Affects corporate earnings
- Impacts stock valuations

**Government Crypto Reserve**:
- Enable/disable button
- Set annual budget
- Manual purchase button

### Scenario Buttons

- **📉 Stock Crash**: -30% drop
- **💥 Crypto Crash**: -50% drop
- **🚀 Crypto Rally**: +30% pump
- **🏦 Enable Crypto Reserve**: Strategic reserve
- **🤖 Generate AI Insights**: Azure OpenAI analysis

### AI Insights Feature

Manual button (not automatic to prevent API spam):

```python
# Analyzes current market state
- Stock index level and trend
- Crypto price and volatility
- Fear & Greed reading
- Portfolio allocations
- Government reserve status

# Returns AI-generated insights
- Market sentiment summary
- Risk assessment
- Policy recommendations
- Correlation analysis
```

Uses Azure OpenAI (GPT-4o) for sophisticated analysis.

## 🧪 Testing & Validation

### Test Suites

**test_scenarios.py**: Comprehensive scenario testing
- Government reserve price impact
- Interest rate effects
- Inflation correlation
- Crash/rally scenarios
- Parameter persistence

**test_parameter_changes.py**: Dynamic parameter testing
- Interest rate changes during simulation
- Government policy changes
- Scenario triggers
- Market responsiveness

**test_markets_simulation.py**: 150-step stability test
- No explosions or crashes
- Realistic volatility patterns
- Stable price ranges
- Normal behavior analysis

### Expected Behaviors

**Interest Rate Hike (3% → 8%)**:
- Crypto: -20% to -60%
- Stocks: -5% to -15%
- Fear & Greed: Falls

**Interest Rate Cut (3% → 1%)**:
- Crypto: +100% to +600%
- Stocks: +50% to +200%
- Fear & Greed: Rises

**Government Reserve Enabled ($500k budget)**:
- Immediate: +8% to +15% crypto pump
- Long-term: Sustained adoption growth
- Regulatory sentiment improves

**Inflation Surge (2% → 8%)**:
- Crypto adoption increases
- Stock P/E ratios compress
- Real returns matter more

## 🔧 Configuration

### Key Parameters (config.py)

```python
# Consumer investment behavior
CONSUMER_RISK_TOLERANCE = 0.3  # 30% willing to invest
CONSUMER_INVESTMENT_PROPENSITY = 0.2  # 20% of income

# AI Features
ENABLE_AI_NARRATIVE = True  # Enable auto-narratives (careful with API costs!)
```

### Crypto Market Parameters

In `agents/crypto_market.py`:

```python
# Supply (affects market cap and price impact)
max_supply = 100_000
circulating_supply = 90_000

# Volatility
volatility = 0.08  # 8% daily (balanced for demo)

# Macro sensitivity
inflation_sensitivity = 5.0
rate_sensitivity = -8.0  # Strong negative
adoption_momentum = 0.02

# Mean reversion
mean_reversion_strength = 0.01  # 1% pull to $50k
```

### Stock Market Parameters

```python
# Base P/E ratio
base_pe = 15

# Sentiment impact
sentiment_factor = 0.2  # ±20% from sentiment
```

## 📐 Economic Theory

### Models Implemented

**Stock Pricing:**
- Gordon Growth Model (implicit)
- P/E ratio approach
- Dividend Discount Model elements

**Crypto Pricing:**
- Network value theory (Metcalfe's Law)
- Stock-to-Flow (implicit in scarcity)
- Macro factor models (NEW! Our contribution)

**Portfolio Theory:**
- Modern Portfolio Theory (risk/return)
- Macro-responsive allocation
- Behavioral finance (FOMO, panic selling)

### Real-World Parallels

**2020-2021: Stimulus Era**
- Fed cuts to 0% → Crypto rallies
- Inflation rises → Digital gold narrative
- Bitcoin: $10k → $69k (+590%)

**2022: Rate Hike Era**
- Fed hikes to 5% → Crypto crashes
- Risk-off sentiment → Flight to safety
- Bitcoin: $69k → $16k (-77%)

**2024: ETF Approval**
- Institutional legitimacy → Rally
- Adoption surge → Network effects
- Bitcoin: $16k → $73k (+356%)

Our simulation captures these dynamics!

## 🎓 Use Cases

### 1. Policy Analysis
- Test crypto regulation proposals
- Model government adoption scenarios
- Analyze central bank digital currency (CBDC) competition

### 2. Investment Research
- Study macro-crypto correlations
- Test hedging strategies
- Model institutional adoption impacts

### 3. Education
- Teach monetary policy transmission
- Visualize asset price dynamics
- Demonstrate portfolio theory

### 4. Hackathon Demo
- Show unique differentiator
- Interactive policy experiments
- AI-powered insights
- Visually stunning charts

## 🚀 Future Enhancements

Potential extensions:
- **Stablecoins**: Crypto pegged to fiat
- **DeFi protocols**: Lending, yield farming
- **NFT markets**: Digital collectibles
- **Bonds market**: Government and corporate debt
- **Options/Derivatives**: Hedging instruments
- **Multiple cryptocurrencies**: Bitcoin, Ethereum, etc.
- **Mining dynamics**: Proof-of-work economics
- **Staking rewards**: Proof-of-stake yields

## 🐛 Known Limitations

1. **Simplified Supply**: Fixed supply, no mining dynamics
2. **No Cross-Asset Arbitrage**: Stocks and crypto move independently (mostly)
3. **Single Crypto**: Only one cryptocurrency type
4. **No Transaction Costs**: Free trading (unrealistic but simplifies)
5. **Perfect Liquidity**: Can always buy/sell at market price
6. **Homogeneous Agents**: All consumers have same risk tolerance distribution

## 📚 References

**Academic:**
- Metcalfe's Law and network value
- Modern Portfolio Theory (Markowitz)
- Interest rate transmission mechanisms
- Behavioral finance (Kahneman & Tversky)

**Real-World:**
- Bitcoin price history (2009-2024)
- Federal Reserve monetary policy
- US Treasury crypto reserve proposals
- El Salvador Bitcoin adoption
- Spot Bitcoin ETF launches (2024)

## 💡 Tips

**For Best Results:**
1. Let simulation run 20-30 steps before making changes
2. Change one parameter at a time to isolate effects
3. Use scenario buttons for dramatic demonstrations
4. Watch Fear & Greed index to predict market turns
5. Compare crypto behavior during high vs low inflation

**For Presentations:**
1. Start with interest rate hike → show crypto crash
2. Enable government reserve → show legitimacy boost
3. Use AI Insights button for "expert analysis"
4. Explain the "why" behind each relationship
5. Compare to real 2022 Fed hikes (very relatable!)

**For Development:**
1. Check test suites for expected behaviors
2. Crypto price should stay in $5k-$500k range
3. P/E ratios should be 5-25 (realistic)
4. No exponential explosions or death spirals
5. Markets should have realistic volatility (ups AND downs)

---

**Questions?** Check the main [README.md](README.md) or [ARCHITECTURE.md](ARCHITECTURE.md) for more details.
