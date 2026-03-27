"""URL routing callback – maps pathname to the correct page layout."""
from urllib.parse import parse_qs

from dash import Input, Output, html
from los_classificados.server import app
from los_classificados.layouts.home import home_layout
from los_classificados.layouts.browse import browse_layout
from los_classificados.layouts.post_ad import post_ad_layout
from los_classificados.layouts.prime import prime_layout
from los_classificados.layouts.leads import leads_layout
from los_classificados.layouts.my_listings import my_listings_layout
from los_classificados.layouts.providers import providers_layout
from los_classificados.layouts.dashboard import dashboard_layout
from los_classificados.layouts.business_profile import business_profile_layout
from los_classificados.layouts.performance import performance_layout


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search"),
)
def render_page(pathname, search):
    pathname = pathname or "/"

    # Parse query-string params (e.g. ?city=Miami&q=apartments&category=rentals)
    params: dict = {}
    if search:
        raw = parse_qs(search.lstrip("?"))
        params = {k: v[0] for k, v in raw.items()}

    if pathname == "/":
        return home_layout()
    if pathname == "/browse":
        return browse_layout(
            search_query=params.get("q", ""),
            selected_category=params.get("category", ""),
            city=params.get("city", ""),
        )
    if pathname == "/post-ad":
        return post_ad_layout()
    if pathname == "/prime":
        return prime_layout()
    if pathname == "/leads":
        return leads_layout()
    if pathname == "/my-listings":
        return my_listings_layout()
    if pathname == "/providers":
        return providers_layout(
            search_query=params.get("q", ""),
            subcategory=params.get("subcategory", ""),
            city=params.get("city", ""),
        )
    if pathname == "/dashboard":
        return dashboard_layout(active_tab=params.get("tab", "overview"))
    if pathname == "/performance":
        return performance_layout()
    if pathname == "/business":
        return business_profile_layout(business_id=params.get("id", "b1"))
    # 404
    return html.Div(
        className="d-flex flex-column align-items-center justify-content-center",
        style={"minHeight": "60vh", "textAlign": "center"},
        children=[
            html.I(className="fas fa-map-marker-alt fa-4x mb-4", style={"color": "var(--accent-teal)"}),
            html.H2("404 – Page Not Found", style={"fontWeight": "800"}),
            html.P("The page you're looking for doesn't exist.",
                   style={"color": "var(--text-secondary)"}),
        ],
    )
