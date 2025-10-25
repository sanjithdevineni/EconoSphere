"""
Economic metrics calculator
"""


class MetricsCalculator:
    """
    Calculates key economic indicators from simulation state
    """

    def __init__(self):
        self.history = {
            'gdp': [],
            'unemployment': [],
            'inflation': [],
            'gini': [],
            'avg_wage': [],
            'avg_price': [],
            'govt_debt': [],
            'interest_rate': []
        }
        self.latest_metrics = None

    def calculate_gdp(self, firms):
        """
        GDP = Total value of goods produced
        Simplified: Sum of all firm revenues
        """
        gdp = sum(firm.revenue for firm in firms)
        return gdp

    def calculate_unemployment_rate(self, consumers):
        """
        Unemployment Rate = (Unemployed / Labor Force) * 100
        """
        total = len(consumers)
        unemployed = sum(1 for c in consumers if not c.employed)
        rate = (unemployed / total) * 100 if total > 0 else 0
        return rate

    def calculate_inflation_rate(self, current_price, previous_price):
        """
        Inflation Rate = (Current Price - Previous Price) / Previous Price * 100
        """
        if previous_price > 0:
            inflation = ((current_price - previous_price) / previous_price) * 100
        else:
            inflation = 0
        return inflation

    def calculate_gini_coefficient(self, consumers):
        """
        Gini Coefficient: Measure of wealth inequality (0 = perfect equality, 1 = perfect inequality)

        Formula: G = (2 * sum(i * wealth_i)) / (n * sum(wealth_i)) - (n + 1) / n
        """
        if not consumers:
            return 0

        # Get wealth distribution
        wealth = sorted([c.wealth for c in consumers])
        n = len(wealth)
        total_wealth = sum(wealth)

        if total_wealth == 0:
            return 0

        # Calculate Gini
        cumulative = 0
        for i, w in enumerate(wealth, 1):
            cumulative += i * w

        gini = (2 * cumulative) / (n * total_wealth) - (n + 1) / n
        return gini

    def calculate_average_wage(self, consumers):
        """
        Average wage across employed consumers
        """
        employed = [c for c in consumers if c.employed]
        if employed:
            avg_wage = sum(c.income for c in employed) / len(employed)
        else:
            avg_wage = 0
        return avg_wage

    def calculate_average_price(self, firms):
        """
        Average price level across firms
        """
        if firms:
            avg_price = sum(f.price for f in firms) / len(firms)
        else:
            avg_price = 0
        return avg_price

    def update_metrics(self, consumers, firms, government, central_bank, goods_market):
        """
        Calculate all metrics at once and store them in history.
        Returns a dictionary of current metrics.
        """
        gdp = self.calculate_gdp(firms)
        unemployment = self.calculate_unemployment_rate(consumers)
        inflation = goods_market.inflation_rate * 100  # Convert to percentage
        gini = self.calculate_gini_coefficient(consumers)
        avg_wage = self.calculate_average_wage(consumers)
        avg_price = self.calculate_average_price(firms)
        govt_debt = government.debt
        budget_balance = government.budget_balance
        interest_rate = central_bank.interest_rate * 100  # Convert to percentage
        money_supply = central_bank.money_supply

        # Store in history
        self.history['gdp'].append(gdp)
        self.history['unemployment'].append(unemployment)
        self.history['inflation'].append(inflation)
        self.history['gini'].append(gini)
        self.history['avg_wage'].append(avg_wage)
        self.history['avg_price'].append(avg_price)
        self.history['govt_debt'].append(govt_debt)
        self.history['interest_rate'].append(interest_rate)

        metrics = {
            'gdp': gdp,
            'unemployment': unemployment,
            'inflation': inflation,
            'gini': gini,
            'avg_wage': avg_wage,
            'avg_price': avg_price,
            'govt_debt': govt_debt,
            'budget_balance': budget_balance,
            'interest_rate': interest_rate,
            'money_supply': money_supply
        }
        self.latest_metrics = metrics
        return metrics

    def get_latest_metrics(self):
        """Return the most recently computed metrics without mutating history."""
        if self.latest_metrics is None:
            return {
                'gdp': 0,
                'unemployment': 0,
                'inflation': 0,
                'gini': 0,
                'avg_wage': 0,
                'avg_price': 0,
                'govt_debt': 0,
                'budget_balance': 0,
                'interest_rate': 0,
                'money_supply': 0
            }
        return self.latest_metrics.copy()

    def get_history(self):
        """Return historical time series data"""
        return self.history

    def reset_history(self):
        """Clear all historical data"""
        for key in self.history:
            self.history[key] = []
        self.latest_metrics = None
