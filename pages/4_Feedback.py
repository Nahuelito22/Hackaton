import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Registramos la página con order=3 para que aparezca en tercera posición
dash.register_page(__name__, path='/feedback', name='Feedback', order=3)

layout = dbc.Container([
    html.H1("Envíanos tu Feedback", className="my-4 text-center"),
    html.P(
        "Tu opinión es muy importante para nosotros. Ayúdanos a mejorar Guidia.",
        className="lead text-center mb-5"
    ),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Label("Tu mensaje:"), width=12),
                        dbc.Col(
                            dcc.Textarea(
                                id="feedback-textarea",
                                placeholder="Escribe tus comentarios, sugerencias o reporta un error aquí...",
                                style={'width': '100%', 'height': 150}
                            ),
                            width=12
                        ),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col(html.Label("¿Qué tan útil te parece la aplicación?"), width=12),
                        dbc.Col(
                            dcc.Slider(
                                id='feedback-rating',
                                min=1,
                                max=5,
                                step=1,
                                marks={i: str(i) for i in range(1, 6)},
                                value=4
                            ),
                            width=12
                        )
                    ], className="mb-4"),
                    dbc.Button("Enviar Feedback", id="submit-feedback-btn", color="primary", n_clicks=0, className="w-100"),
                    html.Div(id="feedback-output", className="mt-3 text-center")
                ])
            ]),
            md=8, lg=6
        )
    ], justify="center")
], fluid=True, className="p-5")

@dash.callback(
    Output("feedback-output", "children"),
    Input("submit-feedback-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_feedback_submission(n_clicks):
    if n_clicks > 0:
        return dbc.Alert("¡Gracias por tu feedback! Lo tendremos en cuenta.", color="success", duration=4000)
    return ""
