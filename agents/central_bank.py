"""
Central Bank Agent: Represents monetary policy authority
"""

from mesa import Agent


class CentralBank(Agent):
    """
    Central Bank agent that:
    - Sets interest rates
    - Controls money supply
    - Targets inflation
    - Can implement quantitative easing
    """

    def __init__(self, unique_id, model, interest_rate=0.05, inflation_target=0.02, money_supply=1_000_000):
        super().__init__(model)
        self.unique_id = unique_id
        self.interest_rate = interest_rate
        self.inflation_target = inflation_target
        self.money_supply = money_supply
        self.reserve_ratio = 0.10

        # Policy mode
        self.auto_policy = False  # If True, automatically adjust rates based on inflation

    def set_interest_rate(self, rate):
        """
        Adjust interest rate (policy control)
        Main monetary policy tool
        """
        self.interest_rate = max(0, min(0.20, rate))  # Keep between 0-20%

    def get_borrowing_cost(self):
        """
        Return current borrowing cost for firms and consumers
        Used by firms for investment decisions
        """
        return self.interest_rate

    def quantitative_easing(self, amount):
        """
        Emergency policy: Expand money supply
        "Print money" to inject liquidity into economy
        """
        self.money_supply += amount
        return amount

    def quantitative_tightening(self, amount):
        """
        Contract money supply to fight inflation
        """
        reduction = min(amount, self.money_supply * 0.1)  # Don't reduce more than 10%
        self.money_supply -= reduction
        return reduction

    def taylor_rule(self, current_inflation, current_unemployment, natural_unemployment=0.05):
        """
        Taylor Rule: Automatic interest rate adjustment based on economic conditions

        Formula (simplified):
        target_rate = neutral_rate + 0.5*(inflation - target_inflation) - 0.5*(unemployment - natural_unemployment)

        If auto_policy is enabled, this adjusts rates automatically
        """
        if not self.auto_policy:
            return self.interest_rate

        neutral_rate = 0.02  # Neutral real interest rate

        # Inflation gap
        inflation_gap = current_inflation - self.inflation_target

        # Unemployment gap
        unemployment_gap = current_unemployment - natural_unemployment

        # Calculate target rate
        target_rate = neutral_rate + (0.5 * inflation_gap) - (0.5 * unemployment_gap)

        # Smooth adjustment (don't jump rates too fast)
        adjustment = (target_rate - self.interest_rate) * 0.3  # 30% of gap
        new_rate = self.interest_rate + adjustment

        # Apply bounds
        self.interest_rate = max(0, min(0.20, new_rate))

        return self.interest_rate

    def enable_auto_policy(self, enabled=True):
        """Enable/disable automatic policy (Taylor Rule)"""
        self.auto_policy = enabled

    def crisis_response(self, crisis_type='recession'):
        """
        Pre-configured crisis response policies
        """
        if crisis_type == 'recession':
            # Slash rates, expand money supply
            self.interest_rate = 0.02  # accommodative but not zero
            self.quantitative_easing(self.money_supply * 0.1)  # 10% expansion

        elif crisis_type == 'inflation':
            # Raise rates aggressively
            self.interest_rate = 0.08  # 8%
            self.quantitative_tightening(self.money_supply * 0.05)  # 5% contraction

    def get_monetary_summary(self):
        """Return summary of monetary policy"""
        return {
            'interest_rate': self.interest_rate,
            'money_supply': self.money_supply,
            'inflation_target': self.inflation_target,
            'auto_policy': self.auto_policy,
            'reserve_ratio': self.reserve_ratio
        }

    def step(self):
        """
        Central bank decisions each time step
        If auto_policy enabled, will adjust rates based on economic conditions
        """
        pass  # Policy adjustments happen via external calls or auto_policy
