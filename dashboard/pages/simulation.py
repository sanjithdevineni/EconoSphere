"""
Main simulation page - Real-time economic simulation with policy controls
"""

import json
import logging
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from urllib.parse import urlparse, parse_qs

from simulation.economy_model import EconomyModel
import config
from dashboard.app import calibration_banner, calibration_snapshot

LOGGER = logging.getLogger(__name__)

# Register this page
dash.register_page(__name__, path='/', name='Simulation', title='Economic Simulation')

# Global simulation instance
simulation = None


def _load_metadata(path: Path) -> tuple[str | None, int | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None, None
    return payload.get("country"), payload.get("year")


def calibration_dropdown_options() -> list[dict[str, str]]:
    """Build dropdown options from available calibration files."""
    options = [
        {"label": "Simulation Defaults", "value": "__defaults__"}
    ]

    seen_keys: set[tuple[str, int]] = set()

    for path in config.list_calibration_files():
        if path.stem.lower() == "latest":
            continue

        country, year = _load_metadata(path)
        label: str
        if country and year and (country.upper(), year) not in seen_keys:
            label = f"{country.upper()} {year}"
            seen_keys.add((country.upper(), year))
        else:
            label = path.stem.replace("_", " ")

        options.append({"label": label, "value": str(path)})

    return options


def current_calibration_value() -> str:
    source = getattr(config, "CALIBRATION_SOURCE", None)
    path = source.get("path") if isinstance(source, dict) else None
    if path:
        cal_path = Path(path)
        if cal_path.stem.lower() == "latest":
            country = source.get("country") if isinstance(source, dict) else None
            year = source.get("year") if isinstance(source, dict) else None
            if country and year:
                for candidate in config.list_calibration_files():
                    if candidate.stem.lower() == "latest":
                        continue
                    c_country, c_year = _load_metadata(candidate)
                    if c_country and c_year and c_country.upper() == country.upper() and c_year == year:
                        return str(candidate)
        return path
    return "__defaults__"


def layout(**kwargs):
    """Create the simulation page layout"""

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Economic Simulation", className="text-center mb-3 mt-3"),
                html.P(
                    "Agent-based economic simulation with real-time policy controls",
                    className="text-center text-muted mb-2"
                ),
                dcc.Dropdown(
                    id="calibration-selector",
                    options=calibration_dropdown_options(),
                    value=current_calibration_value(),
                    clearable=False,
                    className="mb-3",
                ),
                dbc.Alert(
                    id="calibration-banner",
                    children=calibration_banner(),
                    color="info",
                    className="text-center mx-auto",
                    dismissable=False,
                )
            ])
        ]),

        # Control Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Policy Controls")),
                    dbc.CardBody([
                        # Tax Rate (VAT)
                        html.Label("VAT Rate (%)", className="fw-bold"),
                        dcc.Slider(
                            id='tax-rate-slider',
                            min=0,
                            max=50,
                            step=1,
                            value=config.INITIAL_VAT_RATE * 100,
                            marks={i: f'{i}%' for i in range(0, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),

                        # Interest Rate
                        html.Label("Interest Rate (%)", className="fw-bold mt-3"),
                        dcc.Slider(
                            id='interest-rate-slider',
                            min=0,
                            max=10,
                            step=0.25,
                            value=config.INITIAL_INTEREST_RATE * 100,
                            marks={i: f'{i}%' for i in range(0, 11, 2)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),

                        # Welfare Payment
                        html.Label("Welfare Payment ($)", className="fw-bold mt-3"),
                        dcc.Slider(
                            id='welfare-slider',
                            min=0,
                            max=2000,
                            step=100,
                            value=config.INITIAL_WELFARE_PAYMENT,
                            marks={i: f'${i}' for i in range(0, 2001, 500)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),

                        # Government Spending
                        html.Label("Government Spending ($)", className="fw-bold mt-3"),
                        dcc.Slider(
                            id='govt-spending-slider',
                            min=0,
                            max=50000,
                            step=1000,
                            value=config.INITIAL_GOVT_SPENDING,
                            marks={i: f'${i//1000}k' for i in range(0, 50001, 10000)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),

                        # Control Buttons
                        html.Div([
                            dbc.Button("Start Simulation", id="start-btn", color="success", className="me-2"),
                            dbc.Button("Pause", id="pause-btn", color="warning", className="me-2"),
                            dbc.Button("Reset", id="reset-btn", color="danger", className="me-2"),
                        ], className="mt-4"),

                        html.Div([
                            dbc.Button("Trigger Recession", id="recession-btn", color="dark", className="me-2 mt-2"),
                            dbc.Button("Trigger Inflation", id="inflation-btn", color="dark", className="mt-2"),
                        ]),

                        # Auto Policy Toggle
                        html.Div([
                            dbc.Checklist(
                                options=[{"label": "Enable Auto Monetary Policy (Taylor Rule)", "value": 1}],
                                value=[],
                                id="auto-policy-toggle",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ], width=4),

            # Main Charts
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Economic Indicators")),
                    dbc.CardBody([
                        dcc.Graph(id='gdp-chart'),
                        dcc.Graph(id='unemployment-chart'),
                        dcc.Graph(id='inflation-chart'),
                        dcc.Graph(id='inequality-chart'),
                    ])
                ])
            ], width=8)
        ], className="mb-4"),

        # Additional Metrics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Current Snapshot")),
                    dbc.CardBody([
                        html.Div(id='current-metrics', className="row gy-2"),
                        html.Div(id='calibration-panel', children=calibration_snapshot())
                    ])
                ])
            ])
        ]),

        # AI Narrative Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("📰 Economic News Feed", style={'display': 'inline-block'}),
                        html.Span(id='narrative-counter', style={'marginLeft': '20px', 'fontSize': '14px', 'color': '#666'})
                    ]),
                    dbc.CardBody([
                        html.Div(id='ai-narrative', style={'minHeight': '100px'}, children=[
                            html.P("AI narratives will appear here when you trigger a recession or inflation crisis.",
                                   style={'fontSize': '15px', 'color': '#666', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px'})
                        ])
                    ])
                ], className="mt-3")
            ])
        ]),

        # Hidden components for state management
        dcc.Interval(
            id='interval-component',
            interval=config.UPDATE_INTERVAL,
            n_intervals=0,
            disabled=True
        ),
        dcc.Store(id='simulation-state', data={'running': False, 'step': 0}),
        dcc.Location(id='url', refresh=False)

    ], fluid=True)


