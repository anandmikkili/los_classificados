"""Home page callbacks – hero search and category card navigation."""
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import dash
from los_classificados.server import app


@app.callback(
    Output("url", "href"),
    Input("hero-search-btn", "n_clicks"),
    State("hero-search-input", "value"),
    State("hero-city-select", "value"),
    prevent_initial_call=True,
)
def hero_search_navigate(n_clicks, query, city):
    if not n_clicks:
        raise PreventUpdate
    parts = []
    if query:
        parts.append(f"q={query}")
    if city and city != "All Cities":
        parts.append(f"city={city}")
    qs = "&".join(parts)
    return f"/browse?{qs}" if qs else "/browse"


@app.callback(
    Output("url", "href", allow_duplicate=True),
    Input({"type": "cat-card", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def category_card_navigate(n_clicks_list):
    if not dash.ctx.triggered_id or not any(n_clicks_list):
        raise PreventUpdate
    try:
        cat_id = dash.ctx.triggered_id["index"]
        return f"/browse?category={cat_id}"
    except Exception:
        raise PreventUpdate
