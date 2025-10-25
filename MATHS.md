# Mathematical Models in EconoSphere

This document describes all the mathematical formulas and economic theory implemented in the simulation.

## Table of Contents
1. [Consumer Behavior](#consumer-behavior)
2. [Firm Behavior](#firm-behavior)
3. [Labor Market](#labor-market)
4. [Goods Market](#goods-market)
5. [Government (Fiscal Policy)](#government-fiscal-policy)
6. [Central Bank (Monetary Policy)](#central-bank-monetary-policy)
7. [Economic Metrics](#economic-metrics)

---

## Consumer Behavior

### 1. Net Income
**Location**: `agents/consumer.py:54`

```
Net Income = Income - Taxes

where:
Taxes = Income × Tax Rate
```

**Where**:
- Income = Wage from employment
- Taxes = Income × Tax Rate (proportional income tax)

**Theory**: Income after taxes, before transfers.

---

### 2. Cash on Hand
**Location**: `agents/consumer.py:57`

```
Cash on Hand = Wealth(t) + Net Income + Welfare Received
```

**Where**:
- Wealth(t) = Accumulated savings from previous periods
- Net Income = Income - Taxes
- Welfare = Government transfer payment (if unemployed)

**Theory**: Total liquidity available for consumption. This represents all financial resources the consumer can access in the current period.

---

### 3. Consumption Function (Keynesian)
**Location**: `agents/consumer.py:63`

```
Consumption Budget = MPC × Cash on Hand

where MPC = Marginal Propensity to Consume (default: 0.7)

Constraint: Consumption Budget ≤ Cash on Hand
```

**Theory**: Based on Keynes' consumption function, extended to include wealth effects. Consumers spend a fixed proportion of their total available resources (not just current income).

**Real Example**: If MPC = 0.7, wealth = $5000, net income = $1000, welfare = $0:
- Cash on Hand = $5000 + $1000 + $0 = $6000
- Consumption Budget = 0.7 × $6000 = $4200

---

### 4. Quantity Demanded
**Location**: `agents/consumer.py:70`

```
Quantity Demanded = Consumption Budget / Price Level
```

**Theory**: Demand curve - at higher prices, consumers demand fewer goods for the same budget.

---

### 5. Wealth Dynamics
**Location**: `agents/consumer.py:74`

```
Wealth(t+1) = Wealth(t) + Net Income + Welfare - Consumption

or equivalently:

Wealth(t+1) = Wealth(t) + Income - Taxes + Welfare - Consumption
```

**Theory**: Stock-flow consistency. Wealth accumulates from unspent income and transfers. Note that income and welfare are NOT double-counted - they flow into wealth only once after consumption decisions are made.

---

## Firm Behavior

### 1. Production Function (Diminishing Returns)
**Location**: `agents/firm.py:79`

```
Production = Productivity × (Labor ^ gamma)

Q = A × L^γ
```

**Where**:
- Q = Output (quantity produced)
- A = Total Factor Productivity (TFP, default: 2.0)
- L = Labor (number of workers)
- γ = Returns to scale parameter (default: 0.7, typical range: 0.6-0.8)

**Theory**: Production function with diminishing marginal returns to labor. This is similar to a Cobb-Douglas production function but simplified to labor only. Each additional worker adds less output than the previous one.

**Example**: With A = 2.0 and γ = 0.7:
- 1 worker: Q = 2.0 × 1^0.7 = 2.0 units
- 10 workers: Q = 2.0 × 10^0.7 = 10.0 units (not 20 - diminishing returns!)
- 100 workers: Q = 2.0 × 100^0.7 = 50.1 units

**Marginal Product of Labor**:
```
MPL = dQ/dL = A × γ × L^(γ-1)
```
This decreases as L increases when γ < 1.

---

### 2. Labor Demand Function
**Location**: `agents/firm.py:39-50`

```
Labor Demand = Expected Demand / Productivity × Interest Rate Factor × Profitability Factor

where:
Interest Rate Factor = max(0.5, 1 - 2r)
Profitability Factor = 1.2 if profit > 0, else 0.8
```

**Theory**: Firms hire based on expected production needs, but reduce hiring when:
- Interest rates are high (expensive to expand)
- They are currently unprofitable

**Real Example**: If r = 5% (0.05):
- Interest Rate Factor = 1 - 2(0.05) = 0.9
- Firm hires 90% of base labor demand

---

### 3. Price Adjustment (Adaptive Pricing)
**Location**: `agents/firm.py:85-127`

```
Price(t+1) = Price(t) × [1 + θ_d × Excess Demand Ratio + θ_c × Unit Cost Change]

where:

Excess Demand Ratio = (Demand - Supply) / max(Supply, 1)

Unit Cost = (Number of Workers × Wage) / Production

Unit Cost Change = (Unit Cost(t) - Unit Cost(t-1)) / Unit Cost(t-1)

θ_d = Demand sensitivity parameter (default: 0.1, typical: 0.05-0.2)
θ_c = Cost sensitivity parameter (default: 0.1, typical: 0.05-0.2)
```

**Theory**: Continuous adaptive pricing with two components:
1. **Demand-pull**: Prices rise when demand exceeds supply (excess demand > 0)
2. **Cost-push**: Prices rise when unit costs increase (wage inflation, lower productivity)

This combines Walrasian tatonnement with markup pricing theory.

**Example**: Suppose θ_d = 0.1, θ_c = 0.1, current price = $10
- Scenario 1: Demand = 120, Supply = 100, no cost change
  - Excess Demand Ratio = 20/100 = 0.2
  - Price adjustment = 0.1 × 0.2 + 0.1 × 0 = 0.02 (2%)
  - New Price = $10 × 1.02 = $10.20

- Scenario 2: Balanced demand, but wages rose 10%
  - Excess Demand Ratio = 0
  - Unit Cost Change = 0.1
  - Price adjustment = 0.1 × 0 + 0.1 × 0.1 = 0.01 (1%)
  - New Price = $10 × 1.01 = $10.10

---

### 4. Revenue and Profit
**Location**: `agents/firm.py:98, 111`

```
Revenue = Quantity Sold × Price

Costs = Number of Workers × Wage

Profit = Revenue - Costs
```

**Theory**: Standard accounting identities.

---

### 5. Investment Function and Capital Dynamics
**Location**: `agents/firm.py:151-182`

```
Step 1: Capital Depreciation
Capital(t) = max(0, (1 - δ) × Capital(t-1))

where δ = Depreciation Rate (default: 0.05 = 5% per period)

Step 2: Investment Decision
If Profit > 0 AND Interest Rate < 8%:
    Investment = ξ × Profit

    Capital(t+1) = Capital(t) + Investment

    Productivity(t+1) = Productivity(t) × [1 + κ × (Investment / Capital(t))]

where:
ξ = Investment share (default: 0.1 = 10% of profit)
κ = Productivity growth coefficient (default: 0.1)
```

**Theory**:
1. **Capital Depreciation**: Physical capital wears out over time (equipment breaks, buildings deteriorate)
2. **Investment**: Profitable firms reinvest when borrowing costs are low
3. **Endogenous Productivity Growth**: Productivity grows proportional to the investment-to-capital ratio (embodied technological change)

**Example**: Firm with Capital = $100k, Profit = $10k, Interest Rate = 5%
- Step 1: Depreciation reduces capital to (1 - 0.05) × $100k = $95k
- Step 2: Investment = 0.1 × $10k = $1k
- New Capital = $95k + $1k = $96k
- Investment Ratio = $1k / $96k = 0.0104
- Productivity Growth = 0.1 × 0.0104 = 0.00104 (0.104%)
- If old productivity = 2.0, new = 2.0 × 1.00104 = 2.0021

**Capital Accounting**:
```
Capital(t+1) = (1 - δ) × Capital(t) + Profit + Investment - Wages
```

This creates a **Solow-like growth model** at the firm level where sustained investment is needed to maintain capital stock against depreciation.

---

## Labor Market

### 1. Unemployment Rate
**Location**: `simulation/metrics.py:40`, `simulation/markets.py:55`

```
Unemployment Rate = (Number Unemployed / Labor Force) × 100

or equivalently:

Unemployment Rate = (1 - Employment Rate) × 100
```

**Theory**: Standard BLS definition.

---

### 2. Wage Adjustment (Phillips Curve-like)
**Location**: `simulation/markets.py:74-77`

```
If Unemployment > 10%:
    Wage(t+1) = Wage(t) × 0.98   (2% decrease)

If Unemployment < 5%:
    Wage(t+1) = Wage(t) × 1.02   (2% increase)
```

**Theory**: Simplified Phillips Curve. In tight labor markets (low unemployment), wages rise. In slack markets (high unemployment), wages fall.

**Floor Constraint**:
```
Wage ≥ $500
```

---

### 3. Job Matching Algorithm
**Location**: `simulation/markets.py:44-50`

```
For each job opening:
    If unemployed workers remain:
        Match random worker to job
```

**Theory**: Random matching (search and matching model, simplified). No frictions or search costs in current version.

---

## Goods Market

### 1. Market Clearing
**Location**: `simulation/markets.py:154`

```
Quantity Traded = min(Total Demand, Total Supply)
```

**Theory**: Short-side rule. Trade is constrained by the lesser of supply or demand.

---

### 2. Aggregate Demand
**Location**: `simulation/markets.py:129`

```
Total Demand = Σ(Consumer Demand) + Government Spending / Price Level
```

**Theory**: AD = C + G (simplified, no investment or net exports in current version).

---

### 3. Aggregate Supply
**Location**: `simulation/markets.py:108`

```
Total Supply = Σ(Firm Production)
```

---

### 4. Price Level Dynamics
**Location**: `simulation/markets.py:137-140`

```
Excess Demand = Total Demand - Total Supply

If Excess Demand > 0:
    Price Level(t+1) = Price Level(t) × 1.03   (3% increase)

If Excess Demand < 0:
    Price Level(t+1) = Price Level(t) × 0.97   (3% decrease)
```

**Theory**: Quantity theory of money (simplified). Excess demand causes inflation, excess supply causes deflation.

---

### 5. Inflation Rate
**Location**: `simulation/markets.py:146`

```
Inflation = (Price Level(t) - Price Level(t-1)) / Price Level(t-1) × 100
```

**Theory**: Standard inflation calculation (percentage change in price level).

---

## Government (Fiscal Policy)

### 1. Tax Revenue
**Location**: `agents/government.py:38`

```
Tax Revenue = Σ(Consumer Income × Tax Rate)
```

**Theory**: Proportional income tax. In reality, taxes are progressive (higher rates for higher incomes).

---

### 2. Welfare Spending
**Location**: `agents/government.py:48`

```
Total Welfare = Number of Unemployed × Welfare Payment per Person
```

**Theory**: Automatic stabilizer. Welfare spending rises during recessions (high unemployment).

---

### 3. Budget Balance
**Location**: `agents/government.py:70`

```
Budget Balance = Tax Revenue - (Welfare Spending + Government Spending)

If Budget Balance < 0:
    Debt(t+1) = Debt(t) + |Budget Balance|   (deficit adds to debt)

If Budget Balance > 0:
    Debt(t+1) = Debt(t) - min(Budget Balance, Debt(t))   (surplus pays down debt)
```

**Theory**: Government budget constraint. Deficits accumulate as debt.

---

## Central Bank (Monetary Policy)

### 1. Taylor Rule
**Location**: `agents/central_bank.py:62-78`

```
Target Interest Rate = Neutral Rate + 0.5 × Inflation Gap - 0.5 × Unemployment Gap

where:
Inflation Gap = Current Inflation - Target Inflation
Unemployment Gap = Current Unemployment - Natural Unemployment (5%)
Neutral Rate = 2%
```

**Theory**: Taylor Rule (John Taylor, 1993). Central bank raises rates when inflation is above target, lowers rates when unemployment is above natural rate.

**Example**:
- If inflation = 4% (target 2%) and unemployment = 5% (natural rate):
  - Inflation Gap = 4% - 2% = 2%
  - Unemployment Gap = 5% - 5% = 0%
  - Target Rate = 2% + 0.5(2%) - 0.5(0%) = 3%

**Smooth Adjustment**:
```
Actual Rate(t+1) = Actual Rate(t) + 0.3 × (Target Rate - Actual Rate(t))
```

Rates don't jump instantly; they adjust gradually (30% of gap each period).

---

### 2. Quantitative Easing/Tightening
**Location**: `agents/central_bank.py:41-55`

```
Quantitative Easing:
Money Supply(t+1) = Money Supply(t) + Amount

Quantitative Tightening:
Money Supply(t+1) = Money Supply(t) - min(Amount, 10% of Money Supply)
```

**Theory**: Central bank expands/contracts money supply. In reality, this is done through buying/selling bonds. In our model, it directly affects money supply.

---

## Economic Metrics

### 1. GDP (Gross Domestic Product)
**Location**: `simulation/metrics.py:30`

```
GDP = Σ(Firm Revenue)
```

**Theory**: Income approach to GDP. In a complete model:
```
GDP = C + I + G + (X - M)
```

We use a simplified version (sum of all production value).

---

### 2. Gini Coefficient (Wealth Inequality)
**Location**: `simulation/metrics.py:59-77`

```
Gini = (2 × Σ(i × Wealth_i)) / (n × Σ(Wealth)) - (n + 1) / n

where:
- Wealth_i is sorted in ascending order
- i is the rank (1, 2, 3, ...)
- n is the number of consumers
```

**Theory**: Measures inequality in wealth distribution:
- Gini = 0: Perfect equality (everyone has same wealth)
- Gini = 1: Perfect inequality (one person has all wealth)

**Derivation**: Area between Lorenz curve and line of equality.

**Example Calculation**:
For 3 people with wealth [$100, $200, $700]:
```
n = 3
Σ(Wealth) = 1000
Σ(i × Wealth_i) = 1×100 + 2×200 + 3×700 = 2600

Gini = (2 × 2600) / (3 × 1000) - (3 + 1) / 3
     = 5200 / 3000 - 4/3
     = 1.733 - 1.333
     = 0.40
```

This indicates moderate inequality (0.4 out of 1.0).

---

### 3. Average Wage
**Location**: `simulation/metrics.py:87`

```
Average Wage = Σ(Income of Employed) / Number of Employed
```

---

### 4. Average Price Level
**Location**: `simulation/metrics.py:98`

```
Average Price = Σ(Firm Prices) / Number of Firms
```

---

## Stochastic Elements

### 1. Initial Conditions (Random)
**Location**: `simulation/economy_model.py:68-71, 82-85`

```
Consumer Wealth ~ Normal(μ = $5000, σ = $2000)
Firm Capital ~ Normal(μ = $50000, σ = $20000)
```

**Theory**: Heterogeneous agents start with different wealth levels, drawn from normal distributions.

---

### 2. Job Matching (Random)
**Location**: `simulation/markets.py:42`

```
Workers are shuffled randomly before matching to jobs
```

**Theory**: Adds realistic randomness to who gets hired.

---

## Parameter Sensitivity

### Key Parameters and Typical Ranges

| Parameter | Symbol | Default | Range | Impact |
|-----------|--------|---------|-------|--------|
| Tax Rate | τ | 20% | 0-50% | Higher → Lower consumption → Lower GDP |
| Interest Rate | r | 5% | 0-10% | Higher → Less investment → Higher unemployment |
| Welfare Payment | W | $500 | $0-$2000 | Higher → Higher demand → Lower inequality |
| MPC | c | 0.7 | 0.5-0.9 | Higher → More consumption → Higher GDP |
| Productivity (TFP) | A | 2.0 | 1.0-5.0 | Higher → More output per worker |
| Returns to Scale | γ | 0.7 | 0.6-0.8 | Higher → Less diminishing returns |
| Depreciation Rate | δ | 5% | 2-10% | Higher → More investment needed to maintain capital |
| Investment Share | ξ | 10% | 5-20% | Higher → Faster capital growth |
| Productivity Growth | κ | 0.1 | 0.05-0.2 | Higher → Faster tech progress from investment |
| Price Demand Sensitivity | θ_d | 0.1 | 0.05-0.2 | Higher → Prices more volatile with demand |
| Price Cost Sensitivity | θ_c | 0.1 | 0.05-0.2 | Higher → Stronger cost-push inflation |
| Govt Spending | G | $10k | $0-$50k | Higher → Higher AD → Lower unemployment |

---

## Model Limitations

### What's Implemented (Realistic):

1. ✅ **Diminishing Returns Production**: Q = A × L^γ with γ < 1
2. ✅ **Capital Accumulation with Depreciation**: K(t+1) = (1-δ)K(t) + I(t)
3. ✅ **Endogenous Productivity Growth**: Productivity grows with investment
4. ✅ **Adaptive Pricing**: Continuous price adjustment with demand-pull and cost-push
5. ✅ **Wealth Effects on Consumption**: Consumers use both wealth and income

### What's Still Simplified:

1. **No Capital in Production Function**: Production only depends on labor (Q = A × L^γ), not capital. Should be Cobb-Douglas: Q = A × L^α × K^β

2. **Perfect Information**: Agents know market conditions instantly (no information delays)

3. **No Banking Sector**: No fractional reserve banking, credit creation, or bank runs

4. **Closed Economy**: No imports, exports, or exchange rates

5. **Homogeneous Goods**: All firms produce identical goods (no differentiation)

6. **No Expectations**: Agents don't form forward-looking expectations (adaptive vs. rational)

7. **Partial Price Stickiness**: Prices adjust with some smoothing, but still more flexible than reality

8. **No Credit Market**: Consumers cannot borrow, firms don't take loans (only self-finance)

---

## Extensions for Advanced Versions

### Already Implemented (v2.0):

1. ✅ **Diminishing Returns Production**: Q = A × L^γ
2. ✅ **Endogenous Investment with Depreciation**: K(t+1) = (1-δ)K(t) + I(t)
3. ✅ **Productivity Growth**: A(t+1) = A(t) × [1 + κ × I/K]
4. ✅ **Adaptive Price Adjustment**: Continuous with demand and cost components

### Possible Future Improvements:

1. **Full Cobb-Douglas Production** (add capital to production function):
   ```
   Q = A × L^α × K^β
   where α + β = 1 (constant returns to scale)
   ```

2. **Rational Expectations**:
   ```
   Expected_Inflation(t+1) = E[Inflation(t+1) | Information(t)]

   Simple version:
   Expected_Inflation = Actual_Inflation + ε
   where ε ~ Normal(0, σ²)
   ```

3. **Phillips Curve (Expectations-Augmented)**:
   ```
   Inflation = Expected_Inflation - β(Unemployment - Natural_Unemployment)
   ```

4. **Banking Sector**:
   ```
   Money_Supply = Base_Money × Money_Multiplier
   Money_Multiplier = 1 / Reserve_Ratio
   Loans = Deposits × (1 - Reserve_Ratio)
   ```

5. **Credit Market** (consumer and firm borrowing):
   ```
   Consumer_Debt(t+1) = Consumer_Debt(t) + Borrowing - Repayment
   Constraint: Debt_Service_Ratio < 0.4 (40% of income)
   ```

6. **IS-LM Framework**:
   ```
   IS: Y = C(Y - T) + I(r) + G
   LM: M/P = L(Y, r)

   Equilibrium: IS = LM determines Y and r
   ```

7. **Heterogeneous Firms** (different productivity levels):
   ```
   Productivity_i ~ LogNormal(μ, σ)

   Market dynamics favor more productive firms
   ```

---

## Validation Against Real Data

### Empirical Comparisons:

| Metric | Simulation | US Reality (2022) |
|--------|-----------|-------------------|
| Unemployment | 3-8% | 3.6% |
| Inflation | -2% to +5% | 6.5% |
| Tax Rate | 20% | ~24% (effective) |
| Gini | 0.3-0.5 | 0.49 |
| Interest Rate | 0-10% | 4.5% |

**Calibration**: Use `data/world_bank.py` to pull real data and calibrate initial conditions.

---

## Mathematical Notation Summary

| Symbol | Meaning |
|--------|---------|
| t | Time period |
| L | Labor (number of workers) |
| K | Capital stock |
| Q | Quantity produced / Output |
| P | Price level |
| w | Wage rate |
| r | Interest rate |
| τ | Tax rate |
| A | Total Factor Productivity (TFP) |
| γ | Returns to scale parameter (gamma) |
| δ | Depreciation rate (delta) |
| ξ | Investment share (xi) |
| κ | Productivity growth coefficient (kappa) |
| θ_d | Price demand sensitivity (theta_d) |
| θ_c | Price cost sensitivity (theta_c) |
| c / MPC | Marginal Propensity to Consume |
| C | Consumption |
| I | Investment |
| G | Government spending |
| Y | GDP / Income |
| π | Inflation rate (pi) |
| u | Unemployment rate |
| Σ | Summation |
| ~ | "Distributed as" (statistics) |
| E[·] | Expected value |
| MPL | Marginal Product of Labor |

---

## References

**Economic Theory**:
1. Keynes, J.M. (1936). *The General Theory of Employment, Interest and Money*
2. Taylor, J.B. (1993). "Discretion versus Policy Rules in Practice"
3. Phillips, A.W. (1958). "The Relation Between Unemployment and the Rate of Change of Money Wage Rates"
4. Solow, R.M. (1956). "A Contribution to the Theory of Economic Growth"

**Agent-Based Modeling**:
1. Tesfatsion, L. (2006). "Agent-Based Computational Economics: A Constructive Approach"
2. Farmer, J.D. & Foley, D. (2009). "The economy needs agent-based modelling"
3. Geanakoplos, J. et al. (2012). "Getting at Systemic Risk via an Agent-Based Model of the Housing Market"

**Implementation**:
- Mesa Documentation: https://mesa.readthedocs.io/
- World Bank Data: https://data.worldbank.org/

---

**For questions about the math, see `ARCHITECTURE.md` for implementation details.**
