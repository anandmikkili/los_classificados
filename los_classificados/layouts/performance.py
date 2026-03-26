"""Lead Generation & Performance Tools – 4-tab hub at /performance."""
from datetime import datetime

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from los_classificados.utils.mock_data import (
    MOCK_VERIFIED_LEADS, LEAD_QUALITY_LABELS, LEAD_STATUS_LABELS,
    RESPONSE_PACKAGES, SLA_COMPLIANCE,
    MOCK_SEO_SCORES, MOCK_PPC_CAMPAIGNS, PERFORMANCE_ANALYTICS,
)

# ── Constants ─────────────────────────────────────────────────────────────────

_TABS = [
    ("leads",    "fa-bolt",         "Lead Generation"),
    ("response", "fa-clock",        "Guaranteed Response"),
    ("seo",      "fa-search",       "SEO & Visibility"),
    ("ppc",      "fa-ad",           "PPC Campaigns"),
]

_SOURCE_LABELS = {
    "organic":  ("Organic", "#3b82f6"),
    "featured": ("Featured", "#ff6b35"),
    "prime":    ("Prime",    "#ffd700"),
    "ppc":      ("PPC",      "#a855f7"),
}

_STATUS_COLOR_MAP = {
    s: d["color"] for s, d in LEAD_STATUS_LABELS.items()
}


# ── Shared helpers ────────────────────────────────────────────────────────────

def _section_hdr(icon, title, subtitle=None):
    return html.Div(
        className="mb-3",
        children=[
            html.Div(className="d-flex align-items-center gap-2", children=[
                html.I(className=f"fas {icon}",
                       style={"color": "var(--accent-teal)", "fontSize": "1rem"}),
                html.Span(title,
                          style={"fontWeight": "800", "fontSize": "1.05rem"}),
            ]),
            html.Small(subtitle, style={"color": "var(--text-muted)", "fontSize": "0.78rem"})
            if subtitle else None,
        ],
    )


def _kpi_card(value, label, icon, color="var(--accent-teal)", delta=None, suffix=""):
    return html.Div(
        className="lc-card p-3 h-100",
        children=[
            html.Div(className="d-flex justify-content-between align-items-start mb-2", children=[
                html.Div(
                    html.I(className=f"fas {icon}"),
                    style={"width": "36px", "height": "36px", "borderRadius": "8px",
                           "background": f"{color}1a", "color": color,
                           "display": "flex", "alignItems": "center",
                           "justifyContent": "center", "fontSize": "1rem"},
                ),
                html.Span(delta, style={"fontSize": "0.72rem", "color": "#10b981",
                                         "fontWeight": "700"}) if delta else None,
            ]),
            html.Div(f"{value}{suffix}",
                     style={"fontWeight": "800", "fontSize": "1.5rem", "color": color}),
            html.Div(label,
                     style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
        ],
    )


def _quality_badge(tier):
    q = LEAD_QUALITY_LABELS.get(tier, LEAD_QUALITY_LABELS["cold"])
    return html.Span(
        [html.I(className=f"fas {q['icon']} me-1", style={"fontSize": "0.65rem"}), q["label"]],
        style={"background": q["bg"], "color": q["color"],
               "borderRadius": "100px", "padding": "0.1rem 0.55rem",
               "fontSize": "0.7rem", "fontWeight": "700"},
    )


def _verified_badge(is_verified):
    if is_verified:
        return html.Span(
            [html.I(className="fas fa-check-shield me-1", style={"fontSize": "0.65rem"}), "Verified"],
            style={"background": "rgba(16,185,129,0.12)", "color": "#10b981",
                   "borderRadius": "100px", "padding": "0.1rem 0.55rem",
                   "fontSize": "0.7rem", "fontWeight": "700"},
        )
    return html.Span(
        "Unverified",
        style={"background": "rgba(107,114,128,0.1)", "color": "#6b7280",
               "borderRadius": "100px", "padding": "0.1rem 0.55rem",
               "fontSize": "0.7rem"},
    )


def _source_badge(source):
    label, color = _SOURCE_LABELS.get(source, ("Unknown", "#6b7280"))
    return html.Span(
        label,
        style={"background": f"{color}18", "color": color, "border": f"1px solid {color}40",
               "borderRadius": "100px", "padding": "0.1rem 0.5rem", "fontSize": "0.68rem",
               "fontWeight": "600"},
    )


# ── Tab 1: Lead Generation ────────────────────────────────────────────────────

def _quality_funnel_chart():
    funnel = PERFORMANCE_ANALYTICS["funnel"]
    stages = ["Impressions", "Clicks", "Listing Views", "Leads", "Conversions"]
    values = [funnel["impressions"], funnel["clicks"], funnel["views"],
              funnel["leads"], funnel["conversions"]]
    fig = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        marker={"color": ["#00c9a7", "#3b82f6", "#a855f7", "#f59e0b", "#ef4444"]},
        connector={"line": {"color": "rgba(255,255,255,0.1)", "width": 1}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 11},
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=240,
    )
    return fig


