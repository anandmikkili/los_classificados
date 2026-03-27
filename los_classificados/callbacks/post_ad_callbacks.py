"""Post Ad form callbacks – category selection, image upload/management, submit."""
import base64

import dash
from dash import Input, Output, State, ALL, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import CATEGORIES, NEIGHBORHOODS_BY_CITY, SUBCATEGORIES
from los_classificados.utils.safety import check_content_violations

# ── Image validation constants ────────────────────────────────────────────────

# Max photos per plan
IMAGE_LIMITS = {"free": 5, "featured": 10, "prime_boost": 20}
# Accepted MIME types (no GIFs – keep quality consistent)
ACCEPTED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
# 5 MB per file
MAX_FILE_BYTES = 5 * 1024 * 1024

_PLAN_LABEL = {"free": "Free", "featured": "Featured", "prime_boost": "Prime"}


def _parse_data_uri(data_uri: str) -> tuple[str, bytes]:
    """Return (content_type, raw_bytes) from a Dash Upload data URI."""
    header, b64 = data_uri.split(",", 1)
    content_type = header.split(":")[1].split(";")[0].lower()
    return content_type, base64.b64decode(b64)


def _size_kb(data_uri: str) -> float:
    """Estimate file size in KB from a base64 data URI."""
    b64 = data_uri.split(",", 1)[1]
    padding = b64.count("=")
    return round(((len(b64) * 3) // 4 - padding) / 1024, 1)


# ── Category selection ────────────────────────────────────────────────────────

@app.callback(
    Output("selected-category-store", "data"),
    Input({"type": "post-cat-card", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_category(n_clicks_list):
    if not dash.ctx.triggered_id or not any(n_clicks_list):
        raise PreventUpdate
    try:
        return dash.ctx.triggered_id["index"]
    except Exception:
        raise PreventUpdate


@app.callback(
    Output({"type": "post-cat-card", "index": ALL}, "style"),
    Input("selected-category-store", "data"),
    prevent_initial_call=False,
)
def highlight_selected_category(selected):
    return [
        {"border": f"2px solid {cat['color']}", "background": f"{cat['color']}1a"}
        if cat["id"] == selected else {}
        for cat in CATEGORIES
    ]


@app.callback(
    Output("subcategory-container", "children"),
    Input("selected-category-store", "data"),
    prevent_initial_call=False,
)
def show_subcategories(selected):
    if not selected:
        return []
    subs = SUBCATEGORIES.get(selected, [])
    return [
        html.Label("Subcategory", className="form-label"),
        dcc.Dropdown(
            id="post-ad-subcategory",
            options=[{"label": s, "value": s} for s in subs],
            placeholder="Select subcategory",
            className="bg-input",
        ),
    ]


# ── Description character count ───────────────────────────────────────────────

@app.callback(
    Output("desc-char-count", "children"),
    Input("post-ad-description", "value"),
    prevent_initial_call=False,
)
def update_char_count(text):
    count = len(text or "")
    color = "#ef4444" if count > 2800 else "var(--text-muted)"
    return html.Span(f"{count}/3000 characters", style={"color": color})


# ── Image management ──────────────────────────────────────────────────────────

@app.callback(
    Output("image-store", "data"),
    Output("image-upload-alert", "children"),
    Input("post-ad-images", "contents"),
    State("post-ad-images", "filenames"),
    State("image-store", "data"),
    State("post-ad-plan", "value"),
    prevent_initial_call=True,
)
def add_images(contents, filenames, store, plan):
    """Validate and append uploaded images to the store."""
    if not contents:
        raise PreventUpdate

    store = list(store or [])
    limit = IMAGE_LIMITS.get(plan or "free", 5)
    errors = []

    for data_uri, fname in zip(contents, filenames):
        content_type, file_bytes = _parse_data_uri(data_uri)
        size_kb = _size_kb(data_uri)

        if content_type not in ACCEPTED_TYPES:
            ext = fname.rsplit(".", 1)[-1].upper() if "." in fname else "unknown"
            errors.append(f'"{fname}" — {ext} files are not supported. Use JPEG, PNG, or WebP.')
            continue

        if len(file_bytes) > MAX_FILE_BYTES:
            errors.append(
                f'"{fname}" is {size_kb / 1024:.1f} MB — exceeds the 5 MB per-file limit.'
            )
            continue

        if len(store) >= limit:
            errors.append(
                f'Photo limit reached ({limit} for {_PLAN_LABEL.get(plan or "free", "Free")} plan). '
                "Upgrade your plan or remove existing photos to add more."
            )
            break

        store.append({
            "filename": fname,
            "size_kb": size_kb,
            "data_uri": data_uri,
            "content_type": content_type,
        })

    alert = None
    if errors:
        alert = dbc.Alert(
            [html.I(className="fas fa-exclamation-triangle me-2")]
            + [html.Div(e, style={"marginTop": "0.2rem"}) for e in errors],
            color="warning",
            dismissable=True,
            style={"fontSize": "0.82rem", "marginBottom": "0.5rem"},
        )

    return store, alert


@app.callback(
    Output("image-store", "data", allow_duplicate=True),
    Input({"type": "remove-image-btn", "index": ALL}, "n_clicks"),
    State("image-store", "data"),
    prevent_initial_call=True,
)
def remove_image(n_clicks_list, store):
    """Remove a single image from the store when its × button is clicked."""
    if not dash.ctx.triggered_id or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    idx = dash.ctx.triggered_id["index"]
    store = list(store or [])
    if 0 <= idx < len(store):
        store.pop(idx)
    return store


@app.callback(
    Output("uploaded-images-preview", "children"),
    Output("image-upload-counter", "children"),
    Input("image-store", "data"),
    Input("post-ad-plan", "value"),
    prevent_initial_call=False,
)
def render_image_preview(store, plan):
    """Render the preview grid and photo counter from the current image store."""
    store = store or []
    limit = IMAGE_LIMITS.get(plan or "free", 5)
    count = len(store)
    plan_label = _PLAN_LABEL.get(plan or "free", "Free")

    # ── Counter bar ────────────────────────────────────────────────────
    over_limit = count > limit
    count_color = "#ef4444" if over_limit else ("var(--accent-teal)" if count > 0 else "var(--text-muted)")

    counter_children = [
        html.Span(
            f"{count} / {limit} photos",
            style={"fontWeight": "700", "color": count_color, "fontSize": "0.85rem"},
        ),
        html.Span(
            f"  ·  {plan_label} plan",
            style={"color": "var(--text-muted)", "fontSize": "0.82rem"},
        ),
    ]
    if count > 0 and not over_limit:
        counter_children.append(html.Span(
            "  ·  First photo is your cover image",
            style={"color": "var(--text-muted)", "fontSize": "0.78rem"},
        ))
    if over_limit:
        counter_children.append(html.Span(
            f"  ⚠ Over limit — remove {count - limit} photo(s) or upgrade plan",
            style={"color": "#ef4444", "fontWeight": "600", "fontSize": "0.78rem"},
        ))

    counter = html.Div(counter_children)

    if not store:
        return [], counter

    # ── Preview cards ──────────────────────────────────────────────────
    cards = []
    for i, img in enumerate(store):
        is_cover = i == 0
        short_name = img["filename"][:18] + "…" if len(img["filename"]) > 18 else img["filename"]

        cards.append(
            html.Div(
                style={"position": "relative", "width": "140px", "flexShrink": "0"},
                children=[
                    # Thumbnail image
                    html.Img(
                        src=img["data_uri"],
                        style={
                            "width": "140px",
                            "height": "105px",
                            "objectFit": "cover",
                            "borderRadius": "8px",
                            "display": "block",
                            "border": (
                                "2.5px solid var(--accent-teal)"
                                if is_cover
                                else "1.5px solid var(--border-color)"
                            ),
                        },
                        title=img["filename"],
                    ),

                    # COVER badge (first image only)
                    html.Span(
                        [html.I(className="fas fa-star me-1"), "COVER"],
                        style={
                            "position": "absolute",
                            "top": "6px",
                            "left": "6px",
                            "background": "var(--accent-teal)",
                            "color": "#0d1117",
                            "fontSize": "0.58rem",
                            "fontWeight": "800",
                            "padding": "0.15rem 0.45rem",
                            "borderRadius": "4px",
                            "letterSpacing": "0.05em",
                        },
                    ) if is_cover else None,

                    # Remove (×) button
                    html.Button(
                        "×",
                        id={"type": "remove-image-btn", "index": i},
                        n_clicks=0,
                        title=f"Remove {img['filename']}",
                        style={
                            "position": "absolute",
                            "top": "5px",
                            "right": "5px",
                            "background": "rgba(13,17,23,0.72)",
                            "color": "#fff",
                            "border": "none",
                            "borderRadius": "50%",
                            "width": "22px",
                            "height": "22px",
                            "fontSize": "1rem",
                            "lineHeight": "1",
                            "cursor": "pointer",
                            "padding": "0",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                    ),

                    # Filename + size label
                    html.Div(
                        [
                            html.Small(
                                short_name,
                                style={
                                    "color": "var(--text-muted)",
                                    "fontSize": "0.68rem",
                                    "display": "block",
                                    "overflow": "hidden",
                                    "whiteSpace": "nowrap",
                                    "textOverflow": "ellipsis",
                                },
                            ),
                            html.Small(
                                f"{img['size_kb']} KB",
                                style={"color": "var(--text-muted)", "fontSize": "0.68rem"},
                            ),
                        ],
                        style={"marginTop": "0.3rem", "textAlign": "center", "width": "140px"},
                    ),
                ],
            )
        )

    return cards, counter


# ── Location: city → neighborhood dropdown ────────────────────────────────────

@app.callback(
    Output("post-ad-neighborhood", "options"),
    Output("post-ad-neighborhood", "value"),
    Input("post-ad-city", "value"),
    prevent_initial_call=False,
)
def update_post_ad_neighborhoods(city):
    if not city or city == "Other":
        return [], None
    hoods = NEIGHBORHOODS_BY_CITY.get(city, [])
    return [{"label": h, "value": h} for h in hoods], None


# ── Plan visibility toggles ───────────────────────────────────────────────────

@app.callback(
    Output("featured-duration-section", "style"),
    Input("post-ad-plan", "value"),
    prevent_initial_call=False,
)
def toggle_featured_duration(plan):
    if plan in ("featured", "prime_boost"):
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("prime-targeting-section", "style"),
    Input("post-ad-plan", "value"),
    prevent_initial_call=False,
)
def toggle_prime_geo_section(plan):
    if plan == "prime_boost":
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("prime-target-neighborhoods", "options"),
    Output("prime-target-neighborhoods", "value"),
    Output("prime-target-neighborhoods", "disabled"),
    Input("prime-target-cities", "value"),
    prevent_initial_call=False,
)
def update_prime_target_neighborhoods(cities):
    if not cities:
        return [], [], True
    all_hoods = [
        {"label": f"{hood} ({city})", "value": hood}
        for city in cities
        for hood in NEIGHBORHOODS_BY_CITY.get(city, [])
    ]
    return all_hoods, [], False


# ── Submit ────────────────────────────────────────────────────────────────────

@app.callback(
    Output("post-ad-alert", "children"),
    Input("post-ad-submit-btn", "n_clicks"),
    State("post-ad-title", "value"),
    State("post-ad-description", "value"),
    State("post-ad-city", "value"),
    State("post-ad-contact-name", "value"),
    State("selected-category-store", "data"),
    State("post-ad-plan", "value"),
    State("image-store", "data"),
    State("image-rights-consent", "value"),
    prevent_initial_call=True,
)
def submit_ad(n_clicks, title, description, city, contact_name, category, plan,
              images, rights_consent):
    if not n_clicks:
        raise PreventUpdate

    images = images or []
    limit  = IMAGE_LIMITS.get(plan or "free", 5)

    errors = []
    if not title or len(title.strip()) < 5:
        errors.append("Title must be at least 5 characters.")
    if not description or len(description.strip()) < 20:
        errors.append("Description must be at least 20 characters.")
    if not city:
        errors.append("Please select a city.")
    if not contact_name:
        errors.append("Contact name is required.")
    if not category:
        errors.append("Please select a category.")
    if len(images) > limit:
        errors.append(
            f"Too many photos ({len(images)} uploaded, {limit} allowed on {_PLAN_LABEL.get(plan or 'free', 'Free')} plan). "
            "Please remove some before publishing."
        )
    if images and "confirmed" not in (rights_consent or []):
        errors.append(
            "Please confirm you own or have the rights to use all uploaded images "
            "before publishing your ad."
        )
    # Content moderation – server-side gate (mirrors real-time client check)
    violations = check_content_violations(title, description)
    if violations:
        errors.append(f"Content policy violation: {violations[0]}")

    if errors:
        return dbc.Alert(
            [html.I(className="fas fa-exclamation-circle me-2")]
            + [html.Div(e) for e in errors],
            color="danger",
            className="alert-danger",
            dismissable=True,
        )

    # ── Success ────────────────────────────────────────────────────────
    if images:
        photo_note = (
            f"{len(images)} photo{'s' if len(images) > 1 else ''} attached"
        )
    else:
        photo_note = "no photos — consider adding images for 3× more engagement"

    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Ad published successfully! "),
            f"Your listing is now live ({photo_note}). ",
            dcc.Link("View all listings →", href="/browse", style={"color": "#2ea44f"}),
        ],
        color="success",
        className="alert-success",
        dismissable=True,
    )
