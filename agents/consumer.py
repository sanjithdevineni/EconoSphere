"""
Consumer Agent: Represents individual consumers in the economy
"""

import numpy as np
from mesa import Agent


class Consumer(Agent):
    """
    A consumer agent that:
    - Earns income from employment
    - Pays taxes
    - Consumes goods
    - Saves or borrows
    """

    def __init__(self, unique_id, model, initial_wealth, propensity_to_consume=0.7):
        super().__init__(unique_id, model)
        self.wealth = initial_wealth
        self.income = 0
        self.employed = False
        self.employer = None
        self.propensity_to_consume = propensity_to_consume
        self.consumption = 0
        self.taxes_paid = 0
        self.welfare_received = 0

    def receive_income(self, amount):
        """Receive income from employment"""
        self.income = amount
        self.wealth += amount

    def receive_welfare(self, amount):
        """Receive welfare payment from government"""
        self.welfare_received = amount
        self.wealth += amount

    def pay_taxes(self, tax_rate):
        """Pay taxes on income"""
        if self.income > 0:
            self.taxes_paid = self.income * tax_rate
            self.wealth -= self.taxes_paid
            return self.taxes_paid
        return 0

    def consume(self, price_level):
        """
        Decide how much to consume based on wealth and propensity to consume
        Returns: quantity demanded
        """
        # Consumption budget (after taxes, plus any savings)
        disposable_income = self.income - self.taxes_paid + self.welfare_received

        # Consume a portion of disposable income
        consumption_budget = disposable_income * self.propensity_to_consume

        # Can't spend more than wealth
        consumption_budget = min(consumption_budget, self.wealth)

        # Quantity demanded at current price level
        if price_level > 0:
            quantity_demanded = consumption_budget / price_level
            self.consumption = consumption_budget
            self.wealth -= consumption_budget
            return quantity_demanded
        return 0

    def seek_employment(self):
        """
        Consumer seeks employment (handled by labor market)
        """
        self.employed = False
        self.employer = None
        self.income = 0

    def get_employed(self, employer, wage):
        """Get hired by a firm"""
        self.employed = True
        self.employer = employer
        self.receive_income(wage)

    def step(self):
        """
        Consumer's decision-making in each time step
        Called by Mesa scheduler
        """
        # Reset per-step variables
        self.income = 0
        self.taxes_paid = 0
        self.welfare_received = 0
        self.consumption = 0
