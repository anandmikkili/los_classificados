"""Post Ad form callbacks – category selection, image preview, submit."""
import base64

import dash
from dash import Input, Output, State, ALL, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import CATEGORIES, NEIGHBORHOODS_BY_CITY

# Subcategories mapped by category id
SUBCATEGORIES = {
    "real_estate": ["House for Sale", "Apartment for Sale", "Land/Lot", "Commercial Property", "Other"],
    "rentals":     ["Apartment Rental", "House Rental", "Room for Rent", "Commercial Rental", "Vacation Rental"],
    "services":    ["Electrician", "Plumber", "Cleaning", "Landscaping", "Moving", "Handyman", "Tutoring", "Other"],
    "vehicles":    ["Sedan", "SUV/Truck", "Motorcycle", "Boat", "Parts & Accessories", "Other"],
    "electronics": ["Phones", "Laptops", "TVs", "Gaming", "Audio", "Cameras", "Other"],
    "furniture":   ["Sofas & Sectionals", "Beds & Bedframes", "Dining Sets", "Office Furniture", "Other"],
    "jobs":        ["Technology", "Healthcare", "Construction", "Retail", "Finance", "Education", "Other"],
    "other":       ["Collectibles", "Sports & Outdoors", "Baby & Kids", "Clothing", "Books", "Other"],
}


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
    styles = []
    for cat in CATEGORIES:
        if cat["id"] == selected:
            styles.append({
                "border": f"2px solid {cat['color']}",
                "background": f"{cat['color']}1a",
            })
        else:
            styles.append({})
    return styles


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


@app.callback(
    Output("desc-char-count", "children"),
    Input("post-ad-description", "value"),
    prevent_initial_call=False,
)
def update_char_count(text):
    count = len(text or "")
    color = "#ef4444" if count > 2800 else "var(--text-muted)"
    return html.Span(f"{count}/3000 characters", style={"color": color})


@app.callback(
    Output("uploaded-images-preview", "children"),
    Input("post-ad-images", "contents"),
    State("post-ad-images", "filenames"),
    prevent_initial_call=True,
)
def preview_uploaded_images(contents, filenames):
    if not contents:
        return []
    previews = []
    for content, name in zip(contents[:10], filenames[:10]):
        previews.append(
            html.Div(
                style={"position": "relative", "width": "80px"},
                children=[
                    html.Img(
                        src=content,
                        style={
                            "width": "80px", "height": "80px",
                            "objectFit": "cover", "borderRadius": "8px",
                            "border": "1.5px solid var(--border-color)",
                        },
                        title=name,
                    ),
                ],
            )
        )
    return previews


@app.callback(
    Output("post-ad-alert", "children"),
    Input("post-ad-submit-btn", "n_clicks"),
    State("post-ad-title", "value"),
    State("post-ad-description", "value"),
    State("post-ad-city", "value"),
    State("post-ad-contact-name", "value"),
    State("selected-category-store", "data"),
    State("post-ad-plan", "value"),
    prevent_initial_call=True,
)
def submit_ad(n_clicks, title, description, city, contact_name, category, plan):
    if not n_clicks:
        raise PreventUpdate

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

    if errors:
        return dbc.Alert(
            [html.I(className="fas fa-exclamation-circle me-2")] +
            [html.Div(e) for e in errors],
            color="danger",
            className="alert-danger",
            dismissable=True,
        )

    # Success (demo mode – no real DB write)
    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Ad published successfully! "),
            "Your listing is now live. ",
            dcc.Link("View all listings →", href="/browse", style={"color": "#2ea44f"}),
        ],
        color="success",
        className="alert-success",
        dismissable=True,
    )
