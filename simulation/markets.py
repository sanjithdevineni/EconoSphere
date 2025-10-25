
"""
Market mechanisms for labor and goods
"""

import random


class LaborMarket:
    """Coordinates labor market interactions between consumers and firms."""

    def __init__(self, rng=None):
        self.market_wage = 1000  # Average market wage
        self.total_employment = 0
        self.unemployment_rate = 0
        self._rng = rng or random.Random()

    def clear_market(self, consumers, firms):
        """Match unemployed workers with firms seeking labor."""
        for consumer in consumers:
            consumer.seek_employment()

        job_openings = []
        for firm in firms:
            firm.employees = []
            for _ in range(firm.labor_demand):
                job_openings.append(firm)

        unemployed = [c for c in consumers if not c.employed]
        self._rng.shuffle(unemployed)

        matches = 0
        for i, firm in enumerate(job_openings):
            if i < len(unemployed):
                worker = unemployed[i]
                firm.hire_worker(worker, firm.wage_offered)
                matches += 1

        self.total_employment = matches
        total_workers = len(consumers)
        self.unemployment_rate = 1 - (matches / total_workers) if total_workers > 0 else 0

        if firms:
            self.market_wage = sum(f.wage_offered for f in firms) / len(firms)

        return {
            'employment': self.total_employment,
            'unemployment_rate': self.unemployment_rate,
            'market_wage': self.market_wage,
        }

    def adjust_wages(self, firms, eta=None, unemployment_rate=None):
        """Adjust wages based on labor shortages or slack."""
        if eta is None:
            import config
            eta = config.WAGE_ADJUSTMENT_SPEED

        for firm in firms:
            vacancies = firm.labor_demand
            hires = len(firm.employees)
            unfilled_vacancies = max(0, vacancies - hires)
            labor_shortage = (unfilled_vacancies / vacancies) if vacancies > 0 else 0

            if labor_shortage > 0:
                wage_adjustment = eta * labor_shortage
                firm.wage_offered = firm.wage_offered * (1 + wage_adjustment)
            elif unemployment_rate is not None and unemployment_rate > 0.1:
                downward_speed = min(eta, 0.03)
                reduction = downward_speed * min(0.5, unemployment_rate)
                firm.wage_offered = firm.wage_offered * (1 - reduction)

            firm.wage_offered = max(500, firm.wage_offered)


