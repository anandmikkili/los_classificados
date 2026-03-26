"""Browse page callbacks – filtering, sorting, and search."""
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
from los_classificados.server import app
from los_classificados.utils.mock_data import MOCK_LISTINGS, CATEGORIES, NEIGHBORHOODS_BY_CITY


def _listing_row(lst):
    """Horizontal listing row card."""
    has_wa = bool(lst.get("contact_whatsapp"))
    has_ph = bool(lst.get("contact_phone"))
    return html.Div(
        className="lc-card d-flex mb-3",
        style={"overflow": "hidden"},
        children=[
            html.Img(
                src=lst["image"],
                style={"width": "180px", "minWidth": "180px", "objectFit": "cover"},
                alt=lst["title"],
            ),
            html.Div(
                className="p-3 d-flex flex-column flex-grow-1",
                children=[
                    html.Div(className="d-flex justify-content-between align-items-start mb-1", children=[
                        html.Div([
                            html.Span("★ Prime", className="badge-prime me-1") if lst["is_prime"] else None,
                            html.Span([html.I(className="fas fa-check-circle me-1"), "Verified"],
                                      className="badge-verified me-1") if lst["is_verified"] else None,
                            html.Span(lst["subcategory"], className="badge-cat"),
                        ]),
                        html.Small(lst["city"], className="text-muted-lc"),
                    ]),
                    html.Div(lst["title"], className="listing-title mb-1"),
                    html.P(
                        lst["description"][:130] + "…",
                        style={"fontSize": "0.82rem", "color": "var(--text-secondary)",
                               "lineHeight": "1.5", "marginBottom": "0.5rem"},
                    ),
                    html.Div(className="d-flex align-items-center gap-3 mt-auto", children=[
                        html.Div(lst["price_label"], className="listing-price", style={"fontSize": "1.1rem"}),
                        html.Div(
                            [html.I(className="fas fa-map-marker-alt me-1"), lst["neighborhood"]],
                            className="text-muted-lc", style={"fontSize": "0.8rem"},
                        ),
                        html.Div(className="ms-auto d-flex gap-2", children=[
                            html.A(
                                [html.I(className="fab fa-whatsapp me-1"), "WhatsApp"],
                                href=f"https://wa.me/{lst['contact_whatsapp'].replace('+','')}" if has_wa else "#",
                                target="_blank",
                                className="btn btn-sm btn-whatsapp px-3",
                                style={"fontSize": "0.78rem"},
                            ) if has_wa else None,
                            html.A(
                                [html.I(className="fas fa-phone me-1"), "Call"],
                                href=f"tel:{lst['contact_phone']}" if has_ph else "#",
                                className="btn btn-sm btn-call px-3",
                                style={"fontSize": "0.78rem"},
                            ) if has_ph else None,
                        ]),
                    ]),
                ],
            ),
        ],
    )


# ── Neighborhood filter – updated reactively when city changes ──────────────

@app.callback(
    Output("neighborhood-filter-section", "style"),
    Output("filter-neighborhoods", "options"),
    Output("filter-neighborhoods", "value"),
    Input("browse-city-select", "value"),
    prevent_initial_call=False,
)
def update_neighborhood_filter(city):
    """Show and populate neighborhood checklist when a city is selected."""
    if not city:
        return {"display": "none"}, [], []
    hoods = NEIGHBORHOODS_BY_CITY.get(city, [])
    if not hoods:
        return {"display": "none"}, [], []
    options = [{"label": h, "value": h} for h in hoods]
    return {}, options, []


# ── Main results callback ────────────────────────────────────────────────────

