
"""
Market mechanisms for labor and goods.
"""

import random


class LaborMarket:
    """Coordinates labor market interactions between consumers and firms."""

    def __init__(self, rng=None):
        self.market_wage = 1000
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
            unfilled = max(0, vacancies - hires)
            shortage = (unfilled / vacancies) if vacancies > 0 else 0

            if shortage > 0:
                firm.wage_offered *= 1 + eta * shortage
            elif unemployment_rate is not None and unemployment_rate > 0.1:
                downward_speed = min(eta, 0.03)
                reduction = downward_speed * min(0.5, unemployment_rate)
                firm.wage_offered *= 1 - reduction

            firm.wage_offered = max(500, firm.wage_offered)


class GoodsMarket:
    """Coordinates goods market interactions and price discovery."""

    def __init__(self):
        self.total_demand = 0.0
        self.total_supply = 0.0
        self.cpi = 10.0
        self.previous_cpi = 10.0
        self.inflation_rate = 0.0
        self.price_sensitivity = 1.0
        self.demand_smoothing = 0.3
        self.smoothed_demand = 20.0
        self.last_firm_demands = {}

    def collect_demand(self, consumers, firms):
        """Collect planned demand per firm and by consumer."""
        firm_totals = {firm.unique_id: 0.0 for firm in firms}
        consumer_demands = {}

        for consumer in consumers:
            demand_map = consumer.allocate_budget_across_firms(firms, self.price_sensitivity)
            consumer_demands[consumer.unique_id] = demand_map
            for firm_id, qty in demand_map.items():
                firm_totals[firm_id] = firm_totals.get(firm_id, 0.0) + qty

        self.total_demand = sum(firm_totals.values())
        self.last_firm_demands = dict(firm_totals)
        return firm_totals, consumer_demands

    def collect_supply(self, firms):
        self.total_supply = sum(f.production for f in firms)
        return self.total_supply

    def get_expected_demand_per_firm(self, num_firms):
        if num_firms <= 0:
            return self.smoothed_demand
        return self.smoothed_demand / num_firms

    def clear_market(self, consumers, firms, govt_spending=0):
        """Match supply and demand, returning realised transactions."""
        for firm in firms:
            firm.produce()
        self.collect_supply(firms)

        firm_demands, consumer_demands = self.collect_demand(consumers, firms)
        consumer_totals = {firm.unique_id: 0.0 for firm in firms}
        for demand_map in consumer_demands.values():
            for firm_id, qty in demand_map.items():
                consumer_totals[firm_id] = consumer_totals.get(firm_id, 0.0) + qty

        govt_demands = {}
        if govt_spending > 0 and firms:
            avg_price = sum(f.price for f in firms) / len(firms)
            govt_qty = govt_spending / max(avg_price, 1.0)
            for firm in firms:
                if self.total_supply > 0:
                    share = firm.production / self.total_supply
                    amount = govt_qty * share
                    firm_demands[firm.unique_id] = firm_demands.get(firm.unique_id, 0.0) + amount
                    govt_demands[firm.unique_id] = amount

        total_sales_qty = 0.0
        firm_prices = {}
        fulfillment = {}
        realised_gov_qty = 0.0

        import config
        alpha = getattr(config, 'DEMAND_ADJUSTMENT_ALPHA', 0.35)

        for firm in firms:
            fid = firm.unique_id
            demand_for_firm = firm_demands.get(fid, 0.0)
            consumer_demand = consumer_totals.get(fid, 0.0)
            price = firm.price
            actual_sold = firm.sell_goods(demand_for_firm)
            total_sales_qty += actual_sold
            firm_prices[fid] = price

            total_planned = consumer_demand + govt_demands.get(fid, 0.0)
            if total_planned > 0 and consumer_demand > 0:
                consumer_sold = actual_sold * (consumer_demand / total_planned)
                ratio = min(1.0, consumer_sold / consumer_demand)
            elif consumer_demand > 0:
                consumer_sold = min(actual_sold, consumer_demand)
                ratio = consumer_sold / consumer_demand
            else:
                consumer_sold = 0.0
                ratio = 0.0

            realised_gov_qty += max(0.0, actual_sold - consumer_sold)
            fulfillment[fid] = ratio

            firm.expected_future_demand = consumer_sold + alpha * max(0.0, demand_for_firm - consumer_sold)
            lower = max(1.0, consumer_sold * 0.5)
            upper = max(lower, consumer_sold + 15)
            firm.expected_future_demand = max(lower, min(upper, firm.expected_future_demand))

        consumer_purchases = {}
        realised_consumer_qty = 0.0
        for consumer in consumers:
            demand_map = consumer_demands.get(consumer.unique_id, {})
            total_qty = 0.0
            total_spend = 0.0
            for fid, planned_qty in demand_map.items():
                ratio = fulfillment.get(fid, 0.0)
                actual_qty = planned_qty * ratio
                if actual_qty <= 0:
                    continue
                price = firm_prices.get(fid, 0.0)
                total_qty += actual_qty
                total_spend += actual_qty * price
            consumer_purchases[consumer.unique_id] = {
                'quantity': total_qty,
                'spending': total_spend,
            }
            realised_consumer_qty += total_qty

        realised_total_demand = realised_consumer_qty + realised_gov_qty
        self.total_demand = sum(firm_demands.values())

        for firm in firms:
            fid = firm.unique_id
            demand_for_firm = firm_demands.get(fid, 0.0)
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

        observed_demand = realised_total_demand if realised_total_demand > 0 else total_sales_qty
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
            'market_cleared': total_sales_qty,
            'consumer_purchases': consumer_purchases,
            'realized_consumer_quantity': realised_consumer_qty,
            'realized_total_demand': realised_total_demand,
        }

    def adjust_firm_prices(self, firms):
        for firm in firms:
            if firm.inventory > firm.production * 2:
                firm.price *= 0.95
            elif firm.inventory < firm.production * 0.5:
                firm.price *= 1.05
            firm.price = max(1, firm.price)