def _lead_source_chart():
    sources = PERFORMANCE_ANALYTICS["lead_sources_30d"]
    colors = ["#00c9a7", "#ff6b35", "#ffd700", "#a855f7"]
    fig = go.Figure(go.Pie(
        labels=list(sources.keys()),
        values=list(sources.values()),
        hole=0.65,
        marker={"colors": colors, "line": {"color": "rgba(0,0,0,0)", "width": 0}},
        textinfo="none",
        hovertemplate="%{label}: %{value} leads (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 10},
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=180,
        showlegend=True,
        legend={"orientation": "v", "font": {"size": 10}},
    )
    return fig


def _lead_row(lead):
    q   = LEAD_QUALITY_LABELS.get(lead["quality_tier"], LEAD_QUALITY_LABELS["cold"])
    st  = LEAD_STATUS_LABELS.get(lead["status"],  {"label": lead["status"], "color": "#6b7280"})
    cm_icon = {"whatsapp": "fab fa-whatsapp", "call": "fas fa-phone", "email": "fas fa-envelope"}.get(
        lead["contact_method"], "fas fa-comment"
    )
    cm_color = {"whatsapp": "#25d366", "call": "#3b82f6", "email": "#f59e0b"}.get(
        lead["contact_method"], "#6b7280"
    )
    resp_text = (
        f"{lead['response_time_hrs']:.1f}h response"
        if lead.get("response_time_hrs") is not None
        else "Awaiting response"
    )
    value_text = (
        f"~${lead['estimated_value']:,}" if lead.get("estimated_value") else ""
    )
    score_color = q["color"]

    return html.Div(
        className="lc-card p-3 mb-2",
        children=[
            html.Div(className="d-flex align-items-start gap-3", children=[
                # Score circle
                html.Div(
                    str(lead["quality_score"]),
                    style={
                        "minWidth": "42px", "height": "42px", "borderRadius": "50%",
                        "background": q["bg"], "color": score_color,
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "fontWeight": "800", "fontSize": "0.85rem", "flexShrink": "0",
                        "border": f"2px solid {score_color}40",
                    },
                ),
                # Main body
                html.Div(className="flex-grow-1 min-w-0", children=[
                    html.Div(className="d-flex align-items-center flex-wrap gap-1 mb-1", children=[
                        html.Span(lead["requester_name"],
                                  style={"fontWeight": "700", "fontSize": "0.9rem"}),
                        _quality_badge(lead["quality_tier"]),
                        _verified_badge(lead["is_verified"]),
                        _source_badge(lead["lead_source"]),
                        html.Span(
                            [html.I(className="fas fa-map-marker-alt me-1",
                                    style={"fontSize": "0.65rem"}), lead["city"]],
                            style={"fontSize": "0.75rem", "color": "var(--text-muted)"},
                        ),
                    ]),
                    html.Div(
                        lead["message"][:110] + "…" if len(lead["message"]) > 110 else lead["message"],
                        style={"fontSize": "0.82rem", "color": "var(--text-secondary)",
                               "marginBottom": "4px"},
                    ),
                    html.Div(className="d-flex align-items-center flex-wrap gap-2", children=[
                        html.Small(lead["listing_title"],
                                   style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                        html.Span("·", style={"color": "var(--text-muted)"}),
                        html.Small(resp_text,
                                   style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                    ]),
                ]),
                # Right side
                html.Div(className="d-flex flex-column align-items-end gap-1 flex-shrink-0", children=[
                    html.Span(
                        st["label"].upper(),
                        style={"background": f"{st['color']}18", "color": st["color"],
                               "borderRadius": "100px", "padding": "0.1rem 0.55rem",
                               "fontSize": "0.68rem", "fontWeight": "800"},
                    ),
                    html.Div(
                        [html.I(className=f"{cm_icon} me-1", style={"color": cm_color}),
                         html.Span(value_text, style={"fontWeight": "700",
                                                       "color": "var(--accent-teal)",
                                                       "fontSize": "0.82rem"})],
                        style={"fontSize": "0.75rem"},
                    ),
                    html.Small(
                        lead["created_at"].strftime("%b %d, %H:%M"),
                        style={"color": "var(--text-muted)", "fontSize": "0.7rem"},
                    ),
                ]),
            ]),
        ],
    )


def _tab_leads():
    pa   = PERFORMANCE_ANALYTICS
    total_leads = len(MOCK_VERIFIED_LEADS)
    hot_leads   = sum(1 for l in MOCK_VERIFIED_LEADS if l["quality_tier"] == "hot")
    verified    = sum(1 for l in MOCK_VERIFIED_LEADS if l["is_verified"])
    avg_val     = pa["avg_lead_value"]
    pipeline_val = sum(l["estimated_value"] for l in MOCK_VERIFIED_LEADS
                       if l.get("estimated_value") and l["status"] != "closed_lost")

    return html.Div(
        id="perf-panel-leads",
        children=[
            html.H4("Lead Generation", style={"fontWeight": "800", "marginBottom": "1.5rem"}),

            # KPI row
            dbc.Row([
                dbc.Col(_kpi_card(total_leads,    "Total Leads (30d)",  "fa-bolt",
                                  delta="+3 this week"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(hot_leads,       "Hot Leads",          "fa-fire",    "#ef4444",
                                  delta=f"{hot_leads/total_leads*100:.0f}% of total"),
                        xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(f"{verified}",  "Verified Leads",     "fa-shield-halved", "#10b981",
                                  delta=f"{verified/total_leads*100:.0f}% verified"),
                        xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(f"${avg_val:,.0f}", "Avg. Lead Value", "fa-dollar-sign", "#ffd700"),
                        xs=6, lg=3, className="mb-3"),
            ], className="g-3 mb-4"),

            # Charts row
            dbc.Row([
                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-filter", "Conversion Funnel",
                                 "Impressions through to closed deals"),
                    dcc.Graph(figure=_quality_funnel_chart(),
                              config={"displayModeBar": False}),
                ]), md=5, className="mb-3"),

                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-chart-pie", "Lead Sources (30d)"),
                    dcc.Graph(figure=_lead_source_chart(),
                              config={"displayModeBar": False}),
                    # Geographic breakdown
                    html.Hr(style={"borderColor": "var(--border-color)", "margin": "12px 0"}),
                    _section_hdr("fa-map-marker-alt", "Leads by City"),
                    html.Div([
                        html.Div(
                            className="d-flex align-items-center justify-content-between mb-1",
                            children=[
                                html.Span(row["city"],
                                          style={"fontSize": "0.8rem", "fontWeight": "600",
                                                 "minWidth": "80px"}),
                                html.Div(style={"flex": "1", "margin": "0 8px"}, children=[
                                    dbc.Progress(
                                        value=row["leads"] / 9 * 100,
                                        style={"height": "6px", "borderRadius": "3px"},
                                        color="info",
                                    ),
                                ]),
                                html.Span(f"{row['leads']}",
                                          style={"fontSize": "0.78rem", "fontWeight": "700",
                                                 "color": "var(--accent-teal)", "minWidth": "20px",
                                                 "textAlign": "right"}),
                                html.Span(f"{row['conv_rate']:.0f}%",
                                          style={"fontSize": "0.7rem",
                                                 "color": "var(--text-muted)", "minWidth": "36px",
                                                 "textAlign": "right"}),
                            ],
                        )
                        for row in PERFORMANCE_ANALYTICS["geographic_leads"]
                    ]),
                ]), md=7, className="mb-3"),
            ], className="g-3 mb-3"),

            # Lead list
            html.Div(className="lc-card p-3", children=[
                html.Div(className="d-flex align-items-center justify-content-between mb-3",
                         children=[
                    _section_hdr("fa-list", "Verified Lead Inbox",
                                 "Leads ranked by quality score"),
                    html.Div(className="d-flex gap-2", children=[
                        dcc.Dropdown(
                            id="perf-quality-filter",
                            options=[
                                {"label": "All Quality", "value": "all"},
                                {"label": "Hot",         "value": "hot"},
                                {"label": "Warm",        "value": "warm"},
                                {"label": "Cold",        "value": "cold"},
                            ],
                            value="all", clearable=False,
                            style={"width": "130px", "fontSize": "0.8rem"},
                        ),
                        dcc.Dropdown(
                            id="perf-source-filter",
                            options=[
                                {"label": "All Sources",     "value": "all"},
                                {"label": "Organic Search",  "value": "organic"},
                                {"label": "Featured",        "value": "featured"},
                                {"label": "Prime Boost",     "value": "prime"},
                                {"label": "PPC Campaign",    "value": "ppc"},
                            ],
                            value="all", clearable=False,
                            style={"width": "150px", "fontSize": "0.8rem"},
                        ),
                    ]),
                ]),
                html.Div(
                    className="d-flex justify-content-between align-items-center mb-2",
                    children=[
                        html.Small(id="perf-lead-count",
                                   style={"color": "var(--text-muted)", "fontSize": "0.78rem"}),
                        html.Span(
                            [html.I(className="fas fa-dollar-sign me-1"),
                             f"Pipeline value: ${pipeline_val:,.0f}"],
                            style={"fontSize": "0.82rem", "color": "var(--accent-teal)",
                                   "fontWeight": "700"},
                        ),
                    ],
                ),
                html.Div(id="perf-leads-container",
                         children=[_lead_row(l) for l in sorted(
                             MOCK_VERIFIED_LEADS, key=lambda x: x["quality_score"], reverse=True
                         )]),
            ]),
        ],
    )


