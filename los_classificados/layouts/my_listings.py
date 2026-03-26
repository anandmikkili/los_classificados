"""My Listings page – manage the logged-in user's own ads."""
import dash_bootstrap_components as dbc
from dash import html, dcc

from los_classificados.utils.mock_data import (
    MOCK_USER_LISTINGS, PLAN_PRICES, PLAN_FEATURES, time_ago,
)

# ── Plan badge helpers ────────────────────────────────────────────────────────

_PLAN_COLOR = {
    "free":        ("var(--text-muted)",   "transparent",               "1px solid var(--border-color)"),
    "featured":    ("#ff6b35",             "rgba(255,107,53,0.12)",     "1px solid rgba(255,107,53,0.4)"),
    "prime_boost": ("#ffd700",             "rgba(255,215,0,0.1)",       "1px solid rgba(255,215,0,0.4)"),
}
_PLAN_LABEL = {"free": "Free", "featured": "⚡ Featured", "prime_boost": "★ Prime"}

_STATUS_COLOR = {
    "active":  ("#10b981", "rgba(16,185,129,0.12)"),
    "paused":  ("#f59e0b", "rgba(245,158,11,0.12)"),
    "expired": ("#6b7280", "rgba(107,114,128,0.12)"),
}
_STATUS_LABEL = {"active": "Active", "paused": "Paused", "expired": "Expired"}


def _plan_badge(plan):
    color, bg, border = _PLAN_COLOR.get(plan, _PLAN_COLOR["free"])
    return html.Span(
        _PLAN_LABEL.get(plan, plan),
        style={
            "background": bg, "color": color, "border": border,
            "borderRadius": "100px", "padding": "0.1rem 0.55rem",
            "fontSize": "0.72rem", "fontWeight": "700",
        },
    )


def _status_badge(status):
    color, bg = _STATUS_COLOR.get(status, ("#6b7280", "rgba(107,114,128,0.12)"))
    return html.Span(
        _STATUS_LABEL.get(status, status).upper(),
        style={
            "background": bg, "color": color,
            "borderRadius": "100px", "padding": "0.1rem 0.55rem",
            "fontSize": "0.68rem", "fontWeight": "800", "letterSpacing": "0.05em",
        },
    )


