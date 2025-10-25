"""
Main economy simulation model
"""
from types import MethodType
from mesa import Model
from simulation.schedulers import RandomActivation

from agents import Consumer, Firm, Government, CentralBank
from simulation.markets import LaborMarket, GoodsMarket
from simulation.metrics import MetricsCalculator
import config


class EconomyModel(Model):
    """
    Main economic simulation model that coordinates all agents and markets
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
        seed=None
    ):
        super().__init__()
        if seed is not None:
            self.random.seed(seed)

        self._last_step_result = None
        self._recession_cooldown = 0
        self._inflation_cooldown = 0

        original_user_step = self._user_step

        def _capture_step(_self, *args, **kwargs):
            result = original_user_step(*args, **kwargs)
            _self._last_step_result = result
            return result

        self._user_step = MethodType(_capture_step, self)

        original_step = self.step

        def _step_with_return(_self, *args, **kwargs):
            _self._last_step_result = None
            original_step(*args, **kwargs)
            return _self._last_step_result

        self.step = MethodType(_step_with_return, self)

        self.num_consumers = num_consumers
        self.num_firms = num_firms
        self.schedule = RandomActivation(self)
        self.current_step = 0

        # Initialize markets
        self.labor_market = LaborMarket(rng=self.random)
        self.goods_market = GoodsMarket()
        self.metrics = MetricsCalculator()

        # Create agents
        self.consumers = []
        self.firms = []
        self.government = None
        self.central_bank = None

        self._create_agents(initial_vat_rate, initial_payroll_rate, initial_corporate_rate,
                           initial_interest_rate, initial_welfare, initial_govt_spending)

    def _create_agents(self, vat_rate, payroll_rate, corporate_rate, interest_rate, welfare, govt_spending):
        """Initialize all agents"""

        # Create consumers
        for i in range(self.num_consumers):
            wealth = self.random.gauss(
                config.INITIAL_CONSUMER_WEALTH_MEAN,
                config.INITIAL_CONSUMER_WEALTH_STD
            )
            wealth = max(1000, wealth)  # Minimum wealth

            consumer = Consumer(
                unique_id=i,
                model=self,
                initial_wealth=wealth,
                propensity_to_consume=config.CONSUMER_PROPENSITY_TO_CONSUME
            )
            self.consumers.append(consumer)
            self.schedule.add(consumer)

        # Create firms
        for i in range(self.num_firms):
            capital = self.random.gauss(
                config.INITIAL_FIRM_CAPITAL_MEAN,
                config.INITIAL_FIRM_CAPITAL_STD
            )
            capital = max(10000, capital)  # Minimum capital

            firm = Firm(
                unique_id=self.num_consumers + i,
                model=self,
                initial_capital=capital,
                productivity=config.FIRM_PRODUCTIVITY,
                gamma=config.FIRM_GAMMA
            )
            firm.wage_offered = config.INITIAL_WAGE
            firm.price = config.INITIAL_PRICE_LEVEL
            firm.depreciation_rate = config.FIRM_DEPRECIATION_RATE
            self.firms.append(firm)
            self.schedule.add(firm)

        # Create government
        self.government = Government(
            unique_id=self.num_consumers + self.num_firms,
            model=self,
            vat_rate=vat_rate,
            payroll_rate=payroll_rate,
            corporate_rate=corporate_rate,
            welfare_payment=welfare,
            govt_spending=govt_spending
        )
        self.schedule.add(self.government)

        # Create central bank
        self.central_bank = CentralBank(
            unique_id=self.num_consumers + self.num_firms + 1,
            model=self,
            interest_rate=interest_rate,
            inflation_target=config.INFLATION_TARGET,
            money_supply=config.INITIAL_MONEY_SUPPLY
        )
        self.schedule.add(self.central_bank)

    def step(self):
        """
        Execute one time step of the simulation

        Order of operations:
        1. Firms determine labor demand (based on interest rates)
        2. Labor market clears (employment/wages)
        3. Government collects taxes and distributes welfare
        4. Consumers demand goods
        5. Goods market clears (production/prices)
        6. Firms pay wages and calculate profits
        7. Central bank adjusts policy (if auto mode)
        8. Calculate metrics
        """

        # 1. Firms determine labor demand based on smoothed demand expectations
        interest_rate = self.central_bank.get_borrowing_cost()
        default_expected = self.goods_market.get_expected_demand_per_firm(len(self.firms))

        for firm in self.firms:
            expected = firm.expected_future_demand if firm.expected_future_demand > 0 else default_expected
            if self._recession_cooldown > 0:
                expected *= 0.6
            if self._inflation_cooldown > 0:
                expected *= 1.2
            firm.determine_labor_demand(expected, interest_rate)

        # 2. Clear labor market
        labor_results = self.labor_market.clear_market(self.consumers, self.firms)
        unemployment_fraction = labor_results['unemployment_rate']
        self.government.apply_countercyclical_policy(unemployment_fraction * 100)
        self.goods_market.adjust_demand_expectations(unemployment_fraction)

        # 3. Government fiscal policy
        self.government.collect_taxes(self.consumers, self.firms)
        self.government.distribute_welfare(self.consumers)

        # 4. Clear goods market (consumers demand goods, firms sell, prices adjust)
        govt_demand = self.government.government_spending_stimulus(self)
        market_results = self.goods_market.clear_market(self.consumers, self.firms, govt_demand)

        # 5. Firms pay wages and calculate profits
        for firm in self.firms:
            firm.pay_wages()
            firm.calculate_profit()
            firm.make_investment_decision(
                interest_rate,
                xi=config.FIRM_INVESTMENT_SHARE,
                kappa=config.FIRM_PRODUCTIVITY_GROWTH_COEFF
            )

        # 7. Adjust wages based on firm-level labor shortages
        self.labor_market.adjust_wages(
            self.firms,
            unemployment_rate=labor_results['unemployment_rate']
        )

        # 8. Central bank policy (if auto mode)
        if self.central_bank.auto_policy:
            current_inflation = market_results['inflation_rate']
            current_unemployment = labor_results['unemployment_rate']
            self.central_bank.taylor_rule(current_inflation, current_unemployment)

        # 9. Government budget
        self.government.calculate_budget_balance()

        # 10. Calculate metrics
        current_metrics = self.metrics.update_metrics(
            self.consumers,
            self.firms,
            self.government,
            self.central_bank,
            self.goods_market
        )

        # Advance time
        self.current_step += 1
        self.schedule.step()
        if self._recession_cooldown > 0:
            self._recession_cooldown -= 1
        if self._inflation_cooldown > 0:
            self._inflation_cooldown -= 1

        return current_metrics

    def run_simulation(self, steps):
        """Run simulation for specified number of steps"""
        results = []
        for _ in range(steps):
            metrics = self.step()
            results.append(metrics)
        return results

    def get_current_state(self):
        """Get current state of the economy"""
        return self.metrics.get_latest_metrics()

    def reset(self):
        """Reset the simulation to initial conditions"""
        self.current_step = 0
        self.metrics.reset_history()
        self.labor_market = LaborMarket(rng=self.random)
        self.goods_market = GoodsMarket()
        # Re-create all agents
        self.consumers = []
        self.firms = []
        self.schedule = RandomActivation(self)
        self._create_agents(
            config.INITIAL_VAT_RATE,
            config.INITIAL_PAYROLL_RATE,
            config.INITIAL_CORPORATE_RATE,
            config.INITIAL_INTEREST_RATE,
            config.INITIAL_WELFARE_PAYMENT,
            config.INITIAL_GOVT_SPENDING
        )

    # Policy control methods (for dashboard)
    def set_tax_rate(self, rate):
        """Update government tax rate"""
        self.government.set_tax_rate(rate)

    def set_interest_rate(self, rate):
        """Update central bank interest rate"""
        self.central_bank.set_interest_rate(rate)

    def set_welfare_payment(self, amount):
        """Update welfare payment"""
        self.government.set_welfare_payment(amount)

    def set_govt_spending(self, amount):
        """Update government spending"""
        self.government.set_govt_spending(amount)

    def enable_auto_monetary_policy(self, enabled):
        """Enable/disable automatic monetary policy"""
        self.central_bank.enable_auto_policy(enabled)

    def trigger_crisis(self, crisis_type):
        """Trigger a pre-configured crisis scenario"""
        if crisis_type == 'recession':
            # Reduce consumer wealth (simulates demand shock)
            for consumer in self.consumers:
                consumer.wealth *= 0.6
                consumer.propensity_to_consume = max(0.3, consumer.propensity_to_consume - 0.1)
            # Reduce firm capital
            for firm in self.firms:
                firm.capital *= 0.6
                # Slash expected demand and trim open positions
                baseline_expected = self.goods_market.get_expected_demand_per_firm(len(self.firms))
                firm.expected_future_demand = max(1, baseline_expected * 0.3)
                firm.labor_demand = max(1, int(firm.labor_demand * 0.3))
                firm.inventory *= 1.2
                firm.wage_offered *= 0.9
                firm.productivity *= 0.8
            # Lower aggregate demand and raise price sensitivity (households pull back)
            self.goods_market.smoothed_demand = max(
                10, self.goods_market.smoothed_demand * 0.1
            )
            self.goods_market.price_sensitivity = min(
                self.goods_market.price_sensitivity * 1.1, 2.0
            )
            # Cut discretionary government demand
            self.government.govt_spending *= 0.7
            self._recession_cooldown = max(self._recession_cooldown, 6)
            # Central bank responds
            self.central_bank.crisis_response('recession')

        elif crisis_type == 'inflation':
            # Increase money supply (too much money chasing goods)
            self.central_bank.money_supply *= 1.5
            # Increase govt spending
            self.government.govt_spending *= 1.5
            # Households flush with cash and less price sensitive
            for consumer in self.consumers:
                consumer.wealth *= 1.2
            self.goods_market.smoothed_demand = min(
                500, self.goods_market.smoothed_demand * 1.5
            )
            self.goods_market.price_sensitivity = max(
                0.5, self.goods_market.price_sensitivity * 0.8
            )
            # Firms face supply bottlenecks and lift prices
            for firm in self.firms:
                firm.inventory *= 0.5
                firm.price *= 1.12
                uplift_base = self.goods_market.get_expected_demand_per_firm(len(self.firms)) or 1
                if firm.expected_future_demand <= 0:
                    firm.expected_future_demand = uplift_base
                firm.expected_future_demand = min(
                    uplift_base * 2,
                    firm.expected_future_demand * 1.3 + 10
                )
            self._inflation_cooldown = max(self._inflation_cooldown, 5)
            # Central bank responds
            self.central_bank.crisis_response('inflation')