class GoodsMarket:
    """Coordinates goods market interactions and price discovery."""

    def __init__(self):
        self.total_demand = 0
        self.total_supply = 0
        self.cpi = 10
        self.previous_cpi = 10
        self.inflation_rate = 0
        self.price_sensitivity = 1.0
        self.demand_smoothing = 0.3
        self.smoothed_demand = 20.0

    def collect_demand(self, consumers, firms):
        """Collect planned demand per firm and by consumer."""
        firm_totals = {firm.unique_id: 0.0 for firm in firms}
        consumer_demands = {}

        for consumer in consumers:
            demand_map = consumer.allocate_budget_across_firms(firms, self.price_sensitivity)
            consumer_demands[consumer.unique_id] = demand_map
            for firm_id, quantity in demand_map.items():
                firm_totals[firm_id] = firm_totals.get(firm_id, 0.0) + quantity

        self.total_demand = sum(firm_totals.values())
        return firm_totals, consumer_demands

    def collect_supply(self, firms):
        """Aggregate firm production."""
        self.total_supply = sum(f.production for f in firms)
        return self.total_supply

    def get_expected_demand_per_firm(self, num_firms):
        if num_firms <= 0:
            return self.smoothed_demand
        return self.smoothed_demand / num_firms

    def clear_market(self, consumers, firms, govt_spending=0):
        """Match supply and demand, returning realized transactions."""
        for firm in firms:
            firm.produce()
        self.collect_supply(firms)

        firm_demands, consumer_demands = self.collect_demand(consumers, firms)
        consumer_totals = {firm.unique_id: 0.0 for firm in firms}
        for demand_map in consumer_demands.values():
            for firm_id, quantity in demand_map.items():
                consumer_totals[firm_id] = consumer_totals.get(firm_id, 0.0) + quantity

        govt_demands = {}
        if govt_spending > 0 and firms:
            avg_price = sum(f.price for f in firms) / len(firms)
            govt_quantity = govt_spending / max(avg_price, 1)
            for firm in firms:
                if self.total_supply > 0:
                    firm_share = firm.production / self.total_supply
                    govt_amount = govt_quantity * firm_share
                    firm_demands[firm.unique_id] = firm_demands.get(firm.unique_id, 0.0) + govt_amount
                    govt_demands[firm.unique_id] = govt_amount

        total_sales_quantity = 0.0
        firm_prices = {}
        fulfillment_ratios = {}
        realized_gov_quantity = 0.0

        for firm in firms:
            firm_id = firm.unique_id
            demand_for_firm = firm_demands.get(firm_id, 0.0)
            consumer_demand = consumer_totals.get(firm_id, 0.0)
            price = firm.price
            actual_sold = firm.sell_goods(demand_for_firm)
            total_sales_quantity += actual_sold
            firm_prices[firm_id] = price

            total_planned = consumer_demand + govt_demands.get(firm_id, 0.0)
            if total_planned > 0 and consumer_demand > 0:
                consumer_sold = actual_sold * (consumer_demand / total_planned)
                ratio = min(1.0, consumer_sold / consumer_demand)
            elif consumer_demand > 0:
                consumer_sold = min(actual_sold, consumer_demand)
                ratio = consumer_sold / consumer_demand
            else:
                consumer_sold = 0.0
                ratio = 0.0

            realized_gov_quantity += max(0.0, actual_sold - consumer_sold)
            fulfillment_ratios[firm_id] = ratio

            firm.expected_future_demand = consumer_sold + 0.1 * max(0.0, consumer_demand - consumer_sold)
            lower_bound = max(1.0, consumer_sold * 0.5)
            upper_bound = max(lower_bound, consumer_sold + 10)
            firm.expected_future_demand = max(lower_bound, min(upper_bound, firm.expected_future_demand))

        consumer_purchases = {}
        realized_consumer_quantity = 0.0
        for consumer in consumers:
            demand_map = consumer_demands.get(consumer.unique_id, {})
            total_qty = 0.0
            total_spending = 0.0
            for firm_id, planned_qty in demand_map.items():
                ratio = fulfillment_ratios.get(firm_id, 0.0)
                actual_qty = planned_qty * ratio
                if actual_qty <= 0:
                    continue
                price = firm_prices.get(firm_id, 0.0)
                total_qty += actual_qty
                total_spending += actual_qty * price
            consumer_purchases[consumer.unique_id] = {
                'quantity': total_qty,
                'spending': total_spending,
            }
            realized_consumer_quantity += total_qty

        realized_total_demand = realized_consumer_quantity + realized_gov_quantity
        self.total_demand = sum(firm_demands.values())

        import config
        for firm in firms:
            firm_id = firm.unique_id
            demand_for_firm = firm_demands.get(firm_id, 0.0)
            supply_from_firm = firm.production
            firm.set_price(
                demand_for_firm,
                supply_from_firm,
                theta_d=config.PRICE_DEMAND_SENSITIVITY,
                theta_c=config.PRICE_COST_SENSITIVITY,
            )

        if firms:
            total_production = sum(f.production for f in firms)
            if total_production > 0:
                self.cpi = sum(f.price * (f.production / total_production) for f in firms)
            else:
                self.cpi = sum(f.price for f in firms) / len(firms)

        if self.previous_cpi > 0:
            self.inflation_rate = (self.cpi - self.previous_cpi) / self.previous_cpi
        else:
            self.inflation_rate = 0
        self.previous_cpi = self.cpi

        observed_demand = realized_total_demand if realized_total_demand > 0 else total_sales_quantity
        if observed_demand > 0:
            self.smoothed_demand = (
                (1 - self.demand_smoothing) * self.smoothed_demand
                + self.demand_smoothing * observed_demand
            )
        else:
            self.smoothed_demand = (1 - self.demand_smoothing) * self.smoothed_demand
        self.smoothed_demand = max(10, min(self.smoothed_demand, 500))

        return {
            'total_demand': self.total_demand,
            'total_supply': self.total_supply,
            'cpi': self.cpi,
            'inflation_rate': self.inflation_rate,
            'market_cleared': total_sales_quantity,
            'consumer_purchases': consumer_purchases,
            'realized_consumer_quantity': realized_consumer_quantity,
            'realized_total_demand': realized_total_demand,
        }

    def adjust_firm_prices(self, firms):
        """Fallback inventory-based price adjustment."""
        for firm in firms:
            if firm.inventory > firm.production * 2:
                firm.price *= 0.95
            elif firm.inventory < firm.production * 0.5:
                firm.price *= 1.05
            firm.price = max(1, firm.price)
