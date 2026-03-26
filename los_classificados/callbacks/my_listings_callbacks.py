"""My Listings callbacks – filter/sort, bump, upgrade, pause/resume, renew."""
from datetime import datetime, timedelta

import dash
from dash import Input, Output, State, ALL, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import MOCK_USER_LISTINGS

_PLAN_LABEL = {"free": "Free", "featured": "⚡ Featured", "prime_boost": "★ Prime"}
_STATUS_LABEL = {"active": "Active", "paused": "Paused", "expired": "Expired"}

_PLAN_COLOR = {
    "free":        ("var(--text-muted)",   "transparent",              "1px solid var(--border-color)"),
    "featured":    ("#ff6b35",             "rgba(255,107,53,0.12)",    "1px solid rgba(255,107,53,0.4)"),
    "prime_boost": ("#ffd700",             "rgba(255,215,0,0.1)",      "1px solid rgba(255,215,0,0.4)"),
}
_STATUS_COLOR = {
    "active":  ("#10b981", "rgba(16,185,129,0.12)"),
    "paused":  ("#f59e0b", "rgba(245,158,11,0.12)"),
    "expired": ("#6b7280", "rgba(107,114,128,0.12)"),
}


def _badge(text, color, bg, border="none"):
    return html.Span(
        text,
        style={
            "background": bg, "color": color, "border": border,
            "borderRadius": "100px", "padding": "0.1rem 0.55rem",
            "fontSize": "0.72rem", "fontWeight": "700",
        },
    )


def _plan_badge(plan):
    color, bg, border = _PLAN_COLOR.get(plan, _PLAN_COLOR["free"])
    return _badge(_PLAN_LABEL.get(plan, plan), color, bg, border)


def _status_badge(status):
    color, bg = _STATUS_COLOR.get(status, ("#6b7280", "rgba(107,114,128,0.12)"))
    return _badge(_STATUS_LABEL.get(status, status).upper(), color, bg)


def _build_card(lst):
    """Re-render a single listing card from current (possibly overridden) data."""
    status     = lst["status"]
    plan       = lst["plan"]
    is_expired = status == "expired"
    is_paused  = status == "paused"

    days_left = (lst["expires_at"] - datetime.now()).days
    if is_expired:
        expiry_text  = "Expired"
        expiry_color = "#6b7280"
    elif days_left <= 3:
        expiry_text  = f"Expires in {days_left}d"
        expiry_color = "#ef4444"
    else:
        expiry_text  = f"{days_left}d remaining"
        expiry_color = "var(--text-muted)"

    card_style = {"opacity": "0.65"} if is_expired or is_paused else {}

    return html.Div(
        className="lc-card d-flex mb-3",
        style={**card_style, "overflow": "hidden"},
        children=[
            html.Img(
                src=lst["image"],
                style={"width": "130px", "minWidth": "130px", "objectFit": "cover"},
                alt=lst["title"],
            ),
            html.Div(
                className="p-3 d-flex flex-column flex-grow-1",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-start mb-1",
                        children=[
                            html.Div(className="d-flex gap-1 flex-wrap", children=[
                                _status_badge(status),
                                _plan_badge(plan),
                                html.Span(lst["subcategory"], className="badge-cat"),
                            ]),
                            html.Small(expiry_text,
                                       style={"color": expiry_color, "fontSize": "0.72rem",
                                              "whiteSpace": "nowrap"}),
                        ],
                    ),
                    html.Div(lst["title"], className="listing-title mb-1",
                             style={"fontSize": "0.95rem"}),
                    html.Small(
                        [html.I(className="fas fa-map-marker-alt me-1"),
                         lst["city"], " · ", lst["neighborhood"]],
                        style={"color": "var(--text-muted)", "fontSize": "0.75rem"},
                    ),
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
                            html.Span(lst["price_label"], className="listing-price",
                                      style={"fontSize": "0.88rem"}),
                        ],
                    ),
                    html.Div(
                        className="d-flex gap-2 mt-auto pt-2 flex-wrap",
                        children=[
                            dbc.Button(
                                [html.I(className="fas fa-arrow-up me-1"), "Bump"],
                                id={"type": "bump-listing-btn", "index": lst["id"]},
                                size="sm", className="btn-teal", n_clicks=0,
                                style={"fontSize": "0.75rem"},
                                disabled=is_expired,
                            ) if plan != "prime_boost" else None,
                            dbc.Button(
                                [html.I(className="fas fa-star me-1"),
                                 "Upgrade to Prime" if plan == "featured" else "Upgrade"],
                                id={"type": "upgrade-listing-btn", "index": lst["id"]},
                                size="sm", color="warning", outline=True, n_clicks=0,
                                style={"fontSize": "0.75rem", "borderColor": "#ffd700",
                                       "color": "#ffd700"},
                                disabled=is_expired,
                            ) if plan != "prime_boost" else None,
                            dbc.Button(
                                [html.I(className=f"fas fa-{'play' if is_paused else 'pause'} me-1"),
                                 "Resume" if is_paused else "Pause"],
                                id={"type": "toggle-listing-btn", "index": lst["id"]},
                                size="sm", color="secondary", outline=True, n_clicks=0,
                                style={"fontSize": "0.75rem"},
                                disabled=is_expired,
                            ) if not is_expired else None,
                            dbc.Button(
                                [html.I(className="fas fa-redo me-1"), "Renew Listing"],
                                id={"type": "renew-listing-btn", "index": lst["id"]},
                                size="sm", className="btn-teal", n_clicks=0,
                                style={"fontSize": "0.75rem"},
                            ) if is_expired else None,
                        ],
                    ),
                ],
            ),
        ],
    )


