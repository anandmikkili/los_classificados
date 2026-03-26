import dash_bootstrap_components as dbc
from dash import html, dcc
from los_classificados.utils.mock_data import CATEGORIES, CITIES, PLAN_FEATURES


def _section_title(icon, text):
    return html.Div([
        html.I(className=f"fas {icon} me-2 text-teal"),
        html.Span(text, style={"fontWeight": "700", "fontSize": "1.05rem"}),
    ], className="mb-3 pb-2", style={"borderBottom": "1px solid var(--border-color)"})


def post_ad_layout():
    cat_options = [{"label": c["label"], "value": c["id"]} for c in CATEGORIES]
    city_options = [{"label": c, "value": c} for c in CITIES] + [{"label": "Other", "value": "Other"}]

    return html.Div([
        # ── Page header ───────────────────────────────────────────────────
        html.Div(
            style={"background": "var(--bg-secondary)", "borderBottom": "1px solid var(--border-color)",
                   "padding": "1.5rem 0"},
            children=[
                dbc.Container([
                    html.H2([html.I(className="fas fa-plus-circle me-2 text-teal"), "Post a Classified Ad"],
                             style={"fontWeight": "800"}),
                    html.P("Reach thousands of local buyers. Free to post — Prime boosts get you 3× more views.",
                           className="text-secondary-lc mb-0"),
                ], fluid=False),
            ],
        ),

        dbc.Container(className="py-4", children=[
            dbc.Row([

                # ── Left: Form ────────────────────────────────────────────
                dbc.Col([

                    # Notification area
                    html.Div(id="post-ad-alert", className="mb-3"),

                    # ── 1. Category ───────────────────────────────────────
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_title("fa-th-large", "1. Choose Category"),
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    className="category-card",
                                    id={"type": "post-cat-card", "index": cat["id"]},
                                    children=[
                                        html.Div(
                                            html.I(className=f"fas {cat['icon']}"),
                                            className="category-icon",
                                            style={"background": f"{cat['color']}1a", "color": cat["color"]},
                                        ),
                                        html.Div(cat["label"], className="category-label"),
                                    ],
                                ),
                                xs=6, sm=4, md=3, className="mb-2",
                            )
                            for cat in CATEGORIES
                        ]),
                        dcc.Store(id="selected-category-store", data=""),
                        html.Div(id="subcategory-container", className="mt-3"),
                    ]),

                    # ── 2. Ad Details ─────────────────────────────────────
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_title("fa-file-alt", "2. Ad Details"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Title *", className="form-label"),
                                dcc.Input(
                                    id="post-ad-title",
                                    placeholder="e.g. 3BR House for Sale – Great Location",
                                    type="text",
                                    className="form-control mb-3",
                                    maxLength=200,
                                ),
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Description *", className="form-label"),
                                dcc.Textarea(
                                    id="post-ad-description",
                                    placeholder="Describe your listing in detail. Include condition, features, and any relevant information buyers should know.",
                                    className="form-control mb-3",
                                    style={"minHeight": "140px"},
                                    maxLength=3000,
                                ),
                                html.Small(id="desc-char-count", className="text-muted-lc"),
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Price", className="form-label"),
                                dbc.InputGroup([
                                    dbc.InputGroupText("$"),
                                    dbc.Input(
                                        id="post-ad-price",
                                        placeholder="0.00",
                                        type="number",
                                        min=0,
                                        style={"background": "var(--bg-input)", "border": "1.5px solid var(--border-color)",
                                               "color": "var(--text-primary)"},
                                    ),
                                ], className="mb-2"),
                                dbc.Checklist(
                                    id="post-ad-price-opts",
                                    options=[
                                        {"label": "Price is negotiable", "value": "negotiable"},
                                        {"label": "No price / Contact for price", "value": "no_price"},
                                    ],
                                    value=[],
                                    inline=True,
                                    input_style={"accentColor": "var(--accent-teal)"},
                                    label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem", "marginRight": "1rem"},
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("Condition", className="form-label"),
                                dcc.Dropdown(
                                    id="post-ad-condition",
                                    options=[
                                        {"label": "New",           "value": "new"},
                                        {"label": "Like New",      "value": "like_new"},
                                        {"label": "Good",          "value": "good"},
                                        {"label": "Fair",          "value": "fair"},
                                        {"label": "For Parts",     "value": "parts"},
                                        {"label": "N/A (Service)", "value": "na"},
                                    ],
                                    value="good",
                                    clearable=False,
                                    className="mb-3 bg-input",
                                ),
                            ], md=6),
                        ]),
                    ]),

                    # ── 3. Location ───────────────────────────────────────
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_title("fa-map-marker-alt", "3. Location"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("City *", className="form-label"),
                                dcc.Dropdown(
                                    id="post-ad-city",
                                    options=city_options,
                                    placeholder="Select your city",
                                    className="mb-3 bg-input",
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("State / Region", className="form-label"),
                                dcc.Input(
                                    id="post-ad-state",
                                    placeholder="e.g. Florida",
                                    type="text",
                                    className="form-control mb-3",
                                ),
                            ], md=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Neighborhood / Area", className="form-label"),
                                dcc.Dropdown(
                                    id="post-ad-neighborhood",
                                    options=[],
                                    placeholder="Select a neighborhood (choose city first)",
                                    className="mb-3 bg-input",
                                    clearable=True,
                                ),
                            ]),
                        ]),
                        dbc.Checklist(
                            id="post-ad-geo-opts",
                            options=[{"label": "Show approximate location on map", "value": "show_map"}],
                            value=["show_map"],
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                        ),
                    ]),

                    # ── 4. Contact Info ───────────────────────────────────
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_title("fa-address-card", "4. Contact Information"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Phone Number", className="form-label"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fas fa-phone")),
                                    dbc.Input(
                                        id="post-ad-phone",
                                        placeholder="+1 (555) 000-0000",
                                        type="tel",
                                        style={"background": "var(--bg-input)", "border": "1.5px solid var(--border-color)",
                                               "color": "var(--text-primary)"},
                                    ),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                html.Label("WhatsApp Number", className="form-label"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fab fa-whatsapp",
                                                              style={"color": "#25d366"})),
                                    dbc.Input(
                                        id="post-ad-whatsapp",
                                        placeholder="+1 (555) 000-0000",
                                        type="tel",
                                        style={"background": "var(--bg-input)", "border": "1.5px solid var(--border-color)",
                                               "color": "var(--text-primary)"},
                                    ),
                                ], className="mb-3"),
                            ], md=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Email", className="form-label"),
                                dcc.Input(
                                    id="post-ad-email",
                                    placeholder="your@email.com",
                                    type="email",
                                    className="form-control mb-3",
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("Contact Name *", className="form-label"),
                                dcc.Input(
                                    id="post-ad-contact-name",
                                    placeholder="Your name or business name",
                                    type="text",
                                    className="form-control mb-3",
                                ),
                            ], md=6),
                        ]),
                        dbc.Alert(
                            [html.I(className="fas fa-shield-alt me-2"), "Your contact info is only shared with interested parties."],
                            color="info",
                            className="mt-1 alert-info",
                            style={"fontSize": "0.82rem", "padding": "0.6rem 1rem"},
                        ),
                    ]),

                    # ── 5. Photos ─────────────────────────────────────────
                    html.Div(className="lc-card p-4 mb-3", children=[
                        _section_title("fa-images", "5. Photos"),

                        dbc.Row([
                            # Upload zone
                            dbc.Col([
                                dcc.Upload(
                                    id="post-ad-images",
                                    children=html.Div([
                                        html.I(className="fas fa-cloud-upload-alt fa-3x mb-3",
                                               style={"color": "var(--accent-teal)", "opacity": "0.8"}),
                                        html.Div("Drag & drop photos here, or click to select",
                                                 style={"fontWeight": "600", "marginBottom": "0.3rem"}),
                                        html.Small("JPEG · PNG · WebP  ·  Max 5 MB each",
                                                   className="text-muted-lc"),
                                    ], style={"textAlign": "center"}),
                                    className="upload-zone",
                                    multiple=True,
                                    accept="image/jpeg,image/jpg,image/png,image/webp",
                                ),
                            ], md=8),

                            # Photo tips sidebar
                            dbc.Col([
                                html.Div(
                                    className="p-3 h-100",
                                    style={
                                        "background": "var(--bg-secondary)",
                                        "borderRadius": "8px",
                                        "border": "1px solid var(--border-color)",
                                    },
                                    children=[
                                        html.Div(
                                            [html.I(className="fas fa-lightbulb me-2 text-teal"), "Photo Tips"],
                                            style={"fontWeight": "700", "fontSize": "0.875rem", "marginBottom": "0.6rem"},
                                        ),
                                        html.Ul([
                                            html.Li("First photo becomes the cover image",
                                                    style={"fontSize": "0.78rem", "marginBottom": "0.3rem",
                                                           "color": "var(--text-secondary)"}),
                                            html.Li("Use natural lighting & clean backgrounds",
                                                    style={"fontSize": "0.78rem", "marginBottom": "0.3rem",
                                                           "color": "var(--text-secondary)"}),
                                            html.Li("Show all angles or key features",
                                                    style={"fontSize": "0.78rem", "marginBottom": "0.3rem",
                                                           "color": "var(--text-secondary)"}),
                                            html.Li("800 px wide minimum recommended",
                                                    style={"fontSize": "0.78rem", "marginBottom": "0.3rem",
                                                           "color": "var(--text-secondary)"}),
                                            html.Li("Only upload images you own or have rights to use",
                                                    style={"fontSize": "0.78rem", "color": "#ff6b35",
                                                           "fontWeight": "600"}),
                                        ], style={"paddingLeft": "1rem", "marginBottom": "0"}),
                                    ],
                                ),
                            ], md=4),
                        ], className="mb-3 g-3"),

                        # Per-file validation errors
                        html.Div(id="image-upload-alert"),

                        # Photo count / plan limit bar
                        html.Div(id="image-upload-counter", className="mb-2"),

                        # Rich preview grid
                        html.Div(
                            id="uploaded-images-preview",
                            className="d-flex flex-wrap gap-3",
                            style={"minHeight": "0"},
                        ),

                        # Rights & ownership consent
                        html.Hr(className="divider mt-3"),
                        html.Div(
                            className="d-flex align-items-start gap-2 mt-2",
                            children=[
                                dbc.Checklist(
                                    id="image-rights-consent",
                                    options=[{"label": "", "value": "confirmed"}],
                                    value=[],
                                    input_style={"accentColor": "var(--accent-teal)", "marginTop": "2px"},
                                    style={"flexShrink": "0"},
                                ),
                                html.Div([
                                    html.Span(
                                        "I confirm I own or have full rights to use all uploaded images, "
                                        "or they are licensed for commercial use / in the public domain.",
                                        style={"fontSize": "0.82rem", "color": "var(--text-secondary)"},
                                    ),
                                    html.Div(
                                        [
                                            html.I(className="fas fa-shield-alt me-1"),
                                            "Uploading images you do not own may result in your listing "
                                            "being removed and your account suspended.",
                                        ],
                                        style={"fontSize": "0.75rem", "color": "var(--text-muted)",
                                               "marginTop": "0.25rem"},
                                    ),
                                ]),
                            ],
                        ),

                        # Hidden store holding validated image data
                        dcc.Store(id="image-store", data=[]),
                    ]),

                    # ── 6. Plan ───────────────────────────────────────────
                    html.Div(className="lc-card p-4 mb-4", children=[
                        _section_title("fa-star", "6. Choose Your Plan"),
                        dbc.RadioItems(
                            id="post-ad-plan",
                            options=[
                                {
                                    "label": html.Div([
                                        html.Span("Free", style={"fontWeight": "700", "fontSize": "1rem"}),
                                        html.Span(" – Basic listing, newest-first in search. Up to 5 photos.",
                                                  style={"color": "var(--text-secondary)", "fontSize": "0.875rem"}),
                                    ]),
                                    "value": "free",
                                },
                                {
                                    "label": html.Div([
                                        html.Span("⚡ Featured Placement  ", style={"fontWeight": "700", "fontSize": "1rem",
                                                                                    "color": "#ff6b35"}),
                                        html.Span("from $4.99",
                                                  style={"background": "rgba(255,107,53,0.15)", "color": "#ff6b35",
                                                         "border": "1px solid rgba(255,107,53,0.4)",
                                                         "fontWeight": "700", "padding": "0.1rem 0.5rem",
                                                         "borderRadius": "100px", "fontSize": "0.75rem"}),
                                        html.Div("Pinned above all regular listings · ⚡ Featured badge · Time-limited",
                                                 style={"color": "var(--text-secondary)", "fontSize": "0.82rem", "marginTop": "0.2rem"}),
                                    ]),
                                    "value": "featured",
                                },
                                {
                                    "label": html.Div([
                                        html.Span("★ Prime Boost  ", style={"fontWeight": "700", "fontSize": "1rem",
                                                                             "color": "#ffd700"}),
                                        html.Span("$9.99/listing",
                                                  style={"background": "var(--gradient-prime)", "color": "#0d1117",
                                                         "fontWeight": "700", "padding": "0.1rem 0.5rem",
                                                         "borderRadius": "100px", "fontSize": "0.75rem"}),
                                        html.Div("Featured + Prime · 3× more views · 20 photos · Geo-targeting",
                                                 style={"color": "var(--text-secondary)", "fontSize": "0.82rem", "marginTop": "0.2rem"}),
                                    ]),
                                    "value": "prime_boost",
                                },
                            ],
                            value="free",
                            className="mt-2",
                            input_style={"accentColor": "var(--accent-teal)"},
                            label_style={"color": "var(--text-primary)", "marginBottom": "0.75rem"},
                        ),

                        # ── Plan comparison mini-table ──────────────────
                        html.Hr(className="divider mt-3"),
                        html.Div(
                            "Plan comparison",
                            style={"fontSize": "0.75rem", "fontWeight": "700",
                                   "color": "var(--text-muted)", "textTransform": "uppercase",
                                   "letterSpacing": "0.06em", "marginBottom": "0.6rem"},
                        ),
                        html.Div(
                            className="table-responsive",
                            children=[
                                html.Table(
                                    className="w-100",
                                    style={"fontSize": "0.78rem", "borderCollapse": "collapse"},
                                    children=[
                                        html.Thead(html.Tr([
                                            html.Th("Feature", style={"padding": "0.35rem 0.6rem",
                                                                        "color": "var(--text-muted)",
                                                                        "borderBottom": "1px solid var(--border-color)",
                                                                        "fontWeight": "600", "width": "32%"}),
                                            html.Th("Free",    style={"padding": "0.35rem 0.6rem",
                                                                        "color": "var(--text-secondary)",
                                                                        "borderBottom": "1px solid var(--border-color)",
                                                                        "fontWeight": "600", "textAlign": "center"}),
                                            html.Th([html.I(className="fas fa-bolt me-1", style={"color": "#ff6b35"}), "Featured"],
                                                    style={"padding": "0.35rem 0.6rem", "color": "#ff6b35",
                                                           "borderBottom": "1px solid var(--border-color)",
                                                           "fontWeight": "700", "textAlign": "center"}),
                                            html.Th([html.I(className="fas fa-star me-1", style={"color": "#ffd700"}), "Prime"],
                                                    style={"padding": "0.35rem 0.6rem", "color": "#ffd700",
                                                           "borderBottom": "1px solid var(--border-color)",
                                                           "fontWeight": "700", "textAlign": "center"}),
                                        ])),
                                        html.Tbody([
                                            html.Tr([
                                                html.Td(PLAN_FEATURES["free"][i][0],
                                                        style={"padding": "0.3rem 0.6rem",
                                                               "color": "var(--text-muted)",
                                                               "borderBottom": "1px solid var(--border-color)"}),
                                                html.Td(PLAN_FEATURES["free"][i][1],
                                                        style={"padding": "0.3rem 0.6rem", "textAlign": "center",
                                                               "color": "var(--text-secondary)",
                                                               "borderBottom": "1px solid var(--border-color)"}),
                                                html.Td(PLAN_FEATURES["featured"][i][1],
                                                        style={"padding": "0.3rem 0.6rem", "textAlign": "center",
                                                               "color": "var(--text-secondary)",
                                                               "borderBottom": "1px solid var(--border-color)"}),
                                                html.Td(PLAN_FEATURES["prime_boost"][i][1],
                                                        style={"padding": "0.3rem 0.6rem", "textAlign": "center",
                                                               "color": "var(--text-secondary)",
                                                               "borderBottom": "1px solid var(--border-color)"}),
                                            ])
                                            for i in range(len(PLAN_FEATURES["free"]))
                                        ]),
                                    ],
                                ),
                            ],
                        ),
                    ]),

                    # ── 6b. Featured Duration (visible only for Featured / Prime plans) ─
                    html.Div(
                        id="featured-duration-section",
                        style={"display": "none"},
                        children=[
                            html.Div(
                                className="lc-card p-4 mb-4",
                                style={"border": "1.5px solid rgba(255,107,53,0.3)"},
                                children=[
                                    _section_title("fa-clock", "6b. Featured Duration"),
                                    html.P(
                                        "How long should your listing stay pinned above regular results?",
                                        style={"fontSize": "0.875rem", "color": "var(--text-secondary)", "marginBottom": "1rem"},
                                    ),
                                    dbc.RadioItems(
                                        id="post-ad-featured-duration",
                                        options=[
                                            {
                                                "label": html.Div([
                                                    html.Span("7 days", style={"fontWeight": "700"}),
                                                    html.Span("  –  $4.99", style={"color": "#ff6b35", "fontWeight": "600"}),
                                                    html.Span("  Best for quick sales & one-off services",
                                                              style={"color": "var(--text-muted)", "fontSize": "0.82rem"}),
                                                ]),
                                                "value": "7",
                                            },
                                            {
                                                "label": html.Div([
                                                    html.Span("14 days", style={"fontWeight": "700"}),
                                                    html.Span("  –  $8.99", style={"color": "#ff6b35", "fontWeight": "600"}),
                                                    html.Span("  Great for vehicles, real estate & rentals",
                                                              style={"color": "var(--text-muted)", "fontSize": "0.82rem"}),
                                                ]),
                                                "value": "14",
                                            },
                                            {
                                                "label": html.Div([
                                                    html.Span("30 days", style={"fontWeight": "700"}),
                                                    html.Span("  –  $14.99", style={"color": "#ff6b35", "fontWeight": "600"}),
                                                    html.Span("  Ideal for ongoing services & job listings",
                                                              style={"color": "var(--text-muted)", "fontSize": "0.82rem"}),
                                                ]),
                                                "value": "30",
                                            },
                                        ],
                                        value="7",
                                        className="mt-1",
                                        input_style={"accentColor": "#ff6b35"},
                                        label_style={"color": "var(--text-primary)", "marginBottom": "0.6rem"},
                                    ),
                                    dbc.Alert(
                                        [
                                            html.I(className="fas fa-info-circle me-2"),
                                            "Your listing will appear in the ",
                                            html.Strong("⚡ Featured Placements"),
                                            " section at the top of every search until the period expires. "
                                            "You can renew at any time.",
                                        ],
                                        color="warning",
                                        style={"fontSize": "0.82rem", "padding": "0.6rem 1rem", "marginTop": "1rem",
                                               "background": "rgba(255,107,53,0.08)", "border": "1px solid rgba(255,107,53,0.25)",
                                               "color": "var(--text-secondary)"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 7. Prime Geo-Targeting (visible only for Prime Boost plan) ──
                    html.Div(
                        id="prime-targeting-section",
                        style={"display": "none"},
                        children=[
                            html.Div(className="lc-card p-4 mb-4", style={"border": "1.5px solid rgba(255,215,0,0.3)"}, children=[
                                _section_title("fa-crosshairs", "7. Geo-Targeting (Prime)"),
                                html.P(
                                    "Reach buyers in specific cities and neighborhoods. "
                                    "Your listing will be featured prominently to users in these locations.",
                                    style={"fontSize": "0.875rem", "color": "var(--text-secondary)", "marginBottom": "1.25rem"},
                                ),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Target Cities", className="form-label"),
                                        dcc.Dropdown(
                                            id="prime-target-cities",
                                            options=[{"label": c, "value": c} for c in CITIES],
                                            multi=True,
                                            placeholder="Select cities to target…",
                                            className="mb-3 bg-input",
                                        ),
                                    ], md=6),
                                    dbc.Col([
                                        html.Label("Target Neighborhoods", className="form-label"),
                                        dcc.Dropdown(
                                            id="prime-target-neighborhoods",
                                            options=[],
                                            multi=True,
                                            placeholder="Select cities first…",
                                            className="mb-3 bg-input",
                                            disabled=True,
                                        ),
                                    ], md=6),
                                ]),
                                dbc.Checklist(
                                    id="prime-target-opts",
                                    options=[
                                        {"label": "Show only in selected cities (exclude other regions)", "value": "exclusive"},
                                        {"label": "Automatically include nearby cities",                  "value": "nearby"},
                                    ],
                                    value=[],
                                    input_style={"accentColor": "var(--accent-teal)"},
                                    label_style={"color": "var(--text-secondary)", "fontSize": "0.875rem"},
                                ),
                                dbc.Alert(
                                    [
                                        html.I(className="fas fa-info-circle me-2"),
                                        "Geo-targeting boosts your visibility in selected markets. "
                                        "Users browsing those cities will see your listing first.",
                                    ],
                                    color="warning",
                                    style={"fontSize": "0.82rem", "padding": "0.6rem 1rem", "marginTop": "1rem",
                                           "background": "rgba(255,215,0,0.08)", "border": "1px solid rgba(255,215,0,0.25)",
                                           "color": "var(--text-secondary)"},
                                ),
                            ]),
                        ],
                    ),

                    # ── Submit ────────────────────────────────────────────
                    dbc.Row([
                        dbc.Col(
                            dbc.Button(
                                [html.I(className="fas fa-check-circle me-2"), "Publish Ad"],
                                id="post-ad-submit-btn",
                                className="btn-teal w-100 py-3",
                                n_clicks=0,
                                style={"fontSize": "1rem", "fontWeight": "700"},
                            ),
                        ),
                    ]),

                ], md=8),

                # ── Right: Tips sidebar ────────────────────────────────────
                dbc.Col([
                    html.Div(className="lc-card p-4 mb-3", children=[
                        html.H6([html.I(className="fas fa-lightbulb me-2 text-teal"), "Tips for a Great Ad"],
                                 style={"fontWeight": "700", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("Use clear, descriptive titles", style={"marginBottom": "0.5rem", "fontSize": "0.875rem", "color": "var(--text-secondary)"}),
                            html.Li("Add multiple high-quality photos", style={"marginBottom": "0.5rem", "fontSize": "0.875rem", "color": "var(--text-secondary)"}),
                            html.Li("Include specific location details", style={"marginBottom": "0.5rem", "fontSize": "0.875rem", "color": "var(--text-secondary)"}),
                            html.Li("State condition honestly", style={"marginBottom": "0.5rem", "fontSize": "0.875rem", "color": "var(--text-secondary)"}),
                            html.Li("Enable WhatsApp for faster responses", style={"fontSize": "0.875rem", "color": "var(--text-secondary)"}),
                        ], style={"paddingLeft": "1.2rem"}),
                    ]),
                    html.Div(className="prime-cta-banner p-3", children=[
                        html.Div("★ Prime Boost", className="badge-prime mb-2 d-inline-block"),
                        html.H6("Get 3× More Views", style={"fontWeight": "800"}),
                        html.P("Prime listings appear at the top of search results and are highlighted for buyers.",
                               style={"fontSize": "0.82rem", "color": "var(--text-secondary)"}),
                        dbc.Button("Upgrade Now", className="btn-prime w-100 mt-1", id="upgrade-prime-btn", n_clicks=0),
                    ]),
                    html.Div(className="lc-card p-4 mt-3", children=[
                        html.H6([html.I(className="fas fa-shield-alt me-2 text-teal"), "Safe Posting"],
                                 style={"fontWeight": "700", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("Never share bank details upfront", style={"marginBottom": "0.5rem", "fontSize": "0.82rem", "color": "var(--text-secondary)"}),
                            html.Li("Meet in public for transactions", style={"marginBottom": "0.5rem", "fontSize": "0.82rem", "color": "var(--text-secondary)"}),
                            html.Li("Verify buyer identity for high-value items", style={"fontSize": "0.82rem", "color": "var(--text-secondary)"}),
                        ], style={"paddingLeft": "1.2rem"}),
                    ]),
                ], md=4),

            ]),
        ], fluid=False),
    ])