# ── Tab 2: Guaranteed Response ────────────────────────────────────────────────

def _response_time_chart():
    times = SLA_COMPLIANCE["daily_response_times"]
    current_pkg = next((p for p in RESPONSE_PACKAGES if p["is_current"]), RESPONSE_PACKAGES[0])
    sla_line = current_pkg["guarantee_hours"]
    days = list(range(1, 31))
    colors_bar = ["#10b981" if t <= sla_line else "#ef4444" for t in times]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days, y=times, name="Response Time (hrs)",
        marker={"color": colors_bar},
        hovertemplate="Day %{x}: %{y}h<extra></extra>",
    ))
    fig.add_hline(
        y=sla_line, line_color="#ffd700", line_dash="dot",
        annotation_text=f"SLA: {sla_line}h", annotation_position="top right",
        annotation_font={"color": "#ffd700", "size": 10},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 11},
        margin={"t": 20, "b": 30, "l": 10, "r": 10},
        height=220,
        showlegend=False,
        xaxis={"gridcolor": "#21262d", "zeroline": False},
        yaxis={"gridcolor": "#21262d", "zeroline": False,
               "title": {"text": "Hours", "font": {"size": 10}}},
    )
    return fig


def _sla_compliance_chart():
    sl  = SLA_COMPLIANCE
    labels = ["On Time", "Late", "Missed"]
    values = [sl["on_time"], sl["late"], sl["missed"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.7,
        marker={"colors": ["#10b981", "#f59e0b", "#ef4444"],
                "line": {"color": "rgba(0,0,0,0)", "width": 0}},
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    total = sum(values)
    compliance_pct = round(sl["on_time"] / total * 100) if total else 0
    fig.add_annotation(
        text=f"{compliance_pct}%", x=0.5, y=0.55, showarrow=False,
        font={"size": 22, "color": "#10b981", "family": "Inter"},
    )
    fig.add_annotation(
        text="compliance", x=0.5, y=0.38, showarrow=False,
        font={"size": 11, "color": "#8b949e", "family": "Inter"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 10},
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=200,
        showlegend=True,
        legend={"orientation": "h", "y": -0.15, "font": {"size": 9}},
    )
    return fig


def _package_card(pkg):
    is_current = pkg["is_current"]
    border = "2px solid var(--accent-teal)" if is_current else "1px solid var(--border-color)"
    bg     = "rgba(0,201,167,0.04)" if is_current else "var(--surface-card)"

    features = [
        html.Li(
            [html.I(className="fas fa-check me-2", style={"color": "var(--accent-teal)",
                                                            "fontSize": "0.7rem"}), f],
            style={"fontSize": "0.8rem", "marginBottom": "4px", "listStyle": "none"},
        )
        for f in pkg["features"]
    ]

    return dbc.Col(
        html.Div(
            className="p-4 h-100",
            style={"border": border, "borderRadius": "12px", "background": bg,
                   "position": "relative"},
            children=[
                *([html.Div("Current Plan",
                            style={"position": "absolute", "top": "-10px", "left": "20px",
                                   "background": "var(--accent-teal)", "color": "#0d1117",
                                   "fontSize": "0.7rem", "fontWeight": "800",
                                   "padding": "2px 10px", "borderRadius": "100px"})]
                  if is_current else []),
                html.Div(className="d-flex align-items-center justify-content-between mb-2", children=[
                    html.Span(pkg["name"], style={"fontWeight": "800", "fontSize": "1rem"}),
                    html.Span(
                        f"${pkg['price']:.2f}/mo",
                        style={"fontWeight": "700", "color": pkg["badge_color"]}
                    ),
                ]),
                html.Div(
                    [html.I(className="fas fa-clock me-1"), f"Guaranteed within {pkg['guarantee_hours']}h"],
                    style={"fontSize": "0.82rem", "color": pkg["badge_color"],
                           "fontWeight": "600", "marginBottom": "12px"},
                ),
                html.Ul(features, style={"paddingLeft": "0", "marginBottom": "12px"}),
                html.Small(
                    [html.I(className="fas fa-info-circle me-1"), pkg["refund_policy"]],
                    style={"color": "var(--text-muted)", "fontSize": "0.72rem",
                           "display": "block", "marginBottom": "12px"},
                ),
                dbc.Button(
                    "Current Plan" if is_current else "Upgrade",
                    id={"type": "pkg-select-btn", "index": pkg["id"]},
                    n_clicks=0,
                    className="w-100 btn-teal" if not is_current else "w-100",
                    color="secondary" if is_current else None,
                    outline=is_current,
                    disabled=is_current,
                    size="sm",
                ),
            ],
        ),
        md=4, className="mb-3",
    )


def _tab_response():
    sl  = SLA_COMPLIANCE
    current_pkg = next((p for p in RESPONSE_PACKAGES if p["is_current"]), RESPONSE_PACKAGES[0])

    status_icon  = {"on_time": "fa-check-circle", "late": "fa-exclamation-triangle",
                    "missed": "fa-times-circle"}
    status_color = {"on_time": "#10b981", "late": "#f59e0b", "missed": "#ef4444"}

    event_rows = [
        html.Div(className="d-flex align-items-center gap-3 mb-2 pb-2",
                 style={"borderBottom": "1px solid var(--border-color)"}, children=[
            html.I(className=f"fas {status_icon[ev['status']]}",
                   style={"color": status_color[ev["status"]], "fontSize": "1rem",
                          "minWidth": "16px"}),
            html.Div(className="flex-grow-1", children=[
                html.Span(ev["lead"], style={"fontWeight": "600", "fontSize": "0.85rem"}),
                html.Small(ev["date"].strftime(" · %b %d"),
                           style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
            ]),
            html.Span(
                f"{ev['hrs']:.1f}h",
                style={"fontWeight": "700", "fontSize": "0.85rem",
                       "color": status_color[ev["status"]]},
            ),
        ])
        for ev in sl["sla_events"]
    ]

    return html.Div(
        id="perf-panel-response",
        style={"display": "none"},
        children=[
            html.H4("Guaranteed Response", style={"fontWeight": "800", "marginBottom": "1.5rem"}),

            # Current SLA status banner
            html.Div(
                className="lc-card p-4 mb-4",
                style={"borderLeft": f"4px solid {current_pkg['badge_color']}"},
                children=[
                    html.Div(className="d-flex align-items-center justify-content-between flex-wrap gap-3",
                             children=[
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-shield-halved me-2",
                                       style={"color": current_pkg["badge_color"]}),
                                html.Span("Active SLA Package",
                                          style={"fontWeight": "800", "fontSize": "1.05rem"}),
                            ], className="mb-1"),
                            html.Div([
                                html.Span(current_pkg["name"],
                                          style={"fontWeight": "700",
                                                 "color": current_pkg["badge_color"],
                                                 "marginRight": "12px"}),
                                html.Span(
                                    f"Guarantee: respond within {current_pkg['guarantee_hours']}h",
                                    style={"fontSize": "0.85rem", "color": "var(--text-secondary)"},
                                ),
                            ]),
                        ]),
                        html.Div(className="d-flex gap-4", children=[
                            html.Div(className="text-center", children=[
                                html.Div(f"{sl['current_streak']}",
                                         style={"fontWeight": "900", "fontSize": "1.8rem",
                                                "color": "#10b981"}),
                                html.Small("Response streak",
                                           style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                            ]),
                            html.Div(className="text-center", children=[
                                html.Div(f"{sl['avg_response_hrs']:.1f}h",
                                         style={"fontWeight": "900", "fontSize": "1.8rem",
                                                "color": current_pkg["badge_color"]}),
                                html.Small("Avg response time",
                                           style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                            ]),
                            html.Div(className="text-center", children=[
                                html.Div(f"{sl['best_response_hrs']:.1f}h",
                                         style={"fontWeight": "900", "fontSize": "1.8rem",
                                                "color": "var(--accent-teal)"}),
                                html.Small("Best response",
                                           style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                            ]),
                        ]),
                    ]),
                ],
            ),

            dbc.Row([
                # Response time chart
                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-chart-bar", "Daily Response Times (30d)",
                                 "Green = within SLA  |  Red = exceeded SLA"),
                    dcc.Graph(figure=_response_time_chart(),
                              config={"displayModeBar": False}),
                ]), md=8, className="mb-3"),

                # SLA compliance donut
                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-circle-check", "SLA Compliance"),
                    dcc.Graph(figure=_sla_compliance_chart(),
                              config={"displayModeBar": False}),
                    html.Div(className="d-flex justify-content-around mt-2", children=[
                        html.Div(className="text-center", children=[
                            html.Div(str(sl["on_time"]),
                                     style={"fontWeight": "800", "color": "#10b981"}),
                            html.Small("On time", style={"color": "var(--text-muted)",
                                                          "fontSize": "0.7rem"}),
                        ]),
                        html.Div(className="text-center", children=[
                            html.Div(str(sl["late"]),
                                     style={"fontWeight": "800", "color": "#f59e0b"}),
                            html.Small("Late", style={"color": "var(--text-muted)",
                                                       "fontSize": "0.7rem"}),
                        ]),
                        html.Div(className="text-center", children=[
                            html.Div(str(sl["missed"]),
                                     style={"fontWeight": "800", "color": "#ef4444"}),
                            html.Small("Missed", style={"color": "var(--text-muted)",
                                                         "fontSize": "0.7rem"}),
                        ]),
                    ]),
                ]), md=4, className="mb-3"),
            ], className="g-3 mb-4"),

            # Recent SLA events
            dbc.Row([
                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-history", "Recent SLA Events"),
                    *event_rows,
                ]), md=5, className="mb-3"),

                # Package selector
                dbc.Col(html.Div(className="lc-card p-3 h-100", children=[
                    _section_hdr("fa-star", "Response SLA Packages",
                                 "Upgrade your response guarantee to attract more quality leads"),
                    html.Div(id="pkg-select-alert", className="mb-2"),
                    dbc.Row([_package_card(p) for p in RESPONSE_PACKAGES]),
                ]), md=7, className="mb-3"),
            ], className="g-3"),
        ],
    )


