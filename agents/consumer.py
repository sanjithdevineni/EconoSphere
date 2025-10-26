
"""
Consumer Agent: Represents individual consumers in the economy
"""

import math
import config
from mesa import Agent


class Consumer(Agent):
    """Household agent with consumption-savings and investment behaviour."""

    def __init__(self, unique_id, model, initial_wealth, propensity_to_consume=0.7):
        super().__init__(model)
        self.unique_id = unique_id
        self.wealth = initial_wealth
        self.income = 0
        self.employed = False
        self.employer = None
        self.propensity_to_consume = propensity_to_consume
        self.consumption = 0
        self.taxes_paid = 0
        self.welfare_received = 0
        self.planned_consumption = 0
        self.last_quantity_consumed = 0

        # === INVESTMENT PORTFOLIO ===
        # Stock holdings {firm_id: num_shares}
        self.stock_portfolio = {}
        self.stock_portfolio_value = 0

        # Crypto holdings
        self.crypto_holdings = 0
        self.crypto_value = 0

        # Investment behavior parameters
        self.risk_tolerance = config.CONSUMER_RISK_TOLERANCE if hasattr(config, 'CONSUMER_RISK_TOLERANCE') else 0.3
        self.investment_propensity = 0.2  # % of savings allocated to investments

        # Wealth thresholds for investment
        self.min_wealth_to_invest = 5000  # Only invest if wealth > 5k

        # Investment sentiment (follows market)
        self.investment_sentiment = 0.0  # -1 (fearful) to +1 (greedy)

    def receive_income(self, amount):
        self.income = amount

    def receive_welfare(self, amount):
        self.welfare_received = amount

    def allocate_budget_across_firms(self, firms, price_sensitivity=1.0):
        disposable_income = max(0.0, self.income + self.welfare_received)
        wealth_draw = min(self.wealth, self.wealth * config.CONSUMER_WEALTH_SPEND_RATE)
        resources = self.wealth + disposable_income
        consumption_budget = min(
            self.propensity_to_consume * disposable_income + wealth_draw,
            resources,
        )

        self.planned_consumption = consumption_budget

        if consumption_budget <= 0 or not firms:
            return {}

        price_weights = {}
        total_weight = 0.0
        for firm in firms:
            if firm.price > 0:
                weight = math.exp(-price_sensitivity * firm.price)
                price_weights[firm.unique_id] = weight
                total_weight += weight

        firm_demands = {}
        if total_weight > 0:
            for firm in firms:
                weight = price_weights.get(firm.unique_id, 0.0)
                if weight <= 0:
                    continue
                share = weight / total_weight
                spending_on_firm = share * consumption_budget
                quantity = spending_on_firm / max(firm.price, 0.01)
                if quantity > 0:
                    firm_demands[firm.unique_id] = quantity

        return firm_demands

    def finalize_consumption(self, spending, quantity):
        spending = max(0.0, spending)
        quantity = max(0.0, quantity)
        resources = self.wealth + self.income + self.welfare_received
        spending = min(spending, resources)
        self.consumption = spending
        self.last_quantity_consumed = quantity
        self.wealth = max(0.0, resources - spending)

    def seek_employment(self):
        self.employed = False
        self.employer = None
        self.income = 0

    def get_employed(self, employer, wage):
        self.employed = True
        self.employer = employer
        self.receive_income(wage)

    def update_portfolio_values(self, stock_market=None, crypto_market=None):
        """
        Update the current value of investment portfolio

        Args:
            stock_market: StockMarket instance
            crypto_market: CryptoMarket instance
        """
        # Update stock portfolio value
        self.stock_portfolio_value = 0
        if stock_market:
            for firm_id, shares in self.stock_portfolio.items():
                price = stock_market.get_price(firm_id)
                self.stock_portfolio_value += shares * price

        # Update crypto value
        self.crypto_value = 0
        if crypto_market:
            self.crypto_value = self.crypto_holdings * crypto_market.price

    def get_total_wealth(self):
        """Get total wealth including cash + investments"""
        return self.wealth + self.stock_portfolio_value + self.crypto_value

    def make_investment_decisions(self, stock_market=None, crypto_market=None):
        """
        Decide how much to invest in stocks vs crypto vs hold cash

        Investment logic:
        - Only invest if wealth > threshold
        - Allocate based on sentiment and risk tolerance
        - Higher wealth → more investment
        - Bull markets → more stocks
        - High inflation → more crypto

        Args:
            stock_market: StockMarket instance
            crypto_market: CryptoMarket instance
        """
        if not stock_market and not crypto_market:
            return  # No markets available

        total_wealth = self.get_total_wealth()

        # Only invest if wealthy enough
        if total_wealth < self.min_wealth_to_invest:
            return

        # Calculate investable amount (savings not used for consumption)
        savings = self.wealth - self.consumption
        if savings <= 0:
            return

        investment_budget = savings * self.investment_propensity

        # Adjust based on market sentiment
        if stock_market:
            market_sentiment = stock_market.sentiment
            # Bull market → invest more, Bear market → hold cash
            sentiment_multiplier = 1 + (market_sentiment * 0.5)
            investment_budget *= sentiment_multiplier

        # Cap investment at available cash
        investment_budget = min(investment_budget, self.wealth)

        if investment_budget <= 100:  # Minimum investment threshold
            return

        # === ALLOCATION DECISION ===
        # Split between stocks and crypto based on economic conditions

        stock_allocation = 0.7  # Default 70% stocks, 30% crypto

        # Get economic state from model
        if hasattr(self.model, 'inflation') and crypto_market:
            inflation = self.model.inflation

            # High inflation → More crypto (inflation hedge narrative)
            if inflation > 0.04:
                stock_allocation = 0.5  # 50/50 split
            elif inflation > 0.06:
                stock_allocation = 0.3  # 30% stocks, 70% crypto

        # Risk tolerance affects allocation
        # High risk tolerance → more crypto
        crypto_allocation = 1 - stock_allocation
        crypto_allocation *= (1 + self.risk_tolerance)
        stock_allocation = 1 - crypto_allocation

        # === BUY STOCKS ===
        if stock_market and stock_allocation > 0:
            stock_budget = investment_budget * stock_allocation
            self._buy_stocks(stock_market, stock_budget)

        # === BUY CRYPTO ===
        if crypto_market and crypto_allocation > 0:
            crypto_budget = investment_budget * crypto_allocation
            self._buy_crypto(crypto_market, crypto_budget)

    def _buy_stocks(self, stock_market, budget):
        """
        Buy stocks with given budget

        Strategy: Diversify across multiple firms weighted by market cap

        Args:
            stock_market: StockMarket instance
            budget: Amount to spend on stocks
        """
        if budget <= 0:
            return

        # Get all firms and their market caps
        firms = stock_market.firms
        if not firms:
            return

        # Weight by market cap (buy more of larger firms)
        total_market_cap = 0
        firm_weights = {}

        for firm in firms:
            price = stock_market.get_price(firm.unique_id)
            shares = stock_market.shares_outstanding.get(firm.unique_id, 1000)
            market_cap = price * shares
            total_market_cap += market_cap
            firm_weights[firm.unique_id] = market_cap

        if total_market_cap == 0:
            return

        # Allocate budget proportionally
        for firm in firms:
            firm_id = firm.unique_id
            weight = firm_weights[firm_id] / total_market_cap
            firm_budget = budget * weight

            price = stock_market.get_price(firm_id)
            if price <= 0:
                continue

            shares_to_buy = firm_budget / price

            if shares_to_buy > 0.01:  # Minimum shares threshold
                # Update portfolio
                if firm_id not in self.stock_portfolio:
                    self.stock_portfolio[firm_id] = 0

                self.stock_portfolio[firm_id] += shares_to_buy

                # Deduct from wealth
                actual_cost = shares_to_buy * price
                self.wealth -= actual_cost

    def _buy_crypto(self, crypto_market, budget):
        """
        Buy cryptocurrency with given budget

        Args:
            crypto_market: CryptoMarket instance
            budget: Amount to spend on crypto
        """
        if budget <= 0:
            return

        price = crypto_market.price
        if price <= 0:
            return

        coins_to_buy = budget / price

        if coins_to_buy > 0:
            self.crypto_holdings += coins_to_buy
            self.wealth -= budget

    def sell_investments_if_needed(self, stock_market=None, crypto_market=None):
        """
        Sell investments if cash is running low (emergency liquidity)

        Args:
            stock_market: StockMarket instance
            crypto_market: CryptoMarket instance
        """
        # Only sell if wealth is critically low
        if self.wealth > 1000:
            return

        # Need to raise emergency funds
        emergency_target = 2000
        needed = emergency_target - self.wealth

        if needed <= 0:
            return

        # Sell crypto first (more liquid, higher volatility)
        if crypto_market and self.crypto_holdings > 0:
            coins_to_sell = min(self.crypto_holdings, needed / crypto_market.price)
            proceeds = coins_to_sell * crypto_market.price
            self.crypto_holdings -= coins_to_sell
            self.wealth += proceeds
            needed -= proceeds

        # If still need money, sell stocks
        if needed > 0 and stock_market and self.stock_portfolio:
            # Sell proportionally from all holdings
            for firm_id in list(self.stock_portfolio.keys()):
                if needed <= 0:
                    break

                shares = self.stock_portfolio[firm_id]
                price = stock_market.get_price(firm_id)

                shares_to_sell = min(shares, needed / price)
                proceeds = shares_to_sell * price

                self.stock_portfolio[firm_id] -= shares_to_sell
                self.wealth += proceeds
                needed -= proceeds

                # Remove if no shares left
                if self.stock_portfolio[firm_id] <= 0.01:
                    del self.stock_portfolio[firm_id]

    def step(self):
        self.income = 0
        self.taxes_paid = 0
        self.welfare_received = 0
        self.consumption = 0
        self.planned_consumption = 0
        self.last_quantity_consumed = 0
