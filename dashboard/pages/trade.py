"""
International Trade page - Multi-country trade simulation with tariffs and exchange rates
"""

import logging
import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

from simulation.trade_economy_model import TradeEconomyModel
import config

LOGGER = logging.getLogger(__name__)

# Register this page
dash.register_page(__name__, path='/trade', name='International Trade', title='Trade Simulation')

# Global simulation instance
trade_simulation = None


def layout(**kwargs):
    """Create the international trade page layout"""

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("🌍 International Trade Simulation", className="text-center mb-3 mt-3"),
                html.P(
                    "Multi-country trade with tariffs, retaliation, and exchange rate dynamics",
                    className="text-center text-muted mb-2"
                ),
                dbc.Alert([
                    html.Strong("Tier 3 Features: "),
                    "Multi-country model • Tariff retaliation • Exchange rates • Trade wars • Free trade agreements"
                ], color="info", className="text-center")
            ])
        ]),

        # Main Controls and Charts
        dbc.Row([
            # Left Column - Controls
            dbc.Col([
                # Domestic Policy Controls
                dbc.Card([
                    dbc.CardHeader(html.H4("Domestic Policy Controls")),
                    dbc.CardBody([
                        # Tariff Rate
                        html.Label("Import Tariff Rate (%)", className="fw-bold"),
                        dcc.Slider(
                            id='tariff-rate-slider',
                            min=0,
                            max=100,
                            step=5,
                            value=0,
                            marks={i: f'{i}%' for i in range(0, 101, 25)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Small("Tariff on all imported goods", className="text-muted"),
                        html.Br(), html.Br(),

                        # Interest Rate
                        html.Label("Interest Rate (%)", className="fw-bold mt-3"),
                        dcc.Slider(
                            id='trade-interest-rate-slider',
                            min=0,
                            max=10,
                            step=0.25,
                            value=config.INITIAL_INTEREST_RATE * 100,
                            marks={i: f'{i}%' for i in range(0, 11, 2)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Small("Affects exchange rates", className="text-muted"),
                        html.Br(), html.Br(),

                        # Government Spending
                        html.Label("Government Spending ($)", className="fw-bold mt-3"),
                        dcc.Slider(
                            id='trade-govt-spending-slider',
                            min=0,
                            max=50000,
                            step=1000,
                            value=config.INITIAL_GOVT_SPENDING,
                            marks={i: f'${i//1000}k' for i in range(0, 50001, 10000)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),

                        html.Hr(),

                        # Simulation Controls
                        html.Div([
                            dbc.Button("Start Simulation", id="trade-start-btn", color="success", className="me-2 mb-2"),
                            dbc.Button("Pause", id="trade-pause-btn", color="warning", className="me-2 mb-2"),
                            dbc.Button("Reset", id="trade-reset-btn", color="danger", className="mb-2"),
                        ], className="mt-3"),

                        html.Hr(),

                        # Trade Events
                        html.Label("Trade Policy Events", className="fw-bold"),
                        html.Div([
                            dbc.Button("⚔️ Trigger Trade War", id="trade-war-btn",
                                      color="dark", className="w-100 mb-2"),
                            dbc.Button("🤝 Sign FTA with China", id="fta-china-btn",
                                      color="primary", className="w-100 mb-2"),
                            dbc.Button("🇪🇺 Sign FTA with EU", id="fta-eu-btn",
                                      color="primary", className="w-100 mb-2"),
                        ])
                    ])
                ], className="mb-3"),

                # Trading Partners Overview
                dbc.Card([
                    dbc.CardHeader(html.H4("Trading Partners")),
                    dbc.CardBody([
                        html.Div(id='trading-partners-info')
                    ])
                ])

            ], width=4),

            # Right Column - Main Charts
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Trade Indicators")),
                    dbc.CardBody([
                        dcc.Graph(id='trade-balance-chart'),
                        dcc.Graph(id='import-export-chart'),
                        dcc.Graph(id='exchange-rates-chart'),
                    ])
                ])
            ], width=8)
        ], className="mb-4"),

        # Country-Specific Details
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Trade Statistics by Country")),
                    dbc.CardBody([
                        dcc.Graph(id='country-trade-chart')
                    ])
                ])
            ], width=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Retaliation & Tariffs")),
                    dbc.CardBody([
                        dcc.Graph(id='retaliation-chart')
                    ])
                ])
            ], width=6)
        ], className="mb-4"),

        # Current Snapshot
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Current Trade Snapshot")),
                    dbc.CardBody([
                        html.Div(id='trade-current-metrics')
                    ])
                ])
            ])
        ]),

        # Hidden components for state management
        dcc.Interval(
            id='trade-interval-component',
            interval=config.UPDATE_INTERVAL,
            n_intervals=0,
            disabled=True
        ),
        dcc.Store(id='trade-simulation-state', data={'running': False, 'step': 0}),
        dcc.Location(id='trade-url', refresh=False)

    ], fluid=True)