# ── Tab 3: SEO & Visibility ───────────────────────────────────────────────────

def _seo_score_card(entry):
    score = entry["seo_score"]
    grade = entry["grade"]
    if score >= 85:
        bar_color, grade_color = "success", "#10b981"
    elif score >= 65:
        bar_color, grade_color = "warning", "#f59e0b"
    else:
        bar_color, grade_color = "danger", "#ef4444"

    issues = [
        html.Li(
            [html.I(className="fas fa-exclamation-triangle me-1",
                    style={"color": "#f59e0b", "fontSize": "0.65rem"}), issue],
            style={"fontSize": "0.78rem", "marginBottom": "3px"},
        )
        for issue in entry["issues"]
    ]

    kw_pills = [
        html.Span(
            kw,
            style={"background": "rgba(59,130,246,0.1)", "color": "#3b82f6",
                   "borderRadius": "100px", "padding": "2px 10px",
                   "fontSize": "0.7rem", "marginRight": "4px", "marginBottom": "4px",
                   "display": "inline-block"},
        )
        for kw in entry["suggestions"][:4]
    ]

    return html.Div(
        className="lc-card p-3 mb-3",
        children=[
            html.Div(className="d-flex align-items-start gap-3", children=[
                # Grade circle
                html.Div(
                    grade,
                    style={"minWidth": "48px", "height": "48px", "borderRadius": "50%",
                           "background": f"{grade_color}18", "color": grade_color,
                           "display": "flex", "alignItems": "center", "justifyContent": "center",
                           "fontWeight": "900", "fontSize": "1.1rem", "flexShrink": "0",
                           "border": f"2px solid {grade_color}40"},
                ),
                html.Div(className="flex-grow-1", children=[
                    html.Div(className="d-flex align-items-center justify-content-between mb-1",
                             children=[
                        html.Span(entry["listing_title"],
                                  style={"fontWeight": "700", "fontSize": "0.9rem"}),
                        html.Span(f"Score: {score}",
                                  style={"fontWeight": "700", "color": grade_color,
                                         "fontSize": "0.85rem"}),
                    ]),
                    dbc.Progress(value=score, color=bar_color,
                                 style={"height": "6px", "borderRadius": "3px",
                                        "marginBottom": "8px"}),
                    # Metrics chips
                    html.Div(className="d-flex flex-wrap gap-3 mb-2", children=[
                        html.Span(
                            [html.I(className="fas fa-eye me-1",
                                    style={"color": "var(--accent-teal)", "fontSize": "0.65rem"}),
                             f"{entry['impressions_30d']:,} impressions"],
                            style={"fontSize": "0.75rem", "color": "var(--text-secondary)"},
                        ),
                        html.Span(
                            [html.I(className="fas fa-mouse-pointer me-1",
                                    style={"color": "#3b82f6", "fontSize": "0.65rem"}),
                             f"{entry['clicks_30d']} clicks"],
                            style={"fontSize": "0.75rem", "color": "var(--text-secondary)"},
                        ),
                        html.Span(
                            [html.I(className="fas fa-search me-1",
                                    style={"color": "#a855f7", "fontSize": "0.65rem"}),
                             f"Avg pos. {entry['avg_position']}"],
                            style={"fontSize": "0.75rem", "color": "var(--text-secondary)"},
                        ),
                        html.Span(
                            [html.I(className="fas fa-percent me-1",
                                    style={"color": "#f59e0b", "fontSize": "0.65rem"}),
                             f"{entry['organic_ctr']}% CTR"],
                            style={"fontSize": "0.75rem", "color": "var(--text-secondary)"},
                        ),
                    ]),
                    *([html.Div([
                        html.Div("Issues to fix:", style={"fontSize": "0.72rem",
                                                           "fontWeight": "700",
                                                           "color": "var(--text-muted)",
                                                           "marginBottom": "2px"}),
                        html.Ul(issues, style={"paddingLeft": "16px", "marginBottom": "6px"}),
                    ])] if issues else []),
                    # Keyword suggestions
                    html.Div(style={"marginTop": "4px"}, children=[
                        html.Span("Target keywords: ",
                                  style={"fontSize": "0.72rem", "color": "var(--text-muted)",
                                         "marginRight": "4px"}),
                        *kw_pills,
                    ]),
                ]),
            ]),
            # Keyword table (collapsed toggle)
            dbc.Collapse(
                html.Div(
                    className="mt-3 pt-3",
                    style={"borderTop": "1px solid var(--border-color)"},
                    children=[
                        html.Table(
                            [
                                html.Thead(html.Tr([
                                    html.Th("Keyword", style={"fontSize": "0.72rem",
                                                               "color": "var(--text-muted)",
                                                               "fontWeight": "600",
                                                               "padding": "4px 8px"}),
                                    html.Th("Impr.", style={"fontSize": "0.72rem",
                                                             "color": "var(--text-muted)",
                                                             "fontWeight": "600",
                                                             "padding": "4px 8px",
                                                             "textAlign": "right"}),
                                    html.Th("Clicks", style={"fontSize": "0.72rem",
                                                              "color": "var(--text-muted)",
                                                              "fontWeight": "600",
                                                              "padding": "4px 8px",
                                                              "textAlign": "right"}),
                                    html.Th("Position", style={"fontSize": "0.72rem",
                                                                "color": "var(--text-muted)",
                                                                "fontWeight": "600",
                                                                "padding": "4px 8px",
                                                                "textAlign": "right"}),
                                ])),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(kw["keyword"],
                                                style={"fontSize": "0.78rem", "padding": "4px 8px"}),
                                        html.Td(f"{kw['impressions']:,}",
                                                style={"fontSize": "0.78rem", "padding": "4px 8px",
                                                       "textAlign": "right",
                                                       "color": "var(--text-secondary)"}),
                                        html.Td(str(kw["clicks"]),
                                                style={"fontSize": "0.78rem", "padding": "4px 8px",
                                                       "textAlign": "right",
                                                       "color": "var(--accent-teal)"}),
                                        html.Td(str(kw["position"]),
                                                style={"fontSize": "0.78rem", "padding": "4px 8px",
                                                       "textAlign": "right",
                                                       "color": "var(--text-muted)"}),
                                    ])
                                    for kw in entry["top_keywords"]
                                ]),
                            ],
                            style={"width": "100%", "borderCollapse": "collapse"},
                        ),
                    ],
                ),
                id={"type": "seo-kw-collapse", "index": entry["listing_id"]},
                is_open=False,
            ),
            html.Button(
                [html.I(className="fas fa-chevron-down me-1"), "Show keyword details"],
                id={"type": "seo-kw-toggle", "index": entry["listing_id"]},
                n_clicks=0,
                style={"background": "transparent", "border": "none", "color": "var(--accent-teal)",
                       "fontSize": "0.75rem", "cursor": "pointer", "padding": "4px 0",
                       "marginTop": "8px"},
            ),
        ],
    )