# ── Filter + sort ────────────────────────────────────────────────────────────

@app.callback(
    Output("my-listings-container", "children"),
    Output("my-listings-count", "children"),
    Input("my-listings-status-filter", "value"),
    Input("my-listings-plan-filter",   "value"),
    Input("my-listings-sort",          "value"),
    Input("my-listings-overrides",     "data"),
    prevent_initial_call=False,
)
def filter_my_listings(status_filter, plan_filter, sort_by, overrides):
    """Re-render listing cards based on active filters, sort, and session overrides."""
    overrides = overrides or {}
    listings = []
    for base in MOCK_USER_LISTINGS:
        lst = dict(base)
        if str(lst["id"]) in overrides:
            lst.update(overrides[str(lst["id"])])
        # expires_at may have been stored as ISO string
        if isinstance(lst["expires_at"], str):
            lst["expires_at"] = datetime.fromisoformat(lst["expires_at"])
        listings.append(lst)

    # Filter
    if status_filter:
        listings = [l for l in listings if l["status"] == status_filter]
    if plan_filter:
        listings = [l for l in listings if l["plan"] == plan_filter]

    # Sort
    if sort_by == "views":
        listings = sorted(listings, key=lambda l: l["views"], reverse=True)
    elif sort_by == "leads":
        listings = sorted(listings, key=lambda l: l["leads"], reverse=True)
    elif sort_by == "expiry":
        listings = sorted(listings, key=lambda l: l["expires_at"])
    else:  # newest
        listings = sorted(listings, key=lambda l: l["created_at"], reverse=True)

    count_text = f"{len(listings)} listing{'s' if len(listings) != 1 else ''}"

    if not listings:
        return (
            html.Div(
                className="text-center py-5",
                children=[
                    html.I(className="fas fa-clipboard-list fa-3x mb-3",
                           style={"color": "var(--text-muted)"}),
                    html.H5("No listings found", style={"color": "var(--text-secondary)"}),
                    html.P("Try adjusting your filters.",
                           style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                ],
            ),
            count_text,
        )

    return [_build_card(l) for l in listings], count_text


# ── Bump to top ──────────────────────────────────────────────────────────────

@app.callback(
    Output("my-listings-overrides", "data"),
    Output("my-listings-toast", "children"),
    Output("my-listings-toast", "header"),
    Output("my-listings-toast", "is_open"),
    Input({"type": "bump-listing-btn", "index": ALL}, "n_clicks"),
    State("my-listings-overrides", "data"),
    prevent_initial_call=True,
)
def bump_listing(n_clicks_list, overrides):
    """Bump a listing's created_at to now so it appears newest-first."""
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    listing_id = dash.ctx.triggered_id["index"]
    overrides = dict(overrides or {})
    entry = overrides.get(str(listing_id), {})
    entry["created_at"] = datetime.now().isoformat()
    overrides[str(listing_id)] = entry

    # Find title for toast
    title = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short = title[:40] + "…" if len(title) > 40 else title
    msg = html.Span(
        [html.Strong(f'"{short}"'), " has been bumped to the top of search results."],
        style={"fontSize": "0.82rem"},
    )
    return overrides, msg, "Bumped!", True


# ── Pause / Resume ───────────────────────────────────────────────────────────

@app.callback(
    Output("my-listings-overrides", "data", allow_duplicate=True),
    Output("my-listings-toast", "children", allow_duplicate=True),
    Output("my-listings-toast", "header", allow_duplicate=True),
    Output("my-listings-toast", "is_open", allow_duplicate=True),
    Input({"type": "toggle-listing-btn", "index": ALL}, "n_clicks"),
    State("my-listings-overrides", "data"),
    prevent_initial_call=True,
)
def toggle_listing_status(n_clicks_list, overrides):
    """Pause an active listing or resume a paused one."""
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    listing_id = dash.ctx.triggered_id["index"]
    overrides  = dict(overrides or {})

    # Determine current effective status
    base_status = next(
        (l["status"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "active"
    )
    current = overrides.get(str(listing_id), {}).get("status", base_status)
    new_status = "paused" if current == "active" else "active"

    entry = overrides.get(str(listing_id), {})
    entry["status"] = new_status
    overrides[str(listing_id)] = entry

    title = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short = title[:40] + "…" if len(title) > 40 else title
    action = "paused" if new_status == "paused" else "resumed"
    msg = html.Span(
        [html.Strong(f'"{short}"'), f" has been {action}."],
        style={"fontSize": "0.82rem"},
    )
    header = "Listing Paused" if new_status == "paused" else "Listing Resumed"
    return overrides, msg, header, True


# ── Renew (expired) ──────────────────────────────────────────────────────────

@app.callback(
    Output("my-listings-overrides", "data", allow_duplicate=True),
    Output("my-listings-toast", "children", allow_duplicate=True),
    Output("my-listings-toast", "header", allow_duplicate=True),
    Output("my-listings-toast", "is_open", allow_duplicate=True),
    Input({"type": "renew-listing-btn", "index": ALL}, "n_clicks"),
    State("my-listings-overrides", "data"),
    prevent_initial_call=True,
)
def renew_listing(n_clicks_list, overrides):
    """Renew an expired listing for another 30 days."""
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
    msg = html.Span(
        [html.Strong(f'"{short}"'), " has been renewed for 30 days."],
        style={"fontSize": "0.82rem"},
    )
    return overrides, msg, "Listing Renewed", True


# ── Upgrade modal: open ──────────────────────────────────────────────────────

@app.callback(
    Output("upgrade-modal", "is_open"),
    Output("upgrade-listing-id-store", "data"),
    Input({"type": "upgrade-listing-btn", "index": ALL}, "n_clicks"),
    Input("sidebar-upgrade-btn", "n_clicks"),
    Input("upgrade-cancel-btn", "n_clicks"),
    State("upgrade-modal", "is_open"),
    prevent_initial_call=True,
)
def manage_upgrade_modal(upgrade_clicks, sidebar_click, cancel_click, is_open):
    triggered = dash.ctx.triggered_id
    if triggered == "upgrade-cancel-btn":
        return False, dash.no_update
    if triggered == "sidebar-upgrade-btn":
        return True, None
    if isinstance(triggered, dict) and triggered.get("type") == "upgrade-listing-btn":
        if any(n for n in upgrade_clicks if n):
            return True, triggered["index"]
    raise PreventUpdate


# ── Upgrade modal: confirm ───────────────────────────────────────────────────

@app.callback(
    Output("my-listings-overrides", "data", allow_duplicate=True),
    Output("upgrade-modal", "is_open", allow_duplicate=True),
    Output("my-listings-toast", "children", allow_duplicate=True),
    Output("my-listings-toast", "header", allow_duplicate=True),
    Output("my-listings-toast", "is_open", allow_duplicate=True),
    Input("upgrade-confirm-btn", "n_clicks"),
    State("upgrade-plan-select", "value"),
    State("upgrade-listing-id-store", "data"),
    State("my-listings-overrides", "data"),
    prevent_initial_call=True,
)
def confirm_upgrade(n_clicks, new_plan, listing_id, overrides):
    if not n_clicks:
        raise PreventUpdate
    if not listing_id:
        # Sidebar upgrade with no specific listing → just close modal
        return dash.no_update, False, dash.no_update, dash.no_update, dash.no_update

    overrides = dict(overrides or {})
    entry = overrides.get(str(listing_id), {})
    entry["plan"]       = new_plan
    entry["status"]     = "active"
    entry["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    # Featured/prime listings get is_featured = True
    entry["is_featured"] = new_plan in ("featured", "prime_boost")
    entry["is_prime"]    = new_plan == "prime_boost"
    overrides[str(listing_id)] = entry

    title = next((l["title"] for l in MOCK_USER_LISTINGS if l["id"] == listing_id), "Listing")
    short = title[:40] + "…" if len(title) > 40 else title
    plan_label = _PLAN_LABEL.get(new_plan, new_plan)
    msg = html.Span(
        [html.Strong(f'"{short}"'), f" has been upgraded to {plan_label}."],
        style={"fontSize": "0.82rem"},
    )
    return overrides, False, msg, "Plan Upgraded!", True
