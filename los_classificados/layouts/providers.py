"""Service Provider Directory – find verified local pros and request quotes."""
import dash_bootstrap_components as dbc
from dash import html, dcc

from los_classificados.utils.mock_data import (
    MOCK_PROVIDERS, CITIES, NEIGHBORHOODS_BY_CITY,
    PROVIDER_SUBCATEGORIES, PRICE_RANGE_LABEL,
)

# ── Shared helpers ────────────────────────────────────────────────────────────

def _stars(rating, small=False):
    """Render filled/half/empty star icons for a numeric rating."""
    size = "0.72rem" if small else "0.85rem"
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return html.Span(
        [html.I(className="fas fa-star",       style={"color": "#ffd700", "fontSize": size})] * full
        + [html.I(className="fas fa-star-half-alt", style={"color": "#ffd700", "fontSize": size})] * half
        + [html.I(className="far fa-star",     style={"color": "#4b5563", "fontSize": size})] * empty,
        style={"letterSpacing": "0.05em"},
    )


def _response_badge(response_time):
    return html.Span(
        [html.I(className="fas fa-bolt me-1"), response_time],
        style={
            "background": "rgba(0,201,167,0.12)", "color": "var(--accent-teal)",
            "border": "1px solid rgba(0,201,167,0.3)",
            "borderRadius": "100px", "padding": "0.1rem 0.5rem",
            "fontSize": "0.68rem", "fontWeight": "700",
        },
    )


def _price_badge(price_range):
    return html.Span(
        price_range,
        style={
            "background": "var(--bg-tertiary)", "color": "var(--text-secondary)",
            "border": "1px solid var(--border-color)",
            "borderRadius": "4px", "padding": "0.1rem 0.45rem",
            "fontSize": "0.72rem", "fontWeight": "700", "letterSpacing": "0.03em",
        },
        title=PRICE_RANGE_LABEL.get(price_range, ""),
    )


# ── Provider directory card (shown in the grid) ───────────────────────────────

