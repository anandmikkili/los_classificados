"""Performance & Lead Generation callbacks."""
import dash
from dash import Input, Output, State, ALL, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_clasificados.server import app
from los_clasificados.utils.mock_data import (
    MOCK_VERIFIED_LEADS, LEAD_QUALITY_LABELS, LEAD_STATUS_LABELS,
    RESPONSE_PACKAGES, MOCK_PPC_CAMPAIGNS,
)

_TABS = ["leads", "response", "seo", "ppc"]

_SOURCE_LABELS = {
    "organic":  "Organic Search",
    "featured": "Featured",
    "prime":    "Prime Boost",
    "ppc":      "PPC Campaign",
}


# ── Tab switching ─────────────────────────────────────────────────────────────

@app.callback(
    Output("perf-panel-leads",    "style"),
    Output("perf-panel-response", "style"),
    Output("perf-panel-seo",      "style"),
    Output("perf-panel-ppc",      "style"),
    Output("perf-active-tab",     "data"),
    Input({"type": "perf-nav-btn", "index": ALL}, "n_clicks"),
    State("perf-active-tab", "data"),
    prevent_initial_call=True,
)
def switch_perf_tab(n_clicks_list, current_tab):
    triggered = dash.ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        raise PreventUpdate
    if not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    active = triggered["index"]
    styles = [{} if tab == active else {"display": "none"} for tab in _TABS]
    return (*styles, active)


# ── Lead list: filter by quality and source ───────────────────────────────────

def _lead_row_html(lead):
    """Re-render a lead row (mirrors the layout helper)."""
    from los_classificados.layouts.performance import _lead_row
    return _lead_row(lead)


@app.callback(
    Output("perf-leads-container", "children"),
    Output("perf-lead-count",      "children"),
    Input("perf-quality-filter", "value"),
    Input("perf-source-filter",  "value"),
    prevent_initial_call=False,
)
def filter_perf_leads(quality_filter, source_filter):
    leads = list(MOCK_VERIFIED_LEADS)

    if quality_filter and quality_filter != "all":
        leads = [l for l in leads if l["quality_tier"] == quality_filter]
    if source_filter and source_filter != "all":
        leads = [l for l in leads if l["lead_source"] == source_filter]

    leads = sorted(leads, key=lambda x: x["quality_score"], reverse=True)

    from los_clasificados.layouts.performance import _lead_row
    count = f"{len(leads)} lead{'s' if len(leads) != 1 else ''}"

    if not leads:
        return (
            html.Div(
                className="text-center py-4",
                children=[
                    html.I(className="fas fa-inbox fa-2x mb-2",
                           style={"color": "var(--text-muted)"}),
                    html.P("No leads match your filters.",
                           style={"color": "var(--text-muted)", "fontSize": "0.85rem"}),
                ],
            ),
            count,
        )
    return [_lead_row(l) for l in leads], count


# ── Response package selection ────────────────────────────────────────────────

