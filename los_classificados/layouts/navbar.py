import dash_bootstrap_components as dbc
from dash import html, dcc


def navbar_layout():
    return html.Nav(
        className="lc-navbar d-flex align-items-center",
        children=[
            # ── Brand ────────────────────────────────────────────────────
            dcc.Link(
                html.Span([
                    html.I(className="fas fa-map-marker-alt me-2", style={"color": "#00c9a7"}),
                    "Los",
                    html.Span("Classifi", className="lc-brand-alt"),
                    "cados",
                ], className="lc-brand"),
                href="/",
                style={"textDecoration": "none"},
            ),

            # ── Centre search ────────────────────────────────────────────
            html.Div(
                dcc.Input(
                    id="nav-search-input",
                    placeholder="Search listings, services, real estate…",
                    type="text",
                    className="form-control navbar-search-input",
                    debounce=True,
                ),
                className="navbar-search-wrap d-none d-lg-block",
            ),

            # ── Nav links ────────────────────────────────────────────────
            html.Div(
                className="d-flex align-items-center gap-1 ms-auto",
                children=[
                    dcc.Link("Browse",  href="/browse",  className="nav-link-lc"),
                    dcc.Link("Services",href="/browse?category=services", className="nav-link-lc"),
                    dcc.Link("Prime",   href="/prime",   className="nav-link-lc"),
                    dcc.Link(
                        [html.I(className="fas fa-chart-line me-1"), "My Leads"],
                        href="/leads",
                        className="nav-link-lc",
                    ),
                    html.Div(className="vr mx-2", style={"opacity": "0.2", "height": "24px"}),
                    dcc.Link(
                        [html.I(className="fas fa-plus me-1"), "Post Ad"],
                        href="/post-ad",
                        className="btn btn-teal btn-sm px-3 py-2",
                        style={"textDecoration": "none"},
                    ),
                    dbc.DropdownMenu(
                        label=html.I(className="fas fa-user-circle fa-lg"),
                        children=[
                            dbc.DropdownMenuItem("My Profile"),
                            dbc.DropdownMenuItem("My Listings"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Sign Out", href="/"),
                        ],
                        toggle_class_name="btn btn-outline-secondary btn-sm ms-2",
                        align_end=True,
                    ),
                ],
            ),
        ],
    )
