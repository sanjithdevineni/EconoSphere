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

### 1. Disposable Income
**Location**: `agents/consumer.py:53`

```
Disposable Income = Income - Taxes + Welfare Received
```

**Where**:
- Income = Wage from employment
- Taxes = Income × Tax Rate
- Welfare = Government transfer payment (if unemployed)

**Theory**: Standard definition of income available for consumption/saving after taxes and transfers.

---

### 2. Consumption Function (Keynesian)
**Location**: `agents/consumer.py:56`

```
Consumption Budget = Disposable Income × MPC

where MPC = Marginal Propensity to Consume (default: 0.7)
```

**Theory**: Based on Keynes' consumption function. Consumers spend a fixed proportion of their disposable income.

**Real Example**: If MPC = 0.7, a consumer with $1000 disposable income will spend $700.

---

### 3. Quantity Demanded
**Location**: `agents/consumer.py:63`

```
Quantity Demanded = Consumption Budget / Price Level
```

**Theory**: Demand curve - at higher prices, consumers demand fewer goods for the same budget.

**Budget Constraint**:
```
Consumption Budget ≤ Current Wealth
```

Consumers cannot spend more than they have (no borrowing in current version).

---

### 4. Wealth Dynamics
**Location**: `agents/consumer.py:32, 65`

```
Wealth(t+1) = Wealth(t) + Income - Taxes + Welfare - Consumption
```

**Theory**: Stock-flow consistency. Wealth accumulates from unspent income.

---

## Firm Behavior

### 1. Production Function (Linear)
**Location**: `agents/firm.py:72`

```
Production = Number of Workers × Productivity

Q = L × α
```

**Where**:
- Q = Output (quantity produced)
- L = Labor (number of workers)
- α = Productivity parameter (default: 2.0)

**Theory**: Simplified linear production function. In reality, production functions often have diminishing returns (Cobb-Douglas: Q = A × L^α × K^β), but we use linear for simplicity.

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

### 3. Price Adjustment (Supply/Demand)
**Location**: `agents/firm.py:82-88`

```
If Demand/Supply > 1.1:
    Price(t+1) = Price(t) × 1.05   (5% increase)

If Demand/Supply < 0.9:
    Price(t+1) = Price(t) × 0.95   (5% decrease)
```

**Theory**: Tatonnement process (Walrasian auction). Firms raise prices when demand exceeds supply, lower when supply exceeds demand.

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

### 5. Investment Function
**Location**: `agents/firm.py:121-127`

```
If Profit > 0 AND Interest Rate < 8%:
    Investment = Profit × 0.1
    Productivity(t+1) = Productivity(t) × 1.01
```

**Theory**: Firms reinvest profits when profitable and interest rates are low. Investment increases productivity (technological improvement).

**Capital Accumulation**:
```
Capital(t+1) = Capital(t) + Profit + Investment - Wages
```

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
| Productivity | α | 2.0 | 1.0-5.0 | Higher → More output per worker |
| Govt Spending | G | $10k | $0-$50k | Higher → Higher AD → Lower unemployment |

---

## Model Limitations

### What's Simplified:

1. **Linear Production**: Real production functions have diminishing returns (should be Cobb-Douglas: Q = A L^α K^β)

2. **No Capital Accumulation**: Firms don't accumulate capital stock explicitly (K is static)

3. **Perfect Information**: Agents know market conditions instantly (no information delays)

4. **No Banking Sector**: No fractional reserve banking, credit creation, or bank runs

5. **Closed Economy**: No imports, exports, or exchange rates

6. **Homogeneous Goods**: All firms produce identical goods (no differentiation)

7. **No Expectations**: Agents don't form expectations about future (adaptive vs. rational)

8. **No Price Stickiness**: Prices adjust instantly (in reality, wages/prices are sticky)

---

## Extensions for Advanced Versions

### Possible Improvements:

1. **Cobb-Douglas Production**:
   ```
   Q = A × L^α × K^β
   where α + β = 1 (constant returns to scale)
   ```

2. **Endogenous Investment**:
   ```
   Investment = f(Profit, Interest Rate, Expected Return)
   K(t+1) = (1 - δ)K(t) + I(t)
   where δ = depreciation rate
   ```

3. **Rational Expectations**:
   ```
   Expected Inflation = Actual Inflation + ε
   where ε ~ Normal(0, σ²)
   ```

4. **Phillips Curve (Expectations-Augmented)**:
   ```
   Inflation = Expected Inflation - β(Unemployment - Natural Unemployment)
   ```

5. **Solow Growth Model**:
   ```
   Y = A × K^α × L^(1-α)
   dK/dt = sY - δK
   where s = savings rate
   ```

6. **IS-LM Framework**:
   ```
   IS: Y = C(Y - T) + I(r) + G
   LM: M/P = L(Y, r)
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
| Q | Quantity produced |
| P | Price level |
| w | Wage rate |
| r | Interest rate |
| τ | Tax rate |
| α | Productivity parameter |
| β | Parameter |
| C | Consumption |
| I | Investment |
| G | Government spending |
| Y | GDP / Income |
| π | Inflation rate |
| u | Unemployment rate |
| Σ | Summation |
| ~ | "Distributed as" (statistics) |

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
