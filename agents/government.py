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

    def __init__(self, unique_id, model, vat_rate=0.15, payroll_rate=0.10, corporate_rate=0.20,
                 welfare_payment=500, govt_spending=10000):
        super().__init__(unique_id, model)
        # Tax rates
        self.vat_rate = vat_rate  # Value Added Tax on consumption
        self.payroll_rate = payroll_rate  # Payroll tax on wages
        self.corporate_rate = corporate_rate  # Corporate tax on profits

        self.welfare_payment = welfare_payment
        self.govt_spending = govt_spending

        # Fiscal tracking
        self.vat_revenue = 0
        self.payroll_revenue = 0
        self.corporate_revenue = 0
        self.tax_revenue = 0  # Total tax revenue
        self.total_welfare_paid = 0
        self.budget_balance = 0
        self.debt = 0
        self.total_spending = 0

    def set_vat_rate(self, rate):
        """Adjust VAT rate (policy control)"""
        self.vat_rate = max(0, min(1.0, rate))

    def set_payroll_rate(self, rate):
        """Adjust payroll tax rate"""
        self.payroll_rate = max(0, min(1.0, rate))

    def set_corporate_rate(self, rate):
        """Adjust corporate tax rate"""
        self.corporate_rate = max(0, min(1.0, rate))

    def set_welfare_payment(self, amount):
        """Adjust welfare payment per unemployed person"""
        self.welfare_payment = max(0, amount)

    def set_govt_spending(self, amount):
        """Adjust government spending"""
        self.govt_spending = max(0, amount)

    def collect_taxes(self, consumers, firms):
        """
        Collect all taxes: VAT, payroll, and corporate

        Returns total tax revenue
        """
        # 1. VAT: tax on consumer spending
        self.vat_revenue = 0
        for consumer in consumers:
            self.vat_revenue += consumer.consumption * self.vat_rate

        # 2. Payroll Tax: tax on wages paid by firms
        self.payroll_revenue = 0
        for firm in firms:
            total_wages = len(firm.employees) * firm.wage_offered
            self.payroll_revenue += total_wages * self.payroll_rate

        # 3. Corporate Tax: tax on positive profits only
        self.corporate_revenue = 0
        for firm in firms:
            if firm.profit > 0:
                corporate_tax = firm.profit * self.corporate_rate
                self.corporate_revenue += corporate_tax
                firm.cash -= corporate_tax  # Deduct tax from firm cash

        # Total tax revenue
        self.tax_revenue = self.vat_revenue + self.payroll_revenue + self.corporate_revenue
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
            'vat_rate': self.vat_rate,
            'payroll_rate': self.payroll_rate,
            'corporate_rate': self.corporate_rate,
            'vat_revenue': self.vat_revenue,
            'payroll_revenue': self.payroll_revenue,
            'corporate_revenue': self.corporate_revenue,
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
        self.vat_revenue = 0
        self.payroll_revenue = 0
        self.corporate_revenue = 0
        self.tax_revenue = 0
        self.total_welfare_paid = 0
        self.budget_balance = 0
        self.total_spending = 0
