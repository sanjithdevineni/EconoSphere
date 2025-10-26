"""
Main Dash application for multi-page economic simulation dashboard
"""

import dash
from dash import page_container, html
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


# Helper functions from main branch
def calibration_banner():
    """Return a banner showing calibration metadata."""
    source = getattr(config, "CALIBRATION_SOURCE", None)
    if source and not source.get("error"):
        country = source.get("country") or "Unknown"
        year = source.get("year") or "N/A"
        path = source.get("path")
        text = [f"Calibrated parameters loaded: {country} {year}"]
        if path:
            text.append(f"(source: {path})")
        return html.Span(" ".join(text))
    if source and source.get("error"):
        path = source.get("path")
        message = f"Calibration override failed to load ({path}); using built-in defaults."
        return html.Span(message)
    return html.Span(
        "Using built-in simulation defaults. Run scripts/calibrate_economy.py to load real-world parameters.",
        className="text-muted",
    )


def calibration_snapshot():
    """Render a snapshot of calibrated parameters and diagnostics."""
    params = getattr(config, "CALIBRATED_PARAMETERS", None)
    if not params:
        return dbc.Alert(
            "No calibration loaded – simulation is using default parameters.",
            color="light",
            className="mt-3 text-muted",
        )

    items = []

    def fmt_value(key, value):
        if value is None:
            return "—"
        if key == "unemployment_rate":
            return f"{value * 100:.1f}%"
        if key == "gdp_per_capita":
            return f"${value:,.0f}"
        return f"{value:.3f}"

    labels = [
        ("mpc", "MPC (household propensity)"),
        ("tfp_a", "Productivity (A)"),
        ("gamma", "Returns to scale (γ)"),
        ("depreciation", "Capital depreciation (δ)"),
        ("unemployment_rate", "Baseline unemployment"),
        ("gdp_per_capita", "GDP per capita"),
    ]

    for key, label in labels:
        items.append(
            dbc.ListGroupItem(
                [
                    html.Span(label),
                    html.Span(
                        fmt_value(key, params.get(key)),
                        className="fw-semibold",
                    ),
                ],
                className="d-flex justify-content-between align-items-center",
            )
        )

    diagnostics = getattr(config, "CALIBRATION_DIAGNOSTICS", {}) or {}
    diag_rows = []
    for key, diag in diagnostics.items():
        r2 = diag.get("r2")
        mae = diag.get("mae")
        if r2 is None and mae is None:
            continue
        diag_rows.append(
            html.Div(
                [
                    html.Span(key.upper(), className="fw-semibold me-2"),
                    html.Span(
                        f"R² {r2:.2f} · MAE {mae:.3f}"
                        if r2 is not None and mae is not None
                        else f"R² {r2:.2f}" if r2 is not None else f"MAE {mae:.3f}",
                        className="text-muted",
                    ),
                ],
                className="small",
            )
        )

    return html.Div(
        [
            html.H5("ML-Calibrated Parameters", className="mt-3"),
            dbc.ListGroup(items, flush=True),
            html.Div(
                diag_rows,
                className="mt-2",
            ) if diag_rows else html.Div(className="mt-2"),
        ]
    )


if __name__ == '__main__':
    app = create_dashboard()
    app.run(debug=config.DEBUG_MODE, port=config.PORT)