@callback(
    Output('tax-rate-slider', 'value'),
    Output('interest-rate-slider', 'value'),
    Output('welfare-slider', 'value'),
    Output('govt-spending-slider', 'value'),
    Input('url', 'search'),
    prevent_initial_call=False
)
def update_sliders_from_url(search):
    """Update slider values from URL parameters"""
    # Default values
    tax_rate = config.INITIAL_VAT_RATE * 100
    interest_rate = config.INITIAL_INTEREST_RATE * 100
    welfare = config.INITIAL_WELFARE_PAYMENT
    govt_spending = config.INITIAL_GOVT_SPENDING

    if search:
        # Parse query parameters
        params = parse_qs(search.lstrip('?'))

        # Update values if provided in URL
        if 'tax_rate' in params:
            try:
                tax_rate = float(params['tax_rate'][0])
            except (ValueError, IndexError):
                pass

        if 'interest_rate' in params:
            try:
                interest_rate = float(params['interest_rate'][0])
            except (ValueError, IndexError):
                pass

        if 'welfare' in params:
            try:
                welfare = float(params['welfare'][0])
            except (ValueError, IndexError):
                pass

        if 'govt_spending' in params:
            try:
                govt_spending = float(params['govt_spending'][0])
            except (ValueError, IndexError):
                pass

    return tax_rate, interest_rate, welfare, govt_spending


