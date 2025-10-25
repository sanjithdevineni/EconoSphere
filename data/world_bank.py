"""
World Bank API integration for real economic data
"""

import wbgapi as wb
import pandas as pd


class WorldBankAPI:
    """
    Fetch real economic indicators from World Bank API
    Use these to calibrate simulation parameters
    """

    def __init__(self):
        self.indicators = {
            'gdp': 'NY.GDP.MKTP.CD',  # GDP (current US$)
            'unemployment': 'SL.UEM.TOTL.ZS',  # Unemployment rate
            'inflation': 'FP.CPI.TOTL.ZG',  # Inflation, consumer prices
            'gini': 'SI.POV.GINI',  # Gini index
            'tax_revenue': 'GC.TAX.TOTL.GD.ZS',  # Tax revenue (% of GDP)
            'govt_debt': 'GC.DOD.TOTL.GD.ZS',  # Government debt (% of GDP)
        }

    def fetch_indicator(self, indicator, country='USA', year=2022):
        """
        Fetch a specific indicator for a country and year

        Args:
            indicator: Key from self.indicators
            country: ISO country code (default: USA)
            year: Year to fetch (default: 2022)

        Returns:
            Float value or None if not available
        """
        try:
            indicator_code = self.indicators.get(indicator)
            if not indicator_code:
                print(f"Unknown indicator: {indicator}")
                return None

            # Fetch data
            data = wb.data.DataFrame(
                indicator_code,
                country,
                time=year,
                numericTimeKeys=True
            )

            if data.empty:
                print(f"No data available for {indicator} in {country} for {year}")
                return None

            value = data.iloc[0, 0]
            return value

        except Exception as e:
            print(f"Error fetching {indicator}: {e}")
            return None

    def get_initial_conditions(self, country='USA', year=2022):
        """
        Fetch a set of economic indicators to use as initial simulation conditions

        Returns:
            Dictionary with economic indicators
        """
        print(f"Fetching economic data for {country} ({year})...")

        conditions = {}
        for indicator in self.indicators.keys():
            value = self.fetch_indicator(indicator, country, year)
            if value is not None:
                conditions[indicator] = value
                print(f"  {indicator}: {value}")

        return conditions

    def calibrate_simulation(self, country='USA', year=2022):
        """
        Get suggested simulation parameters based on real data

        Returns:
            Dictionary with config parameters
        """
        data = self.get_initial_conditions(country, year)

        # Map World Bank data to simulation parameters
        params = {}

        if 'unemployment' in data:
            # Unemployment rate should match reality
            params['initial_unemployment_target'] = data['unemployment'] / 100

        if 'inflation' in data:
            # Set inflation target based on recent inflation
            params['inflation_target'] = max(0.02, min(0.05, data['inflation'] / 100))

        if 'tax_revenue' in data:
            # Estimate tax rate (this is tax revenue as % of GDP)
            # Rough approximation
            params['tax_rate'] = data['tax_revenue'] / 100

        if 'gini' in data:
            # Use Gini to adjust wealth distribution
            params['wealth_inequality'] = data['gini'] / 100

        return params

    def fetch_time_series(self, indicator, country='USA', start_year=2000, end_year=2023):
        """
        Fetch time series data for an indicator

        Args:
            indicator: Key from self.indicators
            country: ISO country code
            start_year: Start year
            end_year: End year

        Returns:
            Pandas DataFrame with time series
        """
        try:
            indicator_code = self.indicators.get(indicator)
            if not indicator_code:
                return None

            data = wb.data.DataFrame(
                indicator_code,
                country,
                time=range(start_year, end_year + 1),
                numericTimeKeys=True
            )

            return data

        except Exception as e:
            print(f"Error fetching time series: {e}")
            return None


# Example usage
if __name__ == '__main__':
    api = WorldBankAPI()

    # Fetch current US economic conditions
    print("=== US Economic Indicators ===")
    conditions = api.get_initial_conditions('USA', 2022)

    print("\n=== Suggested Simulation Parameters ===")
    params = api.calibrate_simulation('USA', 2022)
    for key, value in params.items():
        print(f"{key}: {value}")
