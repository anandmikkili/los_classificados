"""Business Management Dashboard – tabbed hub for profile, listings, and analytics."""
from datetime import datetime
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from los_classificados.utils.mock_data import (
    MOCK_BUSINESS_PROFILE, MOCK_USER_LISTINGS, MOCK_LEADS,
    BUSINESS_ANALYTICS, LEAD_STATUS_LABELS, CATEGORIES,
    NEIGHBORHOODS_BY_CITY, PLAN_FEATURES,
)

# ── Constants ─────────────────────────────────────────────────────────────────

_PLAN_LABEL = {"free": "Free", "featured": "⚡ Featured", "prime_boost": "★ Prime"}
_PLAN_COLOR = {"free": "#6b7280", "featured": "#ff6b35", "prime_boost": "#ffd700"}

_TIME_OPTIONS = (
    [{"label": "12:00 AM", "value": "00:00"}]
    + [{"label": f"{h}:{m} AM", "value": f"{h:02d}:{m}"}
       for h in range(1, 12) for m in ("00", "30")]
    + [{"label": "12:00 PM", "value": "12:00"}]
    + [{"label": f"{h}:{m} PM", "value": f"{h+12:02d}:{m}"}
       for h in range(1, 12) for m in ("00", "30")]
    + [{"label": "11:30 PM", "value": "23:30"}]
)

_COMPLETENESS_FIELDS = [
    ("tagline",       "Add a tagline"),
    ("description",   "Write your business description"),
    ("logo",          "Upload a logo"),
    ("cover",         "Upload a cover photo"),
    ("phone",         "Add a phone number"),
    ("whatsapp",      "Add a WhatsApp number"),
    ("website",       "Add your website URL"),
    ("social",        "Link at least one social profile"),
    ("service_areas", "Add service areas"),
    ("portfolio",     "Upload portfolio photos"),
]


# ── Shared small helpers ──────────────────────────────────────────────────────

def _section_hdr(icon, title):
    return html.Div(
        className="d-flex align-items-center gap-2 mb-3",
        children=[
            html.I(className=f"fas {icon}", style={"color": "var(--accent-teal)", "fontSize": "1rem"}),
            html.Span(title, style={"fontWeight": "800", "fontSize": "1rem"}),
        ],
    )


