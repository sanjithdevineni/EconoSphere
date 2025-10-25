"""
Pre-configured economic scenarios for demos
"""


class ScenarioManager:
    """
    Manages pre-configured economic scenarios
    Makes it easy to demo different economic situations
    """

    @staticmethod
    def get_scenario(name):
        """
        Get configuration for a named scenario

        Returns:
            Dictionary with policy settings
        """
        scenarios = {
            'baseline': {
                'name': 'Baseline Economy',
                'description': 'Stable, moderate growth economy',
                'tax_rate': 0.20,
                'interest_rate': 0.05,
                'welfare': 500,
                'govt_spending': 10000,
                'auto_policy': False
            },

            'high_tax': {
                'name': 'High Tax Welfare State',
                'description': 'High taxes, generous welfare',
                'tax_rate': 0.40,
                'interest_rate': 0.03,
                'welfare': 1500,
                'govt_spending': 30000,
                'auto_policy': False
            },

            'low_tax': {
                'name': 'Low Tax Economy',
                'description': 'Minimal government intervention',
                'tax_rate': 0.10,
                'interest_rate': 0.02,
                'welfare': 100,
                'govt_spending': 5000,
                'auto_policy': False
            },

            'recession_2008': {
                'name': '2008 Financial Crisis',
                'description': 'Simulates Great Recession with Fed response',
                'tax_rate': 0.20,
                'interest_rate': 0.001,  # Near-zero rates
                'welfare': 1000,  # Increased unemployment benefits
                'govt_spending': 50000,  # Massive stimulus
                'auto_policy': False,
                'trigger_crisis': 'recession'
            },

            'covid_2020': {
                'name': 'COVID-19 Pandemic Response',
                'description': 'Demand shock with fiscal/monetary response',
                'tax_rate': 0.15,  # Tax cuts
                'interest_rate': 0.001,  # Zero rates
                'welfare': 2000,  # Stimulus checks + unemployment
                'govt_spending': 60000,  # Massive spending
                'auto_policy': False,
                'trigger_crisis': 'recession'
            },

            'inflation_1970s': {
                'name': '1970s Stagflation',
                'description': 'High inflation requiring tight monetary policy',
                'tax_rate': 0.25,
                'interest_rate': 0.10,  # Very high rates
                'welfare': 500,
                'govt_spending': 15000,
                'auto_policy': False,
                'trigger_crisis': 'inflation'
            },

            'taylor_rule': {
                'name': 'Automatic Monetary Policy',
                'description': 'Central bank uses Taylor Rule to auto-adjust rates',
                'tax_rate': 0.20,
                'interest_rate': 0.05,
                'welfare': 500,
                'govt_spending': 10000,
                'auto_policy': True
            },

            'ubi_experiment': {
                'name': 'Universal Basic Income',
                'description': 'Test UBI with high welfare payments',
                'tax_rate': 0.30,
                'interest_rate': 0.03,
                'welfare': 1800,  # Very high UBI
                'govt_spending': 10000,
                'auto_policy': False
            }
        }

        return scenarios.get(name, scenarios['baseline'])

    @staticmethod
    def list_scenarios():
        """Return list of available scenario names"""
        return [
            'baseline',
            'high_tax',
            'low_tax',
            'recession_2008',
            'covid_2020',
            'inflation_1970s',
            'taylor_rule',
            'ubi_experiment'
        ]

    @staticmethod
    def apply_scenario(model, scenario_name):
        """
        Apply a scenario configuration to an economy model

        Args:
            model: EconomyModel instance
            scenario_name: Name of scenario to apply
        """
        scenario = ScenarioManager.get_scenario(scenario_name)

        # Apply policies
        model.set_tax_rate(scenario['tax_rate'])
        model.set_interest_rate(scenario['interest_rate'])
        model.set_welfare_payment(scenario['welfare'])
        model.set_govt_spending(scenario['govt_spending'])
        model.enable_auto_monetary_policy(scenario.get('auto_policy', False))

        # Trigger crisis if specified
        if 'trigger_crisis' in scenario:
            model.trigger_crisis(scenario['trigger_crisis'])

        return scenario