@callback(
    Output('calibration-banner', 'children'),
    Output('calibration-panel', 'children'),
    Output('calibration-selector', 'options'),
    Output('calibration-selector', 'value'),
    Input('calibration-selector', 'value'),
    prevent_initial_call=False
)
def handle_calibration_selection(selected_value):
    """Apply selected calibration and refresh UI."""
    global simulation

    target_value = selected_value or current_calibration_value()

    if target_value == "__defaults__":
        config.apply_calibration(None)
        applied_value = "__defaults__"
    else:
        config.apply_calibration(target_value)
        applied_value = target_value

    # Reset simulation so new calibration takes effect on next start
    simulation = None

    options = calibration_dropdown_options()
    available_values = {opt['value'] for opt in options}
    if applied_value not in available_values:
        applied_value = "__defaults__"

    return calibration_banner(), calibration_snapshot(), options, applied_value


@callback(
    Output('simulation-state', 'data'),
    Output('interval-component', 'disabled'),
    Input('start-btn', 'n_clicks'),
    Input('pause-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    Input('recession-btn', 'n_clicks'),
    Input('inflation-btn', 'n_clicks'),
    State('simulation-state', 'data'),
    prevent_initial_call=True
)
def control_simulation(start, pause, reset, recession, inflation, state):
    """Control simulation state"""
    global simulation

    ctx = dash.callback_context
    if not ctx.triggered:
        return state, True

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-btn':
        if simulation is None:
            simulation = EconomyModel()
        state['running'] = True
        return state, False

    elif button_id == 'pause-btn':
        state['running'] = False
        return state, True

    elif button_id == 'reset-btn':
        simulation = EconomyModel()
        state['running'] = False
        state['step'] = 0
        return state, True

    elif button_id == 'recession-btn':
        if simulation:
            simulation.trigger_crisis('recession')
        return state, state.get('running', False) == False

    elif button_id == 'inflation-btn':
        if simulation:
            simulation.trigger_crisis('inflation')
        return state, state.get('running', False) == False

    return state, True


@callback(
    Output('gdp-chart', 'figure'),
    Output('unemployment-chart', 'figure'),
    Output('inflation-chart', 'figure'),
    Output('inequality-chart', 'figure'),
    Output('current-metrics', 'children'),
    Output('ai-narrative', 'children'),
    Output('narrative-counter', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('tax-rate-slider', 'value'),
    Input('interest-rate-slider', 'value'),
    Input('welfare-slider', 'value'),
    Input('govt-spending-slider', 'value'),
    Input('auto-policy-toggle', 'value'),
    State('simulation-state', 'data')
)
def update_simulation(n, tax_rate, interest_rate, welfare, govt_spending, auto_policy, state):
    """Update simulation and charts"""
    global simulation

    # Initialize if needed
    if simulation is None:
        simulation = EconomyModel()

    # Update policies
    simulation.set_tax_rate(tax_rate / 100)
    simulation.set_interest_rate(interest_rate / 100)
    simulation.set_welfare_payment(welfare)
    simulation.set_govt_spending(govt_spending)
    simulation.enable_auto_monetary_policy(len(auto_policy) > 0)

    # Run one step if simulation is running
    current_metrics = None
    if state.get('running', False):
        current_metrics = simulation.step()

    # Get history
    history = simulation.metrics.get_history()
    steps = list(range(len(history['gdp'])))

    # Create charts
    gdp_fig = go.Figure()
    gdp_fig.add_trace(go.Scatter(x=steps, y=history['gdp'], mode='lines', name='GDP'))
    gdp_fig.update_layout(title='GDP Over Time', xaxis_title='Time Step', yaxis_title='GDP ($)')

    unemployment_fig = go.Figure()
    unemployment_fig.add_trace(go.Scatter(x=steps, y=history['unemployment'], mode='lines', name='Unemployment', line=dict(color='red')))
    unemployment_fig.update_layout(title='Unemployment Rate', xaxis_title='Time Step', yaxis_title='Rate (%)')

    inflation_fig = go.Figure()
    inflation_fig.add_trace(go.Scatter(x=steps, y=history['inflation'], mode='lines', name='Inflation', line=dict(color='orange')))
    inflation_fig.update_layout(title='Inflation Rate', xaxis_title='Time Step', yaxis_title='Rate (%)')

    inequality_fig = go.Figure()
    inequality_fig.add_trace(go.Scatter(x=steps, y=history['gini'], mode='lines', name='Gini Coefficient', line=dict(color='purple')))
    inequality_fig.update_layout(title='Wealth Inequality (Gini)', xaxis_title='Time Step', yaxis_title='Gini Coefficient')

    # Current metrics
    current = simulation.get_current_state()
    metrics_display = dbc.Row([
        dbc.Col([
            html.H5("GDP"),
            html.H3(f"${current['gdp']:,.0f}")
        ], width=3),
        dbc.Col([
            html.H5("Unemployment"),
            html.H3(f"{current['unemployment']:.1f}%")
        ], width=3),
        dbc.Col([
            html.H5("Inflation"),
            html.H3(f"{current['inflation']:.2f}%")
        ], width=3),
        dbc.Col([
            html.H5("Govt Debt"),
            html.H3(f"${current['govt_debt']:,.0f}")
        ], width=3),
    ])

    # AI Narrative display - get narrative history
    narrative_history = []

    LOGGER.info(f"Checking narrative sources: current_metrics={current_metrics is not None}, current={current is not None}, simulation={simulation is not None}")

    if current_metrics and 'narrative_history' in current_metrics:
        narrative_history = current_metrics['narrative_history']
        LOGGER.info(f"Found {len(narrative_history)} narratives in current_metrics")
    elif current and 'narrative_history' in current:
        narrative_history = current['narrative_history']
        LOGGER.info(f"Found {len(narrative_history)} narratives in current state")
    elif simulation and hasattr(simulation, 'narrative_history'):
        narrative_history = simulation.narrative_history
        LOGGER.info(f"Found {len(narrative_history)} narratives directly from simulation.narrative_history")
    else:
        LOGGER.warning(f"NO narrative_history found anywhere! current_metrics keys: {current_metrics.keys() if current_metrics else 'None'}, current keys: {current.keys() if current else 'None'}, simulation has attr: {hasattr(simulation, 'narrative_history') if simulation else 'None'}")

    if narrative_history and len(narrative_history) > 0:
        # Build list of narrative cards (newest first)
        narrative_cards = []
        for item in narrative_history:
            narrative_cards.append(
                html.Div([
                    html.Div([
                        html.Strong(f"Step {item['step']}", style={'fontSize': '14px', 'color': '#0066cc'}),
                        html.Span(f" | {simulation.current_step - item['step']} steps ago",
                                 style={'fontSize': '12px', 'color': '#666', 'marginLeft': '10px'})
                    ], style={'marginBottom': '8px'}),
                    html.P(item['text'], style={'fontSize': '15px', 'lineHeight': '1.5', 'color': '#000', 'margin': '0'}),
                ], style={
                    'padding': '15px',
                    'marginBottom': '10px',
                    'backgroundColor': '#ffffff',
                    'border': '1px solid #ddd',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            )

        narrative_display = html.Div([
            html.Div([
                html.Strong(f"{len(narrative_history)} Economic News Update(s)",
                           style={'fontSize': '16px', 'color': '#333'}),
            ], style={'marginBottom': '15px', 'paddingBottom': '10px', 'borderBottom': '2px solid #0066cc'}),
            html.Div(narrative_cards)
        ], style={'padding': '10px'})
        LOGGER.info(f"Returning narrative_display with {len(narrative_history)} items")
    else:
        narrative_display = html.Div([
            html.P("AI narratives will appear here when you trigger a recession or inflation crisis.",
                   style={'fontSize': '15px', 'color': '#666', 'fontStyle': 'italic'})
        ], style={'padding': '20px', 'textAlign': 'center'})
        LOGGER.info("Returning default narrative_display (no narratives)")

    # Add a counter to prove dynamic updates work
    counter_text = f"(Callback #{n} | Step {simulation.current_step} | History: {len(narrative_history)} items)"

    LOGGER.info(f"Callback returning: narrative_display type={type(narrative_display)}, counter={counter_text}")
    return gdp_fig, unemployment_fig, inflation_fig, inequality_fig, metrics_display, narrative_display, counter_text