def _kpi(value, label, icon, color="var(--accent-teal)", delta=None):
    return html.Div(
        className="lc-card p-3",
        children=[
            html.Div(className="d-flex justify-content-between align-items-start mb-1", children=[
                html.Div(
                    html.I(className=f"fas {icon}"),
                    style={"width": "36px", "height": "36px", "borderRadius": "8px",
                           "background": f"{color}1a", "color": color,
                           "display": "flex", "alignItems": "center",
                           "justifyContent": "center", "fontSize": "1rem"},
                ),
                html.Span(
                    delta,
                    style={"fontSize": "0.72rem", "color": "#10b981", "fontWeight": "700"},
                ) if delta else None,
            ]),
            html.Div(str(value), style={"fontWeight": "800", "fontSize": "1.5rem", "color": color}),
            html.Div(label, style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
        ],
    )


# ── Sidebar navigation ────────────────────────────────────────────────────────

_NAV_ITEMS = [
    ("overview",  "fa-th-large",    "Overview"),
    ("profile",   "fa-store",       "Business Profile"),
    ("listings",  "fa-list-alt",    "My Listings"),
    ("analytics", "fa-chart-line",  "Analytics"),
]


def _sidebar(active="overview"):
    bp = MOCK_BUSINESS_PROFILE
    plan = bp["plan"]
    plan_color = _PLAN_COLOR.get(plan, "#6b7280")

    return html.Div(
        style={
            "width": "220px", "minWidth": "220px",
            "borderRight": "1px solid var(--border-color)",
            "paddingTop": "1.5rem",
            "background": "var(--bg-secondary)",
            "display": "flex", "flexDirection": "column",
        },
        children=[
            # Business identity
            html.Div(
                className="px-3 pb-3 mb-2",
                style={"borderBottom": "1px solid var(--border-color)"},
                children=[
                    html.Img(
                        src=bp["logo"],
                        style={"width": "48px", "height": "48px", "borderRadius": "50%",
                               "objectFit": "cover", "border": "2px solid var(--border-color)"},
                    ),
                    html.Div(
                        bp["business_name"],
                        style={"fontWeight": "800", "fontSize": "0.9rem",
                               "marginTop": "0.5rem", "color": "var(--text-primary)"},
                    ),
                    html.Div(
                        className="d-flex align-items-center gap-1 mt-1",
                        children=[
                            html.Span(
                                _PLAN_LABEL.get(plan, "Free"),
                                style={"fontSize": "0.68rem", "fontWeight": "700",
                                       "color": plan_color,
                                       "background": f"{plan_color}18",
                                       "border": f"1px solid {plan_color}40",
                                       "borderRadius": "100px", "padding": "0.05rem 0.4rem"},
                            ),
                            html.Span(
                                [html.I(className="fas fa-check-circle me-1"), "Verified"],
                                className="badge-verified",
                                style={"fontSize": "0.62rem"},
                            ) if bp["is_verified"] else None,
                        ],
                    ),
                ],
            ),

            # Nav items
            html.Div(
                className="px-2 flex-grow-1",
                children=[
                    html.Button(
                        [html.I(className=f"fas {icon} me-2 fa-fw"), label],
                        id={"type": "dash-nav-btn", "index": tab_id},
                        n_clicks=0,
                        style={
                            "width": "100%", "textAlign": "left",
                            "background": "var(--accent-teal)" if tab_id == active else "transparent",
                            "color": "#0d1117" if tab_id == active else "var(--text-secondary)",
                            "border": "none", "borderRadius": "6px",
                            "padding": "0.5rem 0.75rem",
                            "fontSize": "0.85rem", "fontWeight": "600",
                            "cursor": "pointer", "marginBottom": "0.25rem",
                            "display": "block",
                        },
                    )
                    for tab_id, icon, label in _NAV_ITEMS
                ],
            ),

            # Bottom links
            html.Div(
                className="px-3 py-3",
                style={"borderTop": "1px solid var(--border-color)", "marginTop": "auto"},
                children=[
                    dcc.Link(
                        [html.I(className="fas fa-eye me-2"), "View Public Profile"],
                        href="/business",
                        style={"fontSize": "0.78rem", "color": "var(--accent-teal)",
                               "textDecoration": "none", "display": "block", "marginBottom": "0.4rem"},
                    ),
                    dcc.Link(
                        [html.I(className="fas fa-plus me-2"), "Post New Ad"],
                        href="/post-ad",
                        style={"fontSize": "0.78rem", "color": "var(--text-muted)",
                               "textDecoration": "none", "display": "block"},
                    ),
                ],
            ),
        ],
    )


# ── Tab: Overview ─────────────────────────────────────────────────────────────

def _overview_panel():
    bp = MOCK_BUSINESS_PROFILE
    plan = bp["plan"]
    plan_expires_days = (bp["plan_expires"] - datetime.now()).days

    total_views = sum(l["views"] for l in MOCK_USER_LISTINGS)
    total_leads = sum(l["leads"] for l in MOCK_USER_LISTINGS)
    active_count = sum(1 for l in MOCK_USER_LISTINGS if l["status"] == "active")
    new_leads    = sum(1 for l in MOCK_LEADS if l["status"] == "new")

    # Profile completeness
    score = _compute_completeness(bp)
    bar_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 50 else "#ef4444")
    missing = _missing_items(bp)

    return html.Div(
        id="dash-panel-overview",
        children=[
            html.H4("Business Overview", style={"fontWeight": "800", "marginBottom": "1.5rem"}),

            # KPI row
            dbc.Row([
                dbc.Col(_kpi(total_views, "Total Views",  "fa-eye",    delta="+18% this week"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(total_leads, "Total Leads",  "fa-bolt",   "#ffd700", delta=f"+{new_leads} new"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(active_count,"Active Ads",   "fa-check-circle", "#10b981"), xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(f"{bp['rating']:.1f}", "Avg Rating", "fa-star", "#f59e0b"), xs=6, lg=3, className="mb-3"),
            ], className="g-3 mb-3"),

            dbc.Row([
                # Profile completeness card
                dbc.Col(
                    html.Div(
                        className="lc-card p-4 h-100",
                        children=[
                            _section_hdr("fa-tasks", "Profile Completeness"),
                            html.Div(
                                className="d-flex align-items-center gap-3 mb-2",
                                children=[
                                    html.Div(
                                        f"{score}%",
                                        style={"fontWeight": "900", "fontSize": "2rem",
                                               "color": bar_color},
                                    ),
                                    html.Div(
                                        dbc.Progress(
                                            value=score,
                                            style={"height": "10px", "borderRadius": "5px"},
                                            color="success" if score >= 80 else ("warning" if score >= 50 else "danger"),
                                        ),
                                        style={"flexGrow": "1"},
                                    ),
                                ],
                            ),
                            html.P(
                                "A complete profile gets 3× more customer views." if score < 100
                                else "Your profile is 100% complete!",
                                style={"fontSize": "0.8rem", "color": "var(--text-muted)", "marginBottom": "0.75rem"},
                            ),
                            html.Div([
                                html.Div(
                                    className="d-flex align-items-center gap-2 mb-1",
                                    children=[
                                        html.I(
                                            className="fas fa-circle-xmark",
                                            style={"color": "#ef4444", "fontSize": "0.72rem"},
                                        ),
                                        html.Span(item, style={"fontSize": "0.78rem",
                                                               "color": "var(--text-secondary)"}),
                                    ],
                                )
                                for item in missing[:4]
                            ]) if missing else html.Span(
                                [html.I(className="fas fa-circle-check me-1", style={"color": "#10b981"}),
                                 "Everything looks great!"],
                                style={"fontSize": "0.82rem", "color": "#10b981"},
                            ),
                            html.Button(
                                [html.I(className="fas fa-edit me-1"), "Edit Profile"],
                                id={"type": "dash-nav-btn", "index": "profile"},
                                n_clicks=0,
                                style={"marginTop": "0.75rem", "width": "100%",
                                       "background": "var(--accent-teal)", "color": "#0d1117",
                                       "border": "none", "borderRadius": "6px",
                                       "padding": "0.4rem 0.75rem",
                                       "fontSize": "0.82rem", "fontWeight": "700", "cursor": "pointer"},
                            ),
                        ],
                    ),
                    md=6, className="mb-3",
                ),

                # Plan status card
                dbc.Col(
                    html.Div(
                        className="lc-card p-4 h-100",
                        style={"borderLeft": "3px solid #ffd700"},
                        children=[
                            _section_hdr("fa-star", "Plan Status"),
                            html.Div(
                                className="d-flex align-items-center gap-2 mb-2",
                                children=[
                                    html.Span(
                                        _PLAN_LABEL.get(plan, "Free"),
                                        style={"fontWeight": "800", "fontSize": "1.1rem",
                                               "color": _PLAN_COLOR.get(plan, "#6b7280")},
                                    ),
                                    html.Span(
                                        [html.I(className="fas fa-clock me-1"),
                                         f"Expires in {plan_expires_days}d"],
                                        style={"fontSize": "0.75rem", "color": "#f59e0b"
                                               if plan_expires_days <= 7 else "var(--text-muted)"},
                                    ) if plan != "free" else None,
                                ],
                            ),
                            html.Div([
                                html.Div(
                                    className="d-flex align-items-center gap-2 mb-1",
                                    children=[
                                        html.I(className="fas fa-check me-1",
                                               style={"color": "#10b981", "fontSize": "0.72rem", "width": "12px"}),
                                        html.Span(feat[1], style={"fontSize": "0.78rem",
                                                                   "color": "var(--text-secondary)"}),
                                    ],
                                )
                                for feat in PLAN_FEATURES.get(plan, [])
                            ], style={"marginBottom": "0.75rem"}),
                            dcc.Link(
                                [html.I(className="fas fa-arrow-up me-1"), "Upgrade Plan"],
                                href="/prime",
                                className="btn btn-sm w-100",
                                style={"background": "rgba(255,215,0,0.12)", "color": "#ffd700",
                                       "border": "1px solid rgba(255,215,0,0.3)",
                                       "textDecoration": "none", "textAlign": "center",
                                       "fontSize": "0.82rem", "fontWeight": "700",
                                       "borderRadius": "6px", "padding": "0.4rem"},
                            ) if plan != "prime_boost" else html.Span(
                                [html.I(className="fas fa-crown me-1",
                                        style={"color": "#ffd700"}), "You're on the best plan!"],
                                style={"fontSize": "0.82rem", "color": "#ffd700"},
                            ),
                        ],
                    ),
                    md=6, className="mb-3",
                ),
            ], className="g-3 mb-3"),

            # Recent leads preview
            html.Div(
                className="lc-card p-4",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-3",
                        children=[
                            _section_hdr("fa-bolt", "Recent Leads"),
                            dcc.Link("View all →", href="/leads",
                                     style={"fontSize": "0.8rem", "color": "var(--accent-teal)",
                                            "textDecoration": "none"}),
                        ],
                    ),
                    html.Div([
                        html.Div(
                            className="d-flex align-items-center gap-3 py-2",
                            style={"borderBottom": "1px solid var(--border-color)"},
                            children=[
                                html.Div(
                                    html.I(className={
                                        "whatsapp": "fab fa-whatsapp",
                                        "call":     "fas fa-phone",
                                        "email":    "fas fa-envelope",
                                    }.get(l["contact_method"], "fas fa-question")),
                                    style={
                                        "width": "32px", "height": "32px", "borderRadius": "50%",
                                        "background": {"whatsapp": "#25d36618", "call": "#3b82f618",
                                                       "email": "#f59e0b18"}.get(l["contact_method"], "#6b728018"),
                                        "color": {"whatsapp": "#25d366", "call": "#3b82f6",
                                                  "email": "#f59e0b"}.get(l["contact_method"], "#6b7280"),
                                        "display": "flex", "alignItems": "center",
                                        "justifyContent": "center", "flexShrink": "0",
                                    },
                                ),
                                html.Div(className="flex-grow-1 overflow-hidden", children=[
                                    html.Div(l["requester_name"],
                                             style={"fontWeight": "700", "fontSize": "0.85rem"}),
                                    html.Div(
                                        l["message"][:70] + "…" if len(l["message"]) > 70 else l["message"],
                                        style={"fontSize": "0.75rem", "color": "var(--text-secondary)",
                                               "whiteSpace": "nowrap", "overflow": "hidden",
                                               "textOverflow": "ellipsis"},
                                    ),
                                ]),
                                html.Span(
                                    LEAD_STATUS_LABELS[l["status"]]["label"],
                                    style={
                                        "fontSize": "0.68rem", "fontWeight": "700",
                                        "padding": "0.15rem 0.5rem", "borderRadius": "100px",
                                        "background": f"{LEAD_STATUS_LABELS[l['status']]['color']}18",
                                        "color": LEAD_STATUS_LABELS[l["status"]]["color"],
                                        "border": f"1px solid {LEAD_STATUS_LABELS[l['status']]['color']}40",
                                        "flexShrink": "0",
                                    },
                                ),
                            ],
                        )
                        for l in sorted(MOCK_LEADS, key=lambda x: x["created_at"], reverse=True)[:4]
                    ]),
                ],
            ),
        ],
    )


