"""Global community-flagging modal – rendered once in the root layout."""
import dash_bootstrap_components as dbc
from dash import html, dcc

FLAG_REASONS = [
    {"label": "Spam or misleading",              "value": "spam"},
    {"label": "Scam / fraud attempt",            "value": "scam"},
    {"label": "Inappropriate or offensive content", "value": "inappropriate"},
    {"label": "Wrong category",                  "value": "wrong_category"},
    {"label": "Already sold / expired",          "value": "already_sold"},
    {"label": "Counterfeit or prohibited item",  "value": "prohibited"},
    {"label": "Suspected stolen goods",          "value": "stolen"},
    {"label": "Other",                           "value": "other"},
]


def flag_modal_layout() -> html.Div:
    """
    Return the flag modal together with its supporting Stores.

    Place this once in the root app layout so it is always present in the DOM
    and reachable from any page that renders flag buttons.
    """
    return html.Div([
        # Stores that survive page navigation (kept in root layout)
        dcc.Store(id="flag-store", data={}),
        dcc.Store(id="flag-listing-id-store", data=None),

        dbc.Modal(
            id="flag-modal",
            is_open=False,
            size="md",
            centered=True,
            children=[
                dbc.ModalHeader(
                    dbc.ModalTitle([
                        html.I(className="fas fa-flag me-2", style={"color": "#ef4444"}),
                        "Report Listing",
                    ]),
                    close_button=True,
                ),
                dbc.ModalBody([
                    html.P(
                        "Help keep LosClassificados safe. Our moderation team reviews "
                        "every report within 24 hours.",
                        style={
                            "fontSize": "0.875rem",
                            "color": "var(--text-secondary)",
                            "marginBottom": "1.25rem",
                        },
                    ),

                    html.Label("Reason for report *", className="form-label"),
                    dcc.Dropdown(
                        id="flag-reason-select",
                        options=FLAG_REASONS,
                        placeholder="Select a reason…",
                        className="mb-3 bg-input",
                        clearable=False,
                    ),

                    html.Label("Additional details (optional)", className="form-label"),
                    dcc.Textarea(
                        id="flag-details-input",
                        placeholder=(
                            "Describe the issue in more detail — e.g. received a scam "
                            "message, item appears counterfeit, price is bait-and-switch…"
                        ),
                        className="form-control mb-3",
                        style={"minHeight": "90px", "fontSize": "0.875rem"},
                        maxLength=500,
                    ),

                    # Inline feedback (validation errors or thank-you message)
                    html.Div(id="flag-confirmation-area"),
                ]),

                dbc.ModalFooter([
                    dbc.Button(
                        "Cancel",
                        id="flag-cancel-btn",
                        color="secondary",
                        outline=True,
                        className="me-2",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-flag me-2"), "Submit Report"],
                        id="flag-submit-btn",
                        color="danger",
                        n_clicks=0,
                    ),
                ]),
            ],
        ),
    ])
