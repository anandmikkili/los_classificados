"""Browse page callbacks – filtering, sorting, and search."""
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
from los_classificados.server import app
from los_classificados.utils.mock_data import (
    MOCK_LISTINGS, CATEGORIES, NEIGHBORHOODS_BY_CITY, NEARBY_CITIES, SUBCATEGORIES, time_ago,
)


def _listing_row(lst):
    """Horizontal listing row card."""
    has_wa  = bool(lst.get("contact_whatsapp"))
    has_ph  = bool(lst.get("contact_phone"))
    is_feat = bool(lst.get("is_featured"))
    freshness = time_ago(lst["created_at"])

    border_style = {"overflow": "hidden", "border": "1.5px solid rgba(255,107,53,0.35)"} if is_feat else {"overflow": "hidden"}

    return html.Div(
        className="lc-card d-flex mb-3",
        style=border_style,
        children=[
            # featured side stripe
            html.Div(
                style={
                    "width": "4px", "minWidth": "4px",
                    "background": "linear-gradient(180deg, #ff6b35, #ff9a6c)",
                    "flexShrink": "0",
                },
            ) if is_feat else None,
            html.Img(
                src=lst["image"],
                style={"width": "180px", "minWidth": "180px", "objectFit": "cover"},
                alt=lst["title"],
            ),
            html.Div(
                className="p-3 d-flex flex-column flex-grow-1",
                children=[
                    # top row: badges + city + freshness
                    html.Div(className="d-flex justify-content-between align-items-start mb-1", children=[
                        html.Div([
                            html.Span(
                                [html.I(className="fas fa-bolt me-1"), "Featured"],
                                className="me-1",
                                style={
                                    "background": "rgba(255,107,53,0.15)", "color": "#ff6b35",
                                    "border": "1px solid rgba(255,107,53,0.4)",
                                    "borderRadius": "100px", "padding": "0.1rem 0.45rem",
                                    "fontSize": "0.68rem", "fontWeight": "700",
                                },
                            ) if is_feat else None,
                            html.Span("★ Prime", className="badge-prime me-1") if lst["is_prime"] else None,
                            html.Span([html.I(className="fas fa-check-circle me-1"), "Verified"],
                                      className="badge-verified me-1") if lst["is_verified"] else None,
                            html.Span(lst["subcategory"], className="badge-cat"),
                        ]),
                        html.Div(className="d-flex align-items-center gap-2", children=[
                            html.Small(lst["city"], className="text-muted-lc"),
                            html.Small(
                                [html.I(className="fas fa-clock me-1"), freshness],
                                className="text-muted-lc",
                                style={"fontSize": "0.72rem"},
                                title=str(lst["created_at"]),
                            ),
                        ]),
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
                        html.Div(className="ms-auto d-flex gap-2 align-items-center", children=[
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
                            html.Button(
                                html.I(className="fas fa-flag"),
                                id={"type": "flag-btn", "index": lst["id"]},
                                n_clicks=0,
                                title="Report this listing",
                                className="btn btn-sm btn-outline-secondary px-2",
                                style={"fontSize": "0.72rem", "opacity": "0.45", "lineHeight": "1"},
                            ),
                        ]),
                    ]),
                ],
            ),
        ],
    )


def _section_header(text, icon, color="#8b949e"):
    """Thin divider row between featured and regular listing groups."""
    return html.Div(
        className="d-flex align-items-center gap-2 mb-2 mt-1",
        children=[
            html.I(className=f"fas {icon}", style={"color": color, "fontSize": "0.8rem"}),
            html.Span(text, style={"fontSize": "0.75rem", "fontWeight": "700",
                                   "color": color, "letterSpacing": "0.06em",
                                   "textTransform": "uppercase"}),
            html.Hr(style={"flexGrow": "1", "margin": "0", "borderColor": "var(--border-color)"}),
        ],
    )


_BANNER_STYLE = {
    "background": "linear-gradient(135deg, rgba(0,201,167,0.12) 0%, rgba(0,201,167,0.05) 100%)",
    "borderBottom": "1px solid rgba(0,201,167,0.25)",
    "padding": "0.6rem 0",
}


# ── Neighborhood + nearby-cities filters – updated reactively when city changes ─

@app.callback(
    Output("neighborhood-filter-section", "style"),
    Output("filter-neighborhoods", "options"),
    Output("filter-neighborhoods", "value"),
    Output("nearby-cities-section", "style"),
    Input("browse-city-select", "value"),
    prevent_initial_call=False,
)
def update_neighborhood_filter(city):
    """Show neighborhood and nearby-cities filters when a city is selected."""
    if not city:
        return {"display": "none"}, [], [], {"display": "none"}
    hoods = NEIGHBORHOODS_BY_CITY.get(city, [])
    nearby = NEARBY_CITIES.get(city, [])
    nh_style = {} if hoods else {"display": "none"}
    nh_opts = [{"label": h, "value": h} for h in hoods]
    nearby_style = {} if nearby else {"display": "none"}
    return nh_style, nh_opts, [], nearby_style