# ── Completeness helpers ──────────────────────────────────────────────────────

def _compute_completeness(profile: dict) -> int:
    score = 1  # business_name always present
    for field, _ in _COMPLETENESS_FIELDS:
        val = profile.get(field)
        if field == "social":
            if val and any(v for v in val.values()):
                score += 1
        elif field == "service_areas":
            if val:
                score += 1
        elif field == "portfolio":
            if val:
                score += 1
        elif val:
            score += 1
    total = 1 + len(_COMPLETENESS_FIELDS)
    return round(score / total * 100)


def _missing_items(profile: dict) -> list:
    missing = []
    for field, hint in _COMPLETENESS_FIELDS:
        val = profile.get(field)
        if field == "social":
            if not (val and any(v for v in val.values())):
                missing.append(hint)
        elif field in ("service_areas", "portfolio"):
            if not val:
                missing.append(hint)
        elif not val:
            missing.append(hint)
    return missing


# ── Tab: Business Profile Editor ──────────────────────────────────────────────

def _hours_row(day, hours_data):
    is_open = hours_data.get("open", False)
    return html.Div(
        className="d-flex align-items-center gap-2 mb-2",
        children=[
            html.Div(day, style={"width": "90px", "fontSize": "0.82rem",
                                  "fontWeight": "600", "color": "var(--text-secondary)"}),
            dbc.Switch(
                id={"type": "hours-toggle", "index": day},
                value=is_open,
                label="",
                style={"marginBottom": "0"},
            ),
            dcc.Dropdown(
                id={"type": "hours-from", "index": day},
                options=_TIME_OPTIONS,
                value=hours_data.get("from", "08:00"),
                clearable=False,
                className="bg-input",
                style={"width": "110px", "fontSize": "0.78rem",
                       "opacity": "1" if is_open else "0.4", "pointerEvents": "auto"},
                disabled=not is_open,
            ),
            html.Span("to", style={"fontSize": "0.78rem", "color": "var(--text-muted)"}),
            dcc.Dropdown(
                id={"type": "hours-to", "index": day},
                options=_TIME_OPTIONS,
                value=hours_data.get("to", "18:00"),
                clearable=False,
                className="bg-input",
                style={"width": "110px", "fontSize": "0.78rem",
                       "opacity": "1" if is_open else "0.4", "pointerEvents": "auto"},
                disabled=not is_open,
            ),
        ],
    )


