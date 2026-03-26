"""Dashboard callbacks – tab navigation, profile editing, portfolio, listings, analytics."""
from datetime import datetime, timedelta

import dash
from dash import Input, Output, State, ALL, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import (
    MOCK_USER_LISTINGS, MOCK_BUSINESS_PROFILE,
    NEIGHBORHOODS_BY_CITY,
)

# ── Tab IDs in render order ───────────────────────────────────────────────────

_TABS = ["overview", "profile", "listings", "analytics"]

_PLAN_LABEL  = {"free": "Free", "featured": "⚡ Featured", "prime_boost": "★ Prime"}
_STATUS_LABEL = {"active": "Active", "paused": "Paused", "expired": "Expired"}

_PLAN_COLOR = {
    "free":        ("var(--text-muted)",   "transparent",             "1px solid var(--border-color)"),
    "featured":    ("#ff6b35",             "rgba(255,107,53,0.12)",   "1px solid rgba(255,107,53,0.4)"),
    "prime_boost": ("#ffd700",             "rgba(255,215,0,0.1)",     "1px solid rgba(255,215,0,0.4)"),
}
_STATUS_COLOR = {
    "active":  ("#10b981", "rgba(16,185,129,0.12)"),
    "paused":  ("#f59e0b", "rgba(245,158,11,0.12)"),
    "expired": ("#6b7280", "rgba(107,114,128,0.12)"),
}

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


def _compute_completeness(profile: dict) -> int:
    score = 1  # base point for having an account
    for field, _ in _COMPLETENESS_FIELDS:
        val = profile.get(field)
        if field == "social":
            if isinstance(val, dict) and any(v for v in val.values()):
                score += 1
        elif val:
            score += 1
    return round(score / (len(_COMPLETENESS_FIELDS) + 1) * 100)


def _missing_items(profile: dict) -> list:
    missing = []
    for field, hint in _COMPLETENESS_FIELDS:
        val = profile.get(field)
        if field == "social":
            if not isinstance(val, dict) or not any(v for v in val.values()):
                missing.append(hint)
        elif not val:
            missing.append(hint)
    return missing


# ── Tab switching ─────────────────────────────────────────────────────────────

@app.callback(
    Output("dash-panel-overview",  "style"),
    Output("dash-panel-profile",   "style"),
    Output("dash-panel-listings",  "style"),
    Output("dash-panel-analytics", "style"),
    Output("dashboard-active-tab", "data"),
    Input({"type": "dash-nav-btn", "index": ALL}, "n_clicks"),
    State("dashboard-active-tab", "data"),
    prevent_initial_call=True,
)
def switch_dashboard_tab(n_clicks_list, current_tab):
    """Show the clicked tab panel and hide all others."""
    triggered = dash.ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        raise PreventUpdate
    if not any(n for n in n_clicks_list if n):
        raise PreventUpdate

    active = triggered["index"]
    styles = [
        {} if tab == active else {"display": "none"}
        for tab in _TABS
    ]
    return (*styles, active)


# ── Profile: description char count ──────────────────────────────────────────

@app.callback(
    Output("profile-desc-count", "children"),
    Input("profile-description", "value"),
    prevent_initial_call=False,
)
def update_desc_count(value):
    n = len(value) if value else 0
    color = "#ef4444" if n > 1200 else "var(--text-muted)"
    return html.Span(f"{n}/1200", style={"color": color, "fontSize": "0.72rem"})


# ── Profile: logo/cover URL preview ──────────────────────────────────────────

@app.callback(
    Output("profile-logo-preview", "src"),
    Input("profile-logo", "value"),
    prevent_initial_call=False,
)
def update_logo_preview(url):
    return url or ""


# ── Profile: city → service areas options ────────────────────────────────────

@app.callback(
    Output("profile-service-areas", "options"),
    Output("profile-service-areas", "value"),
    Input("profile-city", "value"),
    State("business-profile-store", "data"),
    prevent_initial_call=False,
)
def update_service_areas(city, profile_data):
    profile_data = profile_data or MOCK_BUSINESS_PROFILE
    neighborhoods = NEIGHBORHOODS_BY_CITY.get(city or "", [])
    options = [{"label": n, "value": n} for n in neighborhoods]
    # Restore saved values that still apply to new city
    saved = profile_data.get("service_areas", [])
    valid = [v for v in saved if v in neighborhoods]
    return options, valid


# ── Profile: business hours toggle (enable/disable time dropdowns) ────────────