# ── City context banner – reflects active city and nearby expansion ────────────

@app.callback(
    Output("city-context-banner", "style"),
    Output("city-context-text", "children"),
    Input("browse-city-select", "value"),
    Input("filter-nearby-cities", "value"),
    prevent_initial_call=False,
)
def update_city_banner(city, nearby_opt):
    """Update city context banner to reflect active city and nearby expansion."""
    if not city:
        return {**_BANNER_STYLE, "display": "none"}, ""
    text = f"Showing listings in {city}"
    if nearby_opt and "nearby" in nearby_opt:
        nearby = NEARBY_CITIES.get(city, [])
        if nearby:
            text += f" + nearby cities ({', '.join(nearby)})"
    return {**_BANNER_STYLE, "display": "block"}, text


# ── Subcategory drill-down – shown when exactly 1 category is selected ───────

@app.callback(
    Output("subcategory-drill-down-section", "style"),
    Output("filter-subcategories", "options"),
    Output("filter-subcategories", "value"),
    Input("filter-categories", "value"),
    prevent_initial_call=False,
)
def update_subcategory_filter(selected_cats):
    if selected_cats and len(selected_cats) == 1:
        cat_id = selected_cats[0]
        subs = SUBCATEGORIES.get(cat_id, [])
        opts = [{"label": s, "value": s} for s in subs]
        return {}, opts, []
    return {"display": "none"}, [], []


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
    Input("filter-nearby-cities", "value"),     # nearby markets expansion
    Input("filter-subcategories", "value"),     # subcategory drill-down
    State("browse-search-input", "value"),
    prevent_initial_call=False,
)
def update_browse_results(
    _n, categories, price_range, listing_types, contact_methods,
    sort_by, city, neighborhoods, nearby_cities_opt, subcategories, search_query,
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

    # ── Subcategory filter (drill-down) ───────────────────────
    if subcategories:
        listings = [l for l in listings if l.get("subcategory") in subcategories]

    # ── City filter with optional nearby expansion ─────────────────────
    if city:
        cities_to_search = {city}
        if nearby_cities_opt and "nearby" in nearby_cities_opt:
            cities_to_search.update(NEARBY_CITIES.get(city, []))
        listings = [l for l in listings if l["city"] in cities_to_search]

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

    # ── Sort within each group ─────────────────────────────────────────
    # Featured listings are always pinned above regular ones; within each
    # group the chosen sort order applies independently.
    if sort_by == "price_asc":
        listings = sorted(listings, key=lambda l: l["price"] or 0)
    elif sort_by == "price_desc":
        listings = sorted(listings, key=lambda l: l["price"] or 0, reverse=True)
    elif sort_by == "views":
        listings = sorted(listings, key=lambda l: l["views"], reverse=True)
    elif sort_by == "prime":
        listings = sorted(listings, key=lambda l: (not l["is_prime"], -l["views"]))
    elif sort_by == "featured":
        # Featured-first explicit sort: featured by recency, then regular by recency
        listings = sorted(listings, key=lambda l: (not l.get("is_featured"), l["created_at"]))
    else:  # "recent" (default)
        listings = sorted(listings, key=lambda l: l["created_at"], reverse=True)

    # Build count label with location context
    location_ctx = ""
    if neighborhoods:
        location_ctx = f" in {', '.join(neighborhoods)}"
    elif city:
        if nearby_cities_opt and "nearby" in nearby_cities_opt:
            nearby = NEARBY_CITIES.get(city, [])
            if nearby:
                location_ctx = f" in {city} + {len(nearby)} nearby {'city' if len(nearby) == 1 else 'cities'}"
            else:
                location_ctx = f" in {city}"
        else:
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

    # ── Split into featured vs regular and add section headers ─────────
    featured_rows = [l for l in listings if l.get("is_featured")]
    regular_rows  = [l for l in listings if not l.get("is_featured")]

    rows = []
    if featured_rows:
        rows.append(_section_header("Featured Placements", "fa-bolt", "#ff6b35"))
        rows.extend(_listing_row(l) for l in featured_rows)
    if regular_rows:
        if featured_rows:
            rows.append(_section_header("All Listings", "fa-list", "#8b949e"))
        rows.extend(_listing_row(l) for l in regular_rows)

    return rows, count_text


# ── Clear filters ────────────────────────────────────────────────────────────

@app.callback(
    Output("filter-categories", "value"),
    Output("filter-price-range", "value"),
    Output("filter-listing-type", "value"),
    Output("filter-contact", "value"),
    Output("filter-neighborhoods", "value"),
    Output("filter-nearby-cities", "value"),
    Output("filter-subcategories", "value"),
    Input("clear-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_filters(_n):
    return [], [0, 1_000_000], [], [], [], [], []