def _listing_card(lst):
    """Management card for a single user listing."""
    status = lst["status"]
    plan   = lst["plan"]
    is_expired = status == "expired"
    is_paused  = status == "paused"

    days_left = (lst["expires_at"] - __import__("datetime").datetime.now()).days
    if is_expired:
        expiry_text = "Expired"
        expiry_color = "#6b7280"
    elif days_left <= 3:
        expiry_text = f"Expires in {days_left}d"
        expiry_color = "#ef4444"
    else:
        expiry_text = f"{days_left}d remaining"
        expiry_color = "var(--text-muted)"

    card_style = {"opacity": "0.65"} if is_expired or is_paused else {}

    return html.Div(
        className="lc-card d-flex mb-3",
        style={**card_style, "overflow": "hidden"},
        children=[
            # Thumbnail
            html.Img(
                src=lst["image"],
                style={"width": "130px", "minWidth": "130px", "objectFit": "cover"},
                alt=lst["title"],
            ),

            # Body
            html.Div(
                className="p-3 d-flex flex-column flex-grow-1",
                children=[
                    # Top row: badges + expiry
                    html.Div(
                        className="d-flex justify-content-between align-items-start mb-1",
                        children=[
                            html.Div(className="d-flex gap-1 flex-wrap", children=[
                                _status_badge(status),
                                _plan_badge(plan),
                                html.Span(lst["subcategory"], className="badge-cat"),
                            ]),
                            html.Small(expiry_text, style={"color": expiry_color,
                                                           "fontSize": "0.72rem", "whiteSpace": "nowrap"}),
                        ],
                    ),

                    html.Div(lst["title"], className="listing-title mb-1",
                             style={"fontSize": "0.95rem"}),
                    html.Small(
                        [html.I(className="fas fa-map-marker-alt me-1"), lst["city"], " · ", lst["neighborhood"]],
                        style={"color": "var(--text-muted)", "fontSize": "0.75rem"},
                    ),

                    # Stats row
                    html.Div(
                        className="d-flex gap-3 mt-2",
                        children=[
                            html.Span(
                                [html.I(className="fas fa-eye me-1"), f"{lst['views']} views"],
                                style={"fontSize": "0.78rem", "color": "var(--text-secondary)"},
                            ),
                            html.Span(
                                [html.I(className="fas fa-bolt me-1"), f"{lst['leads']} leads"],
                                style={"fontSize": "0.78rem", "color": "var(--accent-teal)"},
                            ),
                            html.Span(
                                lst["price_label"],
                                className="listing-price",
                                style={"fontSize": "0.88rem"},
                            ),
                        ],
                    ),

                    # Action buttons
                    html.Div(
                        className="d-flex gap-2 mt-auto pt-2 flex-wrap",
                        children=[
                            # Bump to top (active only, non-prime)
                            dbc.Button(
                                [html.I(className="fas fa-arrow-up me-1"), "Bump"],
                                id={"type": "bump-listing-btn", "index": lst["id"]},
                                size="sm",
                                className="btn-teal",
                                n_clicks=0,
                                style={"fontSize": "0.75rem"},
                                disabled=is_expired,
                            ) if plan != "prime_boost" else None,

                            # Upgrade CTA (free/featured only, not expired)
                            dbc.Button(
                                [html.I(className="fas fa-star me-1"),
                                 "Upgrade to Prime" if plan == "featured" else "Upgrade"],
                                id={"type": "upgrade-listing-btn", "index": lst["id"]},
                                size="sm",
                                color="warning",
                                outline=True,
                                n_clicks=0,
                                style={"fontSize": "0.75rem", "borderColor": "#ffd700",
                                       "color": "#ffd700"},
                                disabled=is_expired,
                            ) if plan != "prime_boost" else None,

                            # Pause / Resume
                            dbc.Button(
                                [html.I(className=f"fas fa-{'play' if is_paused else 'pause'} me-1"),
                                 "Resume" if is_paused else "Pause"],
                                id={"type": "toggle-listing-btn", "index": lst["id"]},
                                size="sm",
                                color="secondary",
                                outline=True,
                                n_clicks=0,
                                style={"fontSize": "0.75rem"},
                                disabled=is_expired,
                            ) if not is_expired else None,

                            # Renew (expired only)
                            dbc.Button(
                                [html.I(className="fas fa-redo me-1"), "Renew Listing"],
                                id={"type": "renew-listing-btn", "index": lst["id"]},
                                size="sm",
                                className="btn-teal",
                                n_clicks=0,
                                style={"fontSize": "0.75rem"},
                            ) if is_expired else None,
                        ],
                    ),
                ],
            ),
        ],
    )


