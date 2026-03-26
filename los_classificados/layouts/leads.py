"""Leads Management Dashboard layout – Prime business feature."""
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go

from los_classificados.utils.mock_data import MOCK_LEADS, LEAD_STATUS_LABELS


# ── Helpers ─────────────────────────────────────────────────────────────────

def _kpi_card(value, label, change, change_up=True, icon="fa-chart-line", color="#00c9a7"):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-start mb-2",
                children=[
                    html.Div(
                        html.I(className=f"fas {icon}"),
                        style={
                            "width": "40px", "height": "40px", "borderRadius": "10px",
                            "background": f"{color}1a", "color": color,
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "fontSize": "1.1rem",
                        },
                    ),
                    html.Span(
                        [html.I(className=f"fas fa-arrow-{'up' if change_up else 'down'} me-1"), change],
                        className=f"kpi-change {'up' if change_up else 'down'}",
                    ),
                ],
            ),
            html.Div(value, className="kpi-value", style={"color": color}),
            html.Div(label, className="kpi-label"),
        ],
    )


def _lead_row(lead):
    st = LEAD_STATUS_LABELS.get(lead["status"], {"label": lead["status"], "color": "#6e7681"})
    method_icon = {
        "whatsapp": ("fab fa-whatsapp", "#25d366"),
        "call":     ("fas fa-phone",    "#3b82f6"),
        "email":    ("fas fa-envelope", "#f59e0b"),
    }.get(lead["contact_method"], ("fas fa-question", "#6e7681"))

    return html.Div(
        className="lead-row",
        id={"type": "lead-row", "index": lead["id"]},
        children=[
            # Contact method icon
            html.Div(
                html.I(className=f"{method_icon[0]}"),
                style={
                    "width": "36px", "height": "36px", "borderRadius": "50%",
                    "background": f"{method_icon[1]}18", "color": method_icon[1],
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "flexShrink": "0", "fontSize": "1rem",
                },
            ),
            # Name + message
            html.Div(
                className="flex-grow-1",
                style={"minWidth": "0"},
                children=[
                    html.Div(
                        className="d-flex align-items-center gap-2 mb-1",
                        children=[
                            html.Span(lead["requester_name"], style={"fontWeight": "700", "fontSize": "0.9rem"}),
                            html.Span(
                                [html.I(className="fas fa-map-marker-alt me-1"), lead["city"]],
                                style={"fontSize": "0.75rem", "color": "var(--text-muted)"},
                            ),
                        ],
                    ),
                    html.Div(
                        lead["message"][:100] + ("…" if len(lead["message"]) > 100 else ""),
                        style={"fontSize": "0.8rem", "color": "var(--text-secondary)",
                               "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"},
                    ),
                    html.Div(
                        lead["listing_title"],
                        style={"fontSize": "0.72rem", "color": "var(--text-muted)", "marginTop": "0.2rem"},
                    ),
                ],
            ),
            # Status badge + actions
            html.Div(
                className="d-flex flex-column align-items-end gap-2",
                style={"flexShrink": "0"},
                children=[
                    html.Span(
                        st["label"],
                        style={
                            "fontSize": "0.7rem", "fontWeight": "700",
                            "padding": "0.2rem 0.65rem", "borderRadius": "100px",
                            "background": f"{st['color']}18", "color": st["color"],
                            "border": f"1px solid {st['color']}40",
                        },
                    ),
                    dcc.Dropdown(
                        id={"type": "lead-status-select", "index": lead["id"]},
                        options=[
                            {"label": v["label"], "value": k}
                            for k, v in LEAD_STATUS_LABELS.items()
                        ],
                        value=lead["status"],
                        clearable=False,
                        style={"width": "130px", "fontSize": "0.75rem"},
                        className="bg-input",
                    ),
                ],
            ),
            # Contact buttons
            html.Div(
                className="d-flex gap-1 ms-2",
                children=[
                    html.A(
                        html.I(className="fab fa-whatsapp"),
                        href=f"https://wa.me/{lead['requester_phone'].replace('+','')}",
                        target="_blank",
                        className="btn btn-sm btn-whatsapp px-2 py-1",
                        title="WhatsApp",
                        style={"fontSize": "0.9rem"},
                    ),
                    html.A(
                        html.I(className="fas fa-phone"),
                        href=f"tel:{lead['requester_phone']}",
                        className="btn btn-sm btn-call px-2 py-1",
                        title="Call",
                        style={"fontSize": "0.9rem"},
                    ),
                    html.A(
                        html.I(className="fas fa-envelope"),
                        href=f"mailto:{lead['requester_email']}",
                        className="btn btn-sm btn-outline-teal px-2 py-1",
                        title="Email",
                        style={"fontSize": "0.9rem"},
                    ),
                ],
            ),
        ],
    )