def _profile_panel():
    bp = MOCK_BUSINESS_PROFILE
    cat_options = [{"label": c["label"], "value": c["id"]} for c in CATEGORIES]
    city_hoods  = NEIGHBORHOODS_BY_CITY.get(bp["city"], [])

    return html.Div(
        id="dash-panel-profile",
        style={"display": "none"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center mb-4",
                children=[
                    html.H4("Business Profile", style={"fontWeight": "800", "marginBottom": "0"}),
                    dcc.Link(
                        [html.I(className="fas fa-eye me-1"), "Preview Public Profile"],
                        href="/business",
                        target="_blank",
                        style={"fontSize": "0.82rem", "color": "var(--accent-teal)",
                               "textDecoration": "none"},
                    ),
                ],
            ),

            # Completeness inline bar
            html.Div(id="profile-completeness-inline", className="mb-4"),

            dbc.Row([
                # ── Left column (main fields) ─────────────────────────────
                dbc.Col([
                    # Section 1 – Basic Info
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-store", "Basic Information"),
                        html.Label("Business Name", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Input(id="profile-business-name", value=bp["business_name"],
                                  type="text", className="form-control mb-3",
                                  style={"background": "var(--bg-tertiary)",
                                         "border": "1px solid var(--border-color)", "color": "inherit"}),

                        html.Label("Tagline", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Input(id="profile-tagline", value=bp["tagline"],
                                  placeholder="e.g. Licensed Master Electrician – Same-Day Service",
                                  type="text", className="form-control mb-3",
                                  style={"background": "var(--bg-tertiary)",
                                         "border": "1px solid var(--border-color)", "color": "inherit"}),

                        html.Label("Description", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Textarea(id="profile-description", value=bp["description"],
                                     placeholder="Tell customers about your business…",
                                     className="form-control mb-1",
                                     style={"background": "var(--bg-tertiary)",
                                            "border": "1px solid var(--border-color)",
                                            "color": "inherit", "resize": "vertical",
                                            "minHeight": "100px"}),
                        html.Div(id="profile-desc-count",
                                 style={"fontSize": "0.72rem", "color": "var(--text-muted)",
                                        "textAlign": "right", "marginBottom": "0.75rem"}),

                        html.Label("Category", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Dropdown(id="profile-category", options=cat_options,
                                     value=bp["category"], clearable=False,
                                     className="bg-input mb-3"),
                    ]),

                    # Section 2 – Contact & Reach
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-address-book", "Contact & Reach"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Phone", className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-phone", value=bp["phone"], type="tel",
                                          className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                            dbc.Col([
                                html.Label([html.I(className="fab fa-whatsapp me-1",
                                                   style={"color": "#25d366"}), "WhatsApp"],
                                           className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-whatsapp", value=bp["whatsapp"], type="tel",
                                          className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                        ], className="g-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Email", className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-email", value=bp["email"], type="email",
                                          className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                            dbc.Col([
                                html.Label("Website", className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-website", value=bp["website"], type="url",
                                          className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                        ], className="g-2"),
                    ]),

                    # Section 3 – Social Links
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-share-alt", "Social Links"),
                        dbc.Row([
                            dbc.Col([
                                html.Label([html.I(className="fab fa-facebook me-1",
                                                   style={"color": "#1877f2"}), "Facebook"],
                                           className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-facebook",
                                          value=bp["social"].get("facebook", ""),
                                          placeholder="https://facebook.com/yourbusiness",
                                          type="url", className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                            dbc.Col([
                                html.Label([html.I(className="fab fa-instagram me-1",
                                                   style={"color": "#e1306c"}), "Instagram"],
                                           className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-instagram",
                                          value=bp["social"].get("instagram", ""),
                                          placeholder="https://instagram.com/yourbusiness",
                                          type="url", className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                            dbc.Col([
                                html.Label([html.I(className="fab fa-linkedin me-1",
                                                   style={"color": "#0a66c2"}), "LinkedIn"],
                                           className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-linkedin",
                                          value=bp["social"].get("linkedin", ""),
                                          placeholder="https://linkedin.com/company/...",
                                          type="url", className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                            dbc.Col([
                                html.Label([html.I(className="fab fa-x-twitter me-1"), "X / Twitter"],
                                           className="form-label",
                                           style={"fontSize": "0.82rem", "fontWeight": "600"}),
                                dcc.Input(id="profile-twitter",
                                          value=bp["social"].get("twitter", ""),
                                          placeholder="https://x.com/yourbusiness",
                                          type="url", className="form-control mb-3",
                                          style={"background": "var(--bg-tertiary)",
                                                 "border": "1px solid var(--border-color)",
                                                 "color": "inherit"}),
                            ], md=6),
                        ], className="g-2"),
                    ]),

                    # Section 4 – Business Hours
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-clock", "Business Hours"),
                        html.Div(id="business-hours-editor", children=[
                            _hours_row(day, bp["hours"].get(day, {"open": False}))
                            for day in ["Monday", "Tuesday", "Wednesday",
                                        "Thursday", "Friday", "Saturday", "Sunday"]
                        ]),
                    ]),

                ], md=8),

                # ── Right column (branding + service areas + portfolio) ────
                dbc.Col([
                    # Branding
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-image", "Branding"),
                        html.Div(
                            style={"position": "relative", "marginBottom": "1rem"},
                            children=[
                                html.Div(
                                    style={"height": "90px",
                                           "backgroundImage": f"url({bp['cover']})",
                                           "backgroundSize": "cover",
                                           "backgroundPosition": "center",
                                           "borderRadius": "8px",
                                           "border": "1px solid var(--border-color)"},
                                ),
                                html.Img(
                                    src=bp["logo"],
                                    id="profile-logo-preview",
                                    style={"width": "52px", "height": "52px",
                                           "borderRadius": "50%",
                                           "border": "3px solid var(--bg-secondary)",
                                           "objectFit": "cover",
                                           "position": "absolute",
                                           "bottom": "-16px", "left": "12px"},
                                ),
                            ],
                        ),
                        html.Div(style={"marginTop": "1.5rem"}, children=[
                            html.Label("Logo URL", className="form-label",
                                       style={"fontSize": "0.78rem", "fontWeight": "600"}),
                            dcc.Input(id="profile-logo", value=bp["logo"],
                                      placeholder="https://…",
                                      type="url", className="form-control mb-2",
                                      style={"fontSize": "0.78rem",
                                             "background": "var(--bg-tertiary)",
                                             "border": "1px solid var(--border-color)",
                                             "color": "inherit"}),
                            html.Label("Cover Photo URL", className="form-label",
                                       style={"fontSize": "0.78rem", "fontWeight": "600"}),
                            dcc.Input(id="profile-cover", value=bp["cover"],
                                      placeholder="https://…",
                                      type="url", className="form-control",
                                      style={"fontSize": "0.78rem",
                                             "background": "var(--bg-tertiary)",
                                             "border": "1px solid var(--border-color)",
                                             "color": "inherit"}),
                        ]),
                    ]),

                    # Service Areas
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-map-marker-alt", "Service Areas"),
                        html.Label("City", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dcc.Dropdown(
                            id="profile-city",
                            options=[{"label": c, "value": c}
                                     for c in ["Miami", "Los Angeles", "New York", "Houston",
                                               "Chicago", "Phoenix", "Dallas", "San Antonio"]],
                            value=bp["city"], clearable=False,
                            className="bg-input mb-2",
                        ),
                        html.Label("Neighborhoods Served", className="form-label",
                                   style={"fontSize": "0.82rem", "fontWeight": "600"}),
                        dbc.Checklist(
                            id="profile-service-areas",
                            options=[{"label": h, "value": h} for h in city_hoods],
                            value=bp["service_areas"],
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"fontSize": "0.78rem", "color": "var(--text-secondary)"},
                        ),
                    ]),

                    # Portfolio
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_hdr("fa-images", "Portfolio"),
                        html.P("Showcase your best work — up to 10 photos.",
                               style={"fontSize": "0.78rem", "color": "var(--text-muted)",
                                      "marginBottom": "0.6rem"}),
                        dcc.Upload(
                            id="portfolio-upload",
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-lg mb-1",
                                       style={"color": "var(--accent-teal)"}),
                                html.Div("Upload photos",
                                         style={"fontSize": "0.78rem", "color": "var(--text-muted)"}),
                            ], className="text-center py-2"),
                            accept="image/jpeg,image/jpg,image/png,image/webp",
                            multiple=True,
                            style={"border": "1.5px dashed var(--border-color)",
                                   "borderRadius": "6px", "cursor": "pointer",
                                   "marginBottom": "0.5rem"},
                        ),
                        html.Div(
                            id="portfolio-preview",
                            className="d-flex flex-wrap gap-2 mt-2",
                            children=[
                                html.Div(style={"position": "relative"}, children=[
                                    html.Img(
                                        src=img,
                                        style={"width": "80px", "height": "60px",
                                               "objectFit": "cover", "borderRadius": "4px",
                                               "border": "1px solid var(--border-color)"},
                                    ),
                                    html.Button(
                                        "×",
                                        id={"type": "portfolio-remove-btn", "index": i},
                                        n_clicks=0,
                                        style={"position": "absolute", "top": "2px", "right": "2px",
                                               "background": "rgba(13,17,23,0.7)", "color": "#fff",
                                               "border": "none", "borderRadius": "50%",
                                               "width": "18px", "height": "18px",
                                               "fontSize": "0.8rem", "lineHeight": "1",
                                               "cursor": "pointer", "padding": "0",
                                               "display": "flex", "alignItems": "center",
                                               "justifyContent": "center"},
                                    ),
                                ])
                                for i, img in enumerate(bp["portfolio"])
                            ],
                        ),
                        dcc.Store(id="portfolio-store", data=bp["portfolio"]),
                    ]),

                ], md=4),
            ], className="g-3"),

            # Save bar
            html.Div(
                className="d-flex align-items-center gap-3 mt-2",
                children=[
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "Save Changes"],
                        id="profile-save-btn",
                        className="btn-teal px-4",
                        n_clicks=0,
                    ),
                    html.Div(id="profile-save-alert"),
                ],
            ),
        ],
    )


