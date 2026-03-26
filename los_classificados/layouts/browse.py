import dash_bootstrap_components as dbc
from dash import html, dcc
from los_classificados.utils.mock_data import CATEGORIES, MOCK_LISTINGS, CITIES, time_ago


def _listing_row(lst):
    """Horizontal listing row card for browse view."""
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
                        html.Div([
                            html.I(className="fas fa-map-marker-alt me-1"),
                            lst["neighborhood"],
                        ], className="text-muted-lc", style={"fontSize": "0.8rem"}),
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


def browse_layout(search_query="", selected_category="", city=""):
    cat_options = [{"label": "All Categories", "value": ""}] + [
        {"label": c["label"], "value": c["id"]} for c in CATEGORIES
    ]
    city_options = [{"label": "All Cities", "value": ""}] + [
        {"label": c, "value": c} for c in CITIES
    ]
    sort_options = [
        {"label": "⚡ Featured First", "value": "featured"},
        {"label": "Most Recent",       "value": "recent"},
        {"label": "Lowest Price",      "value": "price_asc"},
        {"label": "Highest Price",     "value": "price_desc"},
        {"label": "Most Viewed",       "value": "views"},
        {"label": "★ Prime First",     "value": "prime"},
    ]

    active_city_banner = html.Div(
        style={
            "background": "linear-gradient(135deg, rgba(0,201,167,0.12) 0%, rgba(0,201,167,0.05) 100%)",
            "borderBottom": "1px solid rgba(0,201,167,0.25)",
            "padding": "0.6rem 0",
            "display": "block" if city else "none",
        },
        id="city-context-banner",
        children=[
            dbc.Container(
                html.Div(className="d-flex align-items-center gap-2", children=[
                    html.I(className="fas fa-map-marker-alt", style={"color": "var(--accent-teal)"}),
                    html.Span(
                        f"Showing listings in {city}" if city else "",
                        style={"fontWeight": "600", "fontSize": "0.9rem"},
                        id="city-context-text",
                    ),
                    html.A(
                        "✕ Clear city",
                        href="/browse",
                        style={
                            "fontSize": "0.78rem",
                            "color": "var(--text-muted)",
                            "textDecoration": "none",
                            "marginLeft": "0.5rem",
                        },
                    ) if city else html.Span(),
                ]),
                fluid=False,
            ),
        ],
    )

    return html.Div([
        # ── City context banner (shown when city is pre-selected from URL) ─
        active_city_banner,

        # ── Top search bar ────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderBottom": "1px solid var(--border-color)",
                   "padding": "1.25rem 0"},
            children=[
                dbc.Container(dbc.Row([
                    dbc.Col(
                        dcc.Input(
                            id="browse-search-input",
                            value=search_query,
                            placeholder="Search listings…",
                            type="text",
                            className="form-control",
                            debounce=True,
                        ),
                        md=5,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="browse-category-select",
                            options=cat_options,
                            value=selected_category or "",
                            placeholder="Category",
                            clearable=False,
                            className="bg-input",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="browse-city-select",
                            options=city_options,
                            value=city or "",
                            placeholder="City",
                            clearable=False,
                            className="bg-input",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "Search"],
                            id="browse-search-btn",
                            className="btn-teal w-100",
                            n_clicks=0,
                        ),
                        md=2,
                    ),
                ], className="g-2"), fluid=False),
            ],
        ),

        # ── Main content ──────────────────────────────────────────────────
        dbc.Container(className="py-4", children=[
            dbc.Row([
                # ── Sidebar ──────────────────────────────────────────────
                dbc.Col(
                    html.Div(className="filter-sidebar", children=[
                        html.Div("Filters", className="section-title mb-4", style={"fontSize": "1.1rem"}),

                        # Category filter
                        html.Div("Category", className="filter-title"),
                        dbc.Checklist(
                            id="filter-categories",
                            options=[{"label": c["label"], "value": c["id"]} for c in CATEGORIES],
                            value=[selected_category] if selected_category else [],
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                        # Subcategory drill-down (reactive: shown when 1 category is checked)
                        html.Div(
                            id="subcategory-drill-down-section",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    className="d-flex align-items-center gap-1 mb-1",
                                    children=[
                                        html.Div("Subcategory", className="filter-title mb-0"),
                                        html.Span(
                                            html.I(className="fas fa-chevron-right"),
                                            style={"color": "var(--accent-teal)", "fontSize": "0.65rem"},
                                        ),
                                    ],
                                ),
                                dbc.Checklist(
                                    id="filter-subcategories",
                                    options=[],
                                    value=[],
                                    className="mb-3",
                                    input_style={"accentColor": "var(--accent-teal)"},
                                    label_style={"color": "var(--text-secondary)", "fontSize": "0.82rem"},
                                ),
                                html.Hr(className="divider"),
                            ],
                        ),

                        html.Hr(className="divider"),

                        # Price range
                        html.Div("Price Range", className="filter-title"),
                        dcc.RangeSlider(
                            id="filter-price-range",
                            min=0, max=1_000_000,
                            step=500,
                            value=[0, 1_000_000],
                            marks={0: "$0", 500000: "$500K", 1000000: "$1M"},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3",
                        ),
                        html.Hr(className="divider"),

                        # Listing type
                        html.Div("Listing Type", className="filter-title"),
                        dbc.Checklist(
                            id="filter-listing-type",
                            options=[
                                {"label": "★ Prime listings",  "value": "prime"},
                                {"label": "✓ Verified sellers", "value": "verified"},
                                {"label": "Free / No price",    "value": "free"},
                                {"label": "Negotiable",         "value": "negotiable"},
                            ],
                            value=[],
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                        html.Hr(className="divider"),

                        # Contact options
                        html.Div("Contact Method", className="filter-title"),
                        dbc.Checklist(
                            id="filter-contact",
                            options=[
                                {"label": "WhatsApp", "value": "whatsapp"},
                                {"label": "Phone Call", "value": "phone"},
                                {"label": "Email", "value": "email"},
                            ],
                            value=[],
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                        html.Hr(className="divider"),

                        # Neighborhood filter (populated dynamically based on city)
                        html.Div(
                            id="neighborhood-filter-section",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    className="d-flex align-items-center gap-1 mb-1",
                                    children=[
                                        html.Div("Neighborhood", className="filter-title mb-0"),
                                        html.Span(
                                            html.I(className="fas fa-location-arrow"),
                                            style={"color": "var(--accent-teal)", "fontSize": "0.7rem"},
                                        ),
                                    ],
                                ),
                                dbc.Checklist(
                                    id="filter-neighborhoods",
                                    options=[],
                                    value=[],
                                    className="mb-3",
                                    input_style={"accentColor": "var(--accent-teal)"},
                                    label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                                ),
                                html.Hr(className="divider"),
                            ],
                        ),

                        # Nearby cities toggle (shown when selected city has adjacent markets)
                        html.Div(
                            id="nearby-cities-section",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    className="d-flex align-items-center gap-1 mb-1",
                                    children=[
                                        html.Div("Nearby Markets", className="filter-title mb-0"),
                                        html.Span(
                                            html.I(className="fas fa-expand-arrows-alt"),
                                            style={"color": "var(--accent-teal)", "fontSize": "0.7rem"},
                                        ),
                                    ],
                                ),
                                dbc.Checklist(
                                    id="filter-nearby-cities",
                                    options=[{"label": "Include nearby cities", "value": "nearby"}],
                                    value=[],
                                    className="mb-3",
                                    input_style={"accentColor": "var(--accent-teal)"},
                                    label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                                ),
                                html.Hr(className="divider"),
                            ],
                        ),

                        dbc.Button(
                            "Clear Filters",
                            id="clear-filters-btn",
                            className="btn-outline-teal w-100",
                            n_clicks=0,
                        ),
                    ]),
                    md=3,
                ),

                # ── Listings column ───────────────────────────────────────
                dbc.Col([
                    # Sort + count bar
                    html.Div(className="d-flex justify-content-between align-items-center mb-3", children=[
                        html.Span(id="browse-results-count",
                                  style={"color": "var(--text-secondary)", "fontSize": "0.875rem"}),
                        dcc.Dropdown(
                            id="browse-sort",
                            options=sort_options,
                            value="recent",
                            clearable=False,
                            style={"width": "180px"},
                            className="bg-input",
                        ),
                    ]),

                    # Results
                    html.Div(id="browse-results-container",
                             children=[_listing_row(lst) for lst in MOCK_LISTINGS]),

                    # Pagination
                    html.Div(
                        dbc.Pagination(
                            id="browse-pagination",
                            max_value=5,
                            active_page=1,
                            fully_expanded=False,
                            className="mt-4 justify-content-center",
                            first_last=True,
                            previous_next=True,
                        ),
                        className="d-flex justify-content-center mt-3",
                    ),
                ], md=9),
            ]),
        ], fluid=False),
    ])
