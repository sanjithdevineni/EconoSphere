"""
Main economy simulation model
"""

import numpy as np
from mesa import Model
from mesa.time import RandomActivation

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
        initial_tax_rate=config.INITIAL_TAX_RATE,
        initial_interest_rate=config.INITIAL_INTEREST_RATE,
        initial_welfare=config.INITIAL_WELFARE_PAYMENT,
        initial_govt_spending=config.INITIAL_GOVT_SPENDING
    ):
        super().__init__()

        self.num_consumers = num_consumers
        self.num_firms = num_firms
        self.schedule = RandomActivation(self)
        self.current_step = 0

        # Initialize markets
        self.labor_market = LaborMarket()
        self.goods_market = GoodsMarket()
        self.metrics = MetricsCalculator()

        # Create agents
        self.consumers = []
        self.firms = []
        self.government = None
        self.central_bank = None

        self._create_agents(initial_tax_rate, initial_interest_rate, initial_welfare, initial_govt_spending)

    def _create_agents(self, tax_rate, interest_rate, welfare, govt_spending):
        """Initialize all agents"""

        # Create consumers
        for i in range(self.num_consumers):
            wealth = np.random.normal(
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
            capital = np.random.normal(
                config.INITIAL_FIRM_CAPITAL_MEAN,
                config.INITIAL_FIRM_CAPITAL_STD
            )
            capital = max(10000, capital)  # Minimum capital

            firm = Firm(
                unique_id=self.num_consumers + i,
                model=self,
                initial_capital=capital,
                productivity=config.FIRM_PRODUCTIVITY
            )
            firm.wage_offered = config.INITIAL_WAGE
            firm.price = config.INITIAL_PRICE_LEVEL
            self.firms.append(firm)
            self.schedule.add(firm)

        # Create government
        self.government = Government(
            unique_id=self.num_consumers + self.num_firms,
            model=self,
            tax_rate=tax_rate,
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

        # 1. Firms determine labor demand
        interest_rate = self.central_bank.get_borrowing_cost()
        for firm in self.firms:
            # Estimate demand based on previous period
            expected_demand = self.goods_market.total_demand if self.goods_market.total_demand > 0 else 100
            firm.determine_labor_demand(expected_demand, interest_rate)

        # 2. Clear labor market
        labor_results = self.labor_market.clear_market(self.consumers, self.firms)

        # 3. Government fiscal policy
        self.government.collect_taxes(self.consumers)
        self.government.distribute_welfare(self.consumers)

        # 4. Consumers consume (creates demand)
        self.goods_market.collect_demand(self.consumers, self.goods_market.price_level)

        # 5. Clear goods market
        govt_demand = self.government.government_spending_stimulus(self)
        market_results = self.goods_market.clear_market(self.consumers, self.firms, govt_demand)

        # 6. Firms pay wages and calculate profits
        for firm in self.firms:
            firm.pay_wages()
            firm.calculate_profit()
            firm.make_investment_decision(interest_rate)

        # 7. Adjust wages based on unemployment
        self.labor_market.adjust_wages(self.firms, labor_results['unemployment_rate'])

        # 8. Central bank policy (if auto mode)
        if self.central_bank.auto_policy:
            current_inflation = market_results['inflation_rate']
            current_unemployment = labor_results['unemployment_rate']
            self.central_bank.taylor_rule(current_inflation, current_unemployment)

        # 9. Government budget
        self.government.calculate_budget_balance()

        # 10. Calculate metrics
        current_metrics = self.metrics.get_all_metrics(
            self.consumers,
            self.firms,
            self.government,
            self.central_bank,
            self.goods_market
        )

        # Advance time
        self.current_step += 1
        self.schedule.step()

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
        return self.metrics.get_all_metrics(
            self.consumers,
            self.firms,
            self.government,
            self.central_bank,
            self.goods_market
        )

    def reset(self):
        """Reset the simulation to initial conditions"""
        self.current_step = 0
        self.metrics.reset_history()
        # Re-create all agents
        self.consumers = []
        self.firms = []
        self.schedule = RandomActivation(self)
        self._create_agents(
            config.INITIAL_TAX_RATE,
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
                consumer.wealth *= 0.7
            # Reduce firm capital
            for firm in self.firms:
                firm.capital *= 0.7
            # Central bank responds
            self.central_bank.crisis_response('recession')

        elif crisis_type == 'inflation':
            # Increase money supply (too much money chasing goods)
            self.central_bank.money_supply *= 1.5
            # Increase govt spending
            self.government.govt_spending *= 1.5
            # Central bank responds
            self.central_bank.crisis_response('inflation')
