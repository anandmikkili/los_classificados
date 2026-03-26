import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def _pricing_card(tier, price, period, features, highlighted=False, cta="Get Started"):
    return html.Div(
        className=f"pricing-card {'featured' if highlighted else ''}",
        children=[
            html.Div([
                html.Span(tier, style={"fontWeight": "800", "fontSize": "1.15rem"}),
                html.Span(" ★", style={"color": "#ffd700"}) if highlighted else None,
            ], className="mb-1"),
            html.Div(
                [html.Span(price, className="pricing-price",
                           style={"color": "#ffd700" if highlighted else "var(--text-primary)"}),
                 html.Div(period, className="pricing-period mt-1")],
                className="my-3",
            ),
            html.Hr(style={"borderColor": "rgba(255,215,0,0.2)" if highlighted else "var(--border-color)"}),
            html.Div(
                [
                    html.Div([
                        html.I(className=f"fas {'fa-check text-teal' if feat['included'] else 'fa-times'} me-2",
                               style={"color": "#2ea44f" if feat["included"] else "#6e7681",
                                      "width": "16px"}),
                        html.Span(feat["label"], style={"fontSize": "0.875rem",
                                                        "color": "var(--text-secondary)" if not feat["included"] else "var(--text-primary)"}),
                    ], className="pricing-feature")
                    for feat in features
                ],
                className="flex-grow-1 mb-4",
            ),
            dbc.Button(
                cta,
                className="btn-prime w-100 mt-auto" if highlighted else "btn-outline-teal w-100 mt-auto",
                n_clicks=0,
            ),
        ],
    )


def _lead_preview_chart():
    df = pd.DataFrame({
        "Week": ["Wk 1", "Wk 2", "Wk 3", "Wk 4", "Wk 5", "Wk 6", "Wk 7", "Wk 8"],
        "Free":  [2, 3, 2, 4, 3, 2, 3, 2],
        "Prime": [5, 9, 14, 18, 22, 27, 31, 38],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Week"], y=df["Free"], name="Free Plan",
        line={"color": "#6e7681", "width": 2, "dash": "dash"},
        fill="tozeroy", fillcolor="rgba(110,118,129,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=df["Week"], y=df["Prime"], name="Prime Plan",
        line={"color": "#00c9a7", "width": 3},
        fill="tozeroy", fillcolor="rgba(0,201,167,0.12)",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter"},
        legend={"bgcolor": "rgba(0,0,0,0)", "orientation": "h",
                 "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"t": 30, "b": 20, "l": 30, "r": 10},
        xaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False},
        yaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False, "title": "Leads / Week"},
        height=260,
    )
    return fig


FREE_FEATURES = [
    {"label": "1 active listing",                "included": True},
    {"label": "Up to 5 photos",                  "included": True},
    {"label": "Basic search visibility",          "included": True},
    {"label": "WhatsApp & phone contact",         "included": True},
    {"label": "Top placement in search",          "included": False},
    {"label": "Lead management dashboard",        "included": False},
    {"label": "Performance analytics",            "included": False},
    {"label": "Verified business badge",          "included": False},
]

PRIME_FEATURES = [
    {"label": "Unlimited listings",               "included": True},
    {"label": "Up to 20 photos per listing",      "included": True},
    {"label": "Top placement in search results",  "included": True},
    {"label": "★ Prime badge on all listings",    "included": True},
    {"label": "Lead management dashboard",        "included": True},
    {"label": "Performance analytics",            "included": True},
    {"label": "Verified business badge",          "included": True},
    {"label": "Priority customer support",        "included": True},
]

ENTERPRISE_FEATURES = [
    {"label": "Everything in Prime",              "included": True},
    {"label": "Dedicated account manager",        "included": True},
    {"label": "API access for integrations",      "included": True},
    {"label": "Custom lead qualification",        "included": True},
    {"label": "White-label option",               "included": True},
    {"label": "SLA-backed uptime guarantee",      "included": True},
    {"label": "Team access (5 users)",            "included": True},
    {"label": "Monthly business review call",     "included": True},
]

