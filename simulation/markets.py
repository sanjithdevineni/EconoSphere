"""
Market mechanisms for labor and goods
"""

import random


class LaborMarket:
    """
    Coordinates labor market interactions between consumers and firms
    Implements job matching and wage determination
    """

    def __init__(self):
        self.market_wage = 1000  # Average market wage
        self.total_employment = 0
        self.unemployment_rate = 0

    def clear_market(self, consumers, firms):
        """
        Match unemployed workers with firms seeking labor

        Simple matching algorithm:
        1. Firms post job openings (labor_demand)
        2. Unemployed consumers apply
        3. Random matching until positions filled or no workers left
        """

        # Reset employment status
        for consumer in consumers:
            consumer.seek_employment()

        # Collect job openings
        job_openings = []
        for firm in firms:
            firm.employees = []  # Reset employees
            for _ in range(firm.labor_demand):
                job_openings.append(firm)

        # Get unemployed workers
        unemployed = [c for c in consumers if not c.employed]
        random.shuffle(unemployed)

        # Match workers to jobs
        matches = 0
        for i, firm in enumerate(job_openings):
            if i < len(unemployed):
                worker = unemployed[i]
                firm.hire_worker(worker, firm.wage_offered)
                matches += 1

        # Calculate employment statistics
        self.total_employment = matches
        total_workers = len(consumers)
        self.unemployment_rate = 1 - (matches / total_workers) if total_workers > 0 else 0

        # Update market wage (average of offered wages)
        if firms:
            self.market_wage = sum(f.wage_offered for f in firms) / len(firms)

        return {
            'employment': self.total_employment,
            'unemployment_rate': self.unemployment_rate,
            'market_wage': self.market_wage
        }

    def adjust_wages(self, firms, unemployment_rate):
        """
        Firms adjust wages based on labor market tightness
        High unemployment -> lower wages
        Low unemployment -> higher wages
        """
        for firm in firms:
            if unemployment_rate > 0.1:  # High unemployment
                firm.wage_offered *= 0.98  # Decrease wages 2%
            elif unemployment_rate < 0.05:  # Low unemployment (tight labor market)
                firm.wage_offered *= 1.02  # Increase wages 2%

            # Floor wage
            firm.wage_offered = max(500, firm.wage_offered)


class GoodsMarket:
    """
    Coordinates goods market interactions
    Implements price discovery and market clearing
    """

    def __init__(self):
        self.market_price = 10  # Average market price
        self.total_demand = 0
        self.total_supply = 0
        self.price_level = 10
        self.previous_price_level = 10
        self.inflation_rate = 0

    def collect_demand(self, consumers, price_level):
        """
        Aggregate consumer demand at current price level
        """
        self.total_demand = sum(c.consume(price_level) for c in consumers)
        return self.total_demand

    def collect_supply(self, firms):
        """
        Aggregate firm production (supply)
        """
        self.total_supply = sum(f.production for f in firms)
        return self.total_supply

    def clear_market(self, consumers, firms, govt_spending=0):
        """
        Match supply and demand, determine market price

        Process:
        1. Firms set prices based on previous period's market conditions
        2. Consumers demand goods at current price
        3. Market clears, adjust prices for next period
        """

        # Firms produce
        for firm in firms:
            firm.produce()

        # Collect total supply
        self.collect_supply(firms)

        # Government spending adds to demand
        total_demand_with_govt = self.total_demand + (govt_spending / self.price_level)

        # Price adjustment based on supply/demand
        if self.total_supply > 0:
            excess_demand = total_demand_with_govt - self.total_supply

            # If demand > supply, prices rise
            if excess_demand > 0:
                self.price_level *= 1.03  # 3% increase
            # If supply > demand, prices fall
            elif excess_demand < 0:
                self.price_level *= 0.97  # 3% decrease

        # Floor price
        self.price_level = max(1, self.price_level)

        # Calculate inflation
        self.inflation_rate = (self.price_level - self.previous_price_level) / self.previous_price_level
        self.previous_price_level = self.price_level

        # Firms update their prices
        for firm in firms:
            firm.set_price(total_demand_with_govt, self.total_supply)

        # Allocate goods to consumers (simplified: proportional rationing)
        actual_sales = min(total_demand_with_govt, self.total_supply)

        # Firms sell goods and earn revenue
        for firm in firms:
            # Each firm sells proportional to their production
            if self.total_supply > 0:
                firm_sales = (firm.production / self.total_supply) * actual_sales
                firm.sell_goods(firm_sales)

        return {
            'total_demand': total_demand_with_govt,
            'total_supply': self.total_supply,
            'price_level': self.price_level,
            'inflation_rate': self.inflation_rate,
            'market_cleared': actual_sales
        }

    def adjust_firm_prices(self, firms):
        """
        Firms individually adjust prices based on their inventory
        """
        for firm in firms:
            # Too much inventory -> lower price
            if firm.inventory > firm.production * 2:
                firm.price *= 0.95
            # Low inventory -> raise price
            elif firm.inventory < firm.production * 0.5:
                firm.price *= 1.05

            firm.price = max(1, firm.price)