# ── Tab: My Listings (inline) ─────────────────────────────────────────────────

def _listings_panel():
    from los_classificados.layouts.my_listings import _listing_card, _plan_comparison_modal
    active = [l for l in MOCK_USER_LISTINGS if l["status"] == "active"]
    other  = [l for l in MOCK_USER_LISTINGS if l["status"] != "active"]

    return html.Div(
        id="dash-panel-listings",
        style={"display": "none"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center mb-4",
                children=[
                    html.H4("My Listings", style={"fontWeight": "800", "marginBottom": "0"}),
                    dcc.Link(
                        [html.I(className="fas fa-plus me-1"), "Post New Ad"],
                        href="/post-ad",
                        className="btn btn-sm btn-teal px-3",
                        style={"textDecoration": "none", "fontSize": "0.82rem"},
                    ),
                ],
            ),
            dcc.Store(id="dash-listings-overrides", data={}),
            html.Div(id="dash-listings-container", children=[
                html.Div([
                    html.Div("Active",
                             style={"fontSize": "0.72rem", "fontWeight": "700",
                                    "color": "#10b981", "textTransform": "uppercase",
                                    "letterSpacing": "0.06em", "marginBottom": "0.5rem"}),
                    *[_listing_card(l) for l in active],
                ]) if active else None,
                html.Div([
                    html.Hr(className="divider"),
                    html.Div("Paused / Expired",
                             style={"fontSize": "0.72rem", "fontWeight": "700",
                                    "color": "var(--text-muted)", "textTransform": "uppercase",
                                    "letterSpacing": "0.06em", "marginBottom": "0.5rem"}),
                    *[_listing_card(l) for l in other],
                ]) if other else None,
            ]),
            _plan_comparison_modal(),
            dbc.Toast(
                id="dash-listings-toast",
                header="", is_open=False, dismissable=True, duration=3500,
                style={"position": "fixed", "bottom": "1.5rem", "right": "1.5rem",
                       "minWidth": "280px", "zIndex": "9999",
                       "background": "var(--bg-secondary)",
                       "border": "1px solid var(--border-color)"},
            ),
        ],
    )