def _plan_comparison_modal():
    """Full plan comparison modal used in the Upgrade flow."""
    rows = [
        html.Tr([
            html.Th("Feature",   style={"width": "30%", "padding": "0.4rem 0.6rem",
                                        "borderBottom": "1px solid var(--border-color)",
                                        "color": "var(--text-muted)", "fontWeight": "600"}),
            html.Th("Free",      style={"padding": "0.4rem 0.6rem",
                                        "borderBottom": "1px solid var(--border-color)",
                                        "color": "var(--text-secondary)", "textAlign": "center"}),
            html.Th([html.I(className="fas fa-bolt me-1", style={"color": "#ff6b35"}), "Featured"],
                    style={"padding": "0.4rem 0.6rem", "color": "#ff6b35",
                           "borderBottom": "1px solid var(--border-color)",
                           "fontWeight": "700", "textAlign": "center"}),
            html.Th([html.I(className="fas fa-star me-1", style={"color": "#ffd700"}), "Prime"],
                    style={"padding": "0.4rem 0.6rem", "color": "#ffd700",
                           "borderBottom": "1px solid var(--border-color)",
                           "fontWeight": "700", "textAlign": "center"}),
        ])
    ] + [
        html.Tr([
            html.Td(PLAN_FEATURES["free"][i][0],
                    style={"padding": "0.35rem 0.6rem", "color": "var(--text-muted)",
                           "borderBottom": "1px solid var(--border-color)", "fontSize": "0.82rem"}),
            html.Td(PLAN_FEATURES["free"][i][1],
                    style={"padding": "0.35rem 0.6rem", "textAlign": "center", "fontSize": "0.82rem",
                           "color": "var(--text-secondary)", "borderBottom": "1px solid var(--border-color)"}),
            html.Td(PLAN_FEATURES["featured"][i][1],
                    style={"padding": "0.35rem 0.6rem", "textAlign": "center", "fontSize": "0.82rem",
                           "color": "var(--text-secondary)", "borderBottom": "1px solid var(--border-color)"}),
            html.Td(PLAN_FEATURES["prime_boost"][i][1],
                    style={"padding": "0.35rem 0.6rem", "textAlign": "center", "fontSize": "0.82rem",
                           "color": "var(--text-secondary)", "borderBottom": "1px solid var(--border-color)"}),
        ])
        for i in range(len(PLAN_FEATURES["free"]))
    ]

    price_row = html.Tr([
        html.Td("Price", style={"padding": "0.4rem 0.6rem", "fontWeight": "700",
                                "color": "var(--text-primary)", "fontSize": "0.88rem"}),
        html.Td("Free", style={"padding": "0.4rem 0.6rem", "textAlign": "center",
                               "fontWeight": "700", "fontSize": "0.88rem",
                               "color": "var(--text-secondary)"}),
        html.Td("from $4.99", style={"padding": "0.4rem 0.6rem", "textAlign": "center",
                                     "fontWeight": "700", "fontSize": "0.88rem", "color": "#ff6b35"}),
        html.Td("$9.99 / listing", style={"padding": "0.4rem 0.6rem", "textAlign": "center",
                                          "fontWeight": "700", "fontSize": "0.88rem", "color": "#ffd700"}),
    ])

    return dbc.Modal(
        id="upgrade-modal",
        size="lg",
        is_open=False,
        children=[
            dbc.ModalHeader(
                dbc.ModalTitle([
                    html.I(className="fas fa-arrow-up me-2", style={"color": "#ffd700"}),
                    "Upgrade Your Listing",
                ]),
            ),
            dbc.ModalBody([
                # Hidden store for which listing is being upgraded
                dcc.Store(id="upgrade-listing-id-store", data=None),

                html.P(
                    "Choose a plan to boost your listing's visibility and reach more buyers.",
                    style={"color": "var(--text-secondary)", "fontSize": "0.9rem", "marginBottom": "1.25rem"},
                ),

                # Plan selector
                dbc.RadioItems(
                    id="upgrade-plan-select",
                    options=[
                        {
                            "label": html.Div([
                                html.Span("⚡ Featured Placement  ",
                                          style={"fontWeight": "700", "color": "#ff6b35"}),
                                html.Span("from $4.99",
                                          style={"background": "rgba(255,107,53,0.15)", "color": "#ff6b35",
                                                 "border": "1px solid rgba(255,107,53,0.4)",
                                                 "fontWeight": "700", "padding": "0.1rem 0.45rem",
                                                 "borderRadius": "100px", "fontSize": "0.72rem"}),
                                html.Div("Pinned above all regular listings · ⚡ badge · 10 photos",
                                         style={"fontSize": "0.78rem", "color": "var(--text-muted)",
                                                "marginTop": "0.15rem"}),
                            ]),
                            "value": "featured",
                        },
                        {
                            "label": html.Div([
                                html.Span("★ Prime Boost  ",
                                          style={"fontWeight": "700", "color": "#ffd700"}),
                                html.Span("$9.99 / listing",
                                          style={"background": "rgba(255,215,0,0.1)", "color": "#ffd700",
                                                 "border": "1px solid rgba(255,215,0,0.4)",
                                                 "fontWeight": "700", "padding": "0.1rem 0.45rem",
                                                 "borderRadius": "100px", "fontSize": "0.72rem"}),
                                html.Div("Top of results · ★ Prime + ⚡ Featured · 20 photos · Geo-targeting",
                                         style={"fontSize": "0.78rem", "color": "var(--text-muted)",
                                                "marginTop": "0.15rem"}),
                            ]),
                            "value": "prime_boost",
                        },
                    ],
                    value="featured",
                    className="mb-3",
                    input_style={"accentColor": "var(--accent-teal)"},
                    label_style={"color": "var(--text-primary)", "marginBottom": "0.6rem"},
                ),

                html.Hr(className="divider"),

                # Comparison table
                html.Div(className="table-responsive", children=[
                    html.Table(
                        className="w-100",
                        style={"fontSize": "0.8rem", "borderCollapse": "collapse"},
                        children=[html.Thead(html.Tr(rows[:1][0].children)), html.Tbody(rows[1:] + [price_row])],
                    )
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="upgrade-cancel-btn", color="secondary", outline=True, className="me-2"),
                dbc.Button(
                    [html.I(className="fas fa-arrow-up me-1"), "Confirm Upgrade"],
                    id="upgrade-confirm-btn",
                    className="btn-teal",
                    n_clicks=0,
                ),
                html.Div(id="upgrade-confirm-alert", className="w-100 mt-2"),
            ]),
        ],
    )


def my_listings_layout():
    """Full My Listings page layout."""

    # KPI bar totals across all user listings
    total_views = sum(l["views"] for l in MOCK_USER_LISTINGS)
    total_leads = sum(l["leads"] for l in MOCK_USER_LISTINGS)
    active_count = sum(1 for l in MOCK_USER_LISTINGS if l["status"] == "active")
    paid_count   = sum(1 for l in MOCK_USER_LISTINGS if l["plan"] != "free")

    def _kpi(value, label, icon, color="var(--accent-teal)"):
        return html.Div(
            className="lc-card p-3 text-center",
            style={"minWidth": "110px"},
            children=[
                html.I(className=f"fas {icon} fa-lg mb-1", style={"color": color}),
                html.Div(str(value), style={"fontWeight": "800", "fontSize": "1.4rem", "color": color}),
                html.Div(label, style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
            ],
        )

    return html.Div([
        # ── Page header ───────────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderBottom": "1px solid var(--border-color)",
                   "padding": "1.5rem 0"},
            children=[
                dbc.Container([
                    html.Div(className="d-flex justify-content-between align-items-center", children=[
                        html.Div([
                            html.H3([
                                html.I(className="fas fa-list-alt me-2", style={"color": "var(--accent-teal)"}),
                                "My Listings",
                            ], style={"fontWeight": "800", "marginBottom": "0.2rem"}),
                            html.P("Manage, upgrade, and track all your classified ads.",
                                   style={"color": "var(--text-secondary)", "marginBottom": "0",
                                          "fontSize": "0.9rem"}),
                        ]),
                        dcc.Link(
                            [html.I(className="fas fa-plus me-1"), "Post New Ad"],
                            href="/post-ad",
                            className="btn btn-teal px-3 py-2",
                            style={"textDecoration": "none", "fontSize": "0.875rem"},
                        ),
                    ]),
                ], fluid=False),
            ],
        ),

        dbc.Container(className="py-4", children=[
            # ── KPI bar ───────────────────────────────────────────────────────
            html.Div(
                className="d-flex gap-3 flex-wrap mb-4",
                children=[
                    _kpi(len(MOCK_USER_LISTINGS), "Total Listings", "fa-clipboard-list"),
                    _kpi(active_count, "Active",        "fa-circle-check", "#10b981"),
                    _kpi(total_views,  "Total Views",   "fa-eye",          "var(--accent-teal)"),
                    _kpi(total_leads,  "Total Leads",   "fa-bolt",         "#ffd700"),
                    _kpi(paid_count,   "Paid Plans",    "fa-star",         "#ff6b35"),
                ],
            ),

            dbc.Row([
                # ── Listings column ───────────────────────────────────────────
                dbc.Col([
                    # Filter / sort bar
                    html.Div(
                        className="d-flex gap-2 align-items-center mb-3 flex-wrap",
                        children=[
                            dcc.Dropdown(
                                id="my-listings-status-filter",
                                options=[
                                    {"label": "All Statuses", "value": ""},
                                    {"label": "Active",       "value": "active"},
                                    {"label": "Paused",       "value": "paused"},
                                    {"label": "Expired",      "value": "expired"},
                                ],
                                value="",
                                clearable=False,
                                style={"width": "155px", "fontSize": "0.82rem"},
                                className="bg-input",
                            ),
                            dcc.Dropdown(
                                id="my-listings-plan-filter",
                                options=[
                                    {"label": "All Plans",    "value": ""},
                                    {"label": "Free",         "value": "free"},
                                    {"label": "⚡ Featured",  "value": "featured"},
                                    {"label": "★ Prime",      "value": "prime_boost"},
                                ],
                                value="",
                                clearable=False,
                                style={"width": "150px", "fontSize": "0.82rem"},
                                className="bg-input",
                            ),
                            dcc.Dropdown(
                                id="my-listings-sort",
                                options=[
                                    {"label": "Newest First", "value": "newest"},
                                    {"label": "Most Views",   "value": "views"},
                                    {"label": "Most Leads",   "value": "leads"},
                                    {"label": "Expiring Soon","value": "expiry"},
                                ],
                                value="newest",
                                clearable=False,
                                style={"width": "160px", "fontSize": "0.82rem"},
                                className="bg-input",
                            ),
                            html.Span(id="my-listings-count",
                                      style={"fontSize": "0.82rem", "color": "var(--text-muted)",
                                             "marginLeft": "auto"}),
                        ],
                    ),

                    # Listings managed via store + overrides
                    dcc.Store(id="my-listings-overrides", data={}),
                    html.Div(
                        id="my-listings-container",
                        children=[_listing_card(l) for l in MOCK_USER_LISTINGS],
                    ),

                ], md=8),

                # ── Right sidebar ─────────────────────────────────────────────
                dbc.Col([
                    # Upgrade CTA card
                    html.Div(
                        className="lc-card p-4 mb-3",
                        style={"border": "1.5px solid rgba(255,215,0,0.3)",
                               "background": "linear-gradient(135deg, rgba(255,215,0,0.05) 0%, transparent 100%)"},
                        children=[
                            html.Div([
                                html.I(className="fas fa-star me-2", style={"color": "#ffd700"}),
                                html.Strong("Go Prime"),
                            ], style={"fontSize": "1rem", "fontWeight": "800", "marginBottom": "0.5rem"}),
                            html.P(
                                "Prime listings get 3× more views, appear at the top of search results, "
                                "and unlock geo-targeting to reach buyers in specific neighborhoods.",
                                style={"fontSize": "0.82rem", "color": "var(--text-secondary)",
                                       "marginBottom": "0.75rem"},
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-arrow-up me-1"), "Upgrade a Listing"],
                                id="sidebar-upgrade-btn",
                                className="btn-teal w-100",
                                size="sm",
                                n_clicks=0,
                                style={"fontSize": "0.82rem"},
                            ),
                        ],
                    ),

                    # Tips card
                    html.Div(
                        className="lc-card p-4",
                        children=[
                            html.Div([
                                html.I(className="fas fa-lightbulb me-2",
                                       style={"color": "var(--accent-teal)"}),
                                html.Strong("Tips to Sell Faster"),
                            ], style={"fontSize": "0.9rem", "marginBottom": "0.75rem"}),
                            html.Ul([
                                html.Li("Add photos — listings with images get 3× more clicks.",
                                        style={"fontSize": "0.78rem", "color": "var(--text-secondary)",
                                               "marginBottom": "0.4rem"}),
                                html.Li("Bump free listings every 48 h to stay near the top.",
                                        style={"fontSize": "0.78rem", "color": "var(--text-secondary)",
                                               "marginBottom": "0.4rem"}),
                                html.Li("Use Featured or Prime before weekends — peak browse traffic.",
                                        style={"fontSize": "0.78rem", "color": "var(--text-secondary)",
                                               "marginBottom": "0.4rem"}),
                                html.Li("Respond to leads within 1 hour for 5× higher close rate.",
                                        style={"fontSize": "0.78rem", "color": "var(--text-secondary)"}),
                            ], style={"paddingLeft": "1.1rem", "marginBottom": "0"}),
                        ],
                    ),
                ], md=4),
            ]),

            # Action feedback toast
            dbc.Toast(
                id="my-listings-toast",
                header="",
                is_open=False,
                dismissable=True,
                duration=3500,
                style={"position": "fixed", "bottom": "1.5rem", "right": "1.5rem",
                       "minWidth": "280px", "zIndex": "9999",
                       "background": "var(--bg-secondary)",
                       "border": "1px solid var(--border-color)"},
            ),
        ], fluid=False),

        # Upgrade modal (portal-rendered once at page level)
        _plan_comparison_modal(),
    ])
