"""
International Trade Economy Model - Extends base model with multi-country trade
"""

import logging
from typing import Dict, List
from simulation.economy_model import EconomyModel
from agents.foreign_sector import ForeignSector
import config

LOGGER = logging.getLogger(__name__)


class TradeEconomyModel(EconomyModel):
    """
    Extended economy model with international trade, tariffs, and multi-country dynamics

    Features:
    - Multiple trading partner countries
    - Import and export flows
    - Tariff policies and retaliation
    - Exchange rate dynamics
    - Trade balance tracking
    """

    def __init__(
        self,
        num_consumers=config.NUM_CONSUMERS,
        num_firms=config.NUM_FIRMS,
        initial_vat_rate=config.INITIAL_VAT_RATE,
        initial_payroll_rate=config.INITIAL_PAYROLL_RATE,
        initial_corporate_rate=config.INITIAL_CORPORATE_RATE,
        initial_interest_rate=config.INITIAL_INTEREST_RATE,
        initial_welfare=config.INITIAL_WELFARE_PAYMENT,
        initial_govt_spending=config.INITIAL_GOVT_SPENDING,
        initial_tariff_rate=0.0,  # New: tariff on imports
        seed=None
    ):
        # Initialize base economy
        super().__init__(
            num_consumers=num_consumers,
            num_firms=num_firms,
            initial_vat_rate=initial_vat_rate,
            initial_payroll_rate=initial_payroll_rate,
            initial_corporate_rate=initial_corporate_rate,
            initial_interest_rate=initial_interest_rate,
            initial_welfare=initial_welfare,
            initial_govt_spending=initial_govt_spending,
            seed=seed
        )

        # Trade-specific parameters
        self.tariff_rate = initial_tariff_rate
        self._last_tariff_rate = initial_tariff_rate

        # Track production for export calculations (exports based on previous period's production)
        self._previous_production = 1000  # Initial estimate

        # AMBITIOUS FEATURES: Capital flows and currency intervention
        self.foreign_reserves = 100000  # Central bank foreign currency reserves
        self.capital_account_balance = 0  # Financial flows (FDI, portfolio investment)
        self.intervention_enabled = True  # Central bank can intervene in FX markets
        self.intervention_threshold = 0.15  # Intervene if E changes > 15% from baseline

        # Track baseline exchange rates for intervention
        self._baseline_exchange_rates = {}

        # Production capacity tracking for realistic export growth
        self.export_sector_capacity = 500  # Dedicated export production capacity (CONSERVATIVE: start small)
        self.capacity_utilization = 0.4  # Start at 40% utilization
        self.max_export_capacity = 5000  # CAP to prevent explosions (TIGHT cap for realism)

        # Trade balance adjustment mechanisms
        self.import_saturation_threshold = 0.35  # Imports can reach 35% of GDP (for metrics only, not enforced)
        self.trade_deficit_dampening = True  # Large deficits reduce import propensity

        # Create foreign sectors (major trading partners)
        self.foreign_sectors: Dict[str, ForeignSector] = {}
        self._create_foreign_sectors()

        # Trade metrics tracking
        self.trade_history = {
            'total_imports': [],
            'total_exports': [],
            'trade_balance': [],
            'tariff_revenue': [],
            'net_exports_pct_gdp': [],
            'capital_flows': [],
            'foreign_reserves': [],
            'export_capacity': [],
            'import_saturation': []
        }

        # Country-specific trade tracking
        for country_name in self.foreign_sectors.keys():
            self.trade_history[f'{country_name}_imports'] = []
            self.trade_history[f'{country_name}_exports'] = []
            self.trade_history[f'{country_name}_exchange_rate'] = []
            self.trade_history[f'{country_name}_tariff'] = []

    def _create_foreign_sectors(self) -> None:
        """Create major trading partner countries with realistic trade parameters"""

        # China - Large economy, significant trade volume
        self.foreign_sectors['China'] = ForeignSector(
            country_name='China',
            gdp=500000,  # Scaled relative to domestic economy
            initial_price_level=8.0,  # Lower prices (competitive)
            initial_exchange_rate=7.0,  # Yuan per Dollar (approximate)
            import_propensity=0.12,  # BALANCED: 12% of domestic consumption from China
            export_elasticity=2.5  # Sensitive to price changes (elastic demand)
        )

        # European Union - Advanced economy
        self.foreign_sectors['EU'] = ForeignSector(
            country_name='EU',
            gdp=600000,
            initial_price_level=12.0,  # Higher prices (quality goods)
            initial_exchange_rate=0.9,  # Euros per Dollar
            import_propensity=0.08,  # BALANCED: 8% of consumption from EU
            export_elasticity=1.8  # Moderately elastic
        )

        # Rest of World - Aggregated other countries
        self.foreign_sectors['ROW'] = ForeignSector(
            country_name='Rest of World',
            gdp=400000,
            initial_price_level=10.0,
            initial_exchange_rate=1.0,
            import_propensity=0.06,  # BALANCED: 6% from ROW
            export_elasticity=2.0
        )

        # Set retaliation sensitivities
        self.foreign_sectors['China'].retaliation_sensitivity = 0.8  # Likely to retaliate strongly
        self.foreign_sectors['EU'].retaliation_sensitivity = 0.6  # Moderate retaliation
        self.foreign_sectors['ROW'].retaliation_sensitivity = 0.4  # Less coordinated retaliation

        # Store baseline exchange rates for central bank intervention
        for country_name, sector in self.foreign_sectors.items():
            self._baseline_exchange_rates[country_name] = sector.exchange_rate

    def set_tariff_rate(self, tariff_rate: float) -> None:
        """
        Set tariff rate on imports

        Args:
            tariff_rate: Tariff rate as decimal (0.25 = 25%)
        """
        self.tariff_rate = max(0.0, min(1.0, tariff_rate))  # Bounded 0-100%

    def _calculate_trade_flows(self) -> Dict[str, float]:
        """
        Calculate import and export flows with all trading partners

        AMBITIOUS FEATURES:
        - Import saturation based on GDP share
        - Export capacity constraints with dynamic growth
        - Trade deficit feedback dampening

        Returns:
            Dict with aggregate trade statistics
        """
        # Get domestic economy state
        # Use latest metrics if available, otherwise use initial values
        if self.metrics.latest_metrics:
            avg_price = self.metrics.latest_metrics.get('avg_price', config.INITIAL_PRICE_LEVEL)
            current_gdp = self.metrics.latest_metrics.get('gdp', 1000)
        else:
            avg_price = config.INITIAL_PRICE_LEVEL
            current_gdp = 1000

        total_consumption_demand = sum(c.wealth * config.CONSUMER_WEALTH_SPEND_RATE for c in self.consumers)

        # Use PREVIOUS period's production for exports (firms produce, then export)
        # PLUS dedicated export sector capacity
        total_production = self._previous_production + self.export_sector_capacity * self.capacity_utilization

        # Track aggregates
        total_imports = 0.0
        total_import_value_pretariff = 0.0  # For trade balance (excludes tariffs)
        total_tariff_revenue = 0.0
        total_exports = 0.0
        total_export_value = 0.0

        # AMBITIOUS: Calculate import saturation factor
        # Imports saturate as they approach threshold % of GDP
        import_saturation_factor = 1.0

        # Process trade with each foreign sector
        for country_name, foreign_sector in self.foreign_sectors.items():
            # AMBITIOUS: Apply trade deficit dampening
            # If persistent deficits, reduce import propensity dynamically
            if self.trade_deficit_dampening and len(self.trade_history['trade_balance']) > 10:
                recent_deficits = sum(1 for tb in self.trade_history['trade_balance'][-10:] if tb < 0)
                if recent_deficits >= 8:  # 8 out of 10 periods in deficit
                    deficit_dampening = 0.90  # Reduce imports by 10%
                    foreign_sector.import_propensity *= deficit_dampening
                    LOGGER.info(f"Trade deficit dampening: reduced {country_name} import propensity to {foreign_sector.import_propensity:.3f}")
                    self.trade_deficit_dampening = False  # Only apply once per episode

            # Calculate imports from this country
            import_result = foreign_sector.supply_imports(
                domestic_demand=total_consumption_demand,
                domestic_price=avg_price,
                domestic_tariff_on_imports=self.tariff_rate
            )

            # REMOVED: Import saturation was too aggressive
            # Instead, trust natural economic forces:
            # - Exchange rate adjustments make imports more/less expensive
            # - Central bank intervention stabilizes currency
            # - Prices adjust based on supply/demand
            # - Capital flows balance current account automatically

            total_imports += import_result['import_quantity']
            total_import_value_pretariff += import_result['import_value_pretariff']  # Use pre-tariff value
            total_tariff_revenue += import_result['tariff_revenue']

            # Calculate exports to this country
            export_result = foreign_sector.demand_exports(
                domestic_price=avg_price,
                domestic_production=total_production
            )

            total_exports += export_result['export_quantity']
            total_export_value += export_result['export_value']

            # Update retaliation
            foreign_sector.update_retaliation(self.tariff_rate)

            # Update exchange rates
            if self.metrics.latest_metrics and len(self.metrics.history['inflation']) > 1:
                domestic_inflation = self.metrics.history['inflation'][-1]
            else:
                domestic_inflation = 0.02
            foreign_sector.update_exchange_rate(
                domestic_inflation=domestic_inflation,
                domestic_interest_rate=self.central_bank.interest_rate
            )

            # Step foreign economy forward
            foreign_sector.step()

        # Calculate trade balance (exports - imports, using pre-tariff import value)
        # Tariffs are domestic tax revenue, not part of trade balance
        trade_balance = total_export_value - total_import_value_pretariff

        # Net exports as % of GDP
        net_exports_pct_gdp = (trade_balance / current_gdp * 100) if current_gdp > 0 else 0

        # AMBITIOUS: Calculate import saturation (imports as % of GDP)
        import_saturation = (total_import_value_pretariff / current_gdp) if current_gdp > 0 else 0

        return {
            'total_imports': total_imports,
            'total_import_value': total_import_value_pretariff,  # Pre-tariff value for trade balance
            'total_exports': total_exports,
            'total_export_value': total_export_value,
            'trade_balance': trade_balance,
            'tariff_revenue': total_tariff_revenue,
            'net_exports_pct_gdp': net_exports_pct_gdp,
            'import_saturation': import_saturation,
            'avg_price': avg_price,
            'current_gdp': current_gdp
        }

    def _integrate_trade_into_economy(self, trade_flows: Dict[str, float]) -> None:
        """
        Integrate trade flows into the domestic economy

        Effects:
        - Imports add to available goods supply
        - Exports reduce available goods supply
        - Tariff revenue goes to government
        - Trade affects price levels and inflation
        """
        # Add tariff revenue to government
        if self.government:
            self.government.tax_revenue += trade_flows['tariff_revenue']

        # Adjust goods market supply
        # Imports increase supply, exports decrease supply
        import_quantity = trade_flows['total_imports']
        export_quantity = trade_flows['total_exports']

        # This affects price pressures
        # More imports → less inflation pressure
        # More exports → more inflation pressure
        net_trade_effect = import_quantity - export_quantity

        # Store for metrics (can be used in inflation calculations)
        self.metrics.net_trade_quantity = net_trade_effect

    def _calculate_capital_flows(self, trade_balance: float, current_gdp: float) -> float:
        """
        Calculate capital account flows (financial flows that balance current account)

        AMBITIOUS FEATURE: Financial account balancing
        - Trade deficits must be financed by capital inflows (foreign investment)
        - Trade surpluses lead to capital outflows (domestic investment abroad)
        - Interest rate differentials affect capital flows

        In reality: Current Account + Capital Account + Statistical Discrepancy ≈ 0
        Simplified: Capital Flows ≈ -Trade Balance + Interest Rate Effect

        Args:
            trade_balance: Current account balance (exports - imports)
            current_gdp: Current GDP for scaling

        Returns:
            Net capital inflow (+) or outflow (-)
        """
        # Base capital flows to balance current account (deficit → inflow, surplus → outflow)
        base_capital_flow = -trade_balance

        # Interest rate differential effect on capital flows
        # Higher domestic rates → attract foreign capital → additional inflow
        domestic_rate = self.central_bank.interest_rate
        foreign_rate_avg = 0.03  # Assume 3% average foreign rate

        rate_differential = domestic_rate - foreign_rate_avg
        rate_effect = rate_differential * current_gdp * 0.5  # Capital is rate-sensitive

        # Total capital flows
        total_capital_flow = base_capital_flow + rate_effect

        # Update capital account balance
        self.capital_account_balance = total_capital_flow

        return total_capital_flow

    def _central_bank_intervention(self, country_name: str, foreign_sector: ForeignSector) -> None:
        """
        Central bank intervenes in FX markets to stabilize exchange rates

        AMBITIOUS FEATURE: Realistic central bank FX intervention
        - Intervenes when E deviates too much from baseline
        - Sells foreign reserves to support domestic currency (when E falls too much)
        - Buys foreign reserves when domestic currency is too strong
        - Limited by available foreign reserves

        Mechanism:
        - If E < baseline × (1 - threshold): Domestic currency too strong → buy foreign currency
        - If E > baseline × (1 + threshold): Domestic currency too weak → sell foreign currency

        Args:
            country_name: Name of foreign country
            foreign_sector: ForeignSector instance
        """
        if not self.intervention_enabled:
            return

        baseline_e = self._baseline_exchange_rates.get(country_name, foreign_sector.exchange_rate)
        current_e = foreign_sector.exchange_rate

        # Calculate deviation from baseline
        deviation = (current_e - baseline_e) / baseline_e

        # Intervention zone: ±15% from baseline
        if abs(deviation) > self.intervention_threshold:
            # Calculate intervention size (proportional to deviation)
            intervention_strength = (abs(deviation) - self.intervention_threshold) * 2.0
            intervention_strength = min(0.2, intervention_strength)  # Cap at 20% adjustment

            if deviation > self.intervention_threshold:
                # Domestic currency too weak (E too high) → Sell foreign reserves
                if self.foreign_reserves > 1000:
                    # Selling foreign currency strengthens domestic currency → reduces E
                    intervention_amount = self.foreign_reserves * intervention_strength * 0.1
                    self.foreign_reserves -= intervention_amount

                    # Apply intervention effect: E decreases
                    foreign_sector.exchange_rate *= (1 - intervention_strength * 0.5)
                    LOGGER.info(f"Central bank intervention: Sold {intervention_amount:.0f} reserves to support currency ({country_name})")

            elif deviation < -self.intervention_threshold:
                # Domestic currency too strong (E too low) → Buy foreign reserves
                # Buying foreign currency weakens domestic currency → increases E
                intervention_amount = self.foreign_reserves * intervention_strength * 0.1

                foreign_sector.exchange_rate *= (1 + intervention_strength * 0.5)
                self.foreign_reserves += intervention_amount
                LOGGER.info(f"Central bank intervention: Bought {intervention_amount:.0f} reserves to weaken currency ({country_name})")

    def _update_export_capacity(self, trade_balance: float, current_production: float, current_gdp: float) -> None:
        """
        Update dedicated export sector production capacity

        REALISTIC FEATURE: Conservative export capacity growth
        - Grows slowly with economy
        - Hard cap to prevent explosions
        - Modest response to trade balance

        Args:
            trade_balance: Current trade balance
            current_production: Current domestic production
            current_gdp: Current GDP for scaling
        """
        # CONSERVATIVE: Slow, steady growth
        base_growth_rate = 0.015  # 1.5% baseline growth per period

        # Small bonus/penalty based on trade balance (max ±0.5%)
        balance_effect = max(-0.005, min(0.005, trade_balance / current_gdp))

        total_growth = base_growth_rate + balance_effect

        # Apply growth
        self.export_sector_capacity *= (1 + total_growth)

        # HARD CAP to prevent explosions
        self.export_sector_capacity = min(self.export_sector_capacity, self.max_export_capacity)

        # Capacity utilization adjusts based on domestic production health (conservative)
        if current_production > self._previous_production * 1.05:
            self.capacity_utilization = min(0.85, self.capacity_utilization * 1.01)  # Slower growth
        else:
            self.capacity_utilization = max(0.4, self.capacity_utilization * 0.99)  # Slower decline

    def step(self):
        """Override step to add trade flows with AMBITIOUS features"""

        # Calculate trade flows (using previous period's production for exports)
        trade_flows = self._calculate_trade_flows()

        # AMBITIOUS: Calculate capital flows (financial account)
        capital_flows = self._calculate_capital_flows(
            trade_balance=trade_flows['trade_balance'],
            current_gdp=trade_flows['current_gdp']
        )

        # AMBITIOUS: Central bank FX intervention for each country
        for country_name, foreign_sector in self.foreign_sectors.items():
            self._central_bank_intervention(country_name, foreign_sector)

        # Integrate trade into economy
        self._integrate_trade_into_economy(trade_flows)

        # Run parent economy step (this calls the wrapped _user_step)
        result = super().step()

        # Save current production for next period's export calculations
        current_production = sum(f.production for f in self.firms) if self.firms else 1000

        # AMBITIOUS: Update export sector capacity
        self._update_export_capacity(
            trade_balance=trade_flows['trade_balance'],
            current_production=current_production,
            current_gdp=trade_flows['current_gdp']
        )

        self._previous_production = current_production

        # Record trade metrics (including new ambitious features)
        self.trade_history['total_imports'].append(trade_flows['total_import_value'])
        self.trade_history['total_exports'].append(trade_flows['total_export_value'])
        self.trade_history['trade_balance'].append(trade_flows['trade_balance'])
        self.trade_history['tariff_revenue'].append(trade_flows['tariff_revenue'])
        self.trade_history['net_exports_pct_gdp'].append(trade_flows['net_exports_pct_gdp'])
        self.trade_history['capital_flows'].append(capital_flows)
        self.trade_history['foreign_reserves'].append(self.foreign_reserves)
        self.trade_history['export_capacity'].append(self.export_sector_capacity)
        self.trade_history['import_saturation'].append(trade_flows['import_saturation'])

        # Record country-specific metrics
        for country_name, foreign_sector in self.foreign_sectors.items():
            state = foreign_sector.get_state()
            self.trade_history[f'{country_name}_imports'].append(state['exports_to_domestic'])
            self.trade_history[f'{country_name}_exports'].append(state['imports_from_domestic'])
            self.trade_history[f'{country_name}_exchange_rate'].append(state['exchange_rate'])
            self.trade_history[f'{country_name}_tariff'].append(state['tariff_rate'])

        # Enhance result with trade data (including ambitious features)
        if result is None:
            result = {}

        result.update({
            'trade_balance': trade_flows['trade_balance'],
            'total_imports': trade_flows['total_import_value'],
            'total_exports': trade_flows['total_export_value'],
            'tariff_revenue': trade_flows['tariff_revenue'],
            'net_exports_pct_gdp': trade_flows['net_exports_pct_gdp'],
            'capital_flows': capital_flows,
            'foreign_reserves': self.foreign_reserves,
            'export_capacity': self.export_sector_capacity,
            'capacity_utilization': self.capacity_utilization,
            'import_saturation': trade_flows['import_saturation'],
            'foreign_sectors': {
                name: sector.get_state()
                for name, sector in self.foreign_sectors.items()
            }
        })

        return result

    def get_trade_state(self) -> Dict:
        """Get current state of international trade"""
        return {
            'tariff_rate': self.tariff_rate,
            'trade_history': self.trade_history,
            'foreign_sectors': {
                name: sector.get_state()
                for name, sector in self.foreign_sectors.items()
            }
        }

    def trigger_trade_war(self, intensity: float = 0.5) -> None:
        """
        Trigger a trade war scenario

        Foreign countries will retaliate gradually based on their retaliation_sensitivity.
        The retaliation will converge to: domestic_tariff × retaliation_sensitivity

        Args:
            intensity: How severe (0.0 to 1.0)
        """
        # Domestic imposes high tariffs immediately (policy decision)
        self.set_tariff_rate(0.25 * intensity)  # Up to 25% tariffs

        # Increase retaliation sensitivity (countries become more aggressive)
        # Foreign tariffs will converge gradually via update_retaliation()
        for foreign_sector in self.foreign_sectors.values():
            foreign_sector.retaliation_sensitivity = min(1.0, foreign_sector.retaliation_sensitivity + 0.2)

        LOGGER.info(f"Trade war triggered with intensity {intensity:.1%}. "
                   f"Foreign retaliation will converge gradually.")

    def trigger_free_trade_agreement(self, country_name: str) -> None:
        """
        Sign free trade agreement with a country

        Args:
            country_name: Name of country to sign FTA with
        """
        if country_name in self.foreign_sectors:
            foreign_sector = self.foreign_sectors[country_name]

            # Reduce tariffs to zero
            foreign_sector.tariff_rate_on_imports = 0.0
            foreign_sector.retaliation_sensitivity = 0.1  # Less likely to retaliate in future

            # Increase trade volume
            foreign_sector.import_propensity *= 1.2  # 20% increase

            LOGGER.info(f"Free trade agreement signed with {country_name}")
