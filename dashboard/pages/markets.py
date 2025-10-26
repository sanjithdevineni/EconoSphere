"""
Financial Markets Page - Stock & Cryptocurrency Markets

HACKATHON DIFFERENTIATOR!
First economic simulator with integrated crypto-macro dynamics.
"""

import logging
import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc

from simulation.financial_markets_model import FinancialMarketsModel
import config

LOGGER = logging.getLogger(__name__)

# Register this page
dash.register_page(__name__, path='/markets', name='Financial Markets', title='Markets - Stocks & Crypto')

# Global simulation instance
markets_simulation = None


def layout(**kwargs):
    """Create the financial markets page layout"""

    return dbc.Container([
        # === HEADER ===
        dbc.Row([
            dbc.Col([
                html.H2([
                    "📈 Financial Markets",
                    html.Span(" 🔗 Stocks & Crypto", className="text-muted", style={"fontSize": "1.5rem"})
                ], className="text-center mb-2 mt-3"),
                html.P(
                    "Watch how stocks and cryptocurrency respond to macro policy in real-time",
                    className="text-center text-muted mb-3"
                ),
                dbc.Alert([
                    html.Strong("NEW! "),
                    "First economic simulator with crypto-macro integration. ",
                    "See how crypto responds to inflation, interest rates, and government reserves."
                ], color="success", className="text-center")
            ])
        ]),

        # === SIMULATION CONTROLS ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Simulation Controls")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "▶️ Start Simulation",
                                    id='markets-start-btn',
                                    color='success',
                                    className="w-100 mb-2"
                                ),
                                dbc.Button(
                                    "⏸️ Pause",
                                    id='markets-pause-btn',
                                    color='warning',
                                    className="w-100 mb-2"
                                ),
                                dbc.Button(
                                    "🔄 Reset",
                                    id='markets-reset-btn',
                                    color='danger',
                                    className="w-100"
                                ),
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.Strong("Simulation Speed:"),
                                    dcc.Slider(
                                        id='markets-speed-slider',
                                        min=500,
                                        max=3000,
                                        step=500,
                                        value=1000,
                                        marks={500: 'Fast', 1500: 'Normal', 3000: 'Slow'}
                                    )
                                ], className="mt-2")
                            ], width=8)
                        ]),
                    ])
                ])
            ], width=12)
        ], className="mb-3"),

        # === POLICY CONTROLS ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Macro Policy Controls")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Interest Rate (%)", className="fw-bold"),
                                dcc.Slider(
                                    id='markets-interest-rate',
                                    min=0,
                                    max=10,
                                    step=0.25,
                                    value=3,
                                    marks={i: f'{i}%' for i in range(0, 11, 2)},
                                    tooltip={"placement": "bottom", "always_visible": True}
                                ),
                            ], width=6),
                            dbc.Col([
                                html.Label("Government Spending ($)", className="fw-bold"),
                                dcc.Slider(
                                    id='markets-govt-spending',
                                    min=0,
                                    max=50000,
                                    step=5000,
                                    value=10000,
                                    marks={i: f'${i//1000}k' for i in range(0, 50001, 10000)},
                                    tooltip={"placement": "bottom", "always_visible": True}
                                ),
                            ], width=6),
                        ]),
                    ])
                ])
            ])
        ], className="mb-3"),

        # === SCENARIO BUTTONS ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("📍 Market Scenarios (One-Click Demo!)")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "💥 Stock Market Crash",
                                    id='trigger-stock-crash',
                                    color='danger',
                                    outline=True,
                                    className="w-100 mb-2"
                                ),
                                html.Small("-30% stock market drop", className="text-muted d-block text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Button(
                                    "📉 Crypto Crash",
                                    id='trigger-crypto-crash',
                                    color='danger',
                                    outline=True,
                                    className="w-100 mb-2"
                                ),
                                html.Small("-50% crypto crash", className="text-muted d-block text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Button(
                                    "🚀 Crypto Rally",
                                    id='trigger-crypto-rally',
                                    color='success',
                                    outline=True,
                                    className="w-100 mb-2"
                                ),
                                html.Small("+30% crypto pump", className="text-muted d-block text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Button(
                                    "🏛️ Enable Govt Crypto Reserve",
                                    id='enable-crypto-reserve',
                                    color='primary',
                                    outline=True,
                                    className="w-100 mb-2"
                                ),
                                html.Small("Government buys crypto!", className="text-muted d-block text-center")
                            ], width=3),
                        ]),
                    ])
                ])
            ])
        ], className="mb-3"),

        # === KEY METRICS CARDS ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Stock Market Index", className="text-muted"),
                        html.H3(id='stock-index-display', children="100.0"),
                        html.Small(id='stock-change-display', className="text-success")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Crypto Price", className="text-muted"),
                        html.H3(id='crypto-price-display', children="$50,000"),
                        html.Small(id='crypto-change-display', className="text-success")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Fear & Greed Index", className="text-muted"),
                        html.H3(id='fear-greed-display', children="50"),
                        html.Small(id='fear-greed-label', children="Neutral")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Govt Crypto Reserve", className="text-muted"),
                        html.H3(id='govt-reserve-display', children="$0"),
                        html.Small(id='govt-reserve-label', children="Not enabled")
                    ])
                ])
            ], width=3),
        ], className="mb-3"),

        # === CHARTS ROW 1: PRICES ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Stock Market Index")),
                    dbc.CardBody([
                        dcc.Graph(id='stock-price-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("₿ Cryptocurrency Price")),
                    dbc.CardBody([
                        dcc.Graph(id='crypto-price-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
        ], className="mb-3"),

        # === CHARTS ROW 2: SENTIMENT & ADOPTION ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("😱 Fear & Greed Index")),
                    dbc.CardBody([
                        dcc.Graph(id='fear-greed-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Crypto Adoption Rate")),
                    dbc.CardBody([
                        dcc.Graph(id='crypto-adoption-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
        ], className="mb-3"),

        # === CHARTS ROW 3: MACRO SENSITIVITY ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🔥 Inflation vs Crypto (Inflation Hedge)")),
                    dbc.CardBody([
                        dcc.Graph(id='inflation-crypto-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("💸 Interest Rate vs Markets")),
                    dbc.CardBody([
                        dcc.Graph(id='rates-markets-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=6),
        ], className="mb-3"),

        # === CHARTS ROW 4: PORTFOLIO DISTRIBUTION ===
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("💼 Consumer Investment Distribution")),
                    dbc.CardBody([
                        dcc.Graph(id='portfolio-distribution-chart', config={'displayModeBar': False})
                    ])
                ])
            ], width=12),
        ], className="mb-3"),

        # === INTERVAL FOR AUTO-UPDATE ===
        dcc.Interval(
            id='markets-update-interval',
            interval=1000,  # milliseconds
            n_intervals=0,
            disabled=True
        ),

        # === STORE FOR SIMULATION STATE ===
        dcc.Store(id='markets-running-state', data={'running': False}),

    ], fluid=True)


# === CALLBACKS ===

@callback(
    [
        Output('markets-update-interval', 'disabled'),
        Output('markets-running-state', 'data'),
        Output('markets-start-btn', 'disabled'),
        Output('markets-pause-btn', 'disabled'),
    ],
    [
        Input('markets-start-btn', 'n_clicks'),
        Input('markets-pause-btn', 'n_clicks'),
        Input('markets-reset-btn', 'n_clicks'),
    ],
    [State('markets-running-state', 'data')]
)
def control_simulation(start_clicks, pause_clicks, reset_clicks, state):
    """Control simulation start/pause/reset"""
    global markets_simulation

    ctx = dash.callback_context
    if not ctx.triggered:
        return True, {'running': False}, False, True

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'markets-start-btn':
        # Initialize simulation if needed
        if markets_simulation is None:
            LOGGER.info("Creating new financial markets simulation...")
            markets_simulation = FinancialMarketsModel(
                num_consumers=config.NUM_CONSUMERS,
                num_firms=config.NUM_FIRMS,
                enable_stock_market=True,
                enable_crypto_market=True,
                enable_govt_crypto_reserve=False,
            )
        return False, {'running': True}, True, False

    elif button_id == 'markets-pause-btn':
        return True, {'running': False}, False, True

    elif button_id == 'markets-reset-btn':
        LOGGER.info("Resetting financial markets simulation...")
        markets_simulation = FinancialMarketsModel(
            num_consumers=config.NUM_CONSUMERS,
            num_firms=config.NUM_FIRMS,
            enable_stock_market=True,
            enable_crypto_market=True,
            enable_govt_crypto_reserve=False,
        )
        return True, {'running': False}, False, True

    return True, {'running': False}, False, True


@callback(
    Output('markets-update-interval', 'interval'),
    Input('markets-speed-slider', 'value')
)
def update_speed(speed):
    """Update simulation speed"""
    return speed


@callback(
    Output('markets-running-state', 'data', allow_duplicate=True),
    [
        Input('trigger-stock-crash', 'n_clicks'),
        Input('trigger-crypto-crash', 'n_clicks'),
        Input('trigger-crypto-rally', 'n_clicks'),
        Input('enable-crypto-reserve', 'n_clicks'),
    ],
    prevent_initial_call=True
)
def trigger_scenarios(stock_crash, crypto_crash, crypto_rally, crypto_reserve):
    """Handle scenario button clicks"""
    global markets_simulation

    if markets_simulation is None:
        return dash.no_update

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'trigger-stock-crash':
        markets_simulation.trigger_stock_crash(severity=0.3)
        LOGGER.info("Stock crash scenario triggered!")

    elif button_id == 'trigger-crypto-crash':
        markets_simulation.trigger_crypto_crash(severity=0.5)
        LOGGER.info("Crypto crash scenario triggered!")

    elif button_id == 'trigger-crypto-rally':
        markets_simulation.trigger_crypto_rally(magnitude=0.3)
        LOGGER.info("Crypto rally scenario triggered!")

    elif button_id == 'enable-crypto-reserve':
        annual_budget = 100000  # $100k annual budget
        markets_simulation.enable_government_crypto_reserve(annual_budget)
        LOGGER.info("Government crypto reserve enabled!")

    return dash.no_update


@callback(
    [
        Input('markets-interest-rate', 'value'),
        Input('markets-govt-spending', 'value'),
    ],
    prevent_initial_call=True
)
def update_policies(interest_rate, govt_spending):
    """Update macro policies"""
    global markets_simulation

    if markets_simulation is None:
        return

    # Convert percentage to decimal
    interest_rate_decimal = interest_rate / 100

    # Update central bank rate
    markets_simulation.central_bank.set_interest_rate(interest_rate_decimal)

    # Update government spending
    markets_simulation.government.set_govt_spending(govt_spending)


@callback(
    [
        Output('stock-index-display', 'children'),
        Output('stock-change-display', 'children'),
        Output('crypto-price-display', 'children'),
        Output('crypto-change-display', 'children'),
        Output('fear-greed-display', 'children'),
        Output('fear-greed-label', 'children'),
        Output('govt-reserve-display', 'children'),
        Output('govt-reserve-label', 'children'),
        Output('stock-price-chart', 'figure'),
        Output('crypto-price-chart', 'figure'),
        Output('fear-greed-chart', 'figure'),
        Output('crypto-adoption-chart', 'figure'),
        Output('inflation-crypto-chart', 'figure'),
        Output('rates-markets-chart', 'figure'),
        Output('portfolio-distribution-chart', 'figure'),
    ],
    Input('markets-update-interval', 'n_intervals'),
    State('markets-running-state', 'data')
)
def update_dashboard(n_intervals, state):
    """Update all dashboard elements"""
    global markets_simulation

    if markets_simulation is None or not state.get('running', False):
        return create_empty_dashboard()

    # Step the simulation
    try:
        markets_simulation.step()
    except Exception as e:
        LOGGER.error(f"Error stepping simulation: {e}")
        return create_empty_dashboard()

    # Get market state
    market_state = markets_simulation.get_market_state()
    metrics = markets_simulation.metrics.latest_metrics

    # === UPDATE METRIC CARDS ===

    # Stock index
    stock_index = metrics.get('stock_index', 100)
    stock_return = metrics.get('stock_daily_return', 0) * 100
    stock_change_text = f"{'+' if stock_return > 0 else ''}{stock_return:.2f}% today"
    stock_change_class = "text-success" if stock_return > 0 else "text-danger"

    # Crypto price
    crypto_price = metrics.get('crypto_price', 50000)
    crypto_change = 0
    if len(markets_simulation.market_history) > 1:
        prev_price = markets_simulation.market_history[-2].get('crypto_price', crypto_price)
        crypto_change = ((crypto_price - prev_price) / prev_price) * 100
    crypto_change_text = f"{'+' if crypto_change > 0 else ''}{crypto_change:.2f}% today"

    # Fear & Greed
    fear_greed = metrics.get('stock_fear_greed', 50)
    if fear_greed > 75:
        fear_greed_label = "Extreme Greed"
    elif fear_greed > 55:
        fear_greed_label = "Greed"
    elif fear_greed > 45:
        fear_greed_label = "Neutral"
    elif fear_greed > 25:
        fear_greed_label = "Fear"
    else:
        fear_greed_label = "Extreme Fear"

    # Government reserve
    govt_reserve_value = metrics.get('govt_crypto_reserve_value', 0)
    if govt_reserve_value > 0:
        govt_reserve_label = f"{metrics.get('govt_crypto_reserve', 0):.2f} coins"
    else:
        govt_reserve_label = "Not enabled"

    # === CREATE CHARTS ===

    # Stock price chart
    stock_history = [m.get('stock_index', 100) for m in markets_simulation.market_history]
    stock_fig = go.Figure()
    stock_fig.add_trace(go.Scatter(
        y=stock_history,
        mode='lines',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    stock_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Crypto price chart
    crypto_history = [m.get('crypto_price', 50000) for m in markets_simulation.market_history]
    crypto_fig = go.Figure()
    crypto_fig.add_trace(go.Scatter(
        y=crypto_history,
        mode='lines',
        line=dict(color='#ff7f0e', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))
    crypto_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Fear & Greed gauge chart
    fg_history = [m.get('stock_fear_greed', 50) for m in markets_simulation.market_history]
    fg_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fear_greed,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 45], 'color': "orange"},
                {'range': [45, 55], 'color': "yellow"},
                {'range': [55, 75], 'color': "lightgreen"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': fear_greed
            }
        }
    ))
    fg_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Crypto adoption chart
    adoption_history = [m.get('crypto_adoption_rate', 0.01) * 100 for m in markets_simulation.market_history]
    adoption_fig = go.Figure()
    adoption_fig.add_trace(go.Scatter(
        y=adoption_history,
        mode='lines',
        line=dict(color='#2ca02c', width=2),
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.2)'
    ))
    adoption_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(title="Adoption %", showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Inflation vs Crypto (dual axis)
    inflation_history = [m.get('inflation_rate', 0.02) * 100 for m in markets_simulation.market_history]
    inflation_crypto_fig = go.Figure()
    inflation_crypto_fig.add_trace(go.Scatter(
        y=inflation_history,
        mode='lines',
        name='Inflation %',
        line=dict(color='red', width=2),
        yaxis='y'
    ))
    inflation_crypto_fig.add_trace(go.Scatter(
        y=crypto_history,
        mode='lines',
        name='Crypto Price',
        line=dict(color='orange', width=2),
        yaxis='y2'
    ))
    inflation_crypto_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(title="Inflation %", showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)'),
        yaxis2=dict(title="Crypto $", overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Interest rate vs Markets (dual axis)
    rate_history = [m.get('interest_rate', 0.03) * 100 for m in markets_simulation.market_history]
    rates_fig = go.Figure()
    rates_fig.add_trace(go.Scatter(
        y=rate_history,
        mode='lines',
        name='Interest Rate %',
        line=dict(color='purple', width=2),
        yaxis='y'
    ))
    rates_fig.add_trace(go.Scatter(
        y=stock_history,
        mode='lines',
        name='Stock Index',
        line=dict(color='blue', width=2),
        yaxis='y2'
    ))
    rates_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(title="Rate %", showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)'),
        yaxis2=dict(title="Stock Index", overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Portfolio distribution pie chart
    consumer_stock = metrics.get('consumer_stock_holdings', 0)
    consumer_crypto = metrics.get('consumer_crypto_holdings', 0)
    total_consumer_wealth = sum(c.wealth for c in markets_simulation.consumers)

    portfolio_fig = go.Figure(data=[go.Pie(
        labels=['Cash', 'Stocks', 'Crypto'],
        values=[total_consumer_wealth, consumer_stock, consumer_crypto],
        hole=.3,
        marker=dict(colors=['#636EFA', '#1f77b4', '#ff7f0e'])
    )])
    portfolio_fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return (
        f"{stock_index:.2f}",
        stock_change_text,
        f"${crypto_price:,.0f}",
        crypto_change_text,
        f"{fear_greed:.0f}",
        fear_greed_label,
        f"${govt_reserve_value:,.0f}",
        govt_reserve_label,
        stock_fig,
        crypto_fig,
        fg_fig,
        adoption_fig,
        inflation_crypto_fig,
        rates_fig,
        portfolio_fig,
    )


def create_empty_dashboard():
    """Create empty dashboard when simulation not running"""
    empty_fig = go.Figure()
    empty_fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return (
        "100.0", "0.00% today",
        "$50,000", "0.00% today",
        "50", "Neutral",
        "$0", "Not enabled",
        empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    )
