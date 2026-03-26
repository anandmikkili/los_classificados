"""Providers directory callbacks – filtering, sorting, profile modal, quote form."""
import dash
from dash import Input, Output, State, ALL, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import MOCK_PROVIDERS
from los_classificados.layouts.providers import _provider_card, _build_profile_body

# Map human response_time strings to sortable minutes
_RESPONSE_MINUTES = {
    "< 30 min":  30,
    "< 1 hour":  60,
    "< 2 hours": 120,
    "< 3 hours": 180,
    "< 4 hours": 240,
}

_RESPONSE_THRESHOLD = {
    "1h": 60,
    "3h": 180,
}


# ── Filter + sort providers ──────────────────────────────────────────────────

@app.callback(
    Output("providers-results-container", "children"),
    Output("providers-count", "children"),
    Input("providers-search-btn", "n_clicks"),
    Input("filter-min-rating", "value"),
    Input("filter-verification", "value"),
    Input("filter-price-tier", "value"),
    Input("filter-response-time", "value"),
    Input("providers-sort", "value"),
    Input("providers-city-select", "value"),
    Input("providers-subcat-select", "value"),
    State("providers-search-input", "value"),
    prevent_initial_call=False,
)
def filter_providers(
    _n, min_rating, verification_filters, price_tiers,
    response_filter, sort_by, city, subcategory, search_query,
):
    providers = list(MOCK_PROVIDERS)

    # ── Text search ─────────────────────────────────────────────────────
    if search_query:
        q = search_query.lower()
        providers = [
            p for p in providers
            if q in p["name"].lower()
            or q in p["owner_name"].lower()
            or q in p["bio"].lower()
            or any(q in s.lower() for s in p["subcategories"])
        ]

    # ── City ────────────────────────────────────────────────────────────
    if city:
        providers = [p for p in providers if p["city"] == city]

    # ── Subcategory ─────────────────────────────────────────────────────
    if subcategory:
        providers = [p for p in providers if subcategory in p["subcategories"]]

    # ── Min rating ──────────────────────────────────────────────────────
    if min_rating:
        providers = [p for p in providers if p["rating"] >= min_rating]

    # ── Verification / Prime ────────────────────────────────────────────
    if verification_filters:
        filtered = []
        for p in providers:
            passes = True
            if "verified" in verification_filters and not p["is_verified"]:
                passes = False
            if "prime" in verification_filters and not p["is_prime"]:
                passes = False
            if passes:
                filtered.append(p)
        providers = filtered

    # ── Price tier ──────────────────────────────────────────────────────
    if price_tiers:
        providers = [p for p in providers if p["price_range"] in price_tiers]

    # ── Response time ────────────────────────────────────────────────────
    if response_filter and response_filter != "any":
        threshold = _RESPONSE_THRESHOLD.get(response_filter, 9999)
        providers = [
            p for p in providers
            if _RESPONSE_MINUTES.get(p["response_time"], 9999) <= threshold
        ]

    # ── Sort ─────────────────────────────────────────────────────────────
    if sort_by == "reviews":
        providers = sorted(providers, key=lambda p: p["review_count"], reverse=True)
    elif sort_by == "response":
        providers = sorted(providers, key=lambda p: _RESPONSE_MINUTES.get(p["response_time"], 9999))
    elif sort_by == "jobs":
        providers = sorted(providers, key=lambda p: p["jobs_completed"], reverse=True)
    elif sort_by == "newest":
        providers = sorted(providers, key=lambda p: p["created_at"], reverse=True)
    else:  # rating (default)
        providers = sorted(providers, key=lambda p: (p["rating"], p["review_count"]), reverse=True)

    count_text = (
        f"Showing {len(providers)} provider{'s' if len(providers) != 1 else ''}"
        + (f" in {city}" if city else "")
    )

    if not providers:
        return (
            html.Div(
                className="text-center py-5 col-12",
                children=[
                    html.I(className="fas fa-search fa-3x mb-3",
                           style={"color": "var(--text-muted)"}),
                    html.H5("No providers found", style={"color": "var(--text-secondary)"}),
                    html.P("Try adjusting your filters or search query.",
                           style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                ],
            ),
            count_text,
        )

    return (
        [html.Div(_provider_card(p), className="col") for p in providers],
        count_text,
    )


# ── Clear filters ────────────────────────────────────────────────────────────

@app.callback(
    Output("filter-min-rating",      "value"),
    Output("filter-verification",    "value"),
    Output("filter-price-tier",      "value"),
    Output("filter-response-time",   "value"),
    Output("providers-city-select",  "value"),
    Output("providers-subcat-select","value"),
    Input("clear-provider-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_provider_filters(_n):
    return 0, [], [], "any", "", ""


# ── Open provider profile modal (from card click or Get-a-Quote button) ──────

@app.callback(
    Output("provider-profile-modal", "is_open"),
    Output("modal-provider-name",    "children"),
    Output("modal-provider-body",    "children"),
    Input({"type": "provider-card",  "index": ALL}, "n_clicks"),
    Input({"type": "get-quote-btn",  "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_provider_profile(card_clicks, quote_clicks):
    triggered = dash.ctx.triggered_id
    if triggered is None:
        raise PreventUpdate

    # Determine which provider id was triggered
    if isinstance(triggered, dict):
        prov_id = triggered.get("index")
    else:
        raise PreventUpdate

    # Check if it was a real click (not initial 0-value render)
    if not any(n for n in (card_clicks + quote_clicks) if n):
        raise PreventUpdate

    prov = next((p for p in MOCK_PROVIDERS if p["id"] == prov_id), None)
    if prov is None:
        raise PreventUpdate

    name_children = [
        html.Img(
            src=prov["avatar"],
            style={"width": "32px", "height": "32px", "borderRadius": "50%",
                   "objectFit": "cover", "marginRight": "0.5rem"},
        ),
        prov["name"],
        html.Span(
            [html.I(className="fas fa-check-circle me-1"), "Verified"],
            className="badge-verified ms-2",
            style={"fontSize": "0.68rem"},
        ) if prov["is_verified"] else None,
        html.Span("★ Prime", className="badge-prime ms-1",
                  style={"fontSize": "0.68rem"}) if prov["is_prime"] else None,
    ]

    return True, name_children, _build_profile_body(prov)


# ── Quote request submission ─────────────────────────────────────────────────

@app.callback(
    Output("quote-alert", "children"),
    Input("quote-submit-btn", "n_clicks"),
    State("quote-name",           "value"),
    State("quote-phone",          "value"),
    State("quote-service-type",   "value"),
    State("quote-contact-method", "value"),
    State("quote-description",    "value"),
    State("quote-budget",         "value"),
    State("quote-provider-id-store", "data"),
    prevent_initial_call=True,
)
def submit_quote(n_clicks, name, phone, service_type, contact_method,
                 description, budget, provider_id):
    if not n_clicks:
        raise PreventUpdate

    errors = []
    if not name or len((name or "").strip()) < 2:
        errors.append("Please enter your name.")
    if not phone or len((phone or "").strip()) < 7:
        errors.append("Please enter a valid phone number.")
    if not service_type:
        errors.append("Please select the service you need.")
    if not description or len((description or "").strip()) < 15:
        errors.append("Please describe your project (at least 15 characters).")

    if errors:
        return dbc.Alert(
            [html.I(className="fas fa-exclamation-circle me-2")]
            + [html.Div(e) for e in errors],
            color="danger",
            className="alert-danger",
            dismissable=True,
            style={"fontSize": "0.82rem", "marginBottom": "0.75rem"},
        )

    prov = next((p for p in MOCK_PROVIDERS if p["id"] == provider_id), None)
    prov_name = prov["owner_name"] if prov else "the provider"

    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Quote request sent! "),
            f"{prov_name} will reach out via "
            f"{'WhatsApp' if contact_method == 'whatsapp' else 'phone call' if contact_method == 'phone' else 'email'} "
            f"typically {prov['response_time'] if prov else 'shortly'}.",
        ],
        color="success",
        className="alert-success",
        dismissable=True,
        style={"fontSize": "0.82rem", "marginBottom": "0.75rem"},
    )