def _pipeline_chart():
    statuses = list(LEAD_STATUS_LABELS.keys())
    counts   = [sum(1 for l in MOCK_LEADS if l["status"] == s) for s in statuses]
    colors   = [LEAD_STATUS_LABELS[s]["color"] for s in statuses]
    labels   = [LEAD_STATUS_LABELS[s]["label"] for s in statuses]

    fig = go.Figure(go.Funnel(
        y=labels,
        x=counts,
        textinfo="value+percent initial",
        marker={"color": colors},
        connector={"line": {"color": "rgba(255,255,255,0.05)", "width": 2}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter"},
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=220,
        showlegend=False,
    )
    return fig


def _weekly_leads_chart():
    weeks  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = [3, 7, 5, 9, 6, 4, 2]

    fig = go.Figure(go.Bar(
        x=weeks,
        y=counts,
        marker_color=["#00c9a7" if c == max(counts) else "#21262d" for c in counts],
        marker_line_width=0,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter"},
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        height=160,
        xaxis={"gridcolor": "rgba(0,0,0,0)", "showline": False, "zeroline": False},
        yaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False},
        bargap=0.3,
    )
    return fig


# ── Main Layout ──────────────────────────────────────────────────────────────

def leads_layout():
    total   = len(MOCK_LEADS)
    new_cnt = sum(1 for l in MOCK_LEADS if l["status"] == "new")
    won_cnt = sum(1 for l in MOCK_LEADS if l["status"] == "closed_won")

    return html.Div([

        # ── Page header ───────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderBottom": "1px solid var(--border-color)",
                   "padding": "1.5rem 0"},
            children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H2([
                                html.I(className="fas fa-chart-line me-2 text-teal"),
                                "Lead Management",
                            ], style={"fontWeight": "800"}),
                            html.P("Track, qualify and respond to your incoming customer leads.",
                                   className="text-secondary-lc mb-0"),
                        ], md=8),
                        dbc.Col([
                            html.Div([
                                html.Span("★ Prime", className="badge-prime me-2"),
                                html.Span("Business Dashboard",
                                          style={"fontSize": "0.82rem", "color": "var(--text-muted)"}),
                            ], className="d-flex align-items-center justify-content-end mt-2"),
                        ], md=4),
                    ]),
                ], fluid=False),
            ],
        ),

        dbc.Container(className="py-4", children=[

            # ── KPI Row ───────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(_kpi_card(str(total),   "Total Leads",      "+12% this week",  True,  "fa-users",       "#00c9a7"), xs=6, md=3, className="mb-3"),
                dbc.Col(_kpi_card(str(new_cnt), "New Leads",        "+5 today",         True,  "fa-bell",        "#3b82f6"), xs=6, md=3, className="mb-3"),
                dbc.Col(_kpi_card(str(won_cnt), "Deals Closed",     "+2 this week",     True,  "fa-handshake",   "#2ea44f"), xs=6, md=3, className="mb-3"),
                dbc.Col(_kpi_card("72%",        "Response Rate",    "-3% this week",    False, "fa-reply",       "#ffd700"), xs=6, md=3, className="mb-3"),
            ], className="g-3 mb-2"),

            # ── Charts Row ────────────────────────────────────────────────
            dbc.Row([
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Lead Pipeline", className="filter-title mb-2"),
                        dcc.Graph(
                            figure=_pipeline_chart(),
                            config={"displayModeBar": False},
                        ),
                    ]),
                    md=5, className="mb-3",
                ),
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Leads This Week", className="filter-title mb-2"),
                        dcc.Graph(
                            figure=_weekly_leads_chart(),
                            config={"displayModeBar": False},
                        ),
                    ]),
                    md=7, className="mb-3",
                ),
            ], className="g-3 mb-2"),

            # ── Filters + Lead List ───────────────────────────────────────
            dbc.Row([
                dbc.Col([
                    # Filter bar
                    html.Div(
                        className="d-flex flex-wrap align-items-center gap-2 mb-3",
                        children=[
                            html.Span("Filter:", style={"fontSize": "0.82rem", "color": "var(--text-muted)", "fontWeight": "600"}),
                            dcc.Dropdown(
                                id="leads-status-filter",
                                options=[{"label": "All Statuses", "value": "all"}] + [
                                    {"label": v["label"], "value": k}
                                    for k, v in LEAD_STATUS_LABELS.items()
                                ],
                                value="all",
                                clearable=False,
                                style={"width": "160px", "fontSize": "0.82rem"},
                                className="bg-input",
                            ),
                            dcc.Dropdown(
                                id="leads-method-filter",
                                options=[
                                    {"label": "All Methods", "value": "all"},
                                    {"label": "WhatsApp",    "value": "whatsapp"},
                                    {"label": "Phone Call",  "value": "call"},
                                    {"label": "Email",       "value": "email"},
                                ],
                                value="all",
                                clearable=False,
                                style={"width": "150px", "fontSize": "0.82rem"},
                                className="bg-input",
                            ),
                            dcc.Dropdown(
                                id="leads-sort",
                                options=[
                                    {"label": "Newest First",   "value": "newest"},
                                    {"label": "Oldest First",   "value": "oldest"},
                                    {"label": "By Status",      "value": "status"},
                                ],
                                value="newest",
                                clearable=False,
                                style={"width": "150px", "fontSize": "0.82rem"},
                                className="bg-input ms-auto",
                            ),
                        ],
                    ),

                    # Result count
                    html.Div(id="leads-count", className="text-muted-lc mb-2",
                             style={"fontSize": "0.82rem"}),

                    # Lead rows
                    html.Div(id="leads-list-container",
                             children=[_lead_row(l) for l in MOCK_LEADS]),

                    # Alert area for status updates
                    html.Div(id="leads-alert", className="mt-2"),

                ], md=12),
            ]),

        ], fluid=False),
    ])
