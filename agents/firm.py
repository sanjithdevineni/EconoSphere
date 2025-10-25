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

    def __init__(self, unique_id, model, initial_capital, productivity=2.0, gamma=0.7):
        super().__init__(model)
        self.unique_id = unique_id
        self.capital = initial_capital  # Physical capital stock (machines, buildings)
        self.cash = initial_capital * 0.1  # Financial position (liquid assets)
        self.productivity = productivity  # Total factor productivity
        self.gamma = gamma  # Returns to scale parameter (0.6-0.8 typical)
        self.employees = []
        self.labor_demand = 0
        self.production = 0
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.price = 10  # Initial price
        self.inventory = 0
        self.wage_offered = 1000  # Initial wage
        self.depreciation_rate = 0.05  # 5% capital depreciation per period

    def determine_labor_demand(self, expected_demand):
        """
        Decide how many workers to hire based on expected demand for goods

        Formula: desired_labor = expected_demand / productivity

        Note: With diminishing returns (Q = A × L^γ), the relationship is:
        L = (expected_demand / A) ^ (1/γ)

        We use a simpler approximation here.
        """
        # Labor needed to produce expected output
        # Approximate inverse of production function
        if expected_demand > 0 and self.productivity > 0:
            # Approximate: L ≈ (Q/A)^(1/γ)
            desired_labor = (expected_demand / self.productivity) ** (1.0 / self.gamma)
            self.labor_demand = max(1, int(desired_labor))
        else:
            self.labor_demand = 1

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
        Produce goods based on number of employees with diminishing returns

        Production function: output = productivity * (labor ^ gamma)
        where gamma is the returns to scale parameter (typically 0.6-0.8)

        This creates diminishing marginal returns to labor
        """
        num_workers = len(self.employees)
        if num_workers > 0:
            self.production = self.productivity * (num_workers ** self.gamma)
        else:
            self.production = 0
        self.inventory += self.production
        return self.production

    def set_price(self, market_demand, market_supply, theta_d=0.1, theta_c=0.1):
        """
        Adjust price based on market conditions using adaptive pricing

        Formula: price_{t+1} = price_t * [1 + theta_d * excess_demand_ratio
                                             + theta_c * unit_cost_change]

        where:
        - theta_d: sensitivity to demand (0.05-0.2 typical)
        - theta_c: sensitivity to cost changes (0.05-0.2 typical)
        - excess_demand_ratio: (demand - supply) / max(supply, 1)
        """
        # Calculate excess demand ratio
        if market_supply > 0:
            excess_demand_ratio = (market_demand - market_supply) / max(market_supply, 1)
        else:
            excess_demand_ratio = 0

        # Calculate unit cost (wage per unit of output)
        if self.production > 0:
            current_unit_cost = (len(self.employees) * self.wage_offered) / self.production
        else:
            current_unit_cost = 0

        # Store previous unit cost for comparison
        if not hasattr(self, 'previous_unit_cost'):
            self.previous_unit_cost = current_unit_cost

        # Calculate unit cost change
        if self.previous_unit_cost > 0:
            unit_cost_change = (current_unit_cost - self.previous_unit_cost) / self.previous_unit_cost
        else:
            unit_cost_change = 0

        # Update price using continuous adjustment
        price_adjustment = theta_d * excess_demand_ratio + theta_c * unit_cost_change
        self.price = self.price * (1 + price_adjustment)

        # Floor price to avoid negative or too low
        self.price = max(1, self.price)

        # Update previous unit cost for next period
        self.previous_unit_cost = current_unit_cost

    def sell_goods(self, quantity_sold):
        """
        Sell goods and record revenue
        """
        actual_sold = min(quantity_sold, self.inventory)
        self.revenue = actual_sold * self.price
        self.inventory -= actual_sold
        return actual_sold

    def pay_wages(self):
        """Pay all employees (affects cash, not capital stock)"""
        total_wages = len(self.employees) * self.wage_offered
        self.costs += total_wages
        self.cash -= total_wages  # Wages paid from cash
        return total_wages

    def calculate_profit(self):
        """Calculate profit/loss (affects cash, not capital stock)"""
        self.profit = self.revenue - self.costs
        self.cash += self.profit  # Profit retained as cash
        return self.profit

    def make_investment_decision(self, interest_rate, xi=0.1, kappa=0.1):
        """
        Decide whether to invest in expansion based on:
        - Current profitability and cash availability
        - Interest rates (borrowing cost)

        Capital accounting: capital_{t+1} = (1 - δ) * capital_t + investment_t
        Productivity growth: productivity_{t+1} = productivity_t * (1 + κ * investment_t / capital_t)

        where:
        - ξ (xi): share of profit/cash invested (typically 0.1)
        - κ (kappa): productivity growth coefficient (typically 0.1)
        - δ (delta): depreciation rate

        Investment is paid from cash and adds to physical capital stock.
        """
        # Step 1: Apply capital depreciation
        self.capital = max(0, (1 - self.depreciation_rate) * self.capital)

        # Step 2: Decide on investment based on profitability and interest rates
        investment = 0
        if self.profit > 0 and interest_rate < 0.08 and self.cash > 0:
            # Invest a fraction of available cash in capital
            investment = min(xi * self.profit, self.cash * 0.5)  # Don't invest more than 50% of cash

            # Pay for investment from cash
            self.cash -= investment

            # Add investment to physical capital stock
            self.capital += investment

            # Productivity growth proportional to investment ratio (embodied technological change)
            if self.capital > 0:
                investment_ratio = investment / max(self.capital, 1)
                productivity_growth = kappa * investment_ratio
                self.productivity = self.productivity * (1 + productivity_growth)

        return investment

    def step(self):
        """
        Firm's decision-making in each time step
        """
        # Reset per-step variables
        self.revenue = 0
        self.costs = 0
        self.profit = 0
        self.production = 0
