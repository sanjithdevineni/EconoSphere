"""
Foreign Sector Agent - Represents trading partner countries
"""

from __future__ import annotations
from typing import Dict, Optional
import random


class ForeignSector:
    """
    Represents a foreign country/region for international trade

    Features:
    - Supplies imported goods at world prices
    - Demands exports from domestic economy
    - Can impose retaliatory tariffs
    - Has own GDP, price level, and demand dynamics
    - Exchange rate fluctuations
    """

    def __init__(
        self,
        country_name: str,
        gdp: float,
        initial_price_level: float = 10.0,
        initial_exchange_rate: float = 1.0,
        import_propensity: float = 0.15,
        export_elasticity: float = 1.5
    ):
        """
        Initialize foreign sector

        Args:
            country_name: Name of the country/region (e.g., "China", "EU")
            gdp: Foreign GDP (determines demand for exports)
            initial_price_level: Initial price level in foreign currency
            initial_exchange_rate: Exchange rate (foreign currency per domestic currency)
            import_propensity: Share of domestic consumption that comes from this country
            export_elasticity: How sensitive foreign demand is to price changes
        """
        self.country_name = country_name
        self.gdp = gdp
        self.price_level = initial_price_level
        self.exchange_rate = initial_exchange_rate  # FC/DC (e.g., Yuan per Dollar)
        self.import_propensity = import_propensity
        self.export_elasticity = export_elasticity

        # Trade flows
        self.exports_to_domestic = 0.0  # Value of goods sold to domestic economy
        self.imports_from_domestic = 0.0  # Value of goods bought from domestic economy
        self.trade_balance = 0.0  # Exports - Imports (from foreign perspective)

        # Tariff policies
        self.tariff_rate_on_imports = 0.0  # Tariff this country imposes on domestic exports
        self.retaliation_sensitivity = 0.5  # How aggressively they retaliate (0-1)

        # Economic state
        self.gdp_growth_rate = 0.02  # Baseline growth
        self.inflation_rate = 0.02

    def supply_imports(
        self,
        domestic_demand: float,
        domestic_price: float,
        domestic_tariff_on_imports: float
    ) -> Dict[str, float]:
        """
        Calculate supply of imports to domestic economy

        Args:
            domestic_demand: Total consumption demand in domestic economy
            domestic_price: Average price level in domestic economy
            domestic_tariff_on_imports: Tariff rate imposed by domestic country

        Returns:
            Dict with import_quantity, import_value, effective_price
        """
        # Base import quantity as share of domestic demand
        base_import_quantity = domestic_demand * self.import_propensity

        # Foreign price in domestic currency (adjusted for exchange rate)
        foreign_price_domestic_currency = self.price_level / self.exchange_rate

        # Effective price including tariff
        effective_price = foreign_price_domestic_currency * (1 + domestic_tariff_on_imports)

        # Price competitiveness factor (if domestic prices rise, imports become more attractive)
        # Even with tariffs, if domestic prices are much higher, imports still competitive
        price_ratio = effective_price / max(domestic_price, 0.1)
        competitiveness = max(0.1, min(2.0, 2.0 - price_ratio))  # Range: 0.1 to 2.0

        # Actual imports adjusted for competitiveness
        import_quantity = base_import_quantity * competitiveness

        # Tariff revenue goes to domestic government
        import_value_pretariff = import_quantity * foreign_price_domestic_currency
        tariff_revenue = import_value_pretariff * domestic_tariff_on_imports
        import_value_total = import_value_pretariff + tariff_revenue

        self.exports_to_domestic = import_value_pretariff  # From foreign perspective, this is an export

        return {
            'import_quantity': import_quantity,
            'import_value': import_value_total,
            'import_value_pretariff': import_value_pretariff,
            'tariff_revenue': tariff_revenue,
            'effective_price': effective_price
        }

    def demand_exports(
        self,
        domestic_price: float,
        domestic_production: float
    ) -> Dict[str, float]:
        """
        Calculate demand for exports from domestic economy

        Args:
            domestic_price: Average price level in domestic economy
            domestic_production: Total production available for export

        Returns:
            Dict with export_quantity, export_value
        """
        # Base export demand as function of foreign GDP
        base_export_demand = self.gdp * 0.05  # 5% of foreign GDP as baseline

        # Domestic price in foreign currency (including foreign tariff)
        domestic_price_foreign_currency = domestic_price * self.exchange_rate
        effective_export_price = domestic_price_foreign_currency * (1 + self.tariff_rate_on_imports)

        # Price elasticity of demand for exports
        # If exports become expensive, foreign country buys less
        price_effect = (self.price_level / max(effective_export_price, 0.1)) ** self.export_elasticity
        price_effect = max(0.1, min(3.0, price_effect))  # Bounded

        export_demand_quantity = base_export_demand * price_effect

        # Can't export more than is produced
        actual_export_quantity = min(export_demand_quantity, domestic_production * 0.3)  # Max 30% of production

        # Export value in domestic currency
        export_value = actual_export_quantity * domestic_price

        self.imports_from_domestic = export_value / self.exchange_rate  # Convert to foreign currency

        return {
            'export_quantity': actual_export_quantity,
            'export_value': export_value
        }

    def update_retaliation(self, domestic_tariff_on_imports: float) -> None:
        """
        Update retaliatory tariff based on domestic tariff policy

        Args:
            domestic_tariff_on_imports: Current tariff rate imposed by domestic country
        """
        # Retaliation: if domestic imposes tariffs, foreign retaliates
        # But not 1:1 - depends on retaliation_sensitivity
        target_tariff = domestic_tariff_on_imports * self.retaliation_sensitivity

        # Gradual adjustment (not instant retaliation)
        adjustment_speed = 0.3
        self.tariff_rate_on_imports += adjustment_speed * (target_tariff - self.tariff_rate_on_imports)

        # Non-negative
        self.tariff_rate_on_imports = max(0.0, self.tariff_rate_on_imports)

    def update_exchange_rate(
        self,
        domestic_inflation: float,
        domestic_interest_rate: float,
        foreign_interest_rate: Optional[float] = None
    ) -> None:
        """
        Update exchange rate based on economic fundamentals

        Uses simplified monetary model:
        - Interest rate differentials
        - Inflation differentials
        - Trade balance effects

        Args:
            domestic_inflation: Inflation rate in domestic economy
            domestic_interest_rate: Interest rate in domestic economy
            foreign_interest_rate: Interest rate in foreign economy (defaults to 0.03)
        """
        if foreign_interest_rate is None:
            foreign_interest_rate = 0.03  # Default 3%

        # Interest rate parity effect
        # Higher domestic rates → stronger domestic currency → HIGHER exchange rate (more FC per DC)
        interest_differential = domestic_interest_rate - foreign_interest_rate

        # Purchasing power parity effect
        # Higher domestic inflation → weaker domestic currency → LOWER exchange rate (less FC per DC)
        inflation_differential = domestic_inflation - self.inflation_rate

        # Trade balance effect (simplified)
        # Trade surplus (exports > imports from domestic perspective) → stronger domestic currency → HIGHER E
        trade_balance_domestic = (self.imports_from_domestic - self.exports_to_domestic)
        trade_balance_effect = trade_balance_domestic / max(self.gdp, 1.0) * 0.1

        # Combined effect (CORRECTED SIGNS)
        exchange_rate_change = (
            -inflation_differential * 0.5 +  # PPP effect: higher inflation → lower E
            +interest_differential * 0.3 +   # Interest rate effect: higher rates → higher E
            +trade_balance_effect            # Trade balance: surplus → higher E
        )

        # Add some random noise
        noise = random.uniform(-0.01, 0.01)
        exchange_rate_change += noise

        # Update exchange rate (with limits to prevent explosions)
        self.exchange_rate *= (1 + max(-0.05, min(0.05, exchange_rate_change)))
        self.exchange_rate = max(0.1, min(10.0, self.exchange_rate))  # Reasonable bounds

    def step(self) -> None:
        """Update foreign economy for one time step"""
        # GDP growth
        self.gdp *= (1 + self.gdp_growth_rate)

        # Price level inflation
        self.price_level *= (1 + self.inflation_rate)

        # Update trade balance
        self.trade_balance = self.exports_to_domestic - self.imports_from_domestic

        # Small random variations
        self.gdp_growth_rate += random.uniform(-0.005, 0.005)
        self.gdp_growth_rate = max(-0.02, min(0.08, self.gdp_growth_rate))

        self.inflation_rate += random.uniform(-0.002, 0.002)
        self.inflation_rate = max(-0.01, min(0.10, self.inflation_rate))

    def get_state(self) -> Dict[str, float]:
        """Get current state of foreign sector"""
        return {
            'country_name': self.country_name,
            'gdp': self.gdp,
            'price_level': self.price_level,
            'exchange_rate': self.exchange_rate,
            'exports_to_domestic': self.exports_to_domestic,
            'imports_from_domestic': self.imports_from_domestic,
            'trade_balance': self.trade_balance,
            'tariff_rate': self.tariff_rate_on_imports,
            'gdp_growth_rate': self.gdp_growth_rate,
            'inflation_rate': self.inflation_rate
        }
