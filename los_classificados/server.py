"""Dash application instance – imported by all callback modules to avoid circular imports."""
import dash
import dash_bootstrap_components as dbc

EXTERNAL_STYLESHEETS = [
    dbc.themes.CYBORG,  # dark Bootstrap base
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
]

EXTERNAL_SCRIPTS = [
    # optional: keep for future map integrations
]

app = dash.Dash(
    __name__,
    external_stylesheets=EXTERNAL_STYLESHEETS,
    suppress_callback_exceptions=True,
    title="LosClassificados – Local Marketplace",
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "Digital marketplace for free classified ads, real estate, rentals and local services."},
        {"property": "og:title", "content": "LosClassificados"},
        {"property": "og:description", "content": "Connect with local service providers and sellers."},
    ],
)

# Expose the underlying Flask server for production WSGI deployment (gunicorn, etc.)
server = app.server
