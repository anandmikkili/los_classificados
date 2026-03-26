"""Public business profile / storefront page – customer-facing view at /business?id=b1."""
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import html, dcc

from los_classificados.utils.mock_data import (
    MOCK_BUSINESS_PROFILE,
    MOCK_USER_LISTINGS,
    PRICE_RANGE_LABEL,
)


# ── Small helpers ─────────────────────────────────────────────────────────────

def _stars(rating: float):
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return html.Span([
        *[html.I(className="fas fa-star", style={"color": "#fbbf24", "fontSize": "0.85rem"}) for _ in range(full)],
        *[html.I(className="fas fa-star-half-alt", style={"color": "#fbbf24", "fontSize": "0.85rem"}) for _ in range(half)],
        *[html.I(className="far fa-star", style={"color": "#fbbf24", "fontSize": "0.85rem"}) for _ in range(empty)],
    ])


def _section_hdr(icon, title):
    return html.Div(
        className="d-flex align-items-center gap-2 mb-3",
        children=[
            html.I(className=f"fas {icon}", style={"color": "var(--accent-teal)", "fontSize": "1rem"}),
            html.Span(title, style={"fontWeight": "800", "fontSize": "1.05rem"}),
        ],
    )


def _stat_chip(value, label, icon):
    return html.Div(
        className="d-flex flex-column align-items-center px-4 py-2",
        children=[
            html.Div([
                html.I(className=f"fas {icon} me-1", style={"color": "var(--accent-teal)"}),
                html.Span(value, style={"fontWeight": "700", "fontSize": "1.1rem"}),
            ]),
            html.Span(label, style={"color": "var(--text-secondary)", "fontSize": "0.75rem"}),
        ],
    )


def _review_card(review):
    stars = _stars(review["rating"])
    date_str = review["date"].strftime("%b %d, %Y")
    return html.Div(
        className="lc-card p-3 mb-3",
        children=[
            html.Div(className="d-flex align-items-start justify-content-between mb-1", children=[
                html.Div([
                    html.Span(review["author"], style={"fontWeight": "700", "marginRight": "8px"}),
                    html.Span(review["city"], style={"color": "var(--text-secondary)", "fontSize": "0.8rem"}),
                ]),
                html.Span(date_str, style={"color": "var(--text-secondary)", "fontSize": "0.78rem"}),
            ]),
            html.Div(stars, className="mb-2"),
            html.P(review["text"], style={"margin": 0, "fontSize": "0.9rem", "lineHeight": "1.5"}),
        ],
    )


def _listing_chip(listing):
    """Compact horizontal listing card for the 'Active Listings' section."""
    price = f"${listing['price']:,.0f}" if listing.get("price") else "Contact"
    if listing.get("is_featured"):
        badge = dbc.Badge("Featured", color="warning", text_color="dark",
                          className="me-2", style={"fontSize": "0.7rem"})
    else:
        badge = None

    return html.Div(
        className="lc-card p-3 mb-2",
        children=[
            html.Div(className="d-flex align-items-center gap-3", children=[
                html.Img(
                    src=listing.get("image", "https://via.placeholder.com/80x60"),
                    style={"width": "80px", "height": "60px", "objectFit": "cover",
                           "borderRadius": "6px", "flexShrink": "0"},
                ),
                html.Div(className="flex-grow-1 min-w-0", children=[
                    html.Div(className="d-flex align-items-center flex-wrap gap-1 mb-1", children=[
                        *([badge] if badge else []),
                        html.Span(listing["title"],
                                  style={"fontWeight": "700", "fontSize": "0.9rem",
                                         "overflow": "hidden", "textOverflow": "ellipsis",
                                         "whiteSpace": "nowrap"}),
                    ]),
                    html.Div([
                        html.I(className="fas fa-map-marker-alt me-1",
                               style={"color": "var(--accent-teal)", "fontSize": "0.75rem"}),
                        html.Span(listing.get("city", ""), style={"fontSize": "0.8rem",
                                  "color": "var(--text-secondary)"}),
                    ]),
                ]),
                html.Div([
                    html.Span(price, style={"fontWeight": "800", "fontSize": "1rem",
                                            "color": "var(--accent-teal)"}),
                ], className="text-end flex-shrink-0"),
            ]),
        ],
    )