def _impressions_chart():
    pa = PERFORMANCE_ANALYTICS
    weeks = [f"W{i+1}" for i in range(8)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks, y=pa["weekly_impressions"], name="Impressions",
        line={"color": "#3b82f6", "width": 2},
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        hovertemplate="%{y:,} impressions<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=pa["weekly_clicks"], name="Clicks", yaxis="y2",
        line={"color": "#00c9a7", "width": 2, "dash": "dot"},
        hovertemplate="%{y:,} clicks<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 10},
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        height=200,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02,
                "xanchor": "right", "x": 1, "font": {"size": 9}},
        xaxis={"gridcolor": "#21262d", "zeroline": False},
        yaxis={"gridcolor": "#21262d", "zeroline": False},
        yaxis2={"overlaying": "y", "side": "right", "showgrid": False, "zeroline": False},
        hovermode="x unified",
    )
    return fig


def _tab_seo():
    total_impressions = sum(s["impressions_30d"] for s in MOCK_SEO_SCORES)
    total_clicks      = sum(s["clicks_30d"]      for s in MOCK_SEO_SCORES)
    avg_position      = round(sum(s["avg_position"] for s in MOCK_SEO_SCORES) / len(MOCK_SEO_SCORES), 1)
    avg_ctr           = round(sum(s["organic_ctr"]  for s in MOCK_SEO_SCORES) / len(MOCK_SEO_SCORES), 1)

    return html.Div(
        id="perf-panel-seo",
        style={"display": "none"},
        children=[
            html.H4("SEO & Visibility", style={"fontWeight": "800", "marginBottom": "1.5rem"}),

            dbc.Row([
                dbc.Col(_kpi_card(f"{total_impressions:,}", "Total Impressions (30d)",
                                  "fa-eye", delta="+12%"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(str(total_clicks), "Organic Clicks (30d)",
                                  "fa-mouse-pointer", "#3b82f6", delta="+8%"),
                        xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(str(avg_position), "Avg. Search Position",
                                  "fa-search", "#a855f7"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(f"{avg_ctr}%", "Avg. Organic CTR",
                                  "fa-percent", "#f59e0b"), xs=6, lg=3, className="mb-3"),
            ], className="g-3 mb-4"),

            # Impressions trend chart
            html.Div(className="lc-card p-3 mb-4", children=[
                _section_hdr("fa-chart-line", "Weekly Search Impressions & Clicks",
                             "Organic search traffic trend over the past 8 weeks"),
                dcc.Graph(figure=_impressions_chart(), config={"displayModeBar": False}),
            ]),

            # Per-listing SEO cards
            _section_hdr("fa-list-check", "Listing SEO Health",
                         "Click 'Show keyword details' to see keyword-level performance"),
            html.Div(id="seo-cards-container",
                     children=[_seo_score_card(e) for e in
                                sorted(MOCK_SEO_SCORES, key=lambda x: x["seo_score"], reverse=True)]),
        ],
    )


# ── Tab 4: PPC Campaigns ──────────────────────────────────────────────────────

def _campaign_card(camp):
    is_active = camp["status"] == "active"
    status_color = "#10b981" if is_active else "#6b7280"
    spent_pct = min(camp["total_spend"] / (camp["daily_budget"] * 30) * 100, 100)
    days_running = (datetime.now() - camp["start_date"]).days

    return html.Div(
        className="lc-card p-3 mb-3",
        style={"opacity": "1" if is_active else "0.7"},
        children=[
            html.Div(className="d-flex align-items-start justify-content-between mb-2", children=[
                html.Div([
                    html.Div(className="d-flex align-items-center gap-2 mb-1", children=[
                        html.Span(
                            ["● ", camp["status"].upper()],
                            style={"fontSize": "0.68rem", "fontWeight": "800",
                                   "color": status_color},
                        ),
                        html.Span(camp["name"],
                                  style={"fontWeight": "800", "fontSize": "0.95rem"}),
                    ]),
                    html.Small(camp["listing_title"],
                               style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                ]),
                # Toggle button
                dbc.Button(
                    [html.I(className=f"fas fa-{'pause' if is_active else 'play'} me-1"),
                     "Pause" if is_active else "Resume"],
                    id={"type": "ppc-toggle-btn", "index": camp["id"]},
                    n_clicks=0, size="sm",
                    color="secondary", outline=True,
                    style={"fontSize": "0.72rem"},
                ),
            ]),

            # Metrics row
            dbc.Row([
                dbc.Col(html.Div(className="text-center", children=[
                    html.Div(f"{camp['impressions']:,}",
                             style={"fontWeight": "800", "fontSize": "1.1rem"}),
                    html.Small("Impressions", style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                ]), xs=4),
                dbc.Col(html.Div(className="text-center", children=[
                    html.Div(f"{camp['clicks']:,}",
                             style={"fontWeight": "800", "fontSize": "1.1rem",
                                    "color": "var(--accent-teal)"}),
                    html.Small("Clicks", style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                ]), xs=4),
                dbc.Col(html.Div(className="text-center", children=[
                    html.Div(str(camp["conversions"]),
                             style={"fontWeight": "800", "fontSize": "1.1rem",
                                    "color": "#ffd700"}),
                    html.Small("Leads", style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                ]), xs=4),
            ], className="g-0 mb-3"),

            # Secondary metrics chips
            html.Div(className="d-flex flex-wrap gap-2 mb-3", children=[
                html.Span(
                    f"CTR {camp['ctr']}%",
                    style={"background": "rgba(0,201,167,0.1)", "color": "var(--accent-teal)",
                           "borderRadius": "100px", "padding": "2px 10px", "fontSize": "0.72rem",
                           "fontWeight": "600"},
                ),
                html.Span(
                    f"CPC ${camp['cpc']:.2f}",
                    style={"background": "rgba(59,130,246,0.1)", "color": "#3b82f6",
                           "borderRadius": "100px", "padding": "2px 10px", "fontSize": "0.72rem",
                           "fontWeight": "600"},
                ),
                html.Span(
                    f"CPL ${camp['cpl']:.2f}",
                    style={"background": "rgba(245,158,11,0.1)", "color": "#f59e0b",
                           "borderRadius": "100px", "padding": "2px 10px", "fontSize": "0.72rem",
                           "fontWeight": "600"},
                ),
                html.Span(
                    f"ROAS {camp['roas']}x",
                    style={"background": "rgba(168,85,247,0.1)", "color": "#a855f7",
                           "borderRadius": "100px", "padding": "2px 10px", "fontSize": "0.72rem",
                           "fontWeight": "600"},
                ),
                html.Span(
                    f"Day {days_running}",
                    style={"background": "rgba(107,114,128,0.1)", "color": "#6b7280",
                           "borderRadius": "100px", "padding": "2px 10px", "fontSize": "0.72rem"},
                ),
            ]),

            # Budget bar
            html.Div(className="d-flex justify-content-between mb-1", children=[
                html.Small(f"Budget: ${camp['total_spend']:.2f} / ${camp['daily_budget'] * 30:.0f}/mo",
                           style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                html.Small(f"{spent_pct:.0f}%",
                           style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
            ]),
            dbc.Progress(value=spent_pct, color="success" if spent_pct < 80 else "warning",
                         style={"height": "6px", "borderRadius": "3px"}),

            # Keywords
            html.Div(className="d-flex flex-wrap gap-1 mt-2", children=[
                html.Span(
                    kw,
                    style={"background": "rgba(255,255,255,0.05)", "color": "var(--text-secondary)",
                           "borderRadius": "4px", "padding": "1px 6px", "fontSize": "0.68rem",
                           "border": "1px solid var(--border-color)"},
                )
                for kw in camp["target_keywords"]
            ]),
        ],
    )


def _ppc_roi_chart():
    pa = PERFORMANCE_ANALYTICS
    camps = MOCK_PPC_CAMPAIGNS
    names  = [c["name"] for c in camps]
    spends = [c["total_spend"] for c in camps]
    roas   = [c["roas"] for c in camps]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Ad Spend ($)", x=names, y=spends,
        marker={"color": "rgba(168,85,247,0.7)"},
        hovertemplate="%{x}: $%{y:.2f}<extra>Spend</extra>",
    ))
    fig.add_trace(go.Scatter(
        name="ROAS", x=names, y=roas, yaxis="y2",
        mode="markers+lines",
        marker={"color": "#ffd700", "size": 10},
        line={"color": "#ffd700", "width": 2},
        hovertemplate="%{x}: %{y}x ROAS<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 11},
        margin={"t": 10, "b": 40, "l": 10, "r": 10},
        height=200,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02,
                "xanchor": "right", "x": 1, "font": {"size": 9}},
        xaxis={"gridcolor": "#21262d", "zeroline": False},
        yaxis={"gridcolor": "#21262d", "zeroline": False,
               "title": {"text": "Spend ($)", "font": {"size": 10}}},
        yaxis2={"overlaying": "y", "side": "right", "showgrid": False, "zeroline": False,
                "title": {"text": "ROAS", "font": {"size": 10}}},
        barmode="group",
    )
    return fig


def _tab_ppc():
    roi = PERFORMANCE_ANALYTICS["roi"]
    total_imp  = sum(c["impressions"]  for c in MOCK_PPC_CAMPAIGNS)
    total_clk  = sum(c["clicks"]       for c in MOCK_PPC_CAMPAIGNS)
    total_conv = sum(c["conversions"]  for c in MOCK_PPC_CAMPAIGNS)
    total_spend = sum(c["total_spend"] for c in MOCK_PPC_CAMPAIGNS)
    avg_roas   = round(sum(c["roas"] for c in MOCK_PPC_CAMPAIGNS) / len(MOCK_PPC_CAMPAIGNS), 1)

    return html.Div(
        id="perf-panel-ppc",
        style={"display": "none"},
        children=[
            html.Div(className="d-flex align-items-center justify-content-between mb-4", children=[
                html.H4("PPC Campaigns", style={"fontWeight": "800", "margin": "0"}),
                dbc.Button(
                    [html.I(className="fas fa-plus me-1"), "New Campaign"],
                    id="ppc-new-campaign-btn", n_clicks=0,
                    className="btn-teal btn-sm px-3",
                ),
            ]),

            # KPI row
            dbc.Row([
                dbc.Col(_kpi_card(f"{total_imp:,}", "Total Impressions",
                                  "fa-eye", delta="+22%"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(f"{total_clk:,}", "Total Clicks",
                                  "fa-mouse-pointer", "#3b82f6", delta="+15%"),
                        xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(str(total_conv), "Conversions (Leads)",
                                  "fa-bolt", "#ffd700"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi_card(f"{avg_roas}x", "Avg. ROAS",
                                  "fa-chart-line", "#a855f7"), xs=6, lg=3, className="mb-3"),
            ], className="g-3 mb-4"),

            dbc.Row([
                # Campaigns list
                dbc.Col(html.Div(children=[
                    _section_hdr("fa-bullhorn", "Active & Paused Campaigns"),
                    html.Div(id="ppc-campaigns-container",
                             children=[_campaign_card(c) for c in MOCK_PPC_CAMPAIGNS]),
                    dbc.Toast(
                        id="ppc-toast", header="", is_open=False,
                        dismissable=True, duration=3000,
                        style={"position": "fixed", "bottom": "1.5rem", "right": "1.5rem",
                               "minWidth": "240px", "zIndex": "9999",
                               "background": "var(--bg-secondary)",
                               "border": "1px solid var(--border-color)"},
                    ),
                ]), md=6, className="mb-3"),

                # ROI summary + chart
                dbc.Col(html.Div(children=[
                    html.Div(className="lc-card p-3 mb-3", children=[
                        _section_hdr("fa-dollar-sign", "ROI Summary"),
                        dbc.Row([
                            dbc.Col(html.Div(className="text-center py-2", children=[
                                html.Div(f"${total_spend:.2f}",
                                         style={"fontWeight": "900", "fontSize": "1.4rem",
                                                "color": "#a855f7"}),
                                html.Small("Total ad spend",
                                           style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                            ]), xs=6),
                            dbc.Col(html.Div(className="text-center py-2", children=[
                                html.Div(f"${roi['estimated_revenue']:,.0f}",
                                         style={"fontWeight": "900", "fontSize": "1.4rem",
                                                "color": "#10b981"}),
                                html.Small("Est. revenue generated",
                                           style={"color": "var(--text-muted)", "fontSize": "0.7rem"}),
                            ]), xs=6),
                        ]),
                        html.Hr(style={"borderColor": "var(--border-color)", "margin": "8px 0"}),
                        dbc.Row([
                            dbc.Col(html.Div(className="text-center", children=[
                                html.Div(f"{roi['roi_pct']:,.0f}%",
                                         style={"fontWeight": "900", "fontSize": "1.4rem",
                                                "color": "var(--accent-teal)"}),
                                html.Small("ROI", style={"color": "var(--text-muted)",
                                                          "fontSize": "0.7rem"}),
                            ]), xs=6),
                            dbc.Col(html.Div(className="text-center", children=[
                                html.Div(f"${roi['cost_per_acquisition']:.2f}",
                                         style={"fontWeight": "900", "fontSize": "1.4rem",
                                                "color": "#f59e0b"}),
                                html.Small("Cost per acquisition",
                                           style={"color": "var(--text-muted)",
                                                  "fontSize": "0.7rem"}),
                            ]), xs=6),
                        ]),
                    ]),
                    html.Div(className="lc-card p-3", children=[
                        _section_hdr("fa-chart-bar", "Spend vs ROAS by Campaign"),
                        dcc.Graph(figure=_ppc_roi_chart(), config={"displayModeBar": False}),
                    ]),
                ]), md=6, className="mb-3"),
            ], className="g-3"),

            # New campaign modal
            dbc.Modal(
                id="ppc-new-campaign-modal",
                size="lg",
                is_open=False,
                children=[
                    dbc.ModalHeader(dbc.ModalTitle("Create New PPC Campaign")),
                    dbc.ModalBody(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Label("Campaign Name", style={"fontSize": "0.82rem",
                                                                    "fontWeight": "600"}),
                                dbc.Input(id="ppc-new-name", placeholder="e.g. Plumber – Miami Spring",
                                          className="mb-3", style={"borderRadius": "8px"}),
                            ], md=8),
                            dbc.Col([
                                html.Label("Daily Budget ($)", style={"fontSize": "0.82rem",
                                                                        "fontWeight": "600"}),
                                dbc.Input(id="ppc-new-budget", placeholder="15.00", type="number",
                                          min=5, max=500, className="mb-3",
                                          style={"borderRadius": "8px"}),
                            ], md=4),
                        ]),
                        html.Label("Target Keywords (comma-separated)",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dbc.Input(id="ppc-new-keywords",
                                  placeholder="electrician Miami, panel upgrade, EV charger",
                                  className="mb-3", style={"borderRadius": "8px"}),
                        html.Label("Target Cities", style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Dropdown(
                            id="ppc-new-cities",
                            options=[
                                {"label": c, "value": c}
                                for c in ["Miami", "Houston", "Austin", "Chicago",
                                          "Dallas", "Phoenix", "Los Angeles", "New York"]
                            ],
                            multi=True, className="mb-3",
                            placeholder="Select target cities...",
                        ),
                        html.Div(id="ppc-new-alert"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Cancel", id="ppc-new-cancel-btn", n_clicks=0,
                                   color="secondary", outline=True, className="me-2"),
                        dbc.Button([html.I(className="fas fa-rocket me-1"), "Launch Campaign"],
                                   id="ppc-new-confirm-btn", n_clicks=0,
                                   className="btn-teal"),
                    ]),
                ],
            ),
        ],
    )


# ── Sidebar navigation ────────────────────────────────────────────────────────

def _sidebar():
    pa = PERFORMANCE_ANALYTICS
    return html.Div(
        style={
            "width": "200px", "minWidth": "200px",
            "borderRight": "1px solid var(--border-color)",
            "paddingTop": "1.5rem", "paddingBottom": "1rem",
            "background": "var(--bg-secondary)",
            "display": "flex", "flexDirection": "column",
        },
        children=[
            # Summary stats
            html.Div(
                className="px-3 pb-3 mb-2",
                style={"borderBottom": "1px solid var(--border-color)"},
                children=[
                    html.Div("Performance Hub",
                             style={"fontWeight": "800", "fontSize": "0.82rem",
                                    "color": "var(--text-primary)", "marginBottom": "8px"}),
                    html.Div(
                        [html.Span(f"{pa['funnel']['leads']}",
                                   style={"fontWeight": "800", "color": "var(--accent-teal)"}),
                         html.Span(" leads this month",
                                   style={"fontSize": "0.72rem", "color": "var(--text-muted)"})],
                        className="mb-1",
                    ),
                    html.Div(
                        [html.Span(f"{pa['response_rate_pct']}%",
                                   style={"fontWeight": "800", "color": "#10b981"}),
                         html.Span(" response rate",
                                   style={"fontSize": "0.72rem", "color": "var(--text-muted)"})],
                        className="mb-1",
                    ),
                    html.Div(
                        [html.Span(f"{pa['verified_lead_pct']:.0f}%",
                                   style={"fontWeight": "800", "color": "#ffd700"}),
                         html.Span(" verified leads",
                                   style={"fontSize": "0.72rem", "color": "var(--text-muted)"})],
                    ),
                ],
            ),

            # Nav items
            html.Div(
                className="px-2 flex-grow-1",
                children=[
                    html.Button(
                        [html.I(className=f"fas {icon} me-2 fa-fw"), label],
                        id={"type": "perf-nav-btn", "index": tab_id},
                        n_clicks=0,
                        style={
                            "width": "100%", "textAlign": "left",
                            "background": "var(--accent-teal)" if tab_id == "leads" else "transparent",
                            "color": "#0d1117" if tab_id == "leads" else "var(--text-secondary)",
                            "border": "none", "borderRadius": "6px",
                            "padding": "0.5rem 0.75rem",
                            "fontSize": "0.82rem", "fontWeight": "600",
                            "cursor": "pointer", "marginBottom": "0.25rem", "display": "block",
                        },
                    )
                    for tab_id, icon, label in _TABS
                ],
            ),

            # Bottom links
            html.Div(
                className="px-3 py-2",
                style={"borderTop": "1px solid var(--border-color)", "marginTop": "auto"},
                children=[
                    dcc.Link(
                        [html.I(className="fas fa-chart-line me-2"), "My Leads"],
                        href="/leads",
                        style={"fontSize": "0.75rem", "color": "var(--text-muted)",
                               "textDecoration": "none", "display": "block", "marginBottom": "4px"},
                    ),
                    dcc.Link(
                        [html.I(className="fas fa-th-large me-2"), "Dashboard"],
                        href="/dashboard",
                        style={"fontSize": "0.75rem", "color": "var(--text-muted)",
                               "textDecoration": "none", "display": "block"},
                    ),
                ],
            ),
        ],
    )


# ── Main entry point ──────────────────────────────────────────────────────────

def performance_layout():
    """Lead Generation & Performance Tools hub."""
    return html.Div([
        # Page header
        html.Div(
            className="d-flex align-items-center px-4 py-3 mb-0",
            style={"borderBottom": "1px solid var(--border-color)",
                   "background": "var(--bg-secondary)"},
            children=[
                html.I(className="fas fa-bolt me-2",
                       style={"color": "var(--accent-teal)", "fontSize": "1.2rem"}),
                html.Span("Growth & Performance",
                          style={"fontWeight": "900", "fontSize": "1.1rem"}),
                html.Div(className="vr mx-3",
                         style={"opacity": "0.2", "height": "20px", "alignSelf": "center"}),
                html.Span("Carlos Electric",
                          style={"color": "var(--text-secondary)", "fontSize": "0.9rem"}),
                html.Div(className="ms-auto d-flex gap-2", children=[
                    dcc.Link(
                        [html.I(className="fas fa-external-link-alt me-1"), "View Profile"],
                        href="/business",
                        style={"fontSize": "0.78rem", "color": "var(--accent-teal)",
                               "textDecoration": "none"},
                    ),
                    dcc.Link(
                        [html.I(className="fas fa-th-large me-1"), "Dashboard"],
                        href="/dashboard",
                        style={"fontSize": "0.78rem", "color": "var(--text-muted)",
                               "textDecoration": "none"},
                    ),
                ]),
            ],
        ),

        dbc.Container(
            html.Div(
                className="d-flex",
                style={"minHeight": "calc(100vh - 120px)"},
                children=[
                    _sidebar(),
                    html.Div(
                        className="flex-grow-1 p-4",
                        children=[
                            dcc.Store(id="perf-active-tab", data="leads"),
                            dcc.Store(id="perf-ppc-overrides", data={}),
                            _tab_leads(),
                            _tab_response(),
                            _tab_seo(),
                            _tab_ppc(),
                        ],
                    ),
                ],
            ),
            fluid=True,
        ),
    ])