@app.callback(
    Output({"type": "hours-from", "index": ALL}, "disabled"),
    Output({"type": "hours-to",   "index": ALL}, "disabled"),
    Input({"type": "hours-toggle", "index": ALL}, "value"),
    prevent_initial_call=False,
)
def update_hours_dropdowns(toggle_values):
    """Disable from/to dropdowns when day toggle is off."""
    # toggle_values is a list of bool values matching the ALL pattern order
    disabled_list = [not v for v in toggle_values]
    return disabled_list, disabled_list


# ── Profile: completeness inline bar ─────────────────────────────────────────

@app.callback(
    Output("profile-completeness-inline", "children"),
    Input("business-profile-store", "data"),
    prevent_initial_call=False,
)
def update_profile_completeness(profile_data):
    profile = profile_data or MOCK_BUSINESS_PROFILE
    score = _compute_completeness(profile)
    missing = _missing_items(profile)
    bar_color = "success" if score >= 80 else ("warning" if score >= 50 else "danger")
    hex_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 50 else "#ef4444")

    tips = [
        html.Li(
            [html.I(className="fas fa-circle me-2",
                    style={"color": "#ef4444", "fontSize": "0.5rem", "verticalAlign": "middle"}),
             item],
            style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "2px"},
        )
        for item in missing[:3]
    ]

    return html.Div(
        className="lc-card p-3 mb-4",
        children=[
            html.Div(
                className="d-flex align-items-center gap-3 mb-2",
                children=[
                    html.Span(f"{score}%", style={"fontWeight": "800", "fontSize": "1.4rem",
                                                    "color": hex_color}),
                    html.Div(
                        dbc.Progress(value=score, color=bar_color,
                                     style={"height": "8px", "borderRadius": "4px"}),
                        style={"flexGrow": "1"},
                    ),
                    html.Span("Profile complete", style={"fontSize": "0.78rem",
                                                          "color": "var(--text-muted)"}),
                ],
            ),
            *([html.Ul(tips, style={"paddingLeft": "0", "listStyle": "none", "marginBottom": "0"})]
              if tips else []),
        ],
    )


# ── Profile: portfolio upload ─────────────────────────────────────────────────

@app.callback(
    Output("portfolio-store", "data"),
    Output("portfolio-preview", "children"),
    Input("portfolio-upload", "contents"),
    Input({"type": "portfolio-remove-btn", "index": ALL}, "n_clicks"),
    State("portfolio-store", "data"),
    State("portfolio-upload", "filename"),
    prevent_initial_call=True,
)
def manage_portfolio(contents, remove_clicks, stored, filenames):
    """Handle portfolio image upload and removal."""
    triggered = dash.ctx.triggered_id
    stored = list(stored or [])

    if triggered == "portfolio-upload" and contents:
        # contents may be a single string or list
        if isinstance(contents, str):
            contents = [contents]
        for data_uri in contents:
            if len(stored) < 10 and data_uri not in stored:
                stored.append(data_uri)

    elif isinstance(triggered, dict) and triggered.get("type") == "portfolio-remove-btn":
        idx = triggered["index"]
        if 0 <= idx < len(stored):
            stored.pop(idx)

    # Build preview grid
    preview_items = []
    for i, src in enumerate(stored):
        preview_items.append(
            dbc.Col(
                html.Div(
                    style={"position": "relative"},
                    children=[
                        html.Img(src=src, style={
                            "width": "100%", "height": "100px", "objectFit": "cover",
                            "borderRadius": "6px",
                        }),
                        html.Button(
                            html.I(className="fas fa-times"),
                            id={"type": "portfolio-remove-btn", "index": i},
                            n_clicks=0,
                            style={
                                "position": "absolute", "top": "4px", "right": "4px",
                                "background": "rgba(0,0,0,0.6)", "color": "#fff",
                                "border": "none", "borderRadius": "50%",
                                "width": "22px", "height": "22px",
                                "display": "flex", "alignItems": "center",
                                "justifyContent": "center", "cursor": "pointer",
                                "fontSize": "0.65rem", "padding": "0",
                            },
                        ),
                    ],
                ),
                xs=6, sm=4, md=3, className="mb-2",
            )
        )

    preview = dbc.Row(preview_items) if preview_items else html.Div(
        "No portfolio photos yet.",
        style={"color": "var(--text-muted)", "fontSize": "0.82rem"},
    )
    return stored, preview


# ── Profile: save ─────────────────────────────────────────────────────────────

