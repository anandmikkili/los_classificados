"""Prime page callbacks – billing toggle and CTA navigation."""
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from los_classificados.server import app
from los_classificados.config import Config


@app.callback(
    Output("url", "href", allow_duplicate=True),
    Input("prime-hero-btn", "n_clicks"),
    prevent_initial_call=True,
)
def prime_hero_cta(n):
    if not n:
        raise PreventUpdate
    # In production this would go to /checkout or /signup
    return "/post-ad"


@app.callback(
    Output("url", "href", allow_duplicate=True),
    Input("prime-final-btn", "n_clicks"),
    prevent_initial_call=True,
)
def prime_final_cta(n):
    if not n:
        raise PreventUpdate
    return "/post-ad"
