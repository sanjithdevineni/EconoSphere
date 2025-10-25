"""
Government Agent: Represents fiscal policy authority
"""

from mesa import Agent


class Government(Agent):
    """
    Government agent that:
    - Collects taxes
    - Provides welfare/transfers
    - Controls government spending
    - Tracks budget balance
    """

    def __init__(self, unique_id, model, tax_rate=0.20, welfare_payment=500, govt_spending=10000):
        super().__init__(unique_id, model)
        self.tax_rate = tax_rate
        self.welfare_payment = welfare_payment
        self.govt_spending = govt_spending

        # Fiscal tracking
        self.tax_revenue = 0
        self.total_welfare_paid = 0
        self.budget_balance = 0
        self.debt = 0
        self.total_spending = 0

    def set_tax_rate(self, rate):
        """Adjust tax rate (policy control)"""
        self.tax_rate = max(0, min(1.0, rate))  # Keep between 0-100%

    def set_welfare_payment(self, amount):
        """Adjust welfare payment per unemployed person"""
        self.welfare_payment = max(0, amount)

    def set_govt_spending(self, amount):
        """Adjust government spending"""
        self.govt_spending = max(0, amount)

    def collect_taxes(self, consumers):
        """
        Collect taxes from all consumers
        Returns total tax revenue
        """
        self.tax_revenue = 0
        for consumer in consumers:
            tax = consumer.pay_taxes(self.tax_rate)
            self.tax_revenue += tax
        return self.tax_revenue

    def distribute_welfare(self, consumers):
        """
        Pay welfare to unemployed consumers
        Returns total welfare paid
        """
        self.total_welfare_paid = 0
        for consumer in consumers:
            if not consumer.employed:
                consumer.receive_welfare(self.welfare_payment)
                self.total_welfare_paid += self.welfare_payment
        return self.total_welfare_paid

    def government_spending_stimulus(self, economy_model):
        """
        Government spending creates demand in the economy
        Simplified: spending goes directly into aggregate demand
        """
        # In a more complex model, this would fund infrastructure,
        # create government jobs, etc.
        return self.govt_spending

    def calculate_budget_balance(self):
        """
        Calculate budget surplus/deficit
        Positive = surplus, Negative = deficit
        """
        self.total_spending = self.total_welfare_paid + self.govt_spending
        self.budget_balance = self.tax_revenue - self.total_spending

        # Add to debt if running deficit
        if self.budget_balance < 0:
            self.debt += abs(self.budget_balance)
        else:
            # Pay down debt if surplus
            debt_payment = min(self.budget_balance, self.debt)
            self.debt -= debt_payment

        return self.budget_balance

    def get_fiscal_summary(self):
        """Return summary of fiscal position"""
        return {
            'tax_rate': self.tax_rate,
            'tax_revenue': self.tax_revenue,
            'welfare_payment': self.welfare_payment,
            'total_welfare_paid': self.total_welfare_paid,
            'govt_spending': self.govt_spending,
            'total_spending': self.total_spending,
            'budget_balance': self.budget_balance,
            'debt': self.debt
        }

    def step(self):
        """Reset per-step tracking variables"""
        self.tax_revenue = 0
        self.total_welfare_paid = 0
        self.budget_balance = 0
        self.total_spending = 0