def _contact_sidebar(profile):
    phone    = profile.get("phone", "")
    whatsapp = profile.get("whatsapp", "")
    email    = profile.get("email", "")

    contact_btns = []
    if phone:
        contact_btns.append(
            html.A(
                [html.I(className="fas fa-phone me-2"), f"Call {phone}"],
                href=f"tel:{phone}",
                className="btn btn-outline-secondary w-100 mb-2",
                style={"borderRadius": "8px"},
            )
        )
    if whatsapp:
        wa_number = whatsapp.replace("+", "").replace(" ", "")
        contact_btns.append(
            html.A(
                [html.I(className="fab fa-whatsapp me-2", style={"color": "#25d366"}), "Chat on WhatsApp"],
                href=f"https://wa.me/{wa_number}",
                target="_blank",
                className="btn btn-outline-secondary w-100 mb-2",
                style={"borderRadius": "8px"},
            )
        )
    if email:
        contact_btns.append(
            html.A(
                [html.I(className="fas fa-envelope me-2"), "Send Email"],
                href=f"mailto:{email}",
                className="btn btn-outline-secondary w-100 mb-2",
                style={"borderRadius": "8px"},
            )
        )
    if profile.get("website"):
        contact_btns.append(
            html.A(
                [html.I(className="fas fa-globe me-2"), "Visit Website"],
                href=profile["website"],
                target="_blank",
                className="btn btn-outline-secondary w-100 mb-2",
                style={"borderRadius": "8px"},
            )
        )

    return html.Div(
        style={"position": "sticky", "top": "80px"},
        children=[
            # Quote request card
            html.Div(
                className="lc-card p-4 mb-3",
                children=[
                    html.H6("Request a Quote", style={"fontWeight": "800", "marginBottom": "16px"}),
                    dbc.Input(id="biz-quote-name",    placeholder="Your name",    className="mb-2",
                              style={"borderRadius": "8px"}),
                    dbc.Input(id="biz-quote-phone",   placeholder="Phone number", className="mb-2",
                              type="tel", style={"borderRadius": "8px"}),
                    dbc.Input(id="biz-quote-email",   placeholder="Email",        className="mb-2",
                              type="email", style={"borderRadius": "8px"}),
                    dbc.Textarea(
                        id="biz-quote-message",
                        placeholder="Describe your project…",
                        rows=3,
                        className="mb-3",
                        style={"borderRadius": "8px", "resize": "none"},
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-paper-plane me-2"), "Send Request"],
                        id="biz-quote-submit",
                        color="teal",
                        className="w-100 btn-teal",
                        n_clicks=0,
                    ),
                    html.Div(id="biz-quote-result", className="mt-2"),
                ],
            ),
            # Contact buttons card
            html.Div(
                className="lc-card p-3",
                children=[
                    html.Div(style={"fontWeight": "700", "marginBottom": "12px"}, children="Contact Directly"),
                    *contact_btns,
                ],
            ),
        ],
    )


# ── Main layout ───────────────────────────────────────────────────────────────