@callback(
    Output('tariff-rate-slider', 'value'),
    Output('trade-interest-rate-slider', 'value'),
    Output('trade-govt-spending-slider', 'value'),
    Input('trade-url', 'search'),
    prevent_initial_call=False
)
def update_sliders_from_url(search):
    """Update slider values from URL parameters"""
    from urllib.parse import parse_qs

    # Default values
    tariff_rate = 0
    interest_rate = config.INITIAL_INTEREST_RATE * 100
    govt_spending = config.INITIAL_GOVT_SPENDING

    if search:
        # Parse query parameters
        params = parse_qs(search.lstrip('?'))

        # Update values if provided in URL
        if 'tariff_rate' in params:
            try:
                tariff_rate = float(params['tariff_rate'][0])
            except (ValueError, IndexError):
                pass

        if 'interest_rate' in params:
            try:
                interest_rate = float(params['interest_rate'][0])
            except (ValueError, IndexError):
                pass

        if 'govt_spending' in params:
            try:
                govt_spending = float(params['govt_spending'][0])
            except (ValueError, IndexError):
                pass

    return tariff_rate, interest_rate, govt_spending


@callback(
    Output('trade-simulation-state', 'data'),
    Output('trade-interval-component', 'disabled'),
    Input('trade-start-btn', 'n_clicks'),
    Input('trade-pause-btn', 'n_clicks'),
    Input('trade-reset-btn', 'n_clicks'),
    Input('trade-war-btn', 'n_clicks'),
    Input('fta-china-btn', 'n_clicks'),
    Input('fta-eu-btn', 'n_clicks'),
    State('trade-simulation-state', 'data'),
    prevent_initial_call=True
)
def control_trade_simulation(start, pause, reset, trade_war, fta_china, fta_eu, state):
    """Control trade simulation state"""
    global trade_simulation

    ctx = dash.callback_context
    if not ctx.triggered:
        return state, True

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'trade-start-btn':
        if trade_simulation is None:
            trade_simulation = TradeEconomyModel()
        state['running'] = True
        return state, False

    elif button_id == 'trade-pause-btn':
        state['running'] = False
        return state, True

    elif button_id == 'trade-reset-btn':
        trade_simulation = TradeEconomyModel()
        state['running'] = False
        state['step'] = 0
        return state, True

    elif button_id == 'trade-war-btn':
        if trade_simulation:
            trade_simulation.trigger_trade_war(intensity=0.8)
        return state, state.get('running', False) == False

    elif button_id == 'fta-china-btn':
        if trade_simulation:
            trade_simulation.trigger_free_trade_agreement('China')
        return state, state.get('running', False) == False

    elif button_id == 'fta-eu-btn':
        if trade_simulation:
            trade_simulation.trigger_free_trade_agreement('EU')
        return state, state.get('running', False) == False

    return state, True