@app.callback(
    Output("browse-results-container", "children"),
    Output("browse-results-count", "children"),
    Input("browse-search-btn", "n_clicks"),
    Input("filter-categories", "value"),
    Input("filter-price-range", "value"),
    Input("filter-listing-type", "value"),
    Input("filter-contact", "value"),
    Input("browse-sort", "value"),
    Input("browse-city-select", "value"),       # promoted from State → Input for reactive city filtering
    Input("filter-neighborhoods", "value"),     # hyperlocal neighborhood filter
    State("browse-search-input", "value"),
    prevent_initial_call=False,
)
def update_browse_results(
    _n, categories, price_range, listing_types, contact_methods,
    sort_by, city, neighborhoods, search_query,
):
    listings = list(MOCK_LISTINGS)

    # ── Text search ────────────────────────────────────────────────────
    if search_query:
        q = search_query.lower()
        listings = [
            l for l in listings
            if q in l["title"].lower() or q in l["description"].lower()
        ]

    # ── Category filter ────────────────────────────────────────────────
    if categories:
        listings = [l for l in listings if l["category"] in categories]

    # ── City filter ────────────────────────────────────────────────────
    if city:
        listings = [l for l in listings if l["city"] == city]

    # ── Neighborhood filter (hyperlocal) ──────────────────────────────
    if neighborhoods:
        listings = [l for l in listings if l.get("neighborhood") in neighborhoods]

    # ── Price range ────────────────────────────────────────────────────
    if price_range:
        lo, hi = price_range
        listings = [
            l for l in listings
            if l["price"] is None or (lo <= (l["price"] or 0) <= hi)
        ]

    # ── Listing type ───────────────────────────────────────────────────
    if listing_types:
        filtered = []
        for l in listings:
            passes = True
            if "prime" in listing_types and not l["is_prime"]:
                passes = False
            if "verified" in listing_types and not l["is_verified"]:
                passes = False
            if "free" in listing_types and l["price"] is not None:
                passes = False
            if passes:
                filtered.append(l)
        listings = filtered

    # ── Contact method ─────────────────────────────────────────────────
    if contact_methods:
        filtered = []
        for l in listings:
            if "whatsapp" in contact_methods and l.get("contact_whatsapp"):
                filtered.append(l)
            elif "phone" in contact_methods and l.get("contact_phone"):
                filtered.append(l)
            elif "email" in contact_methods and l.get("contact_email"):
                filtered.append(l)
        listings = filtered

    # ── Sort ───────────────────────────────────────────────────────────
    if sort_by == "price_asc":
        listings = sorted(listings, key=lambda l: l["price"] or 0)
    elif sort_by == "price_desc":
        listings = sorted(listings, key=lambda l: l["price"] or 0, reverse=True)
    elif sort_by == "views":
        listings = sorted(listings, key=lambda l: l["views"], reverse=True)
    elif sort_by == "prime":
        listings = sorted(listings, key=lambda l: (not l["is_prime"], -l["views"]))
    else:  # recent
        listings = sorted(listings, key=lambda l: l["created_at"], reverse=True)

    # Build count label with location context
    location_ctx = ""
    if neighborhoods:
        location_ctx = f" in {', '.join(neighborhoods)}"
    elif city:
        location_ctx = f" in {city}"
    count_text = f"Showing {len(listings)} listing{'s' if len(listings) != 1 else ''}{location_ctx}"

    if not listings:
        return (
            html.Div(
                className="text-center py-5",
                children=[
                    html.I(className="fas fa-search fa-3x mb-3", style={"color": "var(--text-muted)"}),
                    html.H5("No listings found", style={"color": "var(--text-secondary)"}),
                    html.P("Try adjusting your filters or search query.",
                           style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                ],
            ),
            count_text,
        )

    return [_listing_row(l) for l in listings], count_text


# ── Clear filters ────────────────────────────────────────────────────────────

@app.callback(
    Output("filter-categories", "value"),
    Output("filter-price-range", "value"),
    Output("filter-listing-type", "value"),
    Output("filter-contact", "value"),
    Output("filter-neighborhoods", "value"),
    Input("clear-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_filters(_n):
    return [], [0, 1_000_000], [], [], []
