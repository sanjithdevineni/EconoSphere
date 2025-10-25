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

    def adjust_wages(self, firms, eta=None):
        """
        Firms adjust wages based on their own labor shortage

        Formula: wage_{j,t+1} = wage_{j,t} * (1 + η * labor_shortage_j)

        where:
        - labor_shortage_j = max(0, vacancies_j - hires_j) / max(1, vacancies_j)
        - η (eta): wage adjustment parameter (typically 0.05-0.15)

        If a firm can't fill all its vacancies, it raises wages to attract workers.
        """
        # Use config value if not provided
        if eta is None:
            import config
            eta = config.WAGE_ADJUSTMENT_SPEED

        for firm in firms:
            # Calculate labor shortage
            vacancies = firm.labor_demand
            hires = len(firm.employees)
            unfilled_vacancies = max(0, vacancies - hires)

            if vacancies > 0:
                labor_shortage = unfilled_vacancies / vacancies
            else:
                labor_shortage = 0

            # Adjust wage based on shortage
            wage_adjustment = eta * labor_shortage
            firm.wage_offered = firm.wage_offered * (1 + wage_adjustment)

            # Minimum wage floor (as index, not absolute dollar amount)
            min_wage_index = 500  # Base minimum wage
            firm.wage_offered = max(min_wage_index, firm.wage_offered)


class GoodsMarket:
    """
    Coordinates goods market interactions
    Implements price discovery and market clearing
    """

    def __init__(self):
        self.total_demand = 0
        self.total_supply = 0
        self.cpi = 10  # Consumer Price Index (weighted average of firm prices)
        self.previous_cpi = 10
        self.inflation_rate = 0
        self.price_sensitivity = 1.0  # lambda parameter for price-sensitive allocation

    def collect_demand(self, consumers, firms):
        """
        Aggregate consumer demand using firm-level prices
        Returns dict with total demand value and firm-specific demands
        """
        # Each consumer allocates budget across firms based on prices
        firm_demands = {firm.unique_id: 0 for firm in firms}

        for consumer in consumers:
            consumer_demand = consumer.allocate_budget_across_firms(firms, self.price_sensitivity)
            for firm_id, quantity in consumer_demand.items():
                firm_demands[firm_id] += quantity

        # Total demand in quantity terms
        self.total_demand = sum(firm_demands.values())
        return firm_demands

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
        1. Firms produce goods
        2. Firms set prices based on previous period's market conditions
        3. Consumers allocate budgets across firms based on prices
        4. Market clears with firm-specific sales
        5. Compute CPI from firm prices (no separate price level update)
        """

        # 1. Firms produce
        for firm in firms:
            firm.produce()

        # Collect total supply
        self.collect_supply(firms)

        # 2. Collect demand with firm-level prices (from previous period)
        firm_demands = self.collect_demand(consumers, firms)

        # Add government spending (allocated proportionally by firm output)
        if govt_spending > 0 and firms:
            avg_price = sum(f.price for f in firms) / len(firms)
            govt_quantity = govt_spending / max(avg_price, 1)

            for firm in firms:
                if self.total_supply > 0:
                    firm_share = firm.production / self.total_supply
                    firm_demands[firm.unique_id] += govt_quantity * firm_share

        # 3. Firms sell goods (short-side rule at firm level)
        total_sales_value = 0
        total_sales_quantity = 0

        for firm in firms:
            demand_for_firm = firm_demands.get(firm.unique_id, 0)
            actual_sold = firm.sell_goods(demand_for_firm)
            total_sales_value += actual_sold * firm.price
            total_sales_quantity += actual_sold

        # 4. Firms adjust prices based on their own demand vs supply
        import config
        for firm in firms:
            demand_for_firm = firm_demands.get(firm.unique_id, 0)
            supply_from_firm = firm.production
            firm.set_price(
                demand_for_firm,
                supply_from_firm,
                theta_d=config.PRICE_DEMAND_SENSITIVITY,
                theta_c=config.PRICE_COST_SENSITIVITY
            )

        # 5. Compute CPI as weighted average of firm prices
        if firms:
            # Weight by production share
            total_production = sum(f.production for f in firms)
            if total_production > 0:
                self.cpi = sum(f.price * (f.production / total_production) for f in firms)
            else:
                self.cpi = sum(f.price for f in firms) / len(firms)

        # Calculate inflation from CPI
        if self.previous_cpi > 0:
            self.inflation_rate = (self.cpi - self.previous_cpi) / self.previous_cpi
        else:
            self.inflation_rate = 0
        self.previous_cpi = self.cpi

        # Update total demand for next period
        total_demand_quantity = sum(firm_demands.values())

        return {
            'total_demand': total_demand_quantity,
            'total_supply': self.total_supply,
            'cpi': self.cpi,
            'inflation_rate': self.inflation_rate,
            'market_cleared': total_sales_quantity
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