def _provider_card(prov):
    has_wa = bool(prov.get("contact_whatsapp"))
    sub_label = " · ".join(prov["subcategories"])

    return html.Div(
        className="lc-card p-0 overflow-hidden",
        style={"cursor": "pointer"},
        id={"type": "provider-card", "index": prov["id"]},
        n_clicks=0,
        children=[
            # Cover strip
            html.Div(
                style={
                    "height": "80px",
                    "backgroundImage": f"url({prov['cover']})",
                    "backgroundSize": "cover",
                    "backgroundPosition": "center",
                    "position": "relative",
                },
                children=[
                    # Prime badge
                    html.Span(
                        "★ Prime",
                        className="badge-prime",
                        style={
                            "position": "absolute", "top": "8px", "right": "8px",
                            "fontSize": "0.68rem",
                        },
                    ) if prov["is_prime"] else None,
                ],
            ),

            html.Div(
                className="p-3",
                style={"position": "relative"},
                children=[
                    # Avatar (overlaps cover)
                    html.Img(
                        src=prov["avatar"],
                        style={
                            "width": "54px", "height": "54px", "borderRadius": "50%",
                            "border": "3px solid var(--bg-secondary)",
                            "position": "absolute", "top": "-27px", "left": "14px",
                            "objectFit": "cover",
                        },
                    ),

                    # Name row (leave space for avatar)
                    html.Div(style={"marginTop": "28px"}, children=[
                        html.Div(
                            className="d-flex justify-content-between align-items-start",
                            children=[
                                html.Div([
                                    html.Div(
                                        className="d-flex align-items-center gap-1",
                                        children=[
                                            html.Span(prov["name"],
                                                      style={"fontWeight": "800", "fontSize": "0.95rem"}),
                                            html.Span(
                                                [html.I(className="fas fa-check-circle me-1"), "Verified"],
                                                className="badge-verified",
                                                style={"fontSize": "0.62rem"},
                                            ) if prov["is_verified"] else None,
                                        ],
                                    ),
                                    html.Div(
                                        sub_label,
                                        style={"fontSize": "0.75rem", "color": "var(--text-muted)",
                                               "marginTop": "0.1rem"},
                                    ),
                                ]),
                                _price_badge(prov["price_range"]),
                            ],
                        ),
                    ]),

                    # Rating row
                    html.Div(
                        className="d-flex align-items-center gap-2 mt-2",
                        children=[
                            _stars(prov["rating"]),
                            html.Span(
                                f"{prov['rating']:.1f}",
                                style={"fontWeight": "700", "fontSize": "0.82rem"},
                            ),
                            html.Span(
                                f"({prov['review_count']} reviews)",
                                style={"fontSize": "0.72rem", "color": "var(--text-muted)"},
                            ),
                        ],
                    ),

                    # Location + response time
                    html.Div(
                        className="d-flex align-items-center gap-2 mt-1 flex-wrap",
                        children=[
                            html.Small(
                                [html.I(className="fas fa-map-marker-alt me-1"), prov["city"]],
                                style={"color": "var(--text-muted)", "fontSize": "0.72rem"},
                            ),
                            html.Small("·", style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                            html.Small(
                                f"{prov['years_experience']} yrs exp",
                                style={"color": "var(--text-muted)", "fontSize": "0.72rem"},
                            ),
                            html.Small("·", style={"color": "var(--text-muted)", "fontSize": "0.72rem"}),
                            html.Small(
                                f"{prov['jobs_completed']} jobs",
                                style={"color": "var(--text-muted)", "fontSize": "0.72rem"},
                            ),
                        ],
                    ),

                    # Response time badge
                    html.Div(_response_badge(prov["response_time"]), className="mt-2"),

                    html.Hr(className="divider mt-3"),

                    # CTA row
                    html.Div(
                        className="d-flex gap-2 mt-2",
                        children=[
                            dbc.Button(
                                [html.I(className="fas fa-file-alt me-1"), "Get a Quote"],
                                id={"type": "get-quote-btn", "index": prov["id"]},
                                size="sm",
                                className="btn-teal flex-grow-1",
                                n_clicks=0,
                                style={"fontSize": "0.78rem"},
                            ),
                            html.A(
                                html.I(className="fab fa-whatsapp"),
                                href=f"https://wa.me/{prov['contact_whatsapp'].replace('+', '')}",
                                target="_blank",
                                className="btn btn-sm btn-whatsapp px-2",
                                title="WhatsApp",
                                style={"fontSize": "0.88rem"},
                            ) if has_wa else None,
                            html.A(
                                html.I(className="fas fa-phone"),
                                href=f"tel:{prov['contact_phone']}",
                                className="btn btn-sm btn-call px-2",
                                title="Call",
                                style={"fontSize": "0.88rem"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ── Provider profile modal ────────────────────────────────────────────────────

def _review_item(rev):
    return html.Div(
        className="mb-3 pb-3",
        style={"borderBottom": "1px solid var(--border-color)"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-start mb-1",
                children=[
                    html.Div([
                        html.Span(rev["author"],
                                  style={"fontWeight": "700", "fontSize": "0.85rem"}),
                        html.Span(
                            [html.I(className="fas fa-map-marker-alt me-1"), rev["city"]],
                            style={"fontSize": "0.72rem", "color": "var(--text-muted)", "marginLeft": "0.4rem"},
                        ),
                    ]),
                    html.Div(
                        className="d-flex align-items-center gap-1",
                        children=[
                            _stars(rev["rating"], small=True),
                            html.Small(
                                rev["date"].strftime("%b %d, %Y") if hasattr(rev["date"], "strftime") else "",
                                style={"color": "var(--text-muted)", "fontSize": "0.68rem"},
                            ),
                        ],
                    ),
                ],
            ),
            html.P(rev["text"],
                   style={"fontSize": "0.82rem", "color": "var(--text-secondary)",
                          "marginBottom": "0", "lineHeight": "1.55"}),
        ],
    )


def _provider_profile_modal():
    return dbc.Modal(
        id="provider-profile-modal",
        size="xl",
        scrollable=True,
        is_open=False,
        children=[
            dbc.ModalHeader(dbc.ModalTitle(id="modal-provider-name")),
            dbc.ModalBody(html.Div(id="modal-provider-body")),
        ],
    )


def _build_profile_body(prov):
    """Return the full modal body children for a given provider dict."""
    has_wa = bool(prov.get("contact_whatsapp"))
    hoods  = ", ".join(prov["neighborhoods_served"][:5])
    if len(prov["neighborhoods_served"]) > 5:
        hoods += f" +{len(prov['neighborhoods_served']) - 5} more"

    return [
        # Cover + avatar header
        html.Div(
            style={
                "height": "140px",
                "backgroundImage": f"url({prov['cover']})",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "borderRadius": "8px 8px 0 0",
                "marginBottom": "0",
                "position": "relative",
            },
        ),
        html.Div(
            className="d-flex align-items-flex-end gap-3 px-3",
            style={"marginTop": "-32px", "marginBottom": "0.75rem"},
            children=[
                html.Img(
                    src=prov["avatar"],
                    style={
                        "width": "72px", "height": "72px", "borderRadius": "50%",
                        "border": "4px solid var(--bg-secondary)", "objectFit": "cover",
                    },
                ),
                html.Div(style={"paddingTop": "38px"}, children=[
                    html.Div(
                        className="d-flex align-items-center gap-2 flex-wrap",
                        children=[
                            html.Span(prov["name"],
                                      style={"fontWeight": "800", "fontSize": "1.1rem"}),
                            html.Span(
                                [html.I(className="fas fa-check-circle me-1"), "Verified"],
                                className="badge-verified",
                            ) if prov["is_verified"] else None,
                            html.Span("★ Prime", className="badge-prime") if prov["is_prime"] else None,
                        ],
                    ),
                    html.Div(
                        " · ".join(prov["subcategories"]),
                        style={"fontSize": "0.8rem", "color": "var(--text-muted)"},
                    ),
                ]),
            ],
        ),

        dbc.Row([
            # Left column – stats + bio + portfolio + reviews
            dbc.Col([
                # Quick stats strip
                html.Div(
                    className="d-flex gap-3 flex-wrap mb-3",
                    children=[
                        html.Div(className="text-center", children=[
                            html.Div(_stars(prov["rating"])),
                            html.Div(
                                f"{prov['rating']:.1f} ({prov['review_count']})",
                                style={"fontSize": "0.75rem", "color": "var(--text-muted)", "marginTop": "0.15rem"},
                            ),
                        ]),
                        html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                        html.Div(className="text-center", children=[
                            html.Div(str(prov["jobs_completed"]),
                                     style={"fontWeight": "800", "fontSize": "1.1rem",
                                            "color": "var(--accent-teal)"}),
                            html.Div("Jobs done", style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                        ]),
                        html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                        html.Div(className="text-center", children=[
                            html.Div(str(prov["years_experience"]),
                                     style={"fontWeight": "800", "fontSize": "1.1rem",
                                            "color": "var(--accent-teal)"}),
                            html.Div("Yrs exp", style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                        ]),
                        html.Div(style={"width": "1px", "background": "var(--border-color)"}),
                        html.Div(children=[
                            _response_badge(prov["response_time"]),
                            html.Div("Typical response",
                                     style={"fontSize": "0.68rem", "color": "var(--text-muted)",
                                            "marginTop": "0.15rem", "textAlign": "center"}),
                        ]),
                    ],
                ),

                # Bio
                html.Div(
                    className="lc-card p-3 mb-3",
                    children=[
                        html.Div("About", style={"fontWeight": "700", "fontSize": "0.85rem",
                                                  "color": "var(--text-muted)", "marginBottom": "0.5rem",
                                                  "textTransform": "uppercase", "letterSpacing": "0.05em"}),
                        html.P(prov["bio"],
                               style={"fontSize": "0.875rem", "color": "var(--text-secondary)",
                                      "lineHeight": "1.6", "marginBottom": "0"}),
                    ],
                ),

                # Service areas
                html.Div(
                    className="lc-card p-3 mb-3",
                    children=[
                        html.Div("Service Areas", style={"fontWeight": "700", "fontSize": "0.85rem",
                                                          "color": "var(--text-muted)", "marginBottom": "0.5rem",
                                                          "textTransform": "uppercase", "letterSpacing": "0.05em"}),
                        html.Div(
                            className="d-flex flex-wrap gap-1",
                            children=[
                                html.Span(
                                    h,
                                    style={
                                        "background": "rgba(0,201,167,0.08)",
                                        "color": "var(--accent-teal)",
                                        "border": "1px solid rgba(0,201,167,0.2)",
                                        "borderRadius": "100px",
                                        "padding": "0.15rem 0.55rem",
                                        "fontSize": "0.72rem",
                                        "fontWeight": "600",
                                    },
                                )
                                for h in prov["neighborhoods_served"]
                            ],
                        ),
                    ],
                ),

                # Portfolio
                html.Div(
                    className="lc-card p-3 mb-3",
                    children=[
                        html.Div("Portfolio", style={"fontWeight": "700", "fontSize": "0.85rem",
                                                      "color": "var(--text-muted)", "marginBottom": "0.6rem",
                                                      "textTransform": "uppercase", "letterSpacing": "0.05em"}),
                        html.Div(
                            className="d-flex flex-wrap gap-2",
                            children=[
                                html.Img(
                                    src=img,
                                    style={"width": "140px", "height": "100px",
                                           "objectFit": "cover", "borderRadius": "6px",
                                           "border": "1px solid var(--border-color)"},
                                )
                                for img in prov["portfolio"]
                            ],
                        ),
                    ],
                ),

                # Reviews
                html.Div(
                    className="lc-card p-3",
                    children=[
                        html.Div(
                            className="d-flex justify-content-between align-items-center mb-2",
                            children=[
                                html.Div("Reviews", style={"fontWeight": "700", "fontSize": "0.85rem",
                                                            "color": "var(--text-muted)",
                                                            "textTransform": "uppercase",
                                                            "letterSpacing": "0.05em"}),
                                html.Span(f"{prov['review_count']} total",
                                          style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                            ],
                        ),
                        html.Div([_review_item(r) for r in prov["reviews"]]),
                    ],
                ),
            ], md=7),

            # Right column – quote request form
            dbc.Col([
                html.Div(
                    className="lc-card p-4",
                    style={"position": "sticky", "top": "1rem"},
                    children=[
                        html.Div(
                            className="d-flex align-items-center gap-2 mb-3",
                            children=[
                                html.I(className="fas fa-file-alt", style={"color": "var(--accent-teal)"}),
                                html.Strong("Request a Quote",
                                            style={"fontSize": "1rem", "fontWeight": "800"}),
                            ],
                        ),
                        html.P(
                            f"Describe your project and {prov['owner_name']} will respond typically "
                            f"{prov['response_time']}.",
                            style={"fontSize": "0.8rem", "color": "var(--text-secondary)", "marginBottom": "1rem"},
                        ),

                        # Form fields
                        dcc.Store(id="quote-provider-id-store", data=prov["id"]),

                        html.Div([
                            html.Label("Your Name", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dcc.Input(id="quote-name", type="text", placeholder="Full name",
                                      className="form-control mb-2",
                                      style={"fontSize": "0.82rem", "background": "var(--bg-tertiary)",
                                             "border": "1px solid var(--border-color)", "color": "inherit"}),

                            html.Label("Phone / WhatsApp", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dcc.Input(id="quote-phone", type="tel", placeholder="+1 (555) 000-0000",
                                      className="form-control mb-2",
                                      style={"fontSize": "0.82rem", "background": "var(--bg-tertiary)",
                                             "border": "1px solid var(--border-color)", "color": "inherit"}),

                            html.Label("Service Needed", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dcc.Dropdown(
                                id="quote-service-type",
                                options=[{"label": s, "value": s}
                                         for s in prov["subcategories"]],
                                placeholder="Select service…",
                                className="bg-input mb-2",
                                style={"fontSize": "0.82rem"},
                            ),

                            html.Label("Preferred Contact Method", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dbc.RadioItems(
                                id="quote-contact-method",
                                options=[
                                    {"label": html.Span([html.I(className="fab fa-whatsapp me-1",
                                                                 style={"color": "#25d366"}), "WhatsApp"],
                                                        style={"fontSize": "0.8rem"}),
                                     "value": "whatsapp",
                                     "disabled": not has_wa},
                                    {"label": html.Span([html.I(className="fas fa-phone me-1",
                                                                 style={"color": "#3b82f6"}), "Phone Call"],
                                                        style={"fontSize": "0.8rem"}),
                                     "value": "phone"},
                                    {"label": html.Span([html.I(className="fas fa-envelope me-1",
                                                                 style={"color": "#f59e0b"}), "Email"],
                                                        style={"fontSize": "0.8rem"}),
                                     "value": "email"},
                                ],
                                value="whatsapp" if has_wa else "phone",
                                className="mb-2",
                                input_style={"accentColor": "var(--accent-teal)"},
                            ),

                            html.Label("Project Description", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dcc.Textarea(
                                id="quote-description",
                                placeholder="Describe what you need — location, size, urgency, any relevant details…",
                                className="form-control mb-2",
                                style={"fontSize": "0.82rem", "background": "var(--bg-tertiary)",
                                       "border": "1px solid var(--border-color)", "color": "inherit",
                                       "resize": "vertical", "minHeight": "90px"},
                            ),

                            html.Label("Approximate Budget", className="form-label",
                                       style={"fontSize": "0.82rem", "fontWeight": "600"}),
                            dcc.Dropdown(
                                id="quote-budget",
                                options=[
                                    {"label": "Under $100",    "value": "<100"},
                                    {"label": "$100 – $500",   "value": "100-500"},
                                    {"label": "$500 – $2,000", "value": "500-2000"},
                                    {"label": "$2,000 – $10,000", "value": "2000-10000"},
                                    {"label": "Over $10,000",  "value": ">10000"},
                                    {"label": "Not sure yet",  "value": "unknown"},
                                ],
                                placeholder="Select budget range…",
                                className="bg-input mb-3",
                                style={"fontSize": "0.82rem"},
                            ),

                            html.Div(id="quote-alert"),

                            dbc.Button(
                                [html.I(className="fas fa-paper-plane me-2"), "Send Quote Request"],
                                id="quote-submit-btn",
                                className="btn-teal w-100",
                                n_clicks=0,
                                style={"fontSize": "0.875rem"},
                            ),
                        ]),

                        html.Div(
                            className="d-flex align-items-center gap-1 mt-3",
                            children=[
                                html.I(className="fas fa-shield-alt",
                                       style={"color": "var(--text-muted)", "fontSize": "0.75rem"}),
                                html.Small(
                                    "Your contact info is only shared with this provider.",
                                    style={"color": "var(--text-muted)", "fontSize": "0.72rem"},
                                ),
                            ],
                        ),
                    ],
                ),
            ], md=5),
        ], className="g-3"),
    ]


# ── Main layout ───────────────────────────────────────────────────────────────

def providers_layout(search_query="", subcategory="", city=""):
    subcat_options = (
        [{"label": "All Services", "value": ""}]
        + [{"label": s, "value": s} for s in PROVIDER_SUBCATEGORIES.get("services", [])]
    )
    city_options = (
        [{"label": "All Cities", "value": ""}]
        + [{"label": c, "value": c} for c in CITIES]
    )
    sort_options = [
        {"label": "Top Rated",      "value": "rating"},
        {"label": "Most Reviewed",  "value": "reviews"},
        {"label": "Fastest Reply",  "value": "response"},
        {"label": "Most Jobs Done", "value": "jobs"},
        {"label": "Newest",         "value": "newest"},
    ]

    return html.Div([
        # ── Page header ───────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderBottom": "1px solid var(--border-color)",
                   "padding": "2rem 0 1.5rem"},
            children=[
                dbc.Container([
                    html.Div(
                        className="d-flex align-items-center gap-2 mb-1",
                        children=[
                            html.I(className="fas fa-check-circle fa-lg",
                                   style={"color": "var(--accent-teal)"}),
                            html.H2("Find Verified Service Providers",
                                    style={"fontWeight": "800", "marginBottom": "0"}),
                        ],
                    ),
                    html.P(
                        "Hire trusted, background-checked professionals for any home or business need.",
                        style={"color": "var(--text-secondary)", "marginBottom": "1.25rem",
                               "fontSize": "0.95rem"},
                    ),

                    # Search bar
                    dbc.Row([
                        dbc.Col(
                            dcc.Input(
                                id="providers-search-input",
                                value=search_query,
                                placeholder="Search by name, service, or keyword…",
                                type="text",
                                className="form-control",
                                debounce=True,
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="providers-subcat-select",
                                options=subcat_options,
                                value=subcategory or "",
                                placeholder="Service type",
                                clearable=False,
                                className="bg-input",
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="providers-city-select",
                                options=city_options,
                                value=city or "",
                                placeholder="City",
                                clearable=False,
                                className="bg-input",
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dbc.Button(
                                [html.I(className="fas fa-search me-2"), "Search"],
                                id="providers-search-btn",
                                className="btn-teal w-100",
                                n_clicks=0,
                            ),
                            md=2,
                        ),
                    ], className="g-2"),
                ], fluid=False),
            ],
        ),

        dbc.Container(className="py-4", children=[
            dbc.Row([
                # ── Sidebar filters ───────────────────────────────────────
                dbc.Col(
                    html.Div(className="filter-sidebar", children=[
                        html.Div("Filters", className="section-title mb-4",
                                 style={"fontSize": "1.05rem"}),

                        # Min rating
                        html.Div("Minimum Rating", className="filter-title"),
                        dbc.RadioItems(
                            id="filter-min-rating",
                            options=[
                                {"label": html.Span([html.I(className="fas fa-star me-1",
                                                            style={"color": "#ffd700", "fontSize": "0.75rem"}),
                                                     "Any rating"], style={"fontSize": "0.85rem"}),
                                 "value": 0},
                                {"label": html.Span(["4.0", html.I(className="fas fa-star ms-1",
                                                                    style={"color": "#ffd700", "fontSize": "0.75rem"}),
                                                     " & up"], style={"fontSize": "0.85rem"}),
                                 "value": 4.0},
                                {"label": html.Span(["4.5", html.I(className="fas fa-star ms-1",
                                                                    style={"color": "#ffd700", "fontSize": "0.75rem"}),
                                                     " & up"], style={"fontSize": "0.85rem"}),
                                 "value": 4.5},
                            ],
                            value=0,
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                        html.Hr(className="divider"),

                        # Verification
                        html.Div("Verification", className="filter-title"),
                        dbc.Checklist(
                            id="filter-verification",
                            options=[
                                {"label": html.Span([html.I(className="fas fa-check-circle me-1",
                                                            style={"color": "var(--accent-teal)"}),
                                                     "Verified only"], style={"fontSize": "0.85rem"}),
                                 "value": "verified"},
                                {"label": html.Span(["★ Prime providers"],
                                                    style={"fontSize": "0.85rem"}),
                                 "value": "prime"},
                            ],
                            value=[],
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)"},
                        ),
                        html.Hr(className="divider"),

                        # Price range
                        html.Div("Price Range", className="filter-title"),
                        dbc.Checklist(
                            id="filter-price-tier",
                            options=[
                                {"label": html.Span(["$ – Budget-friendly"],
                                                    style={"fontSize": "0.85rem"}), "value": "$"},
                                {"label": html.Span(["$$ – Mid-range"],
                                                    style={"fontSize": "0.85rem"}), "value": "$$"},
                                {"label": html.Span(["$$$ – Premium"],
                                                    style={"fontSize": "0.85rem"}), "value": "$$$"},
                            ],
                            value=[],
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)"},
                        ),
                        html.Hr(className="divider"),

                        # Response time
                        html.Div("Response Time", className="filter-title"),
                        dbc.RadioItems(
                            id="filter-response-time",
                            options=[
                                {"label": html.Span("Any response time",
                                                    style={"fontSize": "0.85rem"}), "value": "any"},
                                {"label": html.Span(["< 1 hour"],
                                                    style={"fontSize": "0.85rem"}), "value": "1h"},
                                {"label": html.Span(["< 3 hours"],
                                                    style={"fontSize": "0.85rem"}), "value": "3h"},
                            ],
                            value="any",
                            className="mb-3",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                        html.Hr(className="divider"),

                        dbc.Button(
                            "Clear Filters",
                            id="clear-provider-filters-btn",
                            className="btn-outline-teal w-100",
                            n_clicks=0,
                        ),
                    ]),
                    md=3,
                ),

                # ── Provider grid ─────────────────────────────────────────
                dbc.Col([
                    # Sort + count bar
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-3",
                        children=[
                            html.Span(id="providers-count",
                                      style={"color": "var(--text-secondary)", "fontSize": "0.875rem"}),
                            dcc.Dropdown(
                                id="providers-sort",
                                options=sort_options,
                                value="rating",
                                clearable=False,
                                style={"width": "185px"},
                                className="bg-input",
                            ),
                        ],
                    ),

                    # Results grid
                    html.Div(
                        id="providers-results-container",
                        className="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-3",
                        children=[
                            html.Div(_provider_card(p), className="col")
                            for p in sorted(MOCK_PROVIDERS,
                                            key=lambda p: p["rating"], reverse=True)
                        ],
                    ),
                ], md=9),
            ]),
        ], fluid=False),

        # ── Provider profile modal ────────────────────────────────────────
        _provider_profile_modal(),
    ])