@app.callback(
    Output("business-profile-store", "data"),
    Output("profile-save-alert", "children"),
    Input("profile-save-btn", "n_clicks"),
    State("profile-business-name", "value"),
    State("profile-tagline",       "value"),
    State("profile-description",   "value"),
    State("profile-category",      "value"),
    State("profile-phone",         "value"),
    State("profile-whatsapp",      "value"),
    State("profile-email",         "value"),
    State("profile-website",       "value"),
    State("profile-facebook",      "value"),
    State("profile-instagram",     "value"),
    State("profile-linkedin",      "value"),
    State("profile-twitter",       "value"),
    State("profile-logo",          "value"),
    State("profile-cover",         "value"),
    State("profile-city",          "value"),
    State("profile-service-areas", "value"),
    State("portfolio-store",       "data"),
    State("business-profile-store","data"),
    prevent_initial_call=True,
)
def save_profile(n_clicks,
                 biz_name, tagline, description, category,
                 phone, whatsapp, email, website,
                 facebook, instagram, linkedin, twitter,
                 logo, cover, city, service_areas, portfolio,
                 current_profile):
    if not n_clicks:
        raise PreventUpdate

    updated = dict(current_profile or MOCK_BUSINESS_PROFILE)
    updated.update({
        "business_name": biz_name or "",
        "tagline":       tagline or "",
        "description":   description or "",
        "category":      category or "",
        "phone":         phone or "",
        "whatsapp":      whatsapp or "",
        "email":         email or "",
        "website":       website or "",
        "social": {
            "facebook":  facebook or "",
            "instagram": instagram or "",
            "linkedin":  linkedin or "",
            "twitter":   twitter or "",
        },
        "logo":          logo or "",
        "cover":         cover or "",
        "city":          city or "",
        "service_areas": service_areas or [],
        "portfolio":     portfolio or [],
    })

    alert = dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Profile saved successfully!"],
        color="success",
        dismissable=True,
        duration=3000,
        style={"fontSize": "0.85rem", "padding": "0.5rem 1rem"},
    )
    return updated, alert


# ── Dashboard listings: bump to top ──────────────────────────────────────────

def _badge(text, color, bg, border="none"):
    return html.Span(text, style={
        "background": bg, "color": color, "border": border,
        "borderRadius": "100px", "padding": "0.1rem 0.55rem",
        "fontSize": "0.72rem", "fontWeight": "700",
    })


def _build_dash_card(lst):
    """Rebuild a listing card for the dashboard panel."""
    from los_classificados.layouts.my_listings import _listing_card
    return _listing_card(lst)


def _resolve_listings(overrides):
    """Merge overrides into mock listing data, handling ISO-string dates."""
    overrides = overrides or {}
    result = []
    for base in MOCK_USER_LISTINGS:
        lst = dict(base)
        if str(lst["id"]) in overrides:
            lst.update(overrides[str(lst["id"])])
        if isinstance(lst.get("expires_at"), str):
            lst["expires_at"] = datetime.fromisoformat(lst["expires_at"])
        result.append(lst)
    return result


def _render_dash_listings(listings):
    """Render the two-section (active / paused+expired) layout."""
    from los_classificados.layouts.my_listings import _listing_card

    active = [l for l in listings if l["status"] == "active"]
    other  = [l for l in listings if l["status"] != "active"]

    children = []
    if active:
        children.append(html.Div([
            html.Div("Active",
                     style={"fontSize": "0.72rem", "fontWeight": "700",
                            "color": "#10b981", "textTransform": "uppercase",
                            "letterSpacing": "0.06em", "marginBottom": "0.5rem"}),
            *[_listing_card(l) for l in active],
        ]))
    if other:
        children.append(html.Div([
            html.Hr(className="divider"),
            html.Div("Paused / Expired",
                     style={"fontSize": "0.72rem", "fontWeight": "700",
                            "color": "var(--text-muted)", "textTransform": "uppercase",
                            "letterSpacing": "0.06em", "marginBottom": "0.5rem"}),
            *[_listing_card(l) for l in other],
        ]))
    if not children:
        children.append(html.Div(
            className="text-center py-5",
            children=[
                html.I(className="fas fa-clipboard-list fa-3x mb-3",
                       style={"color": "var(--text-muted)"}),
                html.H5("No listings yet", style={"color": "var(--text-secondary)"}),
                dcc.Link("Post your first ad →", href="/post-ad",
                         style={"color": "var(--accent-teal)", "fontSize": "0.88rem"}),
            ],
        ))
    return children


