"""
Cryptocurrency Market Agent - Digital asset with macro-driven dynamics

THIS IS THE HACKATHON DIFFERENTIATOR!
Models crypto's unique relationship with macro policy - no other economic simulator does this.
"""

from typing import Dict
import random
import math


class CryptoMarket:
    """
    Cryptocurrency market with realistic macro-policy interactions

    Unique Features:
    - Inflation hedge narrative (high inflation → crypto adoption)
    - Rate sensitivity (high rates → risk-off, crypto crashes)
    - Government reserve impact (like US Treasury proposals)
    - Adoption network effects
    - Extreme volatility
    - Regulatory sentiment
    """

    def __init__(self, name: str = "Bitcoin"):
        """
        Initialize cryptocurrency market

        Args:
            name: Crypto name (Bitcoin, EconoCoin, etc.)
        """
        self.name = name

        # Price dynamics
        self.price = 50000  # Initial price ($50k like Bitcoin)
        self.price_history = [self.price]

        # Supply (fixed like Bitcoin)
        self.max_supply = 21_000_000
        self.circulating_supply = 19_000_000  # 90% already mined

        # Adoption metrics
        self.holders = 0  # Number of holders
        self.adoption_rate = 0.01  # 1% of population initially
        self.transaction_volume = 0

        # Market dynamics
        self.volatility = 0.15  # 15% daily volatility (realistic for crypto)
        self.liquidity = 1000000  # Market depth

        # Sentiment & narratives
        self.sentiment = 0.0  # -1 (extreme fear) to +1 (extreme greed)
        self.inflation_hedge_belief = 0.3  # 30% believe it's an inflation hedge
        self.regulatory_sentiment = 0.5  # 0 (hostile) to 1 (friendly)

        # Macro sensitivity parameters (UNIQUE TO THIS SIMULATOR!)
        self.inflation_sensitivity = 5.0  # How much inflation drives adoption
        self.rate_sensitivity = -3.0  # How much rates hurt crypto
        self.adoption_momentum = 0.02  # Network effect growth

        # Government/institutional holdings
        self.government_holdings = 0
        self.institutional_holdings = 0

        # Halving events (like Bitcoin)
        self.blocks_until_halving = 210000
        self.mining_reward = 6.25

        # Fear metrics
        self.days_below_ath = 0  # Days since all-time high
        self.all_time_high = self.price
        self.drawdown = 0  # Current drawdown from ATH

    def update_price(self, economic_state: Dict):
        """
        Update crypto price based on macro conditions

        THIS IS THE MAGIC - crypto responds to macro policy in unique ways!

        Args:
            economic_state: Dict with inflation, interest_rate, unemployment, gdp, etc.
        """
        inflation = economic_state.get('inflation', 0.02)
        interest_rate = economic_state.get('interest_rate', 0.03)
        unemployment = economic_state.get('unemployment', 0.05)
        stock_market_return = economic_state.get('stock_return', 0)

        # === MACRO EFFECTS (THE UNIQUE ANGLE) ===

        # 1. INFLATION HEDGE NARRATIVE
        # When inflation rises above 2%, people flee to crypto ("digital gold")
        # This is what happened in 2020-2021!
        inflation_excess = max(0, inflation - 0.02)  # Excess above 2% target
        inflation_boost = inflation_excess * self.inflation_sensitivity * self.inflation_hedge_belief

        # 2. INTEREST RATE EFFECT
        # High rates make crypto less attractive (no yield, opportunity cost)
        # This is what crashed crypto in 2022 when Fed hiked!
        rate_excess = interest_rate - 0.03  # Excess above 3% neutral
        rate_drag = rate_excess * self.rate_sensitivity

        # 3. RISK-OFF / RISK-ON
        # When stocks crash, crypto usually crashes harder (risk-off)
        # When stocks moon, crypto moons harder (risk-on)
        risk_sentiment = stock_market_return * 2.0  # Crypto is 2x levered to stocks

        # 4. UNEMPLOYMENT EFFECT
        # High unemployment → less discretionary income → less crypto buying
        unemployment_effect = -(unemployment - 0.05) * 1.0

        # === ADOPTION DYNAMICS ===

        # 5. NETWORK EFFECTS
        # More holders → more valuable (Metcalfe's Law)
        network_effect = self.adoption_rate * self.adoption_momentum

        # 6. GOVERNMENT LEGITIMACY BOOST
        # If government holds crypto, it legitimizes it (HUGE narrative boost!)
        if self.government_holdings > 0:
            legitimacy_boost = math.log10(self.government_holdings + 1) * 0.05
        else:
            legitimacy_boost = 0

        # 7. REGULATORY SENTIMENT
        # Friendly regulation → boost, hostile → crash
        regulatory_effect = (self.regulatory_sentiment - 0.5) * 0.1

        # === SPECULATION & VOLATILITY ===

        # 8. MOMENTUM / FOMO
        # Recent price action creates FOMO or panic
        if len(self.price_history) > 5:
            recent_returns = [(self.price_history[i] - self.price_history[i-1]) / self.price_history[i-1]
                             for i in range(-5, 0)]
            momentum = sum(recent_returns) * 0.5  # Momentum trading
        else:
            momentum = 0

        # 9. RANDOM VOLATILITY (crypto is wild!)
        random_shock = random.gauss(0, self.volatility)

        # === COMBINE ALL EFFECTS ===
        total_price_change = (
            inflation_boost +      # Inflation hedge narrative
            rate_drag +            # Interest rate opportunity cost
            risk_sentiment +       # Risk-on/risk-off
            unemployment_effect +  # Economic strength
            network_effect +       # Adoption growth
            legitimacy_boost +     # Government validation
            regulatory_effect +    # Regulatory environment
            momentum +             # Speculation
            random_shock           # Volatility
        )

        # Apply price change (with bounds to prevent explosion)
        max_daily_change = 0.5  # Max 50% daily move
        total_price_change = max(-max_daily_change, min(max_daily_change, total_price_change))

        self.price *= (1 + total_price_change)

        # Floor price (can't go below $1)
        self.price = max(1, self.price)

        # Update history
        self.price_history.append(self.price)

        # Keep only recent history (last 200 periods)
        if len(self.price_history) > 200:
            self.price_history.pop(0)

        # === UPDATE ADOPTION ===
        self._update_adoption(total_price_change)

        # === UPDATE SENTIMENT ===
        self._update_sentiment(total_price_change, inflation, interest_rate)

        # === UPDATE ATH METRICS ===
        if self.price > self.all_time_high:
            self.all_time_high = self.price
            self.days_below_ath = 0
        else:
            self.days_below_ath += 1

        self.drawdown = (self.all_time_high - self.price) / self.all_time_high

    def _update_adoption(self, price_change: float):
        """
        Update adoption rate based on price performance

        Network effects: Success breeds success
        """
        # Positive price action → more adoption (FOMO)
        if price_change > 0.05:  # 5% gain
            self.adoption_rate *= 1.02  # 2% more people adopt
        elif price_change < -0.10:  # 10% loss
            self.adoption_rate *= 0.98  # 2% abandon

        # Government holding boosts adoption (legitimacy)
        if self.government_holdings > 0:
            self.adoption_rate *= 1.01

        # Bound adoption (can't exceed 100% or go below 0.1%)
        self.adoption_rate = max(0.001, min(1.0, self.adoption_rate))

    def _update_sentiment(self, price_change: float, inflation: float, interest_rate: float):
        """
        Update market sentiment and narrative beliefs

        Args:
            price_change: Recent price change
            inflation: Current inflation
            interest_rate: Current interest rate
        """
        # Sentiment follows price
        if price_change > 0:
            self.sentiment = min(1.0, self.sentiment + 0.1)
        else:
            self.sentiment = max(-1.0, self.sentiment - 0.1)

        # Inflation hedge belief strengthens when:
        # - Inflation is high AND crypto is rising
        if inflation > 0.04 and price_change > 0:
            self.inflation_hedge_belief = min(1.0, self.inflation_hedge_belief + 0.02)
        elif price_change < -0.1:
            # If crypto crashes, people lose faith in inflation hedge narrative
            self.inflation_hedge_belief = max(0.1, self.inflation_hedge_belief - 0.01)

    def government_buy(self, amount: float):
        """
        Government purchases crypto for strategic reserve

        This is the HUGE narrative event! Like US Treasury proposal.

        Args:
            amount: Dollar amount to purchase
        """
        coins_purchased = amount / self.price
        self.government_holdings += coins_purchased

        # MASSIVE price impact (government buying is bullish signal!)
        demand_shock = amount / (self.price * self.circulating_supply)
        price_pump = min(0.30, demand_shock * 100)  # Cap at 30% instant pump

        self.price *= (1 + price_pump)

        # Legitimacy boost
        self.regulatory_sentiment = min(1.0, self.regulatory_sentiment + 0.2)

        # Adoption surge (people follow government)
        self.adoption_rate *= 1.1

    def trigger_crash(self, severity: float = 0.5):
        """
        Trigger crypto crash (regulatory crackdown, exchange failure, etc.)

        Args:
            severity: Crash magnitude (0.5 = 50% drop)
        """
        self.price *= (1 - severity)
        self.sentiment = -0.9  # Extreme fear
        self.regulatory_sentiment = max(0, self.regulatory_sentiment - 0.3)

    def trigger_rally(self, magnitude: float = 0.3):
        """
        Trigger crypto rally (ETF approval, institutional adoption, etc.)

        Args:
            magnitude: Rally size (0.3 = 30% pump)
        """
        self.price *= (1 + magnitude)
        self.sentiment = 0.8  # Greed
        self.adoption_rate *= 1.05

    def get_market_cap(self) -> float:
        """Calculate market capitalization"""
        return self.price * self.circulating_supply

    def get_dominance(self, total_market_cap: float) -> float:
        """
        Get crypto dominance (% of total financial market)

        Args:
            total_market_cap: Total market cap including stocks
        """
        crypto_cap = self.get_market_cap()
        if total_market_cap + crypto_cap > 0:
            return crypto_cap / (total_market_cap + crypto_cap)
        return 0

    def get_state(self) -> Dict:
        """Get current crypto market state"""
        return {
            'name': self.name,
            'price': self.price,
            'market_cap': self.get_market_cap(),
            'adoption_rate': self.adoption_rate,
            'holders': self.holders,
            'sentiment': self.sentiment,
            'volatility': self.volatility,
            'government_holdings': self.government_holdings,
            'inflation_hedge_belief': self.inflation_hedge_belief,
            'regulatory_sentiment': self.regulatory_sentiment,
            'drawdown': self.drawdown,
            'days_below_ath': self.days_below_ath,
            'all_time_high': self.all_time_high,
            'circulating_supply': self.circulating_supply
        }
