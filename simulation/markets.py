"""
Market mechanisms for labor and goods
"""

import random


class LaborMarket:
    """
    Coordinates labor market interactions between consumers and firms
    Implements job matching and wage determination
    """

    def __init__(self, rng=None):
        self.market_wage = 1000  # Average market wage
        self.total_employment = 0
        self.unemployment_rate = 0
        self._rng = rng or random.Random()
        self.matching_efficiency = 0.96

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
        self._rng.shuffle(unemployed)

        # Match workers to jobs
        matches = 0
        worker_index = 0
        for firm in job_openings:
            if worker_index >= len(unemployed):
                break
            if self._rng.random() <= self.matching_efficiency:
                worker = unemployed[worker_index]
                firm.hire_worker(worker, firm.wage_offered)
                matches += 1
                worker_index += 1
            else:
                worker_index += 1

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

    def adjust_wages(self, firms, eta=None, unemployment_rate=None):
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

            if labor_shortage > 0:
                # Adjust wage based on shortage
                wage_adjustment = eta * labor_shortage
                firm.wage_offered = firm.wage_offered * (1 + wage_adjustment)
            elif unemployment_rate is not None and unemployment_rate > 0.1:
                # Ease wages downward when unemployment is persistently high
                downward_speed = min(eta, 0.03)
                reduction = downward_speed * min(0.5, unemployment_rate)
                firm.wage_offered = firm.wage_offered * (1 - reduction)

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
        self.smoothed_demand = 20
        self.demand_smoothing = 0.25
        self.max_price_adjustment = 0.1
        self.last_firm_demands = {}
        self.expected_demand_smoothing = 0.3
        self.minimum_expected_per_firm = 18.0

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
        self.last_firm_demands = dict(firm_demands)
        return firm_demands

    def collect_supply(self, firms):
        """
        Aggregate firm production (supply)
        """
        self.total_supply = sum(f.production for f in firms)
        return self.total_supply

    def get_expected_demand_per_firm(self, num_firms):
        """
        Return smoothed market demand per firm for use in planning.
        """
        if num_firms <= 0:
            return self.smoothed_demand
        per_firm = self.smoothed_demand / num_firms
        return max(self.minimum_expected_per_firm, per_firm)

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
            backlog = max(0.0, demand_for_firm - actual_sold)
            target_expectation = actual_sold + backlog

            if getattr(firm, "expected_future_demand", 0) > 0:
                smoothing = self.expected_demand_smoothing
                firm.expected_future_demand = (
                    (1 - smoothing) * firm.expected_future_demand
                    + smoothing * target_expectation
                )
            else:
                firm.expected_future_demand = target_expectation

            lower_bound = max(1.0, actual_sold * 0.5)
            upper_bound = max(lower_bound, actual_sold + backlog * 0.35 + 5)
            firm.expected_future_demand = max(lower_bound, min(upper_bound, firm.expected_future_demand))
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

        observed_demand = total_sales_quantity + 0.2 * max(total_demand_quantity - total_sales_quantity, 0)

        if observed_demand > 0:
            self.smoothed_demand = (
                (1 - self.demand_smoothing) * self.smoothed_demand
                + self.demand_smoothing * observed_demand
            )
        else:
            self.smoothed_demand = (1 - self.demand_smoothing) * self.smoothed_demand

        self.smoothed_demand = max(10, min(self.smoothed_demand, 500))

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

    def adjust_demand_expectations(self, unemployment_rate):
        """Adapt price sensitivity and minimum demand floor to slack."""
        if unemployment_rate > 0.25:
            target_sensitivity = max(0.5, 1.0 - (unemployment_rate - 0.25) * 0.8)
        elif unemployment_rate < 0.08:
            target_sensitivity = min(1.2, 1.0 + (0.08 - unemployment_rate) * 1.5)
        else:
            target_sensitivity = 1.0

        self.price_sensitivity += (target_sensitivity - self.price_sensitivity) * 0.2

        target_min = 14 + unemployment_rate * 25
        self.minimum_expected_per_firm += (target_min - self.minimum_expected_per_firm) * 0.2
        self.minimum_expected_per_firm = min(self.minimum_expected_per_firm, 30)
