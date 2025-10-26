"""
Government Agent: Represents fiscal policy authority with strategic crypto reserve
"""

from mesa import Agent


class Government(Agent):
    """
    Government agent that:
    - Collects taxes
    - Provides welfare/transfers
    - Controls government spending
    - Tracks budget balance
    - Manages strategic cryptocurrency reserve (HACKATHON FEATURE!)
    """

    def __init__(self, unique_id, model, vat_rate=0.15, payroll_rate=0.10, corporate_rate=0.20,
                 welfare_payment=500, govt_spending=10000):
        super().__init__(model)
        self.unique_id = unique_id
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

        # === STRATEGIC CRYPTO RESERVE ===
        # Like US Treasury proposal to hold Bitcoin as strategic asset
        self.crypto_reserve = 0  # Coins held in reserve
        self.crypto_reserve_value = 0  # Current USD value
        self.total_crypto_purchased = 0  # Total coins ever purchased
        self.total_crypto_cost = 0  # Total USD spent on crypto
        self.crypto_reserve_enabled = False  # Policy toggle

        # Reserve purchase parameters
        self.crypto_purchase_budget = 0  # Annual budget for crypto purchases
        self.target_reserve_size = 0  # Target reserve (in USD or coins)

    def set_vat_rate(self, rate):
        """Adjust VAT rate (policy control)"""
        self.vat_rate = max(0, min(1.0, rate))

    def set_payroll_rate(self, rate):
        """Adjust payroll tax rate"""
        self.payroll_rate = max(0, min(1.0, rate))

    def set_corporate_rate(self, rate):
        """Adjust corporate tax rate"""
        self.corporate_rate = max(0, min(1.0, rate))

    def set_tax_rate(self, rate):
        """Compatibility wrapper for legacy API expecting a single tax rate setter."""
        self.set_vat_rate(rate)

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

    def enable_crypto_reserve(self, annual_budget=0):
        """
        Enable strategic cryptocurrency reserve program

        Like US Treasury proposal to accumulate Bitcoin as strategic asset

        Args:
            annual_budget: Annual budget for crypto purchases (USD)
        """
        self.crypto_reserve_enabled = True
        self.crypto_purchase_budget = annual_budget

    def disable_crypto_reserve(self):
        """Disable crypto reserve program (but keep existing holdings)"""
        self.crypto_reserve_enabled = False
        self.crypto_purchase_budget = 0

    def buy_crypto_for_reserve(self, crypto_market, amount):
        """
        Purchase cryptocurrency for strategic reserve

        THIS IS A MAJOR NARRATIVE EVENT!
        - Legitimizes crypto (government backing)
        - Creates massive demand shock
        - Affects crypto price and sentiment

        Args:
            crypto_market: CryptoMarket instance
            amount: USD amount to spend on crypto purchase

        Returns:
            Coins purchased
        """
        if amount <= 0:
            return 0

        # Use the crypto market's government_buy method
        # (which handles price impact and legitimacy boost)
        initial_holdings = crypto_market.government_holdings
        crypto_market.government_buy(amount)
        coins_purchased = crypto_market.government_holdings - initial_holdings

        # Track in government records
        self.crypto_reserve = crypto_market.government_holdings
        self.total_crypto_purchased += coins_purchased
        self.total_crypto_cost += amount

        # Update reserve value
        self.crypto_reserve_value = self.crypto_reserve * crypto_market.price

        # Spending reduces fiscal balance
        self.total_spending += amount

        return coins_purchased

    def sell_crypto_from_reserve(self, crypto_market, amount_usd):
        """
        Sell cryptocurrency from strategic reserve

        Government sells crypto (bearish signal)

        Args:
            crypto_market: CryptoMarket instance
            amount_usd: USD value to sell

        Returns:
            USD proceeds
        """
        if amount_usd <= 0:
            return 0

        if self.crypto_reserve <= 0:
            return 0

        # Calculate how many coins to sell
        coins_to_sell = min(self.crypto_reserve, amount_usd / crypto_market.price)

        if coins_to_sell <= 0:
            return 0

        # Sell (negative price impact)
        proceeds = coins_to_sell * crypto_market.price
        self.crypto_reserve -= coins_to_sell
        crypto_market.government_holdings -= coins_to_sell

        # Update reserve value
        self.crypto_reserve_value = self.crypto_reserve * crypto_market.price

        # Revenue increases fiscal balance
        self.tax_revenue += proceeds

        # Negative sentiment from government selling
        crypto_market.regulatory_sentiment = max(0, crypto_market.regulatory_sentiment - 0.1)
        crypto_market.trigger_crash(severity=0.05)  # Small 5% crash from selling

        return proceeds

    def update_crypto_reserve_value(self, crypto_market):
        """
        Update the current value of crypto reserve

        Args:
            crypto_market: CryptoMarket instance
        """
        if crypto_market:
            self.crypto_reserve_value = self.crypto_reserve * crypto_market.price

    def execute_reserve_policy(self, crypto_market, economic_conditions):
        """
        Execute strategic crypto reserve accumulation policy

        Policy logic:
        - Buy when budget surplus exists
        - Buy more during high inflation (inflation hedge narrative)
        - Stop buying if reserve target reached

        Args:
            crypto_market: CryptoMarket instance
            economic_conditions: Dict with inflation, gdp, etc.
        """
        if not self.crypto_reserve_enabled:
            return

        if not crypto_market:
            return

        # Only buy if we have budget surplus
        if self.budget_balance <= 0:
            return

        # Calculate purchase amount
        # Base: use portion of crypto purchase budget
        purchase_amount = self.crypto_purchase_budget / 12  # Monthly allocation

        # Boost purchases during high inflation (strategic hedge)
        inflation = economic_conditions.get('inflation', 0.02)
        if inflation > 0.04:  # Inflation above 4%
            inflation_multiplier = 1 + ((inflation - 0.04) * 10)  # More inflation = more crypto
            purchase_amount *= inflation_multiplier

        # Cap at available surplus
        purchase_amount = min(purchase_amount, self.budget_balance * 0.1)  # Max 10% of surplus

        if purchase_amount >= 1000:  # Minimum purchase threshold
            self.buy_crypto_for_reserve(crypto_market, purchase_amount)

    def get_fiscal_summary(self):
        """Return summary of fiscal position including crypto reserve"""
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
            'debt': self.debt,
            # Crypto reserve info
            'crypto_reserve': self.crypto_reserve,
            'crypto_reserve_value': self.crypto_reserve_value,
            'crypto_reserve_enabled': self.crypto_reserve_enabled,
            'crypto_purchase_budget': self.crypto_purchase_budget,
            'total_crypto_purchased': self.total_crypto_purchased,
            'total_crypto_cost': self.total_crypto_cost,
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
