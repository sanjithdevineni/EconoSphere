"""
Time-series validation page - Compare simulation trajectories to real historical data
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from simulation.economy_model import EconomyModel
from data.calibration.world_bank_client import IndicatorRequest, build_country_macro_dataset
from data.calibration.parameter_fit import calibrate_parameters
import config

# Register this page
dash.register_page(__name__, path='/validation', name='Validation', title='Model Validation')


VALIDATION_COUNTRIES = [
    {'label': 'United States', 'value': 'USA'},
    {'label': 'United Kingdom', 'value': 'GBR'},
    {'label': 'Germany', 'value': 'DEU'},
    {'label': 'France', 'value': 'FRA'},
    {'label': 'Japan', 'value': 'JPN'},
    {'label': 'Canada', 'value': 'CAN'},
    {'label': 'Australia', 'value': 'AUS'},
]

INDICATORS = [
    IndicatorRequest("gdp", "NY.GDP.MKTP.CD"),
    IndicatorRequest("consumption_share", "NE.CON.TOTL.ZS"),
    IndicatorRequest("unemployment", "SL.UEM.TOTL.ZS"),
    IndicatorRequest("capital_formation", "NE.GDI.TOTL.ZS"),
    IndicatorRequest("population", "SP.POP.TOTL"),
    IndicatorRequest("inflation", "FP.CPI.TOTL.ZG"),  # CPI inflation
]


def layout(**kwargs):
    """Create the validation page layout"""

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Model Validation", className="text-center mb-3 mt-3"),
                html.P(
                    "Compare simulation trajectories against real historical economic data",
                    className="text-center text-muted mb-4"
                )
            ])
        ]),

        # Configuration Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Validation Configuration")),
                    dbc.CardBody([
                        # Country Selection
                        html.Label("Select Country", className="fw-bold"),
                        dcc.Dropdown(
                            id='validation-country',
                            options=VALIDATION_COUNTRIES,
                            value='USA',
                            clearable=False,
                            className="mb-3"
                        ),

                        # Year Range
                        html.Label("Start Year", className="fw-bold"),
                        dcc.Dropdown(
                            id='validation-start-year',
                            options=[{'label': str(y), 'value': y} for y in range(2000, 2024)],
                            value=2015,
                            clearable=False,
                            className="mb-3"
                        ),

                        html.Label("End Year", className="fw-bold"),
                        dcc.Dropdown(
                            id='validation-end-year',
                            options=[{'label': str(y), 'value': y} for y in range(2000, 2024)],
                            value=2023,
                            clearable=False,
                            className="mb-3"
                        ),

                        # Metrics Selection
                        html.Label("Metrics to Validate", className="fw-bold"),
                        dcc.Checklist(
                            id='validation-metrics',
                            options=[
                                {'label': ' GDP Growth', 'value': 'gdp'},
                                {'label': ' Unemployment Rate', 'value': 'unemployment'},
                                {'label': ' Inflation Rate', 'value': 'inflation'},
                            ],
                            value=['gdp', 'unemployment', 'inflation'],
                            className="mb-3"
                        ),

                        # Run Button
                        dbc.Button(
                            "Run Validation",
                            id="run-validation-btn",
                            color="primary",
                            className="w-100 mt-3",
                            size="lg"
                        ),

                        # Status
                        html.Div(id='validation-status', className="mt-3")
                    ])
                ])
            ], width=3),

            # Results Panel
            dbc.Col([
                # Metrics Summary Card
                dbc.Card([
                    dbc.CardHeader(html.H4("Validation Metrics")),
                    dbc.CardBody([
                        html.Div(id='validation-metrics-summary')
                    ])
                ], className="mb-3"),

                # Charts
                dbc.Card([
                    dbc.CardHeader(html.H4("Comparison Charts")),
                    dbc.CardBody([
                        dcc.Graph(id='validation-gdp-chart'),
                        dcc.Graph(id='validation-unemployment-chart'),
                        dcc.Graph(id='validation-inflation-chart'),
                    ])
                ])
            ], width=9)
        ]),

        # Store for validation results
        dcc.Store(id='validation-results', data=None)

    ], fluid=True)


@callback(
    Output('validation-results', 'data'),
    Output('validation-status', 'children'),
    Input('run-validation-btn', 'n_clicks'),
    State('validation-country', 'value'),
    State('validation-start-year', 'value'),
    State('validation-end-year', 'value'),
    State('validation-metrics', 'value'),
    prevent_initial_call=True
)
def run_validation(n_clicks, country, start_year, end_year, selected_metrics):
    """Run validation simulation and fetch historical data"""
    if n_clicks is None:
        return None, ""

    try:
        status = dbc.Alert("Running validation... This may take a moment.", color="info")

        # Step 1: Fetch historical data
        historical_data = build_country_macro_dataset(
            country.lower(),
            INDICATORS,
            start_year,
            end_year
        )

        # Step 2: Calibrate parameters for the start year
        country_key = country.upper()

        # Use the full calibration pipeline to get real-world parameters
        calibration_result = calibrate_parameters(
            historical_data,
            country_key,
            start_year,
            baseline_parameters=("mpc", "tfp_a", "gamma", "depreciation")
        )

        # Extract calibrated parameters
        calib_params = calibration_result.parameters

        # Step 3: Scale initial conditions to match real-world
        # Use GDP per capita to scale consumer wealth
        gdp_per_capita = calib_params.get('gdp_per_capita', 57000)
        unemployment_rate = calib_params.get('unemployment_rate', 0.05)

        # Scale wealth: Each consumer represents portion of real economy
        # GDP per capita ~= average wealth per consumer (simplified)
        scaled_wealth_mean = gdp_per_capita * 0.1  # Scale down for simulation
        scaled_wealth_std = scaled_wealth_mean * 0.4  # 40% standard deviation

        # Temporarily set config values for calibrated simulation
        import config as sim_config
        original_config = {
            'mpc': sim_config.CONSUMER_PROPENSITY_TO_CONSUME,
            'tfp': sim_config.FIRM_PRODUCTIVITY,
            'gamma': sim_config.FIRM_GAMMA,
            'depreciation': sim_config.FIRM_DEPRECIATION_RATE,
            'wealth_mean': sim_config.INITIAL_CONSUMER_WEALTH_MEAN,
            'wealth_std': sim_config.INITIAL_CONSUMER_WEALTH_STD,
        }

        # Apply calibrated parameters to config
        sim_config.CONSUMER_PROPENSITY_TO_CONSUME = calib_params.get('mpc', 0.68)
        sim_config.FIRM_PRODUCTIVITY = calib_params.get('tfp_a', 2.0)
        sim_config.FIRM_GAMMA = calib_params.get('gamma', 0.7)
        sim_config.FIRM_DEPRECIATION_RATE = calib_params.get('depreciation', 0.05)
        sim_config.INITIAL_CONSUMER_WEALTH_MEAN = scaled_wealth_mean
        sim_config.INITIAL_CONSUMER_WEALTH_STD = scaled_wealth_std

        # Step 4: Run simulation for the time period
        num_years = end_year - start_year + 1
        num_steps = num_years * 4  # Quarterly steps

        simulation = EconomyModel()

        # Run simulation
        sim_gdp = []
        sim_unemployment = []
        sim_inflation = []

        for step in range(num_steps):
            simulation.step()
            current = simulation.get_current_state()
            sim_gdp.append(current['gdp'])
            sim_unemployment.append(current['unemployment'])
            sim_inflation.append(current['inflation'])

        # Step 4: Process historical data for comparison
        # Calculate GDP growth rates
        hist_years = []
        hist_gdp_growth = []
        hist_unemployment = []
        hist_inflation = []

        for year in range(start_year, end_year + 1):
            try:
                if (country_key, year) in historical_data.index:
                    row = historical_data.loc[(country_key, year)]
                    hist_years.append(year)

                    # GDP growth (calculate if we have previous year)
                    if year > start_year and (country_key, year-1) in historical_data.index:
                        prev_gdp = historical_data.loc[(country_key, year-1), 'gdp']
                        curr_gdp = row['gdp']
                        gdp_growth = ((curr_gdp - prev_gdp) / prev_gdp) * 100
                        hist_gdp_growth.append(gdp_growth)
                    else:
                        hist_gdp_growth.append(0)

                    # Unemployment
                    hist_unemployment.append(row.get('unemployment', np.nan))

                    # Inflation
                    hist_inflation.append(row.get('inflation', np.nan))
            except:
                continue

        # Step 5: Calculate simulated growth rates
        sim_gdp_growth = []
        for i in range(len(sim_gdp)):
            if i > 0:
                growth = ((sim_gdp[i] - sim_gdp[i-1]) / sim_gdp[i-1]) * 100
                sim_gdp_growth.append(growth)
            else:
                sim_gdp_growth.append(0)

        # Step 6: Calculate validation metrics
        # Align data for comparison (annual averages)
        sim_steps_per_year = 4
        sim_gdp_annual_growth = [np.mean(sim_gdp_growth[i*sim_steps_per_year:(i+1)*sim_steps_per_year])
                                   for i in range(num_years)]
        sim_unemployment_annual = [np.mean(sim_unemployment[i*sim_steps_per_year:(i+1)*sim_steps_per_year])
                                    for i in range(num_years)]
        sim_inflation_annual = [np.mean(sim_inflation[i*sim_steps_per_year:(i+1)*sim_steps_per_year])
                                 for i in range(num_years)]

        # Calculate metrics (RMSE, MAE, Correlation)
        def calculate_metrics(sim_data, hist_data):
            """Calculate validation metrics between simulated and historical data"""
            # Align lengths
            min_len = min(len(sim_data), len(hist_data))
            sim = np.array(sim_data[:min_len])
            hist = np.array(hist_data[:min_len])

            # Remove NaN values
            mask = ~np.isnan(hist)
            sim = sim[mask]
            hist = hist[mask]

            if len(sim) == 0:
                return {'rmse': np.nan, 'mae': np.nan, 'correlation': np.nan}

            rmse = np.sqrt(np.mean((sim - hist) ** 2))
            mae = np.mean(np.abs(sim - hist))
            correlation = np.corrcoef(sim, hist)[0, 1] if len(sim) > 1 else np.nan

            return {'rmse': rmse, 'mae': mae, 'correlation': correlation}

        gdp_metrics = calculate_metrics(sim_gdp_annual_growth, hist_gdp_growth)
        unemployment_metrics = calculate_metrics(sim_unemployment_annual, hist_unemployment)
        inflation_metrics = calculate_metrics(sim_inflation_annual, hist_inflation)

        # Restore original config values
        sim_config.CONSUMER_PROPENSITY_TO_CONSUME = original_config['mpc']
        sim_config.FIRM_PRODUCTIVITY = original_config['tfp']
        sim_config.FIRM_GAMMA = original_config['gamma']
        sim_config.FIRM_DEPRECIATION_RATE = original_config['depreciation']
        sim_config.INITIAL_CONSUMER_WEALTH_MEAN = original_config['wealth_mean']
        sim_config.INITIAL_CONSUMER_WEALTH_STD = original_config['wealth_std']

        # Package results
        results = {
            'years': list(range(start_year, end_year + 1)),
            'hist_gdp_growth': hist_gdp_growth,
            'hist_unemployment': hist_unemployment,
            'hist_inflation': hist_inflation,
            'sim_gdp_growth': sim_gdp_annual_growth,
            'sim_unemployment': sim_unemployment_annual,
            'sim_inflation': sim_inflation_annual,
            'gdp_metrics': gdp_metrics,
            'unemployment_metrics': unemployment_metrics,
            'inflation_metrics': inflation_metrics,
            'calibration_info': {
                'mpc': calib_params.get('mpc', 0.68),
                'tfp': calib_params.get('tfp_a', 2.0),
                'gamma': calib_params.get('gamma', 0.7),
                'depreciation': calib_params.get('depreciation', 0.05),
                'gdp_per_capita': gdp_per_capita,
                'unemployment_rate': unemployment_rate,
            }
        }

        success_status = dbc.Alert([
            html.Strong("Validation complete! "),
            html.Span(f"Analyzed {num_years} years of data for {country}. "),
            html.Br(),
            html.Small([
                f"Calibrated parameters - MPC: {calib_params.get('mpc', 0.68):.3f}, ",
                f"TFP: {calib_params.get('tfp_a', 2.0):.3f}, ",
                f"Initial Unemployment: {unemployment_rate:.1%}"
            ])
        ], color="success")

        return results, success_status

    except Exception as e:
        # Restore config even on error
        try:
            sim_config.CONSUMER_PROPENSITY_TO_CONSUME = original_config['mpc']
            sim_config.FIRM_PRODUCTIVITY = original_config['tfp']
            sim_config.FIRM_GAMMA = original_config['gamma']
            sim_config.FIRM_DEPRECIATION_RATE = original_config['depreciation']
            sim_config.INITIAL_CONSUMER_WEALTH_MEAN = original_config['wealth_mean']
            sim_config.INITIAL_CONSUMER_WEALTH_STD = original_config['wealth_std']
        except:
            pass

        error_status = dbc.Alert(
            f"Error during validation: {str(e)}",
            color="danger"
        )
        return None, error_status


@callback(
    Output('validation-metrics-summary', 'children'),
    Input('validation-results', 'data'),
    prevent_initial_call=True
)
def update_metrics_summary(results):
    """Update the validation metrics summary"""
    if results is None:
        return html.P("Run validation to see metrics", className="text-muted")

    gdp_metrics = results['gdp_metrics']
    unemp_metrics = results['unemployment_metrics']
    infl_metrics = results['inflation_metrics']
    calib_info = results.get('calibration_info', {})

    def metric_card(title, metrics, color):
        """Create a metric card"""
        return dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(title, className="card-title"),
                    html.Hr(),
                    html.P([
                        html.Strong("RMSE: "),
                        f"{metrics['rmse']:.3f}" if not np.isnan(metrics['rmse']) else "N/A"
                    ]),
                    html.P([
                        html.Strong("MAE: "),
                        f"{metrics['mae']:.3f}" if not np.isnan(metrics['mae']) else "N/A"
                    ]),
                    html.P([
                        html.Strong("Correlation: "),
                        f"{metrics['correlation']:.3f}" if not np.isnan(metrics['correlation']) else "N/A"
                    ]),
                ], className=f"bg-{color}-subtle")
            ])
        ], width=4)

    return html.Div([
        # Calibration Info Banner
        dbc.Alert([
            html.H6("📊 Calibrated Parameters Used:", className="alert-heading"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.Small([
                        html.Strong("MPC: "), f"{calib_info.get('mpc', 'N/A'):.3f}", html.Br(),
                        html.Strong("TFP: "), f"{calib_info.get('tfp', 'N/A'):.3f}", html.Br(),
                        html.Strong("Gamma: "), f"{calib_info.get('gamma', 'N/A'):.3f}",
                    ])
                ], width=4),
                dbc.Col([
                    html.Small([
                        html.Strong("Depreciation: "), f"{calib_info.get('depreciation', 'N/A'):.3f}", html.Br(),
                        html.Strong("Initial Unemployment: "), f"{calib_info.get('unemployment_rate', 0):.1%}", html.Br(),
                        html.Strong("GDP per Capita: "), f"${calib_info.get('gdp_per_capita', 0):,.0f}",
                    ])
                ], width=4),
                dbc.Col([
                    html.Small([
                        html.Strong("Agents: "), "100 consumers, 10 firms", html.Br(),
                        html.Strong("Scale: "), "Representative agent model", html.Br(),
                        html.Em("Parameters from World Bank data")
                    ])
                ], width=4),
            ])
        ], color="info", className="mb-3"),

        # Validation Metrics
        dbc.Row([
            metric_card("GDP Growth", gdp_metrics, "primary"),
            metric_card("Unemployment", unemp_metrics, "warning"),
            metric_card("Inflation", infl_metrics, "info"),
        ])
    ])


@callback(
    Output('validation-gdp-chart', 'figure'),
    Output('validation-unemployment-chart', 'figure'),
    Output('validation-inflation-chart', 'figure'),
    Input('validation-results', 'data'),
    prevent_initial_call=True
)
def update_validation_charts(results):
    """Update comparison charts"""
    if results is None:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Run validation to see comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return empty_fig, empty_fig, empty_fig

    years = results['years']

    # GDP Growth Chart
    gdp_fig = go.Figure()
    gdp_fig.add_trace(go.Scatter(
        x=years, y=results['hist_gdp_growth'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    gdp_fig.add_trace(go.Scatter(
        x=years, y=results['sim_gdp_growth'],
        mode='lines+markers',
        name='Simulated',
        line=dict(color='red', dash='dash', width=2),
        marker=dict(size=8)
    ))
    gdp_fig.update_layout(
        title='GDP Growth Rate Comparison (%)',
        xaxis_title='Year',
        yaxis_title='GDP Growth (%)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    # Unemployment Chart
    unemp_fig = go.Figure()
    unemp_fig.add_trace(go.Scatter(
        x=years, y=results['hist_unemployment'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    unemp_fig.add_trace(go.Scatter(
        x=years, y=results['sim_unemployment'],
        mode='lines+markers',
        name='Simulated',
        line=dict(color='red', dash='dash', width=2),
        marker=dict(size=8)
    ))
    unemp_fig.update_layout(
        title='Unemployment Rate Comparison (%)',
        xaxis_title='Year',
        yaxis_title='Unemployment Rate (%)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    # Inflation Chart
    infl_fig = go.Figure()
    infl_fig.add_trace(go.Scatter(
        x=years, y=results['hist_inflation'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    infl_fig.add_trace(go.Scatter(
        x=years, y=results['sim_inflation'],
        mode='lines+markers',
        name='Simulated',
        line=dict(color='red', dash='dash', width=2),
        marker=dict(size=8)
    ))
    infl_fig.update_layout(
        title='Inflation Rate Comparison (%)',
        xaxis_title='Year',
        yaxis_title='Inflation Rate (%)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    return gdp_fig, unemp_fig, infl_fig
