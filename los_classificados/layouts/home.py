import dash_bootstrap_components as dbc
from dash import html, dcc
from los_classificados.utils.mock_data import CATEGORIES, MOCK_LISTINGS, STATS, CITIES, CITY_STATS


# ── Helper: listing card ────────────────────────────────────────────────────

def listing_card(listing):
    badges = []
    if listing["is_prime"]:
        badges.append(html.Span("★ Prime", className="badge-prime me-1"))
    if listing["is_verified"]:
        badges.append(html.Span([html.I(className="fas fa-check-circle me-1"), "Verified"], className="badge-verified me-1"))

    has_whatsapp = bool(listing.get("contact_whatsapp"))
    has_phone    = bool(listing.get("contact_phone"))

    return html.Div(
        className="listing-card",
        children=[
            # image
            html.Img(src=listing["image"], className="listing-card-img", alt=listing["title"]),
            # body
            html.Div(className="listing-card-body", children=[
                html.Div(listing["price_label"], className="listing-price"),
                html.Div(listing["title"], className="listing-title"),
                html.Div(
                    [html.I(className="fas fa-map-marker-alt me-1"), f"{listing['neighborhood']}, {listing['city']}"],
                    className="listing-location",
                ),
                html.Div(badges, className="d-flex flex-wrap gap-1 mt-auto"),
            ]),
            # footer
            html.Div(
                className="listing-footer",
                children=[
                    html.A(
                        [html.I(className="fab fa-whatsapp me-1"), "WhatsApp"],
                        href=f"https://wa.me/{listing['contact_whatsapp'].replace('+','')}" if has_whatsapp else "#",
                        target="_blank",
                        className="btn btn-whatsapp btn-sm px-2 py-1",
                        style={"fontSize": "0.75rem"},
                    ) if has_whatsapp else html.Span(),
                    html.A(
                        [html.I(className="fas fa-phone me-1"), "Call"],
                        href=f"tel:{listing['contact_phone']}" if has_phone else "#",
                        className="btn btn-call btn-sm px-2 py-1",
                        style={"fontSize": "0.75rem"},
                    ) if has_phone else html.Span(),
                    html.Span(
                        [html.I(className="fas fa-eye me-1"), str(listing["views"])],
                        className="ms-auto text-muted-lc",
                        style={"fontSize": "0.75rem"},
                    ),
                ],
            ),
        ],
    )


# ── Helper: category card ───────────────────────────────────────────────────

def category_card(cat):
    return dbc.Col(
        html.Div(
            className="category-card",
            id={"type": "cat-card", "index": cat["id"]},
            children=[
                html.Div(
                    html.I(className=f"fas {cat['icon']}"),
                    className="category-icon",
                    style={"background": f"{cat['color']}1a", "color": cat["color"]},
                ),
                html.Div(cat["label"], className="category-label"),
            ],
        ),
        xs=6, sm=4, md=3, lg=3,
    )


# ── Step card for "how it works" ────────────────────────────────────────────

def step_card(number, title, description, icon):
    return dbc.Col(
        html.Div(className="step-card", children=[
            html.Div(str(number), className="step-number"),
            html.I(className=f"fas {icon} fa-2x mb-3", style={"color": "#00c9a7"}),
            html.H5(title, className="fw-bold mb-2"),
            html.P(description, className="text-secondary-lc", style={"fontSize": "0.9rem", "lineHeight": "1.6"}),
        ]),
        md=4,
    )


# ── Main home layout ────────────────────────────────────────────────────────