# ── Tab: Analytics ────────────────────────────────────────────────────────────

def _build_views_chart():
    days = list(range(1, 31))
    views = BUSINESS_ANALYTICS["daily_views"]
    leads = BUSINESS_ANALYTICS["daily_leads"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=views, name="Views",
        line={"color": "#00c9a7", "width": 2},
        fill="tozeroy", fillcolor="rgba(0,201,167,0.08)",
        hovertemplate="%{y} views<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=days, y=leads, name="Leads",
        line={"color": "#ffd700", "width": 2, "dash": "dot"},
        yaxis="y2",
        hovertemplate="%{y} leads<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 11},
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        height=220,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02,
                "xanchor": "right", "x": 1, "font": {"size": 11}},
        xaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False,
               "title": {"text": "Day of month", "font": {"size": 10}}},
        yaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False,
               "title": {"text": "Views", "font": {"size": 10}}},
        yaxis2={"overlaying": "y", "side": "right", "showgrid": False,
                "zeroline": False, "title": {"text": "Leads", "font": {"size": 10}}},
        hovermode="x unified",
    )
    return fig


def _build_source_chart():
    sources = BUSINESS_ANALYTICS["lead_sources"]
    colors  = ["#25d366", "#3b82f6", "#f59e0b"]
    fig = go.Figure(go.Pie(
        labels=list(sources.keys()),
        values=list(sources.values()),
        hole=0.55,
        marker={"colors": colors, "line": {"color": "#161b22", "width": 2}},
        textinfo="label+percent",
        textfont={"size": 11},
        hovertemplate="%{label}: %{value} leads<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter"},
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=220,
        showlegend=False,
    )
    return fig