@app.callback(
    Output("dash-listings-overrides", "data"),
    Output("dash-listings-toast", "children"),
    Output("dash-listings-toast", "header"),
    Output("dash-listings-toast", "is_open"),
    Input({"type": "bump-listing-btn",   "index": ALL}, "n_clicks"),
    State("dash-listings-overrides", "data"),
    prevent_initial_call=True,
)
def dash_bump_listing(n_clicks_list, overrides):
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    listing_id = dash.ctx.triggered_id["index"]
    overrides  = dict(overrides or {})
    entry = overrides.get(str(listing_id), {})
    entry["created_at"] = datetime.now().isoformat()
    overrides[str(listing_id)] = entry

    title = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short = title[:40] + "…" if len(title) > 40 else title
    msg = html.Span([html.Strong(f'"{short}"'), " has been bumped to the top."],
                    style={"fontSize": "0.82rem"})
    return overrides, msg, "Bumped!", True


@app.callback(
    Output("dash-listings-overrides", "data", allow_duplicate=True),
    Output("dash-listings-toast", "children", allow_duplicate=True),
    Output("dash-listings-toast", "header",   allow_duplicate=True),
    Output("dash-listings-toast", "is_open",  allow_duplicate=True),
    Input({"type": "toggle-listing-btn", "index": ALL}, "n_clicks"),
    State("dash-listings-overrides", "data"),
    prevent_initial_call=True,
)
def dash_toggle_listing(n_clicks_list, overrides):
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    listing_id = dash.ctx.triggered_id["index"]
    overrides  = dict(overrides or {})
    base_status = next(
        (l["status"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "active"
    )
    current   = overrides.get(str(listing_id), {}).get("status", base_status)
    new_status = "paused" if current == "active" else "active"
    entry = overrides.get(str(listing_id), {})
    entry["status"] = new_status
    overrides[str(listing_id)] = entry

    title  = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short  = title[:40] + "…" if len(title) > 40 else title
    action = "paused" if new_status == "paused" else "resumed"
    msg = html.Span([html.Strong(f'"{short}"'), f" has been {action}."],
                    style={"fontSize": "0.82rem"})
    header = "Listing Paused" if new_status == "paused" else "Listing Resumed"
    return overrides, msg, header, True


@app.callback(
    Output("dash-listings-overrides", "data", allow_duplicate=True),
    Output("dash-listings-toast", "children", allow_duplicate=True),
    Output("dash-listings-toast", "header",   allow_duplicate=True),
    Output("dash-listings-toast", "is_open",  allow_duplicate=True),
    Input({"type": "renew-listing-btn", "index": ALL}, "n_clicks"),
    State("dash-listings-overrides", "data"),
    prevent_initial_call=True,
)
def dash_renew_listing(n_clicks_list, overrides):
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    listing_id = dash.ctx.triggered_id["index"]
    overrides  = dict(overrides or {})
    entry = overrides.get(str(listing_id), {})
    entry["status"]     = "active"
    entry["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    overrides[str(listing_id)] = entry

    title = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short = title[:40] + "…" if len(title) > 40 else title
    msg = html.Span([html.Strong(f'"{short}"'), " has been renewed for 30 days."],
                    style={"fontSize": "0.82rem"})
    return overrides, msg, "Listing Renewed", True


@app.callback(
    Output("dash-listings-container", "children"),
    Input("dash-listings-overrides", "data"),
    prevent_initial_call=False,
)
def refresh_dash_listings(overrides):
    """Re-render the dashboard listings panel whenever overrides change."""
    listings = _resolve_listings(overrides)
    return _render_dash_listings(listings)


# ── Business profile: quote request form ─────────────────────────────────────

@app.callback(
    Output("biz-quote-result", "children"),
    Input("biz-quote-submit", "n_clicks"),
    State("biz-quote-name",    "value"),
    State("biz-quote-phone",   "value"),
    State("biz-quote-email",   "value"),
    State("biz-quote-message", "value"),
    prevent_initial_call=True,
)
def submit_biz_quote(n_clicks, name, phone, email, message):
    if not n_clicks:
        raise PreventUpdate
    errors = []
    if not name:
        errors.append("Your name is required.")
    if not phone and not email:
        errors.append("Please provide a phone number or email.")
    if not message:
        errors.append("Please describe your project.")
    if errors:
        return dbc.Alert(
            [html.Ul([html.Li(e) for e in errors], className="mb-0")],
            color="danger", style={"fontSize": "0.8rem"},
        )
    return dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"),
         "Your request has been sent! The business will contact you shortly."],
        color="success", style={"fontSize": "0.82rem"},
    )
