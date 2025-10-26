"""
Stock Market Agent - Equity exchange for firm shares
"""

from typing import Dict, List
import random


class StockMarket:
    """
    Stock exchange where firms issue equity and investors trade shares

    Features:
    - Realistic stock pricing based on firm fundamentals
    - Market index tracking
    - Dividend payments
    - Market sentiment dynamics
    - Interest rate sensitivity
    """

    def __init__(self, firms):
        """
        Initialize stock market

        Args:
            firms: List of Firm agents
        """
        self.firms = firms
        self.prices = {}  # {firm_id: current_price}
        self.shares_outstanding = {}  # {firm_id: total_shares}
        self.market_cap = 0
        self.index = 100  # Market index (starts at 100, like S&P 500)
        self.previous_index = 100

        # Market sentiment (-1 to +1)
        self.sentiment = 0.0
        self.fear_greed_index = 50  # 0-100 scale (0=fear, 100=greed)

        # Trading volumes
        self.daily_volume = 0
        self.total_trades = 0

        # Sector tracking
        self.sectors = self._assign_sectors()

        # History
        self.price_history = {firm.unique_id: [] for firm in firms}
        self.index_history = []

        # Initialize shares and prices
        self._initialize_market()

    def _assign_sectors(self) -> Dict[int, str]:
        """Assign sectors to firms for realistic dynamics"""
        sectors = ['Tech', 'Finance', 'Energy', 'Consumer', 'Industrial']
        return {firm.unique_id: random.choice(sectors) for firm in self.firms}

    def _initialize_market(self):
        """Set initial share prices and quantities"""
        for firm in self.firms:
            # Each firm issues shares worth their capital
            self.shares_outstanding[firm.unique_id] = 1000
            # Initial price = capital / shares
            initial_price = max(firm.capital / 1000, 10)
            self.prices[firm.unique_id] = initial_price
            self.price_history[firm.unique_id].append(initial_price)

        self._update_index()
        self.index_history.append(self.index)

    def update_prices(self, interest_rate: float, inflation: float, unemployment: float):
        """
        Update stock prices based on fundamentals and market conditions

        Args:
            interest_rate: Central bank rate (affects discount rate)
            inflation: Current inflation rate
            unemployment: Current unemployment rate
        """
        # Calculate market-wide sentiment
        self._update_sentiment(interest_rate, inflation, unemployment)

        for firm in self.firms:
            firm_id = firm.unique_id

            # 1. FUNDAMENTAL VALUE (Earnings-based)
            earnings = max(firm.profit, 1)

            # P/E ratio depends on interest rates and growth expectations
            # Low rates → High P/E, High rates → Low P/E
            base_pe = 15  # Market average
            rate_adjustment = -(interest_rate - 0.03) * 100  # Deviation from 3% neutral
            growth_premium = 2 if firm.capital > 0 and firm.profit > 0 else -2
            pe_ratio = max(5, base_pe + rate_adjustment + growth_premium)

            fundamental_value = earnings * pe_ratio

            # 2. DIVIDEND YIELD COMPONENT
            # Investors value dividends more when rates are high
            if hasattr(firm, 'dividend_payout'):
                dividend_value = firm.dividend_payout * 10
            else:
                dividend_value = firm.profit * 0.3 * 10  # Assume 30% payout

            # 3. GROWTH EXPECTATIONS
            # Firms with growing capital get premium
            if hasattr(firm, 'capital_growth'):
                growth_factor = 1 + firm.capital_growth * 0.5
            else:
                growth_factor = 1.0

            # 4. SENTIMENT & MOMENTUM
            sentiment_factor = 1 + (self.sentiment * 0.2)  # ±20% from sentiment

            # Current price moves toward fundamental value + sentiment
            target_price = (fundamental_value + dividend_value) * growth_factor * sentiment_factor

            # Smooth price adjustment (not instant)
            adjustment_speed = 0.3  # 30% of gap closed per period
            current_price = self.prices[firm_id]
            new_price = current_price + adjustment_speed * (target_price - current_price)

            # Add realistic noise/volatility
            volatility = 0.05  # 5% daily volatility
            noise = random.gauss(0, volatility)
            new_price *= (1 + noise)

            # Floor price
            new_price = max(1, new_price)

            self.prices[firm_id] = new_price
            self.price_history[firm_id].append(new_price)

        # Update market index
        self._update_index()
        self.index_history.append(self.index)

        # Update fear & greed
        self._update_fear_greed()

    def _update_sentiment(self, interest_rate: float, inflation: float, unemployment: float):
        """
        Update market sentiment based on macro conditions

        Sentiment drivers:
        - Low rates → Positive (cheap borrowing)
        - Low inflation → Positive (stable environment)
        - Low unemployment → Positive (strong economy)
        - Recent returns → Momentum
        """
        # Rate effect (low rates = bullish)
        rate_effect = -(interest_rate - 0.03) * 5  # Neutral at 3%

        # Inflation effect (moderate inflation OK, high/low bad)
        optimal_inflation = 0.02
        inflation_effect = -abs(inflation - optimal_inflation) * 10

        # Unemployment effect (low unemployment = bullish)
        unemployment_effect = -(unemployment - 0.05) * 2  # Neutral at 5%

        # Momentum effect (recent index performance)
        if len(self.index_history) > 1:
            recent_return = (self.index - self.previous_index) / self.previous_index
            momentum_effect = recent_return * 5
        else:
            momentum_effect = 0

        # Combine factors
        new_sentiment = rate_effect + inflation_effect + unemployment_effect + momentum_effect

        # Smooth sentiment changes
        self.sentiment = 0.7 * self.sentiment + 0.3 * new_sentiment

        # Bound sentiment
        self.sentiment = max(-1.0, min(1.0, self.sentiment))

    def _update_index(self):
        """Calculate market-cap weighted index"""
        self.previous_index = self.index

        total_market_cap = 0
        for firm_id in self.prices:
            price = self.prices[firm_id]
            shares = self.shares_outstanding[firm_id]
            market_cap = price * shares
            total_market_cap += market_cap

        self.market_cap = total_market_cap

        # Index scales with market cap (starts at 100)
        initial_cap = sum(f.capital for f in self.firms)
        if initial_cap > 0:
            self.index = 100 * (total_market_cap / initial_cap)

    def _update_fear_greed(self):
        """
        Calculate Fear & Greed Index (0-100)

        Components:
        - Market momentum
        - Stock price strength
        - Volatility
        - Put/call ratio (approximated by sentiment)
        """
        # Market momentum
        if len(self.index_history) > 5:
            recent_returns = [(self.index_history[i] - self.index_history[i-1]) / self.index_history[i-1]
                             for i in range(-5, 0)]
            momentum_score = sum(r > 0 for r in recent_returns) * 20  # 0-100
        else:
            momentum_score = 50

        # Sentiment score
        sentiment_score = (self.sentiment + 1) * 50  # Map -1..1 to 0..100

        # Volatility (low volatility = greed)
        if len(self.index_history) > 10:
            recent_prices = self.index_history[-10:]
            volatility = sum(abs(recent_prices[i] - recent_prices[i-1])
                           for i in range(1, len(recent_prices))) / len(recent_prices)
            volatility_score = max(0, 100 - volatility * 100)  # Lower vol = higher score
        else:
            volatility_score = 50

        # Combine
        self.fear_greed_index = (momentum_score + sentiment_score + volatility_score) / 3
        self.fear_greed_index = max(0, min(100, self.fear_greed_index))

    def get_price(self, firm_id: int) -> float:
        """Get current stock price for a firm"""
        return self.prices.get(firm_id, 0)

    def get_market_return(self) -> float:
        """Get market return (index change %)"""
        if self.previous_index > 0:
            return (self.index - self.previous_index) / self.previous_index
        return 0

    def trigger_crash(self, severity: float = 0.3):
        """
        Trigger market crash

        Args:
            severity: Crash magnitude (0.3 = 30% drop)
        """
        for firm_id in self.prices:
            self.prices[firm_id] *= (1 - severity)

        self.sentiment = -0.8  # Extreme fear
        self.fear_greed_index = 10
        self._update_index()

    def get_state(self) -> Dict:
        """Get current market state"""
        return {
            'index': self.index,
            'market_cap': self.market_cap,
            'sentiment': self.sentiment,
            'fear_greed': self.fear_greed_index,
            'prices': self.prices.copy(),
            'daily_return': self.get_market_return(),
            'sectors': self.sectors
        }