def _build_ctr_chart():
    weeks = [f"Wk {i+1}" for i in range(8)]
    ctr   = BUSINESS_ANALYTICS["weekly_ctr"]
    fig = go.Figure(go.Bar(
        x=weeks, y=ctr,
        marker_color=["#00c9a7" if v == max(ctr) else "#21262d" for v in ctr],
        marker_line_width=0,
        hovertemplate="%{y:.1f}% CTR<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8b949e", "family": "Inter", "size": 11},
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        height=180,
        xaxis={"gridcolor": "rgba(0,0,0,0)", "showline": False, "zeroline": False},
        yaxis={"gridcolor": "#21262d", "showline": False, "zeroline": False,
               "ticksuffix": "%"},
        bargap=0.35,
    )
    return fig


def _analytics_panel():
    analytics = BUSINESS_ANALYTICS
    total_views = sum(analytics["daily_views"])
    total_leads = sum(analytics["daily_leads"])
    best_day_idx = analytics["daily_views"].index(max(analytics["daily_views"])) + 1
    avg_ctr  = round(sum(analytics["weekly_ctr"]) / len(analytics["weekly_ctr"]), 1)

    top = analytics["top_listings"]

    return html.Div(
        id="dash-panel-analytics",
        style={"display": "none"},
        children=[
            html.H4("Analytics", style={"fontWeight": "800", "marginBottom": "1.5rem"}),

            # Summary KPIs
            dbc.Row([
                dbc.Col(_kpi(total_views, "Views (30d)",  "fa-eye",         delta="+18%"),    xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(total_leads, "Leads (30d)",  "fa-bolt",        "#ffd700"),       xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(f"{avg_ctr}%", "Avg CTR",   "fa-mouse-pointer","#3b82f6"),       xs=6, lg=3, className="mb-3"),
                dbc.Col(_kpi(f"Day {best_day_idx}", "Peak Day", "fa-calendar-check", "#10b981"), xs=6, lg=3, className="mb-3"),
            ], className="g-3 mb-3"),

            # Charts row
            dbc.Row([
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Views & Leads – Last 30 Days",
                                 style={"fontSize": "0.82rem", "fontWeight": "700",
                                        "color": "var(--text-muted)", "marginBottom": "0.5rem"}),
                        dcc.Graph(figure=_build_views_chart(), config={"displayModeBar": False}),
                    ]),
                    md=8, className="mb-3",
                ),
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Lead Sources",
                                 style={"fontSize": "0.82rem", "fontWeight": "700",
                                        "color": "var(--text-muted)", "marginBottom": "0.5rem"}),
                        dcc.Graph(figure=_build_source_chart(), config={"displayModeBar": False}),
                    ]),
                    md=4, className="mb-3",
                ),
            ], className="g-3 mb-3"),

            # CTR + Top listings
            dbc.Row([
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Click-Through Rate – Weekly",
                                 style={"fontSize": "0.82rem", "fontWeight": "700",
                                        "color": "var(--text-muted)", "marginBottom": "0.5rem"}),
                        dcc.Graph(figure=_build_ctr_chart(), config={"displayModeBar": False}),
                    ]),
                    md=5, className="mb-3",
                ),
                dbc.Col(
                    html.Div(className="lc-card p-3", children=[
                        html.Div("Top Performing Listings",
                                 style={"fontSize": "0.82rem", "fontWeight": "700",
                                        "color": "var(--text-muted)", "marginBottom": "0.75rem"}),
                        html.Table(
                            className="w-100",
                            style={"fontSize": "0.78rem", "borderCollapse": "collapse"},
                            children=[
                                html.Thead(html.Tr([
                                    html.Th("Listing", style={"padding": "0.25rem 0.4rem",
                                                               "color": "var(--text-muted)",
                                                               "borderBottom": "1px solid var(--border-color)",
                                                               "fontWeight": "600"}),
                                    html.Th("Views", style={"padding": "0.25rem 0.4rem", "textAlign": "right",
                                                             "color": "var(--text-muted)",
                                                             "borderBottom": "1px solid var(--border-color)",
                                                             "fontWeight": "600"}),
                                    html.Th("Leads", style={"padding": "0.25rem 0.4rem", "textAlign": "right",
                                                             "color": "var(--text-muted)",
                                                             "borderBottom": "1px solid var(--border-color)",
                                                             "fontWeight": "600"}),
                                ])),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(
                                            lst["title"][:32] + "…" if len(lst["title"]) > 32 else lst["title"],
                                            style={"padding": "0.3rem 0.4rem",
                                                   "borderBottom": "1px solid var(--border-color)",
                                                   "color": "var(--text-secondary)"}
                                        ),
                                        html.Td(
                                            str(lst["views"]),
                                            style={"padding": "0.3rem 0.4rem", "textAlign": "right",
                                                   "borderBottom": "1px solid var(--border-color)",
                                                   "color": "var(--accent-teal)", "fontWeight": "700"}
                                        ),
                                        html.Td(
                                            str(lst["leads"]),
                                            style={"padding": "0.3rem 0.4rem", "textAlign": "right",
                                                   "borderBottom": "1px solid var(--border-color)",
                                                   "color": "#ffd700", "fontWeight": "700"}
                                        ),
                                    ])
                                    for lst in top
                                ]),
                            ],
                        ),
                    ]),
                    md=7, className="mb-3",
                ),
            ], className="g-3"),
        ],
    )