def home_layout():
    featured = MOCK_LISTINGS[:6]

    return html.Div([

        # ── Hero ─────────────────────────────────────────────────────────
        html.Div(className="lc-hero", children=[
            dbc.Container([
                dbc.Row(dbc.Col([
                    html.H1([
                        "Find Local Services,",
                        html.Br(),
                        html.Span("Real Estate & More", className="highlight"),
                    ], className="hero-tagline mb-3"),
                    html.P(
                        "Connect with verified local professionals and sellers. "
                        "Post free ads or grow your business with Prime leads.",
                        className="hero-subtitle mb-4",
                    ),
                    # Search bar
                    html.Div(
                        className="hero-search-box mb-3",
                        children=[
                            dcc.Input(
                                id="hero-search-input",
                                placeholder="What are you looking for?",
                                type="text",
                                className="hero-search-input form-control",
                            ),
                            dcc.Dropdown(
                                id="hero-city-select",
                                options=[{"label": "All Cities", "value": "All Cities"}] + [
                                    {"label": c, "value": c} for c in CITIES
                                ],
                                value="All Cities",
                                clearable=False,
                                style={
                                    "width": "190px",
                                    "background": "transparent",
                                    "border": "none",
                                    "color": "#f0f6fc",
                                },
                                className="bg-input border-0",
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-search me-2"), "Search"],
                                id="hero-search-btn",
                                className="btn-teal px-4",
                                n_clicks=0,
                            ),
                        ],
                    ),
                    # Quick category links
                    html.Div(
                        className="d-flex flex-wrap gap-2 mt-2",
                        children=[
                            html.A(
                                [html.I(className=f"fas {cat['icon']} me-1"), cat["label"]],
                                href=f"/browse?category={cat['id']}",
                                className="btn btn-sm",
                                style={
                                    "background": f"{cat['color']}18",
                                    "color": cat["color"],
                                    "borderRadius": "100px",
                                    "border": f"1px solid {cat['color']}40",
                                    "fontSize": "0.78rem",
                                    "fontWeight": "600",
                                    "textDecoration": "none",
                                },
                            )
                            for cat in CATEGORIES
                        ],
                    ),
                ], lg=8)),
            ], fluid=False),
        ]),

        # ── Stats Banner ─────────────────────────────────────────────────
        html.Div(className="stats-banner", children=[
            dbc.Container(dbc.Row([
                dbc.Col(html.Div([
                    html.Div(f"{STATS['total_listings']:,}", className="stat-number"),
                    html.Div("Active Listings", className="stat-label"),
                ], className="stat-item"), xs=6, md=3),
                dbc.Col(html.Div([
                    html.Div(f"{STATS['active_users']:,}", className="stat-number"),
                    html.Div("Registered Users", className="stat-label"),
                ], className="stat-item"), xs=6, md=3),
                dbc.Col(html.Div([
                    html.Div(str(STATS["cities_covered"]), className="stat-number"),
                    html.Div("Cities Covered", className="stat-label"),
                ], className="stat-item"), xs=6, md=3),
                dbc.Col(html.Div([
                    html.Div(f"{STATS['prime_businesses']:,}", className="stat-number"),
                    html.Div("Prime Businesses", className="stat-label"),
                ], className="stat-item"), xs=6, md=3),
            ]), fluid=False),
        ]),

        # ── Browse Categories ─────────────────────────────────────────────
        dbc.Container(className="section", children=[
            html.Div([
                html.H2("Browse by Category", className="section-title"),
                html.P("Explore thousands of listings across every category.", className="section-subtitle"),
            ]),
            dbc.Row([category_card(c) for c in CATEGORIES], className="g-3"),
        ], fluid=False),

        # ── Explore by City ───────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderTop": "1px solid var(--border-color)",
                   "borderBottom": "1px solid var(--border-color)"},
            children=[
                dbc.Container(className="section", children=[
                    dbc.Row([
                        dbc.Col([
                            html.H2("Explore by City", className="section-title"),
                            html.P(
                                "Hyperlocal listings in your area — find what's near you.",
                                className="section-subtitle",
                            ),
                        ]),
                        dbc.Col(
                            dcc.Link(
                                "View all cities →",
                                href="/browse",
                                className="btn btn-outline-teal float-end mt-3",
                            ),
                            className="d-flex align-items-start justify-content-end",
                            md=3,
                        ),
                    ]),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Link(
                                    html.Div(
                                        className="lc-card p-3 text-center city-card",
                                        style={"cursor": "pointer", "transition": "transform 0.15s"},
                                        children=[
                                            html.Div(
                                                html.I(className=f"fas {CITY_STATS[city]['icon']} fa-lg"),
                                                style={
                                                    "width": "44px", "height": "44px",
                                                    "borderRadius": "50%",
                                                    "background": "rgba(0,201,167,0.12)",
                                                    "color": "var(--accent-teal)",
                                                    "display": "flex", "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "margin": "0 auto 0.6rem",
                                                    "fontSize": "1.1rem",
                                                },
                                            ),
                                            html.Div(city, style={"fontWeight": "700", "fontSize": "0.9rem"}),
                                            html.Div(
                                                f"{CITY_STATS[city]['listings']:,} listings",
                                                style={"fontSize": "0.75rem", "color": "var(--text-muted)", "marginTop": "0.2rem"},
                                            ),
                                            html.Span(
                                                [html.I(className="fas fa-fire me-1"), "Trending"],
                                                style={
                                                    "fontSize": "0.65rem", "fontWeight": "700",
                                                    "color": "#ff6b35",
                                                    "background": "rgba(255,107,53,0.12)",
                                                    "padding": "0.15rem 0.5rem",
                                                    "borderRadius": "100px",
                                                    "marginTop": "0.4rem",
                                                    "display": "inline-block",
                                                },
                                            ) if CITY_STATS[city]["trending"] else html.Span(),
                                        ],
                                    ),
                                    href=f"/browse?city={city}",
                                    style={"textDecoration": "none", "color": "inherit"},
                                ),
                                xs=6, sm=4, md=3, lg=3, className="mb-3",
                            )
                            for city in CITIES
                        ],
                        className="g-3",
                    ),
                ], fluid=False),
            ],
        ),

        # ── Featured Listings ─────────────────────────────────────────────
        dbc.Container(className="section pt-0", children=[
            dbc.Row([
                dbc.Col([
                    html.H2("Featured Listings", className="section-title"),
                    html.P("Hand-picked, verified listings updated daily.", className="section-subtitle"),
                ]),
                dbc.Col(
                    dcc.Link("View All →", href="/browse", className="btn btn-outline-teal float-end mt-3"),
                    className="d-flex align-items-start justify-content-end",
                    md=3,
                ),
            ]),
            dbc.Row(
                [dbc.Col(listing_card(lst), xs=12, sm=6, lg=4, className="mb-4") for lst in featured],
                className="g-3",
                id="featured-listings-grid",
            ),
        ], fluid=False),

        # ── How It Works ──────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderTop": "1px solid var(--border-color)", "borderBottom": "1px solid var(--border-color)"},
            children=[
                dbc.Container(className="section", children=[
                    html.Div([
                        html.H2("How It Works", className="section-title text-center"),
                        html.P("Three simple steps to connect with buyers, sellers and local pros.",
                               className="section-subtitle text-center"),
                    ]),
                    dbc.Row([
                        step_card(1, "Post Your Ad",
                            "Create a free listing in minutes. Add photos, set your price, and choose a category. Reach thousands of local buyers.",
                            "fa-edit"),
                        step_card(2, "Connect Directly",
                            "Interested parties contact you via WhatsApp or phone call — no middlemen, no fees for basic contact.",
                            "fa-comments"),
                        step_card(3, "Close the Deal",
                            "Meet locally, exchange goods or services, and leave a review. Prime businesses receive pre-qualified leads automatically.",
                            "fa-handshake"),
                    ], className="g-4 mt-1"),
                ], fluid=False),
            ],
        ),

        # ── Prime CTA ─────────────────────────────────────────────────────
        dbc.Container(className="section", children=[
            html.Div(className="prime-cta-banner", children=[
                dbc.Row([
                    dbc.Col([
                        html.Span("★ Prime", className="badge-prime mb-3 d-inline-block"),
                        html.H2("Grow Your Business Faster", className="section-title"),
                        html.P(
                            "Join 1,800+ verified businesses receiving targeted leads from ready-to-buy customers. "
                            "Track inquiries, manage leads, and close more deals — all from one dashboard.",
                            style={"color": "var(--text-secondary)", "maxWidth": "520px", "lineHeight": "1.7"},
                        ),
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-crown me-2"), "Get Prime – $49.99/mo"],
                                href="/prime",
                                external_link=False,
                                className="btn-prime px-4 py-2 me-3",
                                id="prime-cta-btn",
                            ),
                            dcc.Link("Learn more →", href="/prime", style={"color": "var(--accent-gold)", "fontWeight": "600"}),
                        ], className="mt-3"),
                    ], md=7),
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Div("📈", style={"fontSize": "3rem"}),
                                html.Div("3.4×", style={"fontSize": "2.5rem", "fontWeight": "900", "color": "#ffd700"}),
                                html.Div("More leads vs. free", style={"fontSize": "0.85rem", "color": "var(--text-secondary)"}),
                            ], className="text-center p-3"),
                            html.Div([
                                html.Div("⭐", style={"fontSize": "3rem"}),
                                html.Div("4.8/5", style={"fontSize": "2.5rem", "fontWeight": "900", "color": "#ffd700"}),
                                html.Div("Average business rating", style={"fontSize": "0.85rem", "color": "var(--text-secondary)"}),
                            ], className="text-center p-3"),
                        ], className="d-flex gap-4 justify-content-center"),
                        md=5,
                    ),
                ]),
            ]),
        ], fluid=False),

        # ── Footer ────────────────────────────────────────────────────────
        html.Footer(
            style={"background": "var(--bg-secondary)", "borderTop": "1px solid var(--border-color)", "padding": "3rem 0 2rem"},
            children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.Div("LosClassificados", className="lc-brand mb-2"),
                            html.P("Connecting communities through trusted classifieds.",
                                   style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                        ], md=4),
                        dbc.Col([
                            html.H6("Platform", className="text-uppercase fw-bold mb-3",
                                    style={"fontSize": "0.75rem", "color": "var(--text-muted)", "letterSpacing": "1px"}),
                            html.Ul([
                                html.Li(dcc.Link("Post an Ad", href="/post-ad"), style={"listStyle": "none", "marginBottom": "0.5rem", "fontSize": "0.875rem"}),
                                html.Li(dcc.Link("Browse Listings", href="/browse"), style={"listStyle": "none", "marginBottom": "0.5rem", "fontSize": "0.875rem"}),
                                html.Li(dcc.Link("Prime for Business", href="/prime"), style={"listStyle": "none", "fontSize": "0.875rem"}),
                            ], style={"paddingLeft": "0"}),
                        ], md=2),
                        dbc.Col([
                            html.H6("Categories", className="text-uppercase fw-bold mb-3",
                                    style={"fontSize": "0.75rem", "color": "var(--text-muted)", "letterSpacing": "1px"}),
                            html.Ul([
                                html.Li(dcc.Link(c["label"], href=f"/browse?category={c['id']}"),
                                        style={"listStyle": "none", "marginBottom": "0.5rem", "fontSize": "0.875rem"})
                                for c in CATEGORIES[:4]
                            ], style={"paddingLeft": "0"}),
                        ], md=2),
                        dbc.Col([
                            html.H6("Contact Us", className="text-uppercase fw-bold mb-3",
                                    style={"fontSize": "0.75rem", "color": "var(--text-muted)", "letterSpacing": "1px"}),
                            html.A([html.I(className="fab fa-whatsapp me-2"), "WhatsApp Support"],
                                   href="https://wa.me/15550001234", target="_blank",
                                   className="btn btn-sm btn-whatsapp px-3 mb-2 d-block",
                                   style={"textDecoration": "none", "maxWidth": "200px"}),
                            html.A([html.I(className="fas fa-envelope me-2"), "Email Us"],
                                   href="mailto:support@losclassificados.com",
                                   className="btn btn-sm btn-outline-teal px-3 d-block",
                                   style={"textDecoration": "none", "maxWidth": "200px"}),
                        ], md=4),
                    ]),
                    html.Hr(style={"borderColor": "var(--border-color)", "marginTop": "2rem"}),
                    html.P("© 2025 LosClassificados. All rights reserved.",
                           className="text-center text-muted-lc", style={"fontSize": "0.8rem", "marginBottom": "0"}),
                ], fluid=False),
            ],
        ),
    ])
