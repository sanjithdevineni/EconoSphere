"""
Financial Markets Economy Model - Extends base economy with stocks and crypto

THIS IS THE HACKATHON DIFFERENTIATOR!
First economic simulator with integrated stock and cryptocurrency markets
that respond realistically to macro policy.
"""
import logging
from simulation.economy_model import EconomyModel
from agents.stock_market import StockMarket
from agents.crypto_market import CryptoMarket
import config

LOGGER = logging.getLogger(__name__)


class FinancialMarketsModel(EconomyModel):
    """
    Extended economy model with financial markets

    New Features:
    - Stock market with realistic pricing
    - Cryptocurrency market with macro-policy sensitivity
    - Consumer investment behavior
    - Government crypto reserve
    - AI narratives for market events
    """

    def __init__(
        self,
        num_consumers=config.NUM_CONSUMERS,
        num_firms=config.NUM_FIRMS,
        initial_vat_rate=config.INITIAL_VAT_RATE,
        initial_payroll_rate=config.INITIAL_PAYROLL_RATE,
        initial_corporate_rate=config.INITIAL_CORPORATE_RATE,
        initial_interest_rate=config.INITIAL_INTEREST_RATE,
        initial_welfare=config.INITIAL_WELFARE_PAYMENT,
        initial_govt_spending=config.INITIAL_GOVT_SPENDING,
        enable_stock_market=True,
        enable_crypto_market=True,
        enable_govt_crypto_reserve=False,
        seed=None
    ):
        """
        Initialize financial markets economy

        Args:
            (inherits all base economy args)
            enable_stock_market: Enable stock market
            enable_crypto_market: Enable crypto market
            enable_govt_crypto_reserve: Enable government strategic crypto reserve
        """
        # Initialize base economy first
        super().__init__(
            num_consumers=num_consumers,
            num_firms=num_firms,
            initial_vat_rate=initial_vat_rate,
            initial_payroll_rate=initial_payroll_rate,
            initial_corporate_rate=initial_corporate_rate,
            initial_interest_rate=initial_interest_rate,
            initial_welfare=initial_welfare,
            initial_govt_spending=initial_govt_spending,
            seed=seed
        )

        # === FINANCIAL MARKETS ===
        self.stock_market = None
        self.crypto_market = None

        if enable_stock_market:
            LOGGER.info("Initializing stock market...")
            self.stock_market = StockMarket(self.firms)

        if enable_crypto_market:
            LOGGER.info("Initializing crypto market...")
            self.crypto_market = CryptoMarket(name="EconoCoin")

        # Enable government crypto reserve if requested
        if enable_govt_crypto_reserve and self.crypto_market:
            annual_budget = initial_govt_spending * 0.1  # 10% of govt spending
            self.government.enable_crypto_reserve(annual_budget)
            LOGGER.info(f"Government crypto reserve enabled with annual budget: ${annual_budget:,.0f}")

        # Track market metrics
        self.market_history = []

    def step(self):
        """
        Execute one time step with financial markets

        Extended order of operations:
        1-9. (Base economy operations from parent class)
        10. Update stock market prices
        11. Update crypto market prices
        12. Consumers make investment decisions
        13. Government executes crypto reserve policy
        14. Calculate market metrics
        15. Generate market narratives
        """
        # Execute base economy step
        super().step()

        # === FINANCIAL MARKETS UPDATE ===

        # Get current economic state
        economic_state = {
            'inflation': self.metrics.latest_metrics.get('inflation_rate', 0.02),
            'interest_rate': self.central_bank.interest_rate,
            'unemployment': self.metrics.latest_metrics.get('unemployment_rate', 0.05),
            'gdp': self.metrics.latest_metrics.get('gdp', 0),
            'stock_return': 0,
        }

        # 10. Update stock market
        if self.stock_market:
            self.stock_market.update_prices(
                interest_rate=economic_state['interest_rate'],
                inflation=economic_state['inflation'],
                unemployment=economic_state['unemployment']
            )
            economic_state['stock_return'] = self.stock_market.get_market_return()

        # 11. Update crypto market
        if self.crypto_market:
            self.crypto_market.update_price(economic_state)

        # 12. Consumers make investment decisions
        self._process_consumer_investments()

        # 13. Government crypto reserve policy
        if self.government.crypto_reserve_enabled and self.crypto_market:
            self.government.execute_reserve_policy(
                self.crypto_market,
                economic_state
            )

        # 14. Calculate and store market metrics
        market_metrics = self._calculate_market_metrics()
        self.market_history.append(market_metrics)

        # Keep only recent history (last 200 steps)
        if len(self.market_history) > 200:
            self.market_history.pop(0)

        # Add market metrics to main metrics
        self.metrics.latest_metrics.update(market_metrics)

        # 15. Generate market narratives (if AI narrator enabled)
        self._generate_market_narratives(market_metrics)

        self.current_step += 1

    def _process_consumer_investments(self):
        """
        Process consumer investment decisions

        Each consumer:
        1. Updates their portfolio values
        2. Decides how much to invest
        3. Buys stocks/crypto
        4. Sells if cash is low
        """
        for consumer in self.consumers:
            # Update portfolio values
            consumer.update_portfolio_values(self.stock_market, self.crypto_market)

            # Make investment decisions (buy stocks/crypto)
            consumer.make_investment_decisions(self.stock_market, self.crypto_market)

            # Sell investments if running out of cash
            consumer.sell_investments_if_needed(self.stock_market, self.crypto_market)

    def _calculate_market_metrics(self):
        """
        Calculate financial market metrics

        Returns:
            Dict with stock and crypto metrics
        """
        metrics = {}

        # Stock market metrics
        if self.stock_market:
            stock_state = self.stock_market.get_state()
            metrics['stock_index'] = stock_state['index']
            metrics['stock_market_cap'] = stock_state['market_cap']
            metrics['stock_sentiment'] = stock_state['sentiment']
            metrics['stock_fear_greed'] = stock_state['fear_greed']
            metrics['stock_daily_return'] = stock_state['daily_return']

        # Crypto market metrics
        if self.crypto_market:
            crypto_state = self.crypto_market.get_state()
            metrics['crypto_price'] = crypto_state['price']
            metrics['crypto_market_cap'] = crypto_state['market_cap']
            metrics['crypto_adoption_rate'] = crypto_state['adoption_rate']
            metrics['crypto_sentiment'] = crypto_state['sentiment']
            metrics['crypto_government_holdings'] = crypto_state['government_holdings']
            metrics['crypto_inflation_hedge_belief'] = crypto_state['inflation_hedge_belief']
            metrics['crypto_regulatory_sentiment'] = crypto_state['regulatory_sentiment']
            metrics['crypto_drawdown'] = crypto_state['drawdown']
            metrics['crypto_days_below_ath'] = crypto_state['days_below_ath']

        # Consumer portfolio metrics
        total_consumer_stock_value = 0
        total_consumer_crypto_value = 0
        consumers_with_stocks = 0
        consumers_with_crypto = 0

        for consumer in self.consumers:
            total_consumer_stock_value += consumer.stock_portfolio_value
            total_consumer_crypto_value += consumer.crypto_value

            if consumer.stock_portfolio_value > 0:
                consumers_with_stocks += 1
            if consumer.crypto_holdings > 0:
                consumers_with_crypto += 1

        metrics['consumer_stock_holdings'] = total_consumer_stock_value
        metrics['consumer_crypto_holdings'] = total_consumer_crypto_value
        metrics['consumers_invested_stocks'] = consumers_with_stocks
        metrics['consumers_invested_crypto'] = consumers_with_crypto

        # Government crypto reserve
        if self.government.crypto_reserve > 0:
            self.government.update_crypto_reserve_value(self.crypto_market)
            metrics['govt_crypto_reserve'] = self.government.crypto_reserve
            metrics['govt_crypto_reserve_value'] = self.government.crypto_reserve_value

        return metrics

    def _generate_market_narratives(self, market_metrics):
        """
        Generate AI narratives for significant market events

        Events that trigger narratives:
        - Crypto crashes/rallies (>20% move)
        - Stock market crashes/rallies (>10% move)
        - Government crypto reserve announcements
        - Crypto adoption surges

        Args:
            market_metrics: Dict with current market metrics
        """
        if not self.narrator or not self.narrator.enabled:
            return

        narrative_event = None

        # Crypto crash/rally
        if self.crypto_market and len(self.crypto_market.price_history) > 1:
            prev_price = self.crypto_market.price_history[-2]
            curr_price = self.crypto_market.price
            price_change = (curr_price - prev_price) / prev_price

            if price_change > 0.20:
                narrative_event = {
                    'type': 'crypto_rally',
                    'magnitude': price_change,
                    'price': curr_price,
                }
            elif price_change < -0.20:
                narrative_event = {
                    'type': 'crypto_crash',
                    'magnitude': price_change,
                    'price': curr_price,
                }

        # Stock market crash/rally
        if self.stock_market and not narrative_event:
            daily_return = market_metrics.get('stock_daily_return', 0)
            if daily_return > 0.10:
                narrative_event = {
                    'type': 'stock_rally',
                    'magnitude': daily_return,
                    'index': market_metrics.get('stock_index', 0),
                }
            elif daily_return < -0.10:
                narrative_event = {
                    'type': 'stock_crash',
                    'magnitude': daily_return,
                    'index': market_metrics.get('stock_index', 0),
                }

        # Government crypto reserve announcement
        if self.government.crypto_reserve_enabled and not narrative_event:
            if market_metrics.get('govt_crypto_reserve', 0) > 0:
                # Check if this is a new purchase (compare to previous step)
                if len(self.market_history) > 1:
                    prev_reserve = self.market_history[-1].get('govt_crypto_reserve', 0)
                    curr_reserve = market_metrics.get('govt_crypto_reserve', 0)
                    if curr_reserve > prev_reserve * 1.1:  # 10% increase
                        narrative_event = {
                            'type': 'govt_crypto_purchase',
                            'reserve': curr_reserve,
                            'value': market_metrics.get('govt_crypto_reserve_value', 0),
                        }

        # Generate narrative if event detected
        if narrative_event and self.narrative_cooldown <= 0:
            LOGGER.info(f"Market event detected: {narrative_event['type']}")
            # Set cooldown to avoid spam
            self.narrative_cooldown = 5
            self.should_generate_narrative = True

    # === SCENARIO METHODS ===

    def trigger_stock_crash(self, severity=0.3):
        """
        Trigger stock market crash

        Args:
            severity: Crash magnitude (0.3 = 30% drop)
        """
        if self.stock_market:
            self.stock_market.trigger_crash(severity)
            LOGGER.info(f"Stock market crash triggered: {severity*100:.0f}% drop")

    def trigger_crypto_crash(self, severity=0.5):
        """
        Trigger crypto crash (regulatory crackdown, exchange failure, etc.)

        Args:
            severity: Crash magnitude (0.5 = 50% drop)
        """
        if self.crypto_market:
            self.crypto_market.trigger_crash(severity)
            LOGGER.info(f"Crypto crash triggered: {severity*100:.0f}% drop")

    def trigger_crypto_rally(self, magnitude=0.3):
        """
        Trigger crypto rally (ETF approval, institutional adoption)

        Args:
            magnitude: Rally size (0.3 = 30% pump)
        """
        if self.crypto_market:
            self.crypto_market.trigger_rally(magnitude)
            LOGGER.info(f"Crypto rally triggered: {magnitude*100:.0f}% pump")

    def enable_government_crypto_reserve(self, annual_budget):
        """
        Enable government strategic crypto reserve

        THIS IS THE BIG NARRATIVE MOMENT!

        Args:
            annual_budget: Annual budget for crypto purchases
        """
        if self.crypto_market:
            self.government.enable_crypto_reserve(annual_budget)
            LOGGER.info(f"Government crypto reserve enabled: ${annual_budget:,.0f}/year")

            # Immediate one-time purchase to kickstart reserve
            initial_purchase = annual_budget * 0.5  # 50% of annual budget
            if initial_purchase > 0:
                self.government.buy_crypto_for_reserve(self.crypto_market, initial_purchase)
                LOGGER.info(f"Initial reserve purchase: ${initial_purchase:,.0f}")

    def disable_government_crypto_reserve(self):
        """Disable government crypto reserve program"""
        self.government.disable_crypto_reserve()
        LOGGER.info("Government crypto reserve disabled")

    def get_market_state(self):
        """
        Get comprehensive market state for dashboard

        Returns:
            Dict with all market data
        """
        state = {
            'current_step': self.current_step,
            'market_history': self.market_history,
        }

        if self.stock_market:
            state['stock_market'] = self.stock_market.get_state()

        if self.crypto_market:
            state['crypto_market'] = self.crypto_market.get_state()

        if self.government:
            state['government'] = self.government.get_fiscal_summary()

        return state
