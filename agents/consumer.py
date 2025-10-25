"""
Consumer Agent: Represents individual consumers in the economy
"""

import math
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

    def receive_income(self, amount):
        """Receive income from employment (stored but not added to wealth yet)"""
        self.income = amount

    def receive_welfare(self, amount):
        """Receive welfare payment from government (stored but not added to wealth yet)"""
        self.welfare_received = amount

    def allocate_budget_across_firms(self, firms, price_sensitivity=1.0):
        """
        Allocate consumption budget across firms based on their prices

        Formula:
            share_ij = exp(-lambda * price_j) / sum_k exp(-lambda * price_k)
            quantity_ij = (share_ij * consumption_budget) / price_j

        Args:
            firms: list of Firm objects
            price_sensitivity: lambda parameter (higher = more price-sensitive)

        Returns:
            dict mapping firm_id -> quantity demanded from that firm
        """
        disposable_income = max(0, self.income + self.welfare_received)
        accessible_savings = max(0, min(self.wealth * 0.05, self.wealth))
        cash_on_hand = disposable_income + accessible_savings

        # Consumption budget based on MPC (only a share of cash is spent)
        consumption_budget = self.propensity_to_consume * cash_on_hand
        consumption_budget = min(consumption_budget, cash_on_hand)

        self.consumption = consumption_budget

        # If no budget or no firms, return empty demand
        if consumption_budget <= 0 or not firms:
            # Unspent disposable income adds to savings
            self.wealth = self.wealth + disposable_income
            return {}

        # Compute price-sensitive shares using exponential model
        # exp(-lambda * price) gives higher weight to lower prices
        price_weights = {}
        total_weight = 0

        for firm in firms:
            if firm.price > 0:
                weight = math.exp(-price_sensitivity * firm.price)
                price_weights[firm.unique_id] = weight
                total_weight += weight

        # Allocate budget across firms
        firm_demands = {}
        if total_weight > 0:
            for firm in firms:
                share = price_weights.get(firm.unique_id, 0) / total_weight
                spending_on_firm = share * consumption_budget
                quantity = spending_on_firm / max(firm.price, 0.01)  # avoid division by zero
                firm_demands[firm.unique_id] = quantity

        # Portion of consumption financed from disposable income first
        income_used = min(consumption_budget, disposable_income)
        savings_used = min(consumption_budget - income_used, accessible_savings)

        # Update wealth: add unspent disposable income, subtract savings used
        self.wealth = max(0, self.wealth + (disposable_income - income_used) - savings_used)

        return firm_demands

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
