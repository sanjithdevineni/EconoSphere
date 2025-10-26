# International Trade System - Technical Documentation

## Overview

The international trade system extends the base economic model with multi-country trade dynamics, tariffs, exchange rates, and retaliation mechanisms. This document details all mathematical formulas and economic logic used.

---

## Table of Contents
1. [Foreign Sector Agent](#foreign-sector-agent)
2. [Import Supply Logic](#import-supply-logic)
3. [Export Demand Logic](#export-demand-logic)
4. [Tariff Retaliation](#tariff-retaliation)
5. [Exchange Rate Dynamics](#exchange-rate-dynamics)
6. [Trade Integration](#trade-integration)
7. [Economic Indicators](#economic-indicators)

---

## 1. Foreign Sector Agent

Each foreign country/region is represented by a `ForeignSector` agent with the following state variables:

### State Variables

| Variable | Description | Initial Value |
|----------|-------------|---------------|
| `gdp` | Foreign GDP | Country-specific (e.g., China: 500,000) |
| `price_level` | Foreign price level | Country-specific (e.g., China: 8.0) |
| `exchange_rate` | Foreign currency per domestic currency | Country-specific (e.g., China: 7.0 Yuan/$) |
| `import_propensity` | Share of domestic demand from this country | 0.10 - 0.25 |
| `export_elasticity` | Price sensitivity of export demand | 1.5 - 2.0 |
| `tariff_rate_on_imports` | Tariff this country imposes on our exports | 0.0 (initially) |
| `retaliation_sensitivity` | How aggressively they retaliate (0-1) | 0.4 - 0.8 |
| `gdp_growth_rate` | Annual GDP growth | ~0.02 (2%) |
| `inflation_rate` | Annual inflation | ~0.02 (2%) |

### Trading Partners

**China:**
```python
GDP = 500,000
price_level = 8.0  # Lower prices (competitive)
exchange_rate = 7.0  # Yuan per Dollar
import_propensity = 0.25  # 25% of consumption
export_elasticity = 2.0  # Highly price-sensitive
retaliation_sensitivity = 0.8  # High retaliation
```

**European Union:**
```python
GDP = 600,000
price_level = 12.0  # Higher prices (quality goods)
exchange_rate = 0.9  # Euros per Dollar
import_propensity = 0.15  # 15% of consumption
export_elasticity = 1.5
retaliation_sensitivity = 0.6  # Moderate retaliation
```

**Rest of World:**
```python
GDP = 400,000
price_level = 10.0
exchange_rate = 1.0
import_propensity = 0.10
export_elasticity = 1.8
retaliation_sensitivity = 0.4  # Less coordinated
```

---

## 2. Import Supply Logic

### Formula

The foreign sector supplies imports to the domestic economy based on:

```
base_import_quantity = domestic_consumption_demand × import_propensity
```

### Price Competitiveness

Foreign prices are converted to domestic currency using the exchange rate:

```
foreign_price_DC = foreign_price_level / exchange_rate
```

Where:
- `foreign_price_DC` = Foreign price in domestic currency
- `foreign_price_level` = Price level in foreign currency
- `exchange_rate` = Foreign currency units per domestic currency

### Tariff Application

Domestic tariffs increase the effective price of imports:

```
effective_import_price = foreign_price_DC × (1 + domestic_tariff_rate)
```

### Competitiveness Factor

Imports become more/less attractive based on relative prices:

```
price_ratio = effective_import_price / domestic_price_level

competitiveness = max(0.1, min(2.0, 2.0 - price_ratio))
```

**Logic:**
- If `price_ratio = 1.0` (equal prices) → `competitiveness = 1.0` (normal demand)
- If `price_ratio < 1.0` (imports cheaper) → `competitiveness > 1.0` (higher demand)
- If `price_ratio > 1.0` (imports expensive) → `competitiveness < 1.0` (lower demand)
- Bounded between 0.1 and 2.0 to prevent extreme values

### Actual Import Quantity

```
actual_import_quantity = base_import_quantity × competitiveness
```

### Import Value and Tariff Revenue

```
import_value_pretariff = actual_import_quantity × foreign_price_DC

tariff_revenue = import_value_pretariff × domestic_tariff_rate

total_import_value = import_value_pretariff + tariff_revenue
```

**Note:** Tariff revenue goes to the domestic government, not to foreign exporters.

### Complete Import Supply Formula

```python
def supply_imports(domestic_demand, domestic_price, domestic_tariff):
    # Step 1: Base demand
    base_qty = domestic_demand * import_propensity

    # Step 2: Convert foreign price
    foreign_price_dc = foreign_price / exchange_rate

    # Step 3: Apply tariff
    effective_price = foreign_price_dc * (1 + domestic_tariff)

    # Step 4: Competitiveness adjustment
    price_ratio = effective_price / domestic_price
    competitiveness = max(0.1, min(2.0, 2.0 - price_ratio))

    # Step 5: Actual imports
    import_qty = base_qty * competitiveness

    # Step 6: Calculate values
    import_value_pretariff = import_qty * foreign_price_dc
    tariff_revenue = import_value_pretariff * domestic_tariff
    total_value = import_value_pretariff + tariff_revenue

    return {
        'import_quantity': import_qty,
        'import_value': total_value,
        'tariff_revenue': tariff_revenue,
        'effective_price': effective_price
    }
```

---

## 3. Export Demand Logic

### Base Export Demand

Foreign countries demand our exports based on their GDP:

```
base_export_demand = foreign_GDP × 0.05
```

**Rationale:** Assume exports represent approximately 5% of the trading partner's GDP as a baseline.

### Price Elasticity of Export Demand

Foreign demand is sensitive to our export prices:

```
domestic_price_FC = domestic_price × exchange_rate
```

Where:
- `domestic_price_FC` = Our price in foreign currency
- `domestic_price` = Our domestic price level
- `exchange_rate` = Foreign currency per domestic currency

### Foreign Tariff Application

The foreign country may impose tariffs on our exports:

```
effective_export_price = domestic_price_FC × (1 + foreign_tariff_rate)
```

### Price Effect on Demand

Using elasticity of demand:

```
price_effect = (foreign_price_level / effective_export_price) ^ export_elasticity
```

Bounded to prevent extremes:

```
price_effect = max(0.1, min(3.0, price_effect))
```

**Interpretation:**
- If our exports are cheap relative to foreign prices → higher demand
- If our exports are expensive → lower demand
- `export_elasticity` typically 1.5-2.0 (elastic demand)

### Export Quantity

```
export_demand_quantity = base_export_demand × price_effect
```

### Production Constraint

Can't export more than we produce:

```
actual_export_quantity = min(export_demand_quantity, domestic_production × 0.3)
```

**Constraint:** Maximum 30% of domestic production can be exported (rest consumed domestically).

### Export Value

```
export_value = actual_export_quantity × domestic_price
```

**Note:** Export value calculated in domestic currency.

### Complete Export Demand Formula

```python
def demand_exports(domestic_price, domestic_production):
    # Step 1: Base foreign demand
    base_demand = foreign_gdp * 0.05

    # Step 2: Convert to foreign currency
    domestic_price_fc = domestic_price * exchange_rate

    # Step 3: Apply foreign tariff
    effective_price = domestic_price_fc * (1 + foreign_tariff_rate)

    # Step 4: Price elasticity effect
    price_effect = (foreign_price / effective_price) ** export_elasticity
    price_effect = max(0.1, min(3.0, price_effect))

    # Step 5: Calculate demand
    export_demand = base_demand * price_effect

    # Step 6: Production constraint
    actual_exports = min(export_demand, domestic_production * 0.3)

    # Step 7: Export value
    export_value = actual_exports * domestic_price

    return {
        'export_quantity': actual_exports,
        'export_value': export_value
    }
```

---

## 4. Tariff Retaliation

### Retaliation Mechanism

When the domestic economy imposes tariffs, foreign countries retaliate based on their sensitivity:

```
target_foreign_tariff = domestic_tariff_rate × retaliation_sensitivity
```

### Gradual Adjustment

Tariffs don't change instantly (allows for negotiation period):

```
adjustment_speed = 0.3

Δtariff = adjustment_speed × (target_foreign_tariff - current_foreign_tariff)

new_foreign_tariff = current_foreign_tariff + Δtariff
```

**Non-negativity constraint:**
```
foreign_tariff_rate = max(0, new_foreign_tariff)
```

### Example Scenarios

**Scenario 1: US imposes 25% tariff on China**
```
Domestic tariff = 0.25
China retaliation_sensitivity = 0.8
Target Chinese tariff = 0.25 × 0.8 = 0.20 (20%)

After step 1: 0 + 0.3 × (0.20 - 0) = 0.06 (6%)
After step 2: 0.06 + 0.3 × (0.20 - 0.06) = 0.102 (10.2%)
After step 3: 0.102 + 0.3 × (0.20 - 0.102) = 0.131 (13.1%)
...converges to 20%
```

**Scenario 2: Trade War (50% tariffs)**
```
Domestic tariff = 0.50
China retaliation = 0.50 × 0.8 = 0.40 (40%)
EU retaliation = 0.50 × 0.6 = 0.30 (30%)
ROW retaliation = 0.50 × 0.4 = 0.20 (20%)
```

---

## 5. Exchange Rate Dynamics

The exchange rate fluctuates based on three economic forces:

### Interest Rate Parity

Higher domestic interest rates attract foreign capital → stronger domestic currency:

```
interest_differential = domestic_interest_rate - foreign_interest_rate

interest_rate_effect = -interest_differential × 0.3
```

**Sign:** Negative because higher domestic rates → LOWER exchange rate (fewer foreign currency units per domestic unit = stronger domestic currency)

### Purchasing Power Parity (PPP)

Higher domestic inflation → weaker domestic currency:

```
inflation_differential = domestic_inflation - foreign_inflation

PPP_effect = inflation_differential × 0.5
```

**Sign:** Positive because higher domestic inflation → HIGHER exchange rate (more foreign currency units needed = weaker domestic currency)

### Trade Balance Effect

Trade surplus → stronger domestic currency:

```
trade_balance_domestic = foreign_imports_from_us - foreign_exports_to_us

trade_balance_effect = -(trade_balance / foreign_GDP) × 0.1
```

**Sign:** Negative because surplus → LOWER exchange rate (stronger domestic currency)

### Combined Exchange Rate Change

```
ΔE = PPP_effect + interest_rate_effect + trade_balance_effect + noise

where noise ~ Uniform(-0.01, 0.01)
```

### Exchange Rate Update

```
new_exchange_rate = current_exchange_rate × (1 + ΔE)
```

**Bounds:** Constrained between 0.1 and 10.0 to prevent unrealistic values.

### Complete Exchange Rate Formula

```python
def update_exchange_rate(domestic_inflation, domestic_interest_rate,
                        foreign_interest_rate=0.03):
    # Interest rate parity
    interest_diff = domestic_interest_rate - foreign_interest_rate
    interest_effect = -interest_diff * 0.3

    # Purchasing power parity
    inflation_diff = domestic_inflation - self.inflation_rate
    ppp_effect = inflation_diff * 0.5

    # Trade balance effect
    trade_balance_domestic = (self.imports_from_domestic -
                             self.exports_to_domestic)
    trade_effect = -(trade_balance_domestic / self.gdp) * 0.1

    # Random fluctuation
    noise = random.uniform(-0.01, 0.01)

    # Total change (max ±5% per period)
    total_change = ppp_effect + interest_effect + trade_effect + noise
    total_change = max(-0.05, min(0.05, total_change))

    # Update
    self.exchange_rate *= (1 + total_change)
    self.exchange_rate = max(0.1, min(10.0, self.exchange_rate))
```

### Example Calculation

**Initial State:**
- Domestic interest rate: 5%
- Foreign interest rate: 3%
- Domestic inflation: 3%
- Foreign inflation: 2%
- Trade balance: -$10,000 (deficit)
- Foreign GDP: $500,000
- Current exchange rate: 7.0

**Calculations:**
```
interest_effect = -(0.05 - 0.03) × 0.3 = -0.006 (stronger)
ppp_effect = (0.03 - 0.02) × 0.5 = 0.005 (weaker)
trade_effect = -(-10,000 / 500,000) × 0.1 = 0.002 (weaker due to deficit)
noise = 0.003 (random)

total_change = 0.005 - 0.006 + 0.002 + 0.003 = 0.004 (0.4% change)

new_exchange_rate = 7.0 × (1 + 0.004) = 7.028
```

---

## 6. Trade Integration

### Tariff Revenue Distribution

All tariff revenue collected goes directly to the domestic government:

```python
government.tax_revenue += tariff_revenue
```

This increases government's budget and can offset other fiscal needs.

### Net Trade Effect on Goods Supply

Net imports affect domestic goods availability:

```
net_trade_quantity = total_imports - total_exports
```

**Economic Effect:**
- Positive net trade (imports > exports) → increases goods supply → downward pressure on inflation
- Negative net trade (exports > imports) → decreases goods supply → upward pressure on inflation

This is stored for potential use in inflation calculations:

```python
metrics.net_trade_quantity = net_trade_quantity
```

---

## 7. Economic Indicators

### Trade Balance

```
trade_balance = total_export_value - total_import_value
```

**Interpretation:**
- Positive: Trade surplus (exports > imports)
- Negative: Trade deficit (imports > exports)

### Net Exports as % of GDP

```
net_exports_pct_GDP = (trade_balance / GDP) × 100
```

**Typical values:**
- USA: -3% to -5% (persistent deficit)
- China: +2% to +5% (persistent surplus)
- Germany: +6% to +8% (large surplus)

### Country-Specific Trade Tracking

For each trading partner, we track:

```python
per_country_metrics = {
    'imports_from_country': foreign_sector.exports_to_domestic,
    'exports_to_country': foreign_sector.imports_from_domestic,
    'bilateral_balance': (exports_to_country - imports_from_country),
    'exchange_rate': foreign_sector.exchange_rate,
    'their_tariff_on_us': foreign_sector.tariff_rate_on_imports
}
```

### Aggregate Trade Flows

```python
total_imports = sum(foreign_sector.exports_to_domestic
                   for foreign_sector in all_foreign_sectors)

total_exports = sum(foreign_sector.imports_from_domestic
                   for foreign_sector in all_foreign_sectors)

total_tariff_revenue = sum(tariff_revenue_per_country)
```

---

## 8. Policy Scenarios

### Trade War Scenario

When triggered with intensity `I`:

```python
domestic_tariff = 0.25 × I  # Up to 25% tariffs
```

For each foreign country:
```python
foreign_tariff = 0.20 × I  # Immediate retaliation
retaliation_sensitivity = min(1.0, current_sensitivity + 0.2)  # Become more aggressive
```

**Example:** Intensity = 1.0 (full trade war)
- Domestic tariff: 25%
- China retaliates: 20%
- EU retaliates: 20%
- ROW retaliates: 20%

### Free Trade Agreement (FTA)

When FTA signed with a country:

```python
# Remove tariffs
foreign_tariff_on_us = 0.0
domestic_tariff_on_them = 0.0  # (would need to implement)

# Reduce retaliation tendency
retaliation_sensitivity = 0.1

# Increase trade volume
import_propensity *= 1.2  # 20% increase
```

**Economic Effect:**
- More trade with FTA partner
- Less trade with non-FTA countries (trade diversion)
- Lower consumer prices
- Reduced tariff revenue

---

## 9. Mathematical Properties

### Equilibrium Conditions

In steady state (no policy changes):

**Exchange Rate Equilibrium:**
```
ΔE = 0

⟹ inflation_diff × 0.5 = interest_diff × 0.3 + (trade_balance/GDP) × 0.1
```

**Trade Balance Equilibrium:**
```
exports = imports

⟹ Σ(export_demand_i) = Σ(import_supply_i)
```

### Stability Analysis

The system is **stable** because:

1. **Retaliation converges:** adjustment_speed < 1
2. **Exchange rates bounded:** Hard limits [0.1, 10.0]
3. **Competitiveness bounded:** [0.1, 2.0]
4. **Price effect bounded:** [0.1, 3.0]

### Elasticity Bounds

All elasticities are realistic:
- Export elasticity: 1.5 - 2.0 (elastic demand for traded goods)
- Import propensity: 0.10 - 0.25 (typical import shares)
- Retaliation sensitivity: 0.4 - 0.8 (varies by country)

---

## 10. Calibration Notes

### Parameter Choices

**Import Propensity:**
- Based on typical import/GDP ratios (15-25% for open economies)
- China: 0.25 (many consumer goods)
- EU: 0.15 (quality goods, machinery)
- ROW: 0.10 (diverse)

**Export Elasticity:**
- Literature suggests 1.5-2.5 for manufactured goods
- Used 1.5-2.0 as conservative estimate
- Higher values = more price-sensitive demand

**Retaliation Sensitivity:**
- Based on observed trade war behavior
- China: 0.8 (historically strong retaliator)
- EU: 0.6 (measured response)
- ROW: 0.4 (less coordinated)

**Exchange Rate Effects:**
- Interest rate: 0.3 (moderate effect)
- Inflation: 0.5 (dominant in long run - PPP)
- Trade balance: 0.1 (small short-term effect)

### Scaling

Since the base model uses scaled values (representative agents):
- GDPs scaled relative to domestic economy
- Trade flows as % of consumption/production
- Absolute values less important than ratios

---

## 11. Limitations & Future Enhancements

### Current Limitations

1. **No capital flows:** Only goods trade, no financial flows
2. **Static GDP:** Foreign GDPs grow exogenously
3. **No supply chains:** Intermediate goods not modeled
4. **Symmetric tariffs:** Domestic can't set country-specific tariffs
5. **No quotas:** Only tariffs, not quantity restrictions

### Potential Enhancements

1. **Capital flows:**
   ```
   exchange_rate_effect += capital_inflows / GDP
   ```

2. **Country-specific tariffs:**
   ```python
   tariff_rates = {
       'China': 0.25,
       'EU': 0.10,
       'ROW': 0.15
   }
   ```

3. **Import quotas:**
   ```
   actual_imports = min(demand_based_imports, quota_limit)
   ```

4. **Currency intervention:**
   ```
   central_bank_fx_purchases → affects exchange_rate
   ```

5. **Terms of trade effects:**
   ```
   welfare_change = import_price_change × import_share
   ```

---

## 12. References & Economic Theory

### Theoretical Foundations

**Mundell-Fleming Model:**
- Exchange rate responds to interest differentials
- Capital mobility affects currency values

**Heckscher-Ohlin Trade Theory:**
- Countries export goods they can produce relatively cheaply
- Import goods that are expensive to produce domestically

**Elasticities Approach to Trade:**
- Trade flows depend on price ratios and elasticities
- Marshall-Lerner condition for exchange rate effects

**Tariff Economics:**
- Deadweight loss from protection
- Terms of trade effects
- Retaliation reduces gains from tariffs

### Empirical Support

- Import elasticities: Typically 1.0-2.5 (Hooper et al., 2000)
- Export elasticities: 1.5-2.0 for manufactures (Marquez, 2002)
- Exchange rate pass-through: 50-80% in long run (Campa & Goldberg, 2005)
- Tariff retaliation: Observed in 2018-2019 US-China trade war

---

## 13. Code Implementation Map

| Economic Concept | Code Location | Key Method |
|-----------------|---------------|------------|
| Import Supply | `agents/foreign_sector.py` | `supply_imports()` |
| Export Demand | `agents/foreign_sector.py` | `demand_exports()` |
| Retaliation | `agents/foreign_sector.py` | `update_retaliation()` |
| Exchange Rates | `agents/foreign_sector.py` | `update_exchange_rate()` |
| Trade Integration | `simulation/trade_economy_model.py` | `_integrate_trade_into_economy()` |
| Aggregate Flows | `simulation/trade_economy_model.py` | `_calculate_trade_flows()` |
| Policy Scenarios | `simulation/trade_economy_model.py` | `trigger_trade_war()`, `trigger_free_trade_agreement()` |

---

## Version History

- **v1.0** (2025-01-XX): Initial Tier 3 implementation with multi-country trade, tariffs, retaliation, and exchange rates.

---

**End of Documentation**
