"""
News Insights page - Real-time economic policy news with AI analysis
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime

from data.news_client import get_news_client
from data.news_analyzer import get_news_analyzer

# Register this page
dash.register_page(__name__, path='/news', name='News Insights', title='Economic News & Policy Insights')


def layout(**kwargs):
    """Create the news insights page layout"""

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("📰 Economic News & Policy Insights", className="text-center mb-3 mt-3"),
                html.P(
                    "Latest economic policy news analyzed by AI • Simulate real-world policies in your model",
                    className="text-center text-muted mb-4"
                )
            ])
        ]),

        # Controls
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("News Timeframe", className="fw-bold"),
                        dcc.Dropdown(
                            id='news-timeframe',
                            options=[
                                {'label': 'Last 24 hours', 'value': 1},
                                {'label': 'Last 3 days', 'value': 3},
                                {'label': 'Last week', 'value': 7},
                                {'label': 'Last 2 weeks', 'value': 14},
                            ],
                            value=7,
                            clearable=False,
                            className="mb-3"
                        ),

                        dbc.Button(
                            "🔄 Refresh News",
                            id="refresh-news-btn",
                            color="primary",
                            className="w-100"
                        ),

                        html.Hr(className="my-3"),

                        html.Div([
                            html.Small([
                                html.Strong("💡 How it works:"), html.Br(),
                                "• Fetches latest economic policy news", html.Br(),
                                "• AI analyzes policy impact & sentiment", html.Br(),
                                "• One-click scenario simulation", html.Br(),
                                html.Br(),
                                html.Em("Powered by NewsAPI & Azure OpenAI")
                            ], className="text-muted")
                        ])
                    ])
                ])
            ], width=3),

            # News Feed
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Latest Policy News", style={'display': 'inline-block'}),
                        html.Span(id='news-last-updated',
                                 style={'float': 'right', 'fontSize': '12px', 'color': '#666'})
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            id="news-loading",
                            type="default",
                            children=html.Div(id='news-feed')
                        )
                    ])
                ])
            ], width=9)
        ]),

        # Store for news data
        dcc.Store(id='news-data', data=None),

        # Modal for showing scenario details
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("📊 Simulate This Policy Scenario")),
            dbc.ModalBody(id='scenario-modal-body'),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-scenario-modal", className="me-2"),
                dcc.Link(
                    dbc.Button("Go to Simulation Page", color="primary"),
                    id="go-to-simulation-link",
                    href="/"
                ),
            ])
        ], id='scenario-modal', size="lg", is_open=False),

    ], fluid=True)


@callback(
    Output('news-data', 'data'),
    Output('news-last-updated', 'children'),
    Input('refresh-news-btn', 'n_clicks'),
    Input('news-timeframe', 'value'),
    prevent_initial_call=False
)
def fetch_news(n_clicks, days_back):
    """Fetch and analyze news articles"""
    try:
        # Fetch news
        news_client = get_news_client()
        articles = news_client.fetch_economic_policy_news(
            days_back=days_back,
            max_articles=10
        )

        # Analyze articles with AI
        analyzer = get_news_analyzer()
        analyzed_articles = []

        for article in articles:
            analysis = analyzer.analyze_article(article)
            analyzed_articles.append({
                'title': article.title,
                'description': article.description,
                'url': article.url,
                'published_at': article.published_at,
                'source': article.source,
                'analysis': analysis
            })

        timestamp = datetime.now().strftime('%I:%M %p')
        return analyzed_articles, f"Last updated: {timestamp}"

    except Exception as e:
        return [], f"Error: {str(e)}"


@callback(
    Output('news-feed', 'children'),
    Input('news-data', 'data'),
    prevent_initial_call=False
)
def display_news(articles):
    """Display news articles with AI analysis"""
    if not articles:
        return html.Div([
            html.P("Loading news...", className="text-center text-muted p-5")
        ])

    news_cards = []

    for idx, article in enumerate(articles):
        analysis = article['analysis']

        # Determine sentiment color and label
        sentiment = analysis['sentiment']
        if sentiment > 0.3:
            sentiment_color = "success"
            sentiment_label = "Expansionary"
            sentiment_icon = "📈"
        elif sentiment < -0.3:
            sentiment_color = "danger"
            sentiment_label = "Contractionary"
            sentiment_icon = "📉"
        else:
            sentiment_color = "warning"
            sentiment_label = "Neutral"
            sentiment_icon = "➡️"

        # Policy type badge color
        policy_colors = {
            'monetary': 'primary',
            'fiscal': 'info',
            'mixed': 'secondary',
            'indicator': 'light'
        }
        policy_color = policy_colors.get(analysis['policy_type'], 'secondary')

        # Check if we have suggested parameters
        suggested_params = analysis['suggested_params']
        has_suggestions = any(v is not None for v in suggested_params.values())

        # Build parameter changes text
        param_changes = []
        if suggested_params.get('interest_rate') is not None:
            param_changes.append(f"Interest Rate → {suggested_params['interest_rate']}%")
        if suggested_params.get('govt_spending') is not None:
            param_changes.append(f"Govt Spending → ${suggested_params['govt_spending']:,}")
        if suggested_params.get('tax_rate') is not None:
            param_changes.append(f"Tax Rate → {suggested_params['tax_rate']}%")
        if suggested_params.get('welfare_payment') is not None:
            param_changes.append(f"Welfare → ${suggested_params['welfare_payment']}")

        # Parse published date
        try:
            pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            time_ago = _time_ago(pub_date)
        except:
            time_ago = "Recently"

        news_cards.append(
            dbc.Card([
                dbc.CardBody([
                    # Header row
                    dbc.Row([
                        dbc.Col([
                            html.H5(article['title'], className="mb-2"),
                            html.Small([
                                html.Span(article['source'], className="text-primary"),
                                " • ",
                                html.Span(time_ago, className="text-muted")
                            ])
                        ], width=8),
                        dbc.Col([
                            dbc.Badge(analysis['policy_type'].title(),
                                     color=policy_color, className="me-2"),
                            dbc.Badge(f"{sentiment_icon} {sentiment_label}",
                                     color=sentiment_color),
                        ], width=4, className="text-end")
                    ]),

                    html.Hr(),

                    # Description
                    html.P(article['description'], className="mb-3"),

                    # AI Analysis
                    dbc.Alert([
                        html.Strong("🤖 AI Analysis: "),
                        analysis['summary'],
                        html.Br(),
                        html.Small([
                            html.Strong("Confidence: "),
                            f"{analysis['confidence']*100:.0f}%"
                        ], className="text-muted")
                    ], color="light", className="mb-3"),

                    # Impact indicators
                    html.Div([
                        html.Strong("Expected Impact: "),
                        _impact_badge("GDP Growth", analysis['impact']['gdp_growth']),
                        _impact_badge("Inflation", analysis['impact']['inflation']),
                        _impact_badge("Unemployment", analysis['impact']['unemployment']),
                    ], className="mb-3"),

                    # Suggested parameters
                    html.Div([
                        html.Strong("Suggested Policy Changes: "),
                        html.Br(),
                        html.Small(", ".join(param_changes) if param_changes else "No specific changes suggested",
                                  className="text-muted")
                    ], className="mb-3") if has_suggestions else html.Div(),

                    # Actions
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                "🔗 Read Full Article"
                            ], href=article['url'], target="_blank",
                               color="link", size="sm", className="me-2")
                        ], width=6),
                        dbc.Col([
                            dbc.Button([
                                "▶️ Simulate This Policy"
                            ], id={'type': 'simulate-btn', 'index': idx},
                               color="success", size="sm", className="float-end",
                               disabled=not has_suggestions)
                        ], width=6)
                    ])
                ])
            ], className="mb-3")
        )

    if not news_cards:
        return html.Div([
            html.P("No news articles found. Try a different timeframe.",
                  className="text-center text-muted p-5")
        ])

    return html.Div(news_cards)


def _impact_badge(label, impact):
    """Create a colored badge for impact indicators"""
    if impact == "positive" or impact == "decrease" and label == "Unemployment":
        color = "success"
        icon = "↑" if impact == "positive" else "↓"
    elif impact == "negative" or impact == "increase" and label != "Inflation":
        color = "danger"
        icon = "↓" if impact == "negative" else "↑"
    else:
        color = "secondary"
        icon = "→"

    return dbc.Badge(f"{label} {icon}", color=color, className="me-2")


def _time_ago(dt):
    """Convert datetime to 'X hours ago' format"""
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"


@callback(
    Output('scenario-modal', 'is_open'),
    Output('scenario-modal-body', 'children'),
    Output('go-to-simulation-link', 'href'),
    Input({'type': 'simulate-btn', 'index': ALL}, 'n_clicks'),
    Input('close-scenario-modal', 'n_clicks'),
    State('news-data', 'data'),
    State('scenario-modal', 'is_open'),
    prevent_initial_call=True
)
def handle_simulate_click(simulate_clicks, close_clicks, articles, is_open):
    """Handle simulate button clicks and show modal with scenario details"""
    if not ctx.triggered:
        return is_open, "", "/"

    triggered_id = ctx.triggered_id

    # Close button clicked
    if triggered_id == 'close-scenario-modal':
        return False, "", "/"

    # Simulate button clicked
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'simulate-btn':
        article_idx = triggered_id['index']

        if not articles or article_idx >= len(articles):
            return is_open, "Error: Article not found", "/"

        article = articles[article_idx]
        analysis = article['analysis']
        suggested_params = analysis['suggested_params']

        # Build URL with query parameters
        url_params = []
        if suggested_params.get('interest_rate') is not None:
            url_params.append(f"interest_rate={suggested_params['interest_rate']}")
        if suggested_params.get('govt_spending') is not None:
            url_params.append(f"govt_spending={suggested_params['govt_spending']}")
        if suggested_params.get('tax_rate') is not None:
            url_params.append(f"tax_rate={suggested_params['tax_rate']}")
        if suggested_params.get('welfare_payment') is not None:
            url_params.append(f"welfare={suggested_params['welfare_payment']}")

        simulation_url = "/?" + "&".join(url_params) if url_params else "/"

        # Build scenario details
        modal_content = [
            dbc.Alert([
                html.H5(article['title'], className="mb-2"),
                html.P([
                    html.Strong("Source: "), article['source'], " • ",
                    html.Strong("Policy Type: "), analysis['policy_type'].title()
                ])
            ], color="info"),

            html.H6("🤖 AI Analysis:", className="mt-3"),
            html.P(analysis['summary']),

            html.Hr(),

            html.H6("📋 Suggested Simulation Parameters:", className="mt-3"),
            html.P("Copy these values and paste them into the Simulation page:", className="text-muted mb-3"),
        ]

        # Parameter cards
        param_cards = []

        if suggested_params.get('interest_rate') is not None:
            param_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Interest Rate", className="card-title"),
                        html.H3(f"{suggested_params['interest_rate']}%", className="text-primary"),
                        html.Small("Set the Interest Rate slider to this value", className="text-muted")
                    ])
                ], className="mb-2")
            )

        if suggested_params.get('govt_spending') is not None:
            param_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Government Spending", className="card-title"),
                        html.H3(f"${suggested_params['govt_spending']:,}", className="text-primary"),
                        html.Small("Set the Government Spending slider to this value", className="text-muted")
                    ])
                ], className="mb-2")
            )

        if suggested_params.get('tax_rate') is not None:
            param_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("VAT Rate", className="card-title"),
                        html.H3(f"{suggested_params['tax_rate']}%", className="text-primary"),
                        html.Small("Set the VAT Rate slider to this value", className="text-muted")
                    ])
                ], className="mb-2")
            )

        if suggested_params.get('welfare_payment') is not None:
            param_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Welfare Payment", className="card-title"),
                        html.H3(f"${suggested_params['welfare_payment']:,}", className="text-primary"),
                        html.Small("Set the Welfare Payment slider to this value", className="text-muted")
                    ])
                ], className="mb-2")
            )

        if param_cards:
            modal_content.extend(param_cards)
        else:
            modal_content.append(
                dbc.Alert("No specific parameter changes suggested for this article.", color="warning")
            )

        # Instructions
        modal_content.append(html.Hr())
        modal_content.append(
            dbc.Alert([
                html.Strong("💡 Next Steps:"), html.Br(),
                "1. Review the parameter values above", html.Br(),
                "2. Click 'Go to Simulation Page' button below", html.Br(),
                "3. The sliders will be automatically set to these values!", html.Br(),
                "4. Click 'Start Simulation' and observe the results"
            ], color="success")
        )

        return True, modal_content, simulation_url

    return is_open, "", "/"
