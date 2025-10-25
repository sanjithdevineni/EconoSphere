"""
Firm Agent: Represents businesses in the economy
"""

import numpy as np
from mesa import Agent


class Firm(Agent):
    """
    A firm agent that:
    - Hires workers
    - Produces goods
    - Sets prices
    - Makes investment decisions based on interest rates
    """

    def __init__(self, unique_id, model, initial_capital, productivity=2.0):
        super().__init__(unique_id, model)
        self.capital = initial_capital
        self.productivity = productivity  # Output per worker
        self.employees = []
        self.labor_demand = 0
        self.production = 0
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.price = 10  # Initial price
        self.inventory = 0
        self.wage_offered = 1000  # Initial wage

    def determine_labor_demand(self, expected_demand, interest_rate):
        """
        Decide how many workers to hire based on:
        - Expected demand for goods
        - Interest rates (cost of capital/investment)
        """
        # Base labor demand on expected production needs
        base_labor_demand = int(expected_demand / self.productivity)

        # Adjust for interest rates (high rates = less expansion)
        interest_rate_factor = max(0.5, 1 - (interest_rate * 2))

        # Adjust for profitability
        if self.profit > 0:
            profitability_factor = 1.2
        else:
            profitability_factor = 0.8

        self.labor_demand = max(1, int(base_labor_demand * interest_rate_factor * profitability_factor))
        return self.labor_demand

    def hire_worker(self, worker, wage):
        """Hire a worker"""
        self.employees.append(worker)
        worker.get_employed(self, wage)

    def fire_workers(self, num_to_fire):
        """Fire workers if needed to reduce costs"""
        for _ in range(min(num_to_fire, len(self.employees))):
            if self.employees:
                worker = self.employees.pop()
                worker.employed = False
                worker.employer = None

    def produce(self):
        """
        Produce goods based on number of employees
        Production = workers × productivity
        """
        num_workers = len(self.employees)
        self.production = num_workers * self.productivity
        self.inventory += self.production
        return self.production

    def set_price(self, market_demand, market_supply):
        """
        Adjust price based on market conditions
        Simple supply/demand pricing
        """
        if market_supply > 0:
            demand_supply_ratio = market_demand / market_supply

            # Raise price if demand > supply, lower if supply > demand
            if demand_supply_ratio > 1.1:
                self.price *= 1.05  # 5% increase
            elif demand_supply_ratio < 0.9:
                self.price *= 0.95  # 5% decrease

            # Floor price to avoid negative
            self.price = max(1, self.price)

    def sell_goods(self, quantity_sold):
        """
        Sell goods and record revenue
        """
        actual_sold = min(quantity_sold, self.inventory)
        self.revenue = actual_sold * self.price
        self.inventory -= actual_sold
        return actual_sold

    def pay_wages(self):
        """Pay all employees"""
        total_wages = len(self.employees) * self.wage_offered
        self.costs += total_wages
        self.capital -= total_wages
        return total_wages

    def calculate_profit(self):
        """Calculate profit/loss"""
        self.profit = self.revenue - self.costs
        self.capital += self.profit
        return self.profit

    def make_investment_decision(self, interest_rate):
        """
        Decide whether to invest in expansion based on:
        - Current profitability
        - Interest rates (borrowing cost)
        """
        if self.profit > 0 and interest_rate < 0.08:
            # Invest 10% of profit in capital
            investment = self.profit * 0.1
            self.capital += investment
            # Small productivity boost from investment
            self.productivity *= 1.01
            return investment
        return 0

    def step(self):
        """
        Firm's decision-making in each time step
        """
        # Reset per-step variables
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.production = 0
