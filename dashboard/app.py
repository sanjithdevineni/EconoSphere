"""
Main Dash application for multi-page economic simulation dashboard
"""

import dash
from dash import page_container
import dash_bootstrap_components as dbc

import config


def create_dashboard():
    """Create and configure the multi-page Dash application"""

    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        use_pages=True  # Enable multi-page support
    )

    app.layout = create_layout()

    return app


def create_layout():
    """Create the main application layout with navigation"""

    return dbc.Container([
        # Navigation Bar
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Simulation", href="/")),
                dbc.NavItem(dbc.NavLink("Validation", href="/validation")),
                dbc.NavItem(dbc.NavLink("News Insights", href="/news")),
            ],
            brand="EconoSphere - Macroeconomic Simulator",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4",
            fluid=True,
        ),

        # Page Container (where individual pages are rendered)
        page_container

    ], fluid=True, className="p-0")


if __name__ == '__main__':
    app = create_dashboard()
    app.run(debug=config.DEBUG_MODE, port=config.PORT)
