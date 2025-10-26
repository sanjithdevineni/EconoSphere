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

        # Create foreign sectors (major trading partners)
        self.foreign_sectors: Dict[str, ForeignSector] = {}
        self._create_foreign_sectors()

        # Trade metrics tracking
        self.trade_history = {
            'total_imports': [],
            'total_exports': [],
            'trade_balance': [],
            'tariff_revenue': [],
            'net_exports_pct_gdp': []
        }

        # Country-specific trade tracking
        for country_name in self.foreign_sectors.keys():
            self.trade_history[f'{country_name}_imports'] = []
            self.trade_history[f'{country_name}_exports'] = []
            self.trade_history[f'{country_name}_exchange_rate'] = []
            self.trade_history[f'{country_name}_tariff'] = []

    def _create_foreign_sectors(self) -> None:
        """Create major trading partner countries"""

        # China - Large economy, significant trade volume
        self.foreign_sectors['China'] = ForeignSector(
            country_name='China',
            gdp=500000,  # Scaled relative to domestic economy
            initial_price_level=8.0,  # Lower prices (competitive)
            initial_exchange_rate=7.0,  # Yuan per Dollar (approximate)
            import_propensity=0.25,  # 25% of domestic consumption could be from China
            export_elasticity=2.0  # Sensitive to price changes
        )

        # European Union - Advanced economy
        self.foreign_sectors['EU'] = ForeignSector(
            country_name='EU',
            gdp=600000,
            initial_price_level=12.0,  # Higher prices (quality goods)
            initial_exchange_rate=0.9,  # Euros per Dollar
            import_propensity=0.15,  # 15% of consumption from EU
            export_elasticity=1.5
        )

        # Rest of World - Aggregated other countries
        self.foreign_sectors['ROW'] = ForeignSector(
            country_name='Rest of World',
            gdp=400000,
            initial_price_level=10.0,
            initial_exchange_rate=1.0,
            import_propensity=0.10,
            export_elasticity=1.8
        )

        # Set retaliation sensitivities
        self.foreign_sectors['China'].retaliation_sensitivity = 0.8  # Likely to retaliate strongly
        self.foreign_sectors['EU'].retaliation_sensitivity = 0.6  # Moderate retaliation
        self.foreign_sectors['ROW'].retaliation_sensitivity = 0.4  # Less coordinated retaliation

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

        Returns:
            Dict with aggregate trade statistics
        """
        # Get domestic economy state
        # Use latest metrics if available, otherwise use initial values
        if self.metrics.latest_metrics:
            avg_price = self.metrics.latest_metrics.get('avg_price', config.INITIAL_PRICE_LEVEL)
        else:
            avg_price = config.INITIAL_PRICE_LEVEL
        total_consumption_demand = sum(c.wealth * config.CONSUMER_WEALTH_SPEND_RATE for c in self.consumers)
        total_production = sum(f.production for f in self.firms) if self.firms else 1000

        # Track aggregates
        total_imports = 0.0
        total_import_value = 0.0
        total_tariff_revenue = 0.0
        total_exports = 0.0
        total_export_value = 0.0

        # Process trade with each foreign sector
        for country_name, foreign_sector in self.foreign_sectors.items():
            # Calculate imports from this country
            import_result = foreign_sector.supply_imports(
                domestic_demand=total_consumption_demand,
                domestic_price=avg_price,
                domestic_tariff_on_imports=self.tariff_rate
            )

            total_imports += import_result['import_quantity']
            total_import_value += import_result['import_value']
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

        # Calculate trade balance (exports - imports)
        trade_balance = total_export_value - total_import_value

        # Net exports as % of GDP
        if self.metrics.latest_metrics:
            current_gdp = self.metrics.latest_metrics.get('gdp', 1.0)
        else:
            current_gdp = 1.0
        net_exports_pct_gdp = (trade_balance / current_gdp * 100) if current_gdp > 0 else 0

        return {
            'total_imports': total_imports,
            'total_import_value': total_import_value,
            'total_exports': total_exports,
            'total_export_value': total_export_value,
            'trade_balance': trade_balance,
            'tariff_revenue': total_tariff_revenue,
            'net_exports_pct_gdp': net_exports_pct_gdp,
            'avg_price': avg_price
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

    def step(self):
        """Override step to add trade flows"""

        # Calculate trade flows before main economy step
        trade_flows = self._calculate_trade_flows()

        # Integrate trade into economy
        self._integrate_trade_into_economy(trade_flows)

        # Run parent economy step (this calls the wrapped _user_step)
        result = super().step()

        # Record trade metrics
        self.trade_history['total_imports'].append(trade_flows['total_import_value'])
        self.trade_history['total_exports'].append(trade_flows['total_export_value'])
        self.trade_history['trade_balance'].append(trade_flows['trade_balance'])
        self.trade_history['tariff_revenue'].append(trade_flows['tariff_revenue'])
        self.trade_history['net_exports_pct_gdp'].append(trade_flows['net_exports_pct_gdp'])

        # Record country-specific metrics
        for country_name, foreign_sector in self.foreign_sectors.items():
            state = foreign_sector.get_state()
            self.trade_history[f'{country_name}_imports'].append(state['exports_to_domestic'])
            self.trade_history[f'{country_name}_exports'].append(state['imports_from_domestic'])
            self.trade_history[f'{country_name}_exchange_rate'].append(state['exchange_rate'])
            self.trade_history[f'{country_name}_tariff'].append(state['tariff_rate'])

        # Enhance result with trade data
        if result is None:
            result = {}

        result.update({
            'trade_balance': trade_flows['trade_balance'],
            'total_imports': trade_flows['total_import_value'],
            'total_exports': trade_flows['total_export_value'],
            'tariff_revenue': trade_flows['tariff_revenue'],
            'net_exports_pct_gdp': trade_flows['net_exports_pct_gdp'],
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

        Args:
            intensity: How severe (0.0 to 1.0)
        """
        # Domestic imposes high tariffs
        self.set_tariff_rate(0.25 * intensity)  # Up to 25% tariffs

        # All countries retaliate immediately
        for foreign_sector in self.foreign_sectors.values():
            foreign_sector.tariff_rate_on_imports = 0.20 * intensity
            foreign_sector.retaliation_sensitivity = min(1.0, foreign_sector.retaliation_sensitivity + 0.2)

        LOGGER.info(f"Trade war triggered with intensity {intensity:.1%}")

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