# ── Main dashboard layout ─────────────────────────────────────────────────────

def dashboard_layout(active_tab="overview"):
    return html.Div([
        # Page header bar
        html.Div(
            style={"background": "var(--bg-secondary)",
                   "borderBottom": "1px solid var(--border-color)",
                   "padding": "0.75rem 0"},
            children=[
                dbc.Container(
                    html.Div(className="d-flex align-items-center gap-2", children=[
                        html.I(className="fas fa-tachometer-alt",
                               style={"color": "var(--accent-teal)"}),
                        html.Span("Business Dashboard",
                                  style={"fontWeight": "800", "fontSize": "1rem"}),
                        html.Span("·", style={"color": "var(--text-muted)"}),
                        html.Span(MOCK_BUSINESS_PROFILE["business_name"],
                                  style={"fontSize": "0.9rem", "color": "var(--text-secondary)"}),
                    ]),
                    fluid=False,
                ),
            ],
        ),

        # Dashboard body: sidebar + content
        dbc.Container(
            html.Div(
                className="d-flex",
                style={"minHeight": "calc(100vh - 120px)", "gap": "0"},
                children=[
                    # Left sidebar
                    _sidebar(active_tab),

                    # Main content area
                    html.Div(
                        className="flex-grow-1 p-4 overflow-auto",
                        style={"minWidth": "0"},
                        children=[
                            dcc.Store(id="dashboard-active-tab", data=active_tab),
                            dcc.Store(id="business-profile-store",
                                      data=MOCK_BUSINESS_PROFILE),
                            _overview_panel(),
                            _profile_panel(),
                            _listings_panel(),
                            _analytics_panel(),
                        ],
                    ),
                ],
            ),
            fluid=True,
            style={"padding": "0"},
        ),
    ])