@callback(
    Output('trade-balance-chart', 'figure'),
    Output('import-export-chart', 'figure'),
    Output('exchange-rates-chart', 'figure'),
    Output('country-trade-chart', 'figure'),
    Output('retaliation-chart', 'figure'),
    Output('trade-current-metrics', 'children'),
    Output('trading-partners-info', 'children'),
    Input('trade-interval-component', 'n_intervals'),
    Input('tariff-rate-slider', 'value'),
    Input('trade-interest-rate-slider', 'value'),
    Input('trade-govt-spending-slider', 'value'),
    State('trade-simulation-state', 'data')
)
def update_trade_simulation(n, tariff_rate, interest_rate, govt_spending, state):
    """Update trade simulation and all charts"""
    global trade_simulation

    # Initialize if needed
    if trade_simulation is None:
        trade_simulation = TradeEconomyModel()

    # Update policies
    trade_simulation.set_tariff_rate(tariff_rate / 100)
    trade_simulation.set_interest_rate(interest_rate / 100)
    trade_simulation.set_govt_spending(govt_spending)

    # Run one step if simulation is running
    step_result = None
    if state.get('running', False):
        step_result = trade_simulation.step()

    # Get trade history
    history = trade_simulation.trade_history
    steps = list(range(len(history['trade_balance'])))

    # 1. Trade Balance Chart
    trade_balance_fig = go.Figure()
    trade_balance_fig.add_trace(go.Scatter(
        x=steps, y=history['trade_balance'],
        mode='lines', name='Trade Balance',
        line=dict(color='blue', width=2),
        fill='tozeroy'
    ))
    trade_balance_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    trade_balance_fig.update_layout(
        title='Trade Balance (Exports - Imports)',
        xaxis_title='Time Step',
        yaxis_title='Balance ($)',
        hovermode='x unified'
    )

    # 2. Import/Export Chart
    import_export_fig = go.Figure()
    import_export_fig.add_trace(go.Scatter(
        x=steps, y=history['total_exports'],
        mode='lines', name='Exports', line=dict(color='green')
    ))
    import_export_fig.add_trace(go.Scatter(
        x=steps, y=history['total_imports'],
        mode='lines', name='Imports', line=dict(color='red')
    ))
    import_export_fig.add_trace(go.Scatter(
        x=steps, y=history['tariff_revenue'],
        mode='lines', name='Tariff Revenue', line=dict(color='orange', dash='dot')
    ))
    import_export_fig.update_layout(
        title='Exports, Imports & Tariff Revenue',
        xaxis_title='Time Step',
        yaxis_title='Value ($)',
        hovermode='x unified'
    )

    # 3. Exchange Rates Chart
    exchange_fig = go.Figure()
    for country in ['China', 'EU', 'ROW']:
        if f'{country}_exchange_rate' in history:
            exchange_fig.add_trace(go.Scatter(
                x=steps, y=history[f'{country}_exchange_rate'],
                mode='lines', name=f'{country}'
            ))
    exchange_fig.update_layout(
        title='Exchange Rates (Foreign Currency per $1)',
        xaxis_title='Time Step',
        yaxis_title='Exchange Rate',
        hovermode='x unified'
    )

    # 4. Country Trade Chart
    country_trade_fig = go.Figure()
    for country in ['China', 'EU', 'ROW']:
        if f'{country}_imports' in history:
            # Exports to this country (from domestic perspective)
            country_trade_fig.add_trace(go.Bar(
                x=[country], y=[history[f'{country}_exports'][-1] if history[f'{country}_exports'] else 0],
                name='Exports To', marker_color='green', showlegend=(country == 'China')
            ))
            # Imports from this country
            country_trade_fig.add_trace(go.Bar(
                x=[country], y=[history[f'{country}_imports'][-1] if history[f'{country}_imports'] else 0],
                name='Imports From', marker_color='red', showlegend=(country == 'China')
            ))
    country_trade_fig.update_layout(
        title='Current Trade by Country',
        xaxis_title='Country',
        yaxis_title='Value ($)',
        barmode='group'
    )

    # 5. Retaliation Chart
    retaliation_fig = go.Figure()
    domestic_tariff_history = [tariff_rate / 100] * len(steps)  # Current domestic tariff
    retaliation_fig.add_trace(go.Scatter(
        x=steps, y=domestic_tariff_history,
        mode='lines', name='Domestic Tariff', line=dict(color='blue', width=3)
    ))
    for country in ['China', 'EU', 'ROW']:
        if f'{country}_tariff' in history:
            retaliation_fig.add_trace(go.Scatter(
                x=steps, y=history[f'{country}_tariff'],
                mode='lines', name=f'{country} Retaliation'
            ))
    retaliation_fig.update_layout(
        title='Tariff Rates: Domestic vs Foreign Retaliation',
        xaxis_title='Time Step',
        yaxis_title='Tariff Rate',
        hovermode='x unified'
    )

    # Current Metrics
    current_state = step_result or trade_simulation.get_current_state()
    trade_state = trade_simulation.get_trade_state()

    latest_trade_balance = history['trade_balance'][-1] if history['trade_balance'] else 0
    latest_exports = history['total_exports'][-1] if history['total_exports'] else 0
    latest_imports = history['total_imports'][-1] if history['total_imports'] else 0
    latest_tariff_revenue = history['tariff_revenue'][-1] if history['tariff_revenue'] else 0
    net_exports_pct = history['net_exports_pct_gdp'][-1] if history['net_exports_pct_gdp'] else 0

    metrics_display = dbc.Row([
        dbc.Col([
            html.H5("Trade Balance"),
            html.H3(f"${latest_trade_balance:,.0f}",
                   style={'color': 'green' if latest_trade_balance > 0 else 'red'})
        ], width=3),
        dbc.Col([
            html.H5("Exports"),
            html.H3(f"${latest_exports:,.0f}", style={'color': 'green'})
        ], width=2),
        dbc.Col([
            html.H5("Imports"),
            html.H3(f"${latest_imports:,.0f}", style={'color': 'red'})
        ], width=2),
        dbc.Col([
            html.H5("Tariff Revenue"),
            html.H3(f"${latest_tariff_revenue:,.0f}", style={'color': 'orange'})
        ], width=2),
        dbc.Col([
            html.H5("Net Exports % GDP"),
            html.H3(f"{net_exports_pct:.1f}%")
        ], width=3),
    ])

    # Trading Partners Info
    partners_info = []
    for country_name, foreign_sector in trade_simulation.foreign_sectors.items():
        state = foreign_sector.get_state()
        partners_info.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"🌐 {country_name}", className="mb-2"),
                    html.Small([
                        html.Strong("Exchange Rate: "),
                        f"{state['exchange_rate']:.2f}", html.Br(),
                        html.Strong("Their Tariff: "),
                        f"{state['tariff_rate']*100:.1f}%", html.Br(),
                        html.Strong("GDP Growth: "),
                        f"{state['gdp_growth_rate']*100:.1f}%", html.Br(),
                        html.Strong("Trade Balance: "),
                        html.Span(
                            f"${state['trade_balance']:,.0f}",
                            style={'color': 'green' if state['trade_balance'] > 0 else 'red'}
                        )
                    ])
                ])
            ], className="mb-2")
        )

    return (trade_balance_fig, import_export_fig, exchange_fig,
            country_trade_fig, retaliation_fig, metrics_display, partners_info)
