"""Leads dashboard callbacks – filtering, sorting, and status updates."""
import dash
from dash import Input, Output, State, ALL, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from los_classificados.server import app
from los_classificados.utils.mock_data import MOCK_LEADS, LEAD_STATUS_LABELS
from los_classificados.layouts.leads import _lead_row


@app.callback(
    Output("leads-list-container", "children"),
    Output("leads-count", "children"),
    Input("leads-status-filter", "value"),
    Input("leads-method-filter", "value"),
    Input("leads-sort", "value"),
    prevent_initial_call=False,
)
def filter_leads(status_filter, method_filter, sort_by):
    leads = list(MOCK_LEADS)

    if status_filter and status_filter != "all":
        leads = [l for l in leads if l["status"] == status_filter]

    if method_filter and method_filter != "all":
        leads = [l for l in leads if l["contact_method"] == method_filter]

    if sort_by == "oldest":
        leads = sorted(leads, key=lambda l: l["created_at"])
    elif sort_by == "status":
        order = list(LEAD_STATUS_LABELS.keys())
        leads = sorted(leads, key=lambda l: order.index(l["status"]) if l["status"] in order else 99)
    else:  # newest
        leads = sorted(leads, key=lambda l: l["created_at"], reverse=True)

    count = f"{len(leads)} lead{'s' if len(leads) != 1 else ''}"

    if not leads:
        return (
            html.Div(
                className="text-center py-4",
                children=[
                    html.I(className="fas fa-inbox fa-2x mb-2", style={"color": "var(--text-muted)"}),
                    html.P("No leads match your filters.",
                           style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                ],
            ),
            count,
        )

    return [_lead_row(l) for l in leads], count


@app.callback(
    Output("leads-alert", "children"),
    Input({"type": "lead-status-select", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def lead_status_changed(values):
    if not dash.ctx.triggered:
        raise PreventUpdate
    new_status = dash.ctx.triggered[0]["value"]
    if new_status is None:
        raise PreventUpdate
    st = LEAD_STATUS_LABELS.get(new_status, {"label": new_status, "color": "#6e7681"})
    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            f"Lead status updated to ",
            html.Strong(st["label"]),
            ".",
        ],
        color="success",
        className="alert-success",
        duration=3000,
        dismissable=True,
        style={"fontSize": "0.875rem"},
    )
