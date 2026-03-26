"""
LosClassificados – Digital Marketplace
Entry point for the Plotly Dash application (uv environment).

Run with:
    uv run python main.py
    # or for production:
    uv run gunicorn main:server -b 0.0.0.0:8050
"""
from dash import html, dcc

# ── 1. Create Dash app instance (must come first) ────────────────────────────
from los_classificados.server import app as app  # re-exported so Dash finds it

# Expose Flask server for production WSGI: `gunicorn main:server`
server = app.server

# ── 2. Import layouts ─────────────────────────────────────────────────────────
from los_classificados.layouts.navbar import navbar_layout

# ── 3. Register all callbacks (side-effect imports – decorators run on import) ─
import los_classificados.callbacks as _cb  # registers all @app.callback decorators
_ = _cb  # mark as used

# ── 4. Database init (graceful – falls back to demo mode if MySQL unavailable) ─
from los_classificados.db.connection import init_db, DB_AVAILABLE

if DB_AVAILABLE:
    try:
        init_db()
    except Exception as exc:
        print(f"[DB] Table creation skipped: {exc}")
else:
    print("[DB] MySQL not configured – running in demo/mock-data mode.")

# ── 5. Root app layout ────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"minHeight": "100vh", "background": "var(--bg-primary)"},
    children=[
        dcc.Location(id="url", refresh=False),

        # Persistent top navigation
        navbar_layout(),

        # Page content – swapped out by the routing callback
        html.Div(id="page-content"),
    ],
)

# ── 6. Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from los_classificados.config import Config

    print(f"""
  ╔══════════════════════════════════════════════════╗
  ║   LosClassificados – Digital Marketplace         ║
  ║   http://{Config.APP_HOST}:{Config.APP_PORT}                   ║
  ║   DB mode : {'MySQL' if DB_AVAILABLE else 'Demo (mock data)'}                      ║
  ╚══════════════════════════════════════════════════╝
    """)

    app.run(
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        debug=Config.DEBUG,
    )