@app.callback(
    Output("pkg-select-alert", "children"),
    Input({"type": "pkg-select-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_response_package(n_clicks_list):
    triggered = dash.ctx.triggered_id
    if not triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    pkg_id = triggered["index"]
    pkg = next((p for p in RESPONSE_PACKAGES if p["id"] == pkg_id), None)
    if not pkg:
        raise PreventUpdate
    return dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"),
         f"Switched to {pkg['name']} — ${pkg['price']:.2f}/mo. "
         f"Your listings now show the '{pkg['badge']}' badge."],
        color="success", dismissable=True, duration=4000,
        style={"fontSize": "0.82rem"},
    )


# ── SEO keyword detail toggles ────────────────────────────────────────────────

@app.callback(
    Output({"type": "seo-kw-collapse", "index": ALL}, "is_open"),
    Input({"type": "seo-kw-toggle",   "index": ALL}, "n_clicks"),
    State({"type": "seo-kw-collapse", "index": ALL}, "is_open"),
    prevent_initial_call=True,
)
def toggle_seo_keywords(n_clicks_list, is_open_list):
    triggered = dash.ctx.triggered_id
    if not triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    triggered_idx = triggered["index"]
    new_states = []
    # Match by listing_id - the order of ALL components matches
    for i, (n, is_open) in enumerate(zip(n_clicks_list, is_open_list)):
        # We need to find which component index corresponds to triggered_idx
        # Since ALL preserves order, we toggle the one that was clicked
        if dash.ctx.triggered[0]["prop_id"].startswith(f'{{"index":{triggered_idx}'):
            new_states.append(not is_open)
        else:
            new_states.append(is_open)
    return new_states


# ── PPC: toggle campaign active/paused ───────────────────────────────────────

@app.callback(
    Output("perf-ppc-overrides", "data"),
    Output("ppc-toast", "children"),
    Output("ppc-toast", "header"),
    Output("ppc-toast", "is_open"),
    Input({"type": "ppc-toggle-btn", "index": ALL}, "n_clicks"),
    State("perf-ppc-overrides", "data"),
    prevent_initial_call=True,
)
def toggle_ppc_campaign(n_clicks_list, overrides):
    triggered = dash.ctx.triggered_id
    if not triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    camp_id  = triggered["index"]
    overrides = dict(overrides or {})

    base_status = next(
        (c["status"] for c in MOCK_PPC_CAMPAIGNS if c["id"] == camp_id), "active"
    )
    current    = overrides.get(camp_id, {}).get("status", base_status)
    new_status = "paused" if current == "active" else "active"
    entry      = overrides.get(camp_id, {})
    entry["status"] = new_status
    overrides[camp_id] = entry

    camp_name = next((c["name"] for c in MOCK_PPC_CAMPAIGNS if c["id"] == camp_id), "Campaign")
    action    = "paused" if new_status == "paused" else "resumed"
    msg = html.Span([html.Strong(camp_name), f" has been {action}."],
                    style={"fontSize": "0.82rem"})
    header = "Campaign Paused" if new_status == "paused" else "Campaign Resumed"
    return overrides, msg, header, True


# ── PPC: new campaign modal open/close ────────────────────────────────────────

@app.callback(
    Output("ppc-new-campaign-modal", "is_open"),
    Input("ppc-new-campaign-btn",    "n_clicks"),
    Input("ppc-new-cancel-btn",      "n_clicks"),
    Input("ppc-new-confirm-btn",     "n_clicks"),
    State("ppc-new-campaign-modal",  "is_open"),
    prevent_initial_call=True,
)
def toggle_ppc_modal(open_clicks, cancel_clicks, confirm_clicks, is_open):
    triggered = dash.ctx.triggered_id
    if triggered == "ppc-new-campaign-btn":
        return True
    if triggered in ("ppc-new-cancel-btn", "ppc-new-confirm-btn"):
        return False
    raise PreventUpdate


# ── PPC: new campaign form validation ────────────────────────────────────────

@app.callback(
    Output("ppc-new-alert", "children"),
    Input("ppc-new-confirm-btn", "n_clicks"),
    State("ppc-new-name",    "value"),
    State("ppc-new-budget",  "value"),
    State("ppc-new-keywords","value"),
    State("ppc-new-cities",  "value"),
    prevent_initial_call=True,
)
def submit_ppc_campaign(n_clicks, name, budget, keywords, cities):
    if not n_clicks:
        raise PreventUpdate
    errors = []
    if not name:
        errors.append("Campaign name is required.")
    if not budget or float(budget) < 5:
        errors.append("Daily budget must be at least $5.")
    if not keywords:
        errors.append("At least one target keyword is required.")
    if not cities:
        errors.append("Select at least one target city.")
    if errors:
        return dbc.Alert(
            [html.Ul([html.Li(e) for e in errors], className="mb-0")],
            color="danger", style={"fontSize": "0.8rem"},
        )
    return dbc.Alert(
        [html.I(className="fas fa-rocket me-2"),
         f"Campaign '{name}' launched! It will start delivering within 24 hours."],
        color="success", style={"fontSize": "0.82rem"},
    )
