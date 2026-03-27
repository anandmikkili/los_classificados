"""
Safety feature callbacks
========================

Covers four areas:

1. Community flagging – open/close the flag modal and persist submitted reports
   in the global ``flag-store``.
2. Email mask preview – show the masked address live as the user types.
3. Image-rights enforcement – disable the publish button until the poster
   confirms image ownership.
4. Real-time content moderation – scan title + description and show an inline
   alert for any prohibited-term hits.
"""
from __future__ import annotations

import dash
from dash import Input, Output, State, ALL, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.safety import (
    mask_email,
    check_content_violations,
    CONTENT_GUIDELINES,
)


# ── 1. Community flagging ─────────────────────────────────────────────────────

@app.callback(
    Output("flag-modal", "is_open"),
    Output("flag-listing-id-store", "data"),
    Output("flag-reason-select", "value"),
    Output("flag-details-input", "value"),
    Output("flag-confirmation-area", "children"),
    Input({"type": "flag-btn", "index": ALL}, "n_clicks"),
    Input("flag-cancel-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_or_close_flag_modal(flag_clicks, _cancel):
    """Open the modal for the clicked listing, or close it on Cancel."""
    triggered = dash.ctx.triggered_id

    if triggered == "flag-cancel-btn":
        return False, None, None, "", []

    if not any(n for n in flag_clicks if n):
        raise PreventUpdate

    listing_id = triggered["index"]
    return True, listing_id, None, "", []


@app.callback(
    Output("flag-modal", "is_open", allow_duplicate=True),
    Output("flag-confirmation-area", "children", allow_duplicate=True),
    Output("flag-store", "data"),
    Input("flag-submit-btn", "n_clicks"),
    State("flag-reason-select", "value"),
    State("flag-details-input", "value"),
    State("flag-listing-id-store", "data"),
    State("flag-store", "data"),
    prevent_initial_call=True,
)
def submit_flag(n_clicks, reason, details, listing_id, store):
    """Persist the flag and close the modal, or show a validation error."""
    if not n_clicks:
        raise PreventUpdate

    if not reason:
        return (
            dash.no_update,
            dbc.Alert(
                [html.I(className="fas fa-exclamation-circle me-2"),
                 "Please select a reason before submitting."],
                color="warning",
                className="mb-0",
                style={"fontSize": "0.82rem"},
            ),
            dash.no_update,
        )

    store = dict(store or {})
    key = str(listing_id)
    flags = store.get(key, [])
    flags.append({"reason": reason, "details": details or ""})
    store[key] = flags

    return False, [], store


# ── 2. Email mask preview ─────────────────────────────────────────────────────

@app.callback(
    Output("post-ad-email-masked-preview", "children"),
    Output("post-ad-email-masked-preview", "style"),
    Input("post-ad-email", "value"),
    Input("post-ad-email-mask", "value"),
    prevent_initial_call=False,
)
def update_email_mask_preview(email, mask_opts):
    """Show the masked address live while the user types their email."""
    if not mask_opts or "mask" not in mask_opts:
        return [], {"display": "none"}

    masked = mask_email(email or "")
    return [
        html.I(className="fas fa-eye-slash me-1", style={"color": "var(--accent-teal)"}),
        html.Span("Public display: ", style={"fontWeight": "600"}),
        html.Code(
            masked,
            style={
                "color": "var(--accent-teal)",
                "background": "var(--bg-secondary)",
                "padding": "0.1rem 0.4rem",
                "borderRadius": "4px",
            },
        ),
        html.Span(
            " — your real address is never shown to visitors.",
            style={"color": "var(--text-muted)", "fontSize": "0.78rem"},
        ),
    ], {"fontSize": "0.82rem", "marginTop": "0.4rem"}


# ── 3. Image-rights enforcement ───────────────────────────────────────────────

@app.callback(
    Output("post-ad-submit-btn", "disabled"),
    Output("image-consent-warning", "children"),
    Input("image-store", "data"),
    Input("image-rights-consent", "value"),
    prevent_initial_call=False,
)
def enforce_image_consent(store, consent):
    """Disable publish until the poster confirms ownership of uploaded images."""
    has_images = bool(store)
    consented = "confirmed" in (consent or [])

    if has_images and not consented:
        return True, html.Div(
            [
                html.I(className="fas fa-exclamation-triangle me-1"),
                "Please confirm you own or have rights to all uploaded images to enable publishing.",
            ],
            style={"fontSize": "0.78rem", "color": "#f59e0b", "marginTop": "0.3rem"},
        )

    return False, []


# ── 4. Real-time content moderation ──────────────────────────────────────────

@app.callback(
    Output("content-moderation-alert", "children"),
    Input("post-ad-title", "value"),
    Input("post-ad-description", "value"),
    prevent_initial_call=False,
)
def check_content(title, description):
    """Scan title + description and show an inline alert for any policy violations."""
    violations = check_content_violations(title, description)
    if not violations:
        return []

    return dbc.Alert(
        [
            html.Div(
                [html.I(className="fas fa-shield-alt me-2"),
                 html.Strong("Content policy violation detected")],
                className="mb-2",
            ),
        ] + [
            html.Div(
                [html.I(className="fas fa-times-circle me-1"), v],
                style={"fontSize": "0.82rem", "marginTop": "0.2rem"},
            )
            for v in violations
        ],
        color="danger",
        className="alert-danger mb-0",
        style={"fontSize": "0.82rem"},
    )


# ── 5. Content-guidelines panel toggle ───────────────────────────────────────

@app.callback(
    Output("content-guidelines-collapse", "is_open"),
    Output("guidelines-chevron", "className"),
    Input("content-guidelines-toggle", "n_clicks"),
    State("content-guidelines-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_guidelines(n_clicks, is_open):
    """Expand / collapse the content-guidelines reference card."""
    if not n_clicks:
        raise PreventUpdate
    new_open = not is_open
    chevron_cls = "fas fa-chevron-up" if new_open else "fas fa-chevron-down"
    return new_open, chevron_cls
