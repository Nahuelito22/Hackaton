import dash
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar la app
app = Dash(__name__, 
        use_pages=True, 
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True)

# Exponer el servidor Flask
server = app.server

# --- El "Caparazón" de la App ---
app.layout = dbc.Container(
    [
        # --- 0. CONTROLADOR DE URL ---
        # Componente esencial para que funcionen las redirecciones
        dcc.Location(id="url"),

        # --- 1. MENÚ DE NAVEGACIÓN ---
        dbc.NavbarSimple(
            children=[
                # Excluimos las páginas legales, login y registro
                dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path']))
                for page in dash.page_registry.values() if page['path'] not in [
                    '/terminos-y-condiciones', 
                    '/politica-de-privacidad',
                    '/login',
                    '/registro'
                ]
            ],
            brand=html.Img(src='/assets/Guidia_Texto.png', height='30px'),
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4"
        ),

        # --- 2. CONTENEDOR DE PÁGINA ---
        dash.page_container,

        # --- 3. ALMACÉN DE SESIÓN (SESSION STORAGE) ---
        dcc.Store(id='session-storage', storage_type='session'),

        # --- 4. FOOTER PERSONALIZADO ---
        html.Footer(
            html.Div(
                [
                    html.Span("© 2025 Guidia. Todos los derechos reservados."),
                    html.Span(" | ", className="mx-3"),
                    html.A("Términos y Condiciones", href="/terminos-y-condiciones"),
                    html.Span(" | ", className="mx-1"),
                    html.A("Política de Privacidad", href="/politica-de-privacidad")
                ],
                className="footer"
            )
        )
    ],
    fluid=True
)


# --- 5. LÓGICA DE PROTECCIÓN DE PÁGINAS (¡NUEVA!) ---
# Este callback protege las páginas que no son de autenticación

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    State("session-storage", "data"),
    prevent_initial_call=True
)
def auth_guard(pathname, session_data):
    # Comprueba si el usuario está autenticado
    is_authenticated = session_data and session_data.get('user_authenticated', False)
    
    # Páginas públicas
    public_pages = ['/login', '/registro']

    if pathname not in public_pages and not is_authenticated:
        # Si el usuario intenta acceder a una página protegida (ej. '/')
        # sin estar autenticado, lo mandamos a /login
        return "/login"
        
    elif pathname in public_pages and is_authenticated:
        # Si el usuario ya está autenticado e intenta ir a /login
        # o /registro, lo mandamos a su perfil (la raíz '/')
        return "/"

    # Si no, no hacemos nada
    return dash.no_update


if __name__ == '_main_':
    app.run(debug=True)