def business_profile_layout(business_id: str = "b1"):
    """Public storefront page for a business profile."""
    # For now use the mock profile; a real app would look up by business_id
    profile  = MOCK_BUSINESS_PROFILE
    listings = [l for l in MOCK_USER_LISTINGS if l.get("status") == "active"]

    name         = profile.get("business_name", "Business")
    tagline      = profile.get("tagline", "")
    description  = profile.get("description", "")
    rating       = profile.get("rating", 0.0)
    review_count = profile.get("review_count", 0)
    logo         = profile.get("logo", "")
    cover        = profile.get("cover", "")
    is_verified  = profile.get("is_verified", False)
    is_prime     = profile.get("is_prime", False)
    reviews      = profile.get("reviews", [])
    portfolio    = profile.get("portfolio", [])
    service_areas = profile.get("service_areas", [])
    city         = profile.get("city", "")
    member_since = profile.get("member_since")
    social       = profile.get("social", {})

    member_str = member_since.strftime("%B %Y") if member_since else "—"
    price_label = PRICE_RANGE_LABEL.get(profile.get("price_range", ""), "")

    # ── Badges ────────────────────────────────────────────────────────────────
    badges = []
    if is_verified:
        badges.append(dbc.Badge(
            [html.I(className="fas fa-check-circle me-1"), "Verified"],
            color="success", className="me-1 px-2 py-1",
        ))
    if is_prime:
        badges.append(dbc.Badge(
            [html.I(className="fas fa-star me-1"), "Prime"],
            style={"background": "linear-gradient(135deg,#ffd700,#ff8c00)",
                   "color": "#1a1a2e"},
            className="me-1 px-2 py-1",
        ))

    # ── Social links ─────────────────────────────────────────────────────────
    social_links = []
    icon_map = {
        "facebook":  ("fab fa-facebook-f",  "#1877f2"),
        "instagram": ("fab fa-instagram",   "#e1306c"),
        "linkedin":  ("fab fa-linkedin-in", "#0a66c2"),
        "twitter":   ("fab fa-twitter",     "#1da1f2"),
    }
    for platform, url in social.items():
        if url:
            ico, color = icon_map.get(platform, ("fas fa-link", "#6b7280"))
            social_links.append(
                html.A(
                    html.I(className=f"{ico}"),
                    href=url, target="_blank",
                    style={"width": "34px", "height": "34px", "borderRadius": "50%",
                           "background": color, "color": "#fff", "display": "inline-flex",
                           "alignItems": "center", "justifyContent": "center",
                           "fontSize": "0.85rem", "textDecoration": "none"},
                    className="me-2",
                )
            )

    # ── Cover + header block ──────────────────────────────────────────────────
    cover_block = html.Div(
        style={"position": "relative", "marginBottom": "60px"},
        children=[
            # Cover image
            html.Div(
                style={
                    "height": "240px",
                    "background": f"url({cover}) center/cover no-repeat" if cover
                                  else "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
                    "borderRadius": "0 0 12px 12px",
                },
            ),
            # Logo avatar overlapping cover
            html.Div(
                style={
                    "position": "absolute", "bottom": "-48px", "left": "40px",
                    "width": "96px", "height": "96px", "borderRadius": "50%",
                    "border": "4px solid var(--surface-dark)",
                    "overflow": "hidden", "background": "var(--surface-card)",
                },
                children=[
                    html.Img(src=logo, style={"width": "100%", "height": "100%", "objectFit": "cover"})
                    if logo else html.I(className="fas fa-store fa-2x",
                                        style={"color": "var(--accent-teal)", "padding": "28px"}),
                ],
            ),
            # Back link
            dcc.Link(
                [html.I(className="fas fa-arrow-left me-2"), "Back to Directory"],
                href="/providers",
                style={"position": "absolute", "top": "16px", "left": "16px",
                       "color": "#fff", "textDecoration": "none", "background": "rgba(0,0,0,0.45)",
                       "padding": "6px 14px", "borderRadius": "20px", "fontSize": "0.85rem"},
            ),
            # Dashboard link (owner)
            dcc.Link(
                [html.I(className="fas fa-cog me-1"), "Manage"],
                href="/dashboard",
                style={"position": "absolute", "top": "16px", "right": "16px",
                       "color": "#fff", "textDecoration": "none", "background": "rgba(0,0,0,0.45)",
                       "padding": "6px 14px", "borderRadius": "20px", "fontSize": "0.85rem"},
            ),
        ],
    )

    # ── Business identity ─────────────────────────────────────────────────────
    identity_block = html.Div(
        className="ps-2 mb-3",
        children=[
            html.Div(className="d-flex align-items-start justify-content-between flex-wrap gap-2", children=[
                html.Div([
                    html.H1(name, style={"fontWeight": "900", "fontSize": "1.8rem", "margin": "0 0 4px"}),
                    html.P(tagline, style={"color": "var(--text-secondary)", "margin": "0 0 8px",
                                          "fontSize": "1rem"}),
                    html.Div(className="d-flex align-items-center flex-wrap gap-1 mb-2", children=[
                        *badges,
                        html.Span(f"★ {rating:.1f}",
                                  style={"fontWeight": "700", "color": "#fbbf24", "fontSize": "0.9rem"}),
                        html.Span(f"({review_count} reviews)",
                                  style={"color": "var(--text-secondary)", "fontSize": "0.85rem",
                                         "marginLeft": "4px"}),
                        html.Span("·", style={"color": "var(--text-secondary)", "margin": "0 4px"}),
                        html.I(className="fas fa-map-marker-alt me-1",
                               style={"color": "var(--accent-teal)", "fontSize": "0.8rem"}),
                        html.Span(city, style={"fontSize": "0.85rem", "color": "var(--text-secondary)"}),
                    ]),
                    html.Div(social_links) if social_links else None,
                ]),
            ]),
        ],
    )

    # ── Stats strip ───────────────────────────────────────────────────────────
    stats_strip = html.Div(
        className="lc-card mb-4",
        style={"borderRadius": "12px", "overflow": "hidden"},
        children=[
            html.Div(
                className="d-flex justify-content-around flex-wrap",
                style={"borderBottom": "1px solid var(--border-color)", "padding": "4px 0"},
                children=[
                    _stat_chip(f"{profile.get('jobs_completed', 0)}+",   "Jobs Completed",    "fa-briefcase"),
                    html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                    _stat_chip(f"{profile.get('years_experience', 0)} yrs", "Experience",      "fa-certificate"),
                    html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                    _stat_chip(profile.get("response_time", "—"),          "Avg. Response",    "fa-clock"),
                    html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                    _stat_chip(price_label or profile.get("price_range", "—"), "Price Range",  "fa-tag"),
                    html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                    _stat_chip(member_str,                                  "Member Since",     "fa-calendar-alt"),
                ],
            ),
        ],
    )

    # ── About section ─────────────────────────────────────────────────────────
    about_section = html.Div(
        className="lc-card p-4 mb-4",
        children=[
            _section_hdr("fa-info-circle", "About"),
            html.P(description, style={"color": "var(--text-secondary)", "lineHeight": "1.7",
                                        "margin": 0}),
        ],
    )

    # ── Service areas ─────────────────────────────────────────────────────────
    area_chips = [
        html.Span(
            area,
            style={"background": "rgba(0,201,167,0.12)", "color": "var(--accent-teal)",
                   "borderRadius": "20px", "padding": "4px 12px", "fontSize": "0.82rem",
                   "fontWeight": "600"},
            className="me-2 mb-2 d-inline-block",
        )
        for area in service_areas
    ]

    areas_section = html.Div(
        className="lc-card p-4 mb-4",
        children=[
            _section_hdr("fa-map-marked-alt", "Service Areas"),
            html.Div(area_chips, className="d-flex flex-wrap"),
        ],
    ) if area_chips else None

    # ── Portfolio section ─────────────────────────────────────────────────────
    portfolio_section = None
    if portfolio:
        portfolio_items = [
            dbc.Col(
                html.Img(
                    src=url,
                    style={"width": "100%", "height": "160px", "objectFit": "cover",
                           "borderRadius": "8px", "cursor": "pointer"},
                ),
                xs=6, sm=4, md=3, className="mb-3",
            )
            for url in portfolio
        ]
        portfolio_section = html.Div(
            className="lc-card p-4 mb-4",
            children=[
                _section_hdr("fa-images", "Portfolio"),
                dbc.Row(portfolio_items),
            ],
        )

    # ── Active listings ───────────────────────────────────────────────────────
    listings_section = None
    if listings:
        listings_section = html.Div(
            className="mb-4",
            children=[
                _section_hdr("fa-list-alt", f"Active Listings ({len(listings)})"),
                *[_listing_chip(l) for l in listings],
                dcc.Link(
                    "Browse all listings →",
                    href="/browse",
                    style={"color": "var(--accent-teal)", "fontSize": "0.85rem",
                           "textDecoration": "none"},
                ),
            ],
        )

    # ── Reviews ───────────────────────────────────────────────────────────────
    reviews_section = None
    if reviews:
        reviews_section = html.Div(
            className="mb-4",
            children=[
                _section_hdr("fa-star", f"Customer Reviews ({review_count})"),
                html.Div(className="d-flex align-items-center gap-3 mb-4", children=[
                    html.Span(f"{rating:.1f}", style={"fontWeight": "900", "fontSize": "3rem",
                                                       "color": "var(--accent-teal)"}),
                    html.Div([
                        _stars(rating),
                        html.Div(f"Based on {review_count} reviews",
                                 style={"fontSize": "0.8rem", "color": "var(--text-secondary)",
                                        "marginTop": "4px"}),
                    ]),
                ]),
                *[_review_card(r) for r in reviews],
            ],
        )

    # ── Assemble page ─────────────────────────────────────────────────────────
    main_col = html.Div([
        identity_block,
        stats_strip,
        about_section,
        *([areas_section]   if areas_section   else []),
        *([portfolio_section] if portfolio_section else []),
        *([listings_section] if listings_section else []),
        *([reviews_section]  if reviews_section  else []),
    ])

    return html.Div([
        cover_block,
        dbc.Container([
            dbc.Row([
                dbc.Col(main_col,                    md=8, className="mb-4"),
                dbc.Col(_contact_sidebar(profile),   md=4, className="mb-4"),
            ]),
        ], fluid="lg"),
    ])
