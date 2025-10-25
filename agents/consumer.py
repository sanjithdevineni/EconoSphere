
"""
Consumer Agent: Represents individual consumers in the economy
"""

import math
import config
from mesa import Agent


class Consumer(Agent):
    """Household agent with simple consumption-savings behaviour."""

    def __init__(self, unique_id, model, initial_wealth, propensity_to_consume=0.7):
        super().__init__(model)
        self.unique_id = unique_id
        self.wealth = initial_wealth
        self.income = 0
        self.employed = False
        self.employer = None
        self.propensity_to_consume = propensity_to_consume
        self.consumption = 0
        self.taxes_paid = 0
        self.welfare_received = 0
        self.planned_consumption = 0
        self.last_quantity_consumed = 0

    def receive_income(self, amount):
        self.income = amount

    def receive_welfare(self, amount):
        self.welfare_received = amount

    def allocate_budget_across_firms(self, firms, price_sensitivity=1.0):
        disposable_income = max(0.0, self.income + self.welfare_received)
        wealth_draw = min(self.wealth, self.wealth * config.CONSUMER_WEALTH_SPEND_RATE)
        resources = self.wealth + disposable_income
        consumption_budget = min(
            self.propensity_to_consume * disposable_income + wealth_draw,
            resources,
        )

        self.planned_consumption = consumption_budget

        if consumption_budget <= 0 or not firms:
            return {}

        price_weights = {}
        total_weight = 0.0
        for firm in firms:
            if firm.price > 0:
                weight = math.exp(-price_sensitivity * firm.price)
                price_weights[firm.unique_id] = weight
                total_weight += weight

        firm_demands = {}
        if total_weight > 0:
            for firm in firms:
                weight = price_weights.get(firm.unique_id, 0.0)
                if weight <= 0:
                    continue
                share = weight / total_weight
                spending_on_firm = share * consumption_budget
                quantity = spending_on_firm / max(firm.price, 0.01)
                if quantity > 0:
                    firm_demands[firm.unique_id] = quantity

        return firm_demands

    def finalize_consumption(self, spending, quantity):
        spending = max(0.0, spending)
        quantity = max(0.0, quantity)
        resources = self.wealth + self.income + self.welfare_received
        spending = min(spending, resources)
        self.consumption = spending
        self.last_quantity_consumed = quantity
        self.wealth = max(0.0, resources - spending)

    def seek_employment(self):
        self.employed = False
        self.employer = None
        self.income = 0

    def get_employed(self, employer, wage):
        self.employed = True
        self.employer = employer
        self.receive_income(wage)

    def step(self):
        self.income = 0
        self.taxes_paid = 0
        self.welfare_received = 0
        self.consumption = 0
        self.planned_consumption = 0
        self.last_quantity_consumed = 0