TESTIMONIALS = [
    {
        "name": "PowerPro Electric",
        "city": "Houston, TX",
        "rating": 5,
        "text": "Prime tripled our lead volume in the first month. The dashboard makes it easy to track every inquiry and respond lightning fast.",
        "icon": "⚡",
    },
    {
        "name": "CleanPro Chicago",
        "city": "Chicago, IL",
        "rating": 5,
        "text": "We went from 5 leads a week to over 30. The verified badge alone made clients trust us more. Best marketing investment for our cleaning business.",
        "icon": "🧹",
    },
    {
        "name": "Urban Rentals LA",
        "city": "Los Angeles, CA",
        "rating": 4,
        "text": "Prime analytics showed us which listings perform best. We now focus only on high-demand neighborhoods and our occupancy rate is at 95%.",
        "icon": "🏢",
    },
]


def prime_layout():
    return html.Div([

        # ── Hero ──────────────────────────────────────────────────────────
        html.Div(
            style={
                "background": "linear-gradient(145deg, #0d1117 0%, #0f1a00 50%, #0d1117 100%)",
                "borderBottom": "1px solid rgba(255,215,0,0.15)",
                "padding": "4rem 0 3rem",
                "position": "relative",
                "overflow": "hidden",
            },
            children=[
                html.Div(style={
                    "position": "absolute", "top": "-80px", "right": "-80px",
                    "width": "400px", "height": "400px",
                    "background": "radial-gradient(circle, rgba(255,215,0,0.1) 0%, transparent 70%)",
                    "pointerEvents": "none",
                }),
                dbc.Container([
                    html.Div(className="text-center", children=[
                        html.Span("★ Prime for Business", className="badge-prime mb-3 d-inline-block",
                                  style={"fontSize": "0.85rem", "padding": "0.35rem 1rem"}),
                        html.H1("Grow Your Business\nFaster with Prime",
                                style={"fontWeight": "900", "fontSize": "clamp(2rem,5vw,3.2rem)",
                                       "letterSpacing": "-1px", "lineHeight": "1.15", "marginBottom": "1rem",
                                       "whiteSpace": "pre-line"}),
                        html.P("Join 1,847 verified businesses receiving targeted, pre-qualified customer leads. "
                               "Track performance, manage inquiries, and close more deals from one powerful dashboard.",
                               style={"maxWidth": "600px", "margin": "0 auto 2rem",
                                      "color": "var(--text-secondary)", "lineHeight": "1.7"}),
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-crown me-2"), "Start Prime – $49.99/mo"],
                                id="prime-hero-btn",
                                className="btn-prime px-5 py-3 me-3",
                                style={"fontSize": "1rem"},
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Compare Plans",
                                id="prime-compare-btn",
                                className="btn-outline-teal px-4 py-3",
                                n_clicks=0,
                            ),
                        ]),
                        # Trust indicators
                        html.Div([
                            html.Span([html.I(className="fas fa-lock me-1"), "No long-term contract"],
                                      className="me-4", style={"fontSize": "0.8rem", "color": "var(--text-muted)"}),
                            html.Span([html.I(className="fas fa-undo me-1"), "Cancel anytime"],
                                      className="me-4", style={"fontSize": "0.8rem", "color": "var(--text-muted)"}),
                            html.Span([html.I(className="fas fa-star me-1"), "4.8/5 business rating"],
                                      style={"fontSize": "0.8rem", "color": "var(--text-muted)"}),
                        ], className="mt-3"),
                    ]),
                ], fluid=False),
            ],
        ),

        # ── Lead Preview Chart ─────────────────────────────────────────────
        dbc.Container(className="section", children=[
            dbc.Row([
                dbc.Col([
                    html.H2("More Leads, More Business", className="section-title"),
                    html.P("Prime businesses average 3.4× more leads than free listings. "
                           "See the difference a Prime listing makes over 8 weeks.",
                           className="section-subtitle"),
                    html.Div([
                        html.Div([
                            html.Div("3.4×", style={"fontSize": "2.5rem", "fontWeight": "900", "color": "#00c9a7"}),
                            html.Div("More leads on average", style={"color": "var(--text-muted)", "fontSize": "0.85rem"}),
                        ], className="me-4"),
                        html.Div([
                            html.Div("92%", style={"fontSize": "2.5rem", "fontWeight": "900", "color": "#ffd700"}),
                            html.Div("Businesses renew Prime", style={"color": "var(--text-muted)", "fontSize": "0.85rem"}),
                        ]),
                    ], className="d-flex mb-3"),
                ], md=5, className="d-flex flex-column justify-content-center"),
                dbc.Col(
                    dcc.Graph(
                        figure=_lead_preview_chart(),
                        config={"displayModeBar": False},
                        className="lc-card p-3",
                    ),
                    md=7,
                ),
            ], className="g-4 align-items-center"),
        ], fluid=False),

        # ── Pricing ───────────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderTop": "1px solid var(--border-color)",
                   "borderBottom": "1px solid var(--border-color)", "padding": "4rem 0"},
            children=[
                dbc.Container([
                    html.Div(className="text-center mb-4", children=[
                        html.H2("Simple, Transparent Pricing", className="section-title"),
                        html.P("Choose the plan that fits your business. No hidden fees.", className="section-subtitle"),
                        # toggle monthly/annual
                        html.Div([
                            html.Span("Monthly", style={"color": "var(--text-secondary)", "fontWeight": "600", "marginRight": "0.5rem"}),
                            dbc.Switch(id="billing-toggle", value=False, className="d-inline-block"),
                            html.Span("Annual ", style={"color": "var(--text-secondary)", "fontWeight": "600", "marginLeft": "0.5rem"}),
                            html.Span("Save 33%", className="badge-prime ms-2"),
                        ], className="d-flex align-items-center justify-content-center gap-1"),
                    ]),
                    dbc.Row([
                        dbc.Col(
                            _pricing_card("Free", "$0", "forever", FREE_FEATURES, cta="Post Free Ad"),
                            md=4, className="mb-4",
                        ),
                        dbc.Col(
                            _pricing_card("Prime", "$49.99", "per month", PRIME_FEATURES, highlighted=True, cta="★ Start Prime"),
                            md=4, className="mb-4",
                        ),
                        dbc.Col(
                            _pricing_card("Enterprise", "Custom", "contact us", ENTERPRISE_FEATURES, cta="Contact Sales"),
                            md=4, className="mb-4",
                        ),
                    ]),
                    html.P("All plans include phone & WhatsApp direct contact. Prime and Enterprise include a 14-day free trial.",
                           className="text-center text-muted-lc mt-2", style={"fontSize": "0.83rem"}),
                ], fluid=False),
            ],
        ),

        # ── Testimonials ──────────────────────────────────────────────────
        dbc.Container(className="section", children=[
            html.H2("What Prime Businesses Say", className="section-title text-center"),
            html.P("Real results from real businesses on our platform.", className="section-subtitle text-center"),
            dbc.Row([
                dbc.Col(
                    html.Div(className="lc-card p-4 h-100", children=[
                        html.Div(["⭐" * t["rating"]], style={"fontSize": "1rem", "marginBottom": "0.75rem", "color": "#ffd700"}),
                        html.P(f'"{t["text"]}"', style={"color": "var(--text-secondary)", "lineHeight": "1.7",
                                                         "fontStyle": "italic", "fontSize": "0.9rem"}),
                        html.Div(className="d-flex align-items-center gap-3 mt-3", children=[
                            html.Div(t["icon"], style={"fontSize": "2rem",
                                                        "background": "rgba(0,201,167,0.1)",
                                                        "borderRadius": "50%",
                                                        "width": "48px", "height": "48px",
                                                        "display": "flex", "alignItems": "center",
                                                        "justifyContent": "center"}),
                            html.Div([
                                html.Div(t["name"], style={"fontWeight": "700", "fontSize": "0.9rem"}),
                                html.Div(t["city"], style={"color": "var(--text-muted)", "fontSize": "0.8rem"}),
                            ]),
                            html.Span([html.I(className="fas fa-check-circle me-1"), "Prime Verified"],
                                      className="badge-verified ms-auto"),
                        ]),
                    ]),
                    md=4, className="mb-4",
                )
                for t in TESTIMONIALS
            ], className="g-4"),
        ], fluid=False),

        # ── Final CTA ─────────────────────────────────────────────────────
        html.Div(
            style={"background": "linear-gradient(135deg, #0a0800, #0d1117)",
                   "borderTop": "1px solid rgba(255,215,0,0.2)", "padding": "3rem 0", "textAlign": "center"},
            children=[
                dbc.Container([
                    html.H2("Ready to Get More Leads?", className="section-title"),
                    html.P("Start your 14-day free trial. No credit card required.",
                           className="section-subtitle"),
                    dbc.Button(
                        [html.I(className="fas fa-crown me-2"), "Start Prime Free Trial"],
                        className="btn-prime px-5 py-3",
                        style={"fontSize": "1.05rem"},
                        n_clicks=0,
                        id="prime-final-btn",
                    ),
                ], fluid=False),
            ],
        ),
    ])
