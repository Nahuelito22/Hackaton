import dash
from dash import dcc, html, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# La ruta (path) de ESTA página es "/login"
dash.register_page(__name__, path='/login', name='Login', order=2)

# --- Contenido de la Página de Login ---
layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Inicio de Sesión", className="card-title text-center mb-4"),
                    
                    dbc.Alert(
                        id="login-alert",
                        children="",
                        color="danger",
                        is_open=False,
                        duration=4000,
                    ),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Label("Usuario o Email", html_for="login-email", width=3),
                            dbc.Col(
                                dbc.Input(
                                    type="email",
                                    id="login-email",
                                    placeholder="Ingresa tu email",
                                ),
                                width=9,
                            ),
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Label("Contraseña", html_for="login-password", width=3),
                            dbc.Col(
                                dbc.Input(
                                    type="password",
                                    id="login-password",
                                    placeholder="Ingresa tu contraseña",
                                ),
                                width=9,
                            ),
                        ], className="mb-3"),
                        
                        dbc.Button(
                            "Ingresar",
                            id="login-button",
                            color="primary",
                            className="w-100",
                            n_clicks=0,
                        ),
                    ]),
                    
                    html.Div(
                        ["¿No tienes una cuenta? ", dcc.Link("Regístrate aquí", href="/registro")],
                        className="mt-4 text-center",
                    )
                ]),
                className="shadow-sm rounded-3",
            ),
            width=10,
            md=6,
            lg=5,
            xl=4,
        ),
        justify="center",
        align="center",
        className="vh-100", 
    )
], fluid=True, className="p-0 m-0")

@callback(
    Output("login-alert", "children"),
    Output("login-alert", "is_open"),
    Output("session-storage", "data", allow_duplicate=True),  
    Output("url", "pathname", allow_duplicate=True), 
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    State("session-storage", "data"), 
    prevent_initial_call=True 
)
def handle_login(n_clicks, email, password, session_data):
    if n_clicks == 0:
        raise PreventUpdate

    if not email or not password:
        return "Por favor, ingresa usuario y contraseña", True, dash.no_update, dash.no_update

    if session_data is None or 'user_database' not in session_data:
        return "No hay ningún usuario registrado. Por favor, regístrate primero.", True, dash.no_update, dash.no_update

    stored_user = session_data['user_database']
    
    if email == stored_user['email'] and password == stored_user['password']:
        # ¡Login exitoso!
        session_data['user_authenticated'] = True
        session_data['user_email'] = email
        
        # La ruta de destino (Perfil) es "/"
        ruta_correcta_perfil = "/" # <-- ¡Correcto!
        
        return "¡Inicio de sesión exitoso!", True, session_data, ruta_correcta_perfil

    else:
        # Credenciales incorrectas
        return "Usuario o contraseña incorrectos", True, dash.no_update, dash.no_update