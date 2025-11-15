import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Registrar esta página
dash.register_page(__name__, path='/registro', name='Registro', order=1)

# --- Contenido de la Página de Registro ---

layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Crear Cuenta", className="card-title text-center mb-4"),
                    
                    # Alerta para mostrar mensajes
                    dbc.Alert(
                        id="register-alert",
                        children="",
                        color="danger", # Cambiará a 'success' si el registro es exitoso
                        is_open=False,
                        duration=4000,
                    ),
                    
                    # Formulario de Registro
                    dbc.Form([
                        # Campo de Email
                        dbc.Row([
                            dbc.Label("Email", html_for="register-email", width=3),
                            dbc.Col(
                                dbc.Input(
                                    type="email",
                                    id="register-email",
                                    placeholder="Ingresa tu email",
                                ),
                                width=9,
                            ),
                        ], className="mb-3"),
                        
                        # Campo de Contraseña
                        dbc.Row([
                            dbc.Label("Contraseña", html_for="register-password", width=3),
                            dbc.Col(
                                dbc.Input(
                                    type="password",
                                    id="register-password",
                                    placeholder="Crea una contraseña",
                                ),
                                width=9,
                            ),
                        ], className="mb-3"),

                        # Campo de Confirmar Contraseña
                        dbc.Row([
                            dbc.Label("Confirmar", html_for="register-confirm", width=3),
                            dbc.Col(
                                dbc.Input(
                                    type="password",
                                    id="register-confirm",
                                    placeholder="Confirma tu contraseña",
                                ),
                                width=9,
                            ),
                        ], className="mb-3"),
                        
                        # Botón de Registrarse
                        dbc.Button(
                            "Registrarse",
                            id="register-button",
                            color="primary",
                            className="w-100",
                            n_clicks=0,
                        ),
                    ]),
                    
                    # Link a la página de login
                    html.Div(
                        ["¿Ya tienes una cuenta? ", dcc.Link("Inicia sesión", href="/login")],
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


# --- Lógica del Callback de Registro (¡ACTUALIZADO!) ---
# Este callback guarda el nuevo usuario en la sesión

@callback(
    Output("register-alert", "children"),
    Output("register-alert", "is_open"),
    Output("register-alert", "color"),
    Output("url", "pathname", allow_duplicate=True), 
    Output("session-storage", "data", allow_duplicate=True), # Escribe en la sesión
    Input("register-button", "n_clicks"),
    State("register-email", "value"),
    State("register-password", "value"),
    State("register-confirm", "value"),
    State("session-storage", "data"), # Lee la sesión actual
    prevent_initial_call=True
)
def handle_registration(n_clicks, email, password, confirm_password, session_data):
    if n_clicks == 0:
        raise PreventUpdate

    if not email or not password or not confirm_password:
        return "Todos los campos son obligatorios", True, "danger", dash.no_update, dash.no_update

    if password != confirm_password:
        return "Las contraseñas no coinciden", True, "danger", dash.no_update, dash.no_update

    # --- LÓGICA DE REGISTRO (Guardar en la sesión) ---
    
    # Inicializamos la sesión si no existe
    if session_data is None:
        session_data = {}
        
    # Guardamos el nuevo usuario en nuestra "base de datos" de sesión
    # (Esto soluciona el error de "duplicado" que tenías)
    session_data['user_database'] = {
        'email': email,
        'password': password
    }

    # Redirigimos al login y guardamos los datos en la sesión
    return "¡Cuenta creada con éxito! Serás redirigido al login.", True, "success", "/login", session_data