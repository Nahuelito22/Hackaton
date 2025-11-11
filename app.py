import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os

# Cargar variables de entorno (GOOGLE_API_KEY)
load_dotenv()

# Inicializar la app de Dash
# use_pages=True activa la carpeta /pages
# external_stylesheets nos da un look profesional (Bootstrap)
app = Dash(__name__, 
           use_pages=True, 
           external_stylesheets=[dbc.themes.BOOTSTRAP])

# --- El "Caparazón" de la App ---
app.layout = dbc.Container(
    [
        # --- 1. MENÚ DE NAVEGACIÓN ---
        # Un menú simple que se crea solo con las páginas
        dbc.NavbarSimple(
            children=[
                # Crear un link para cada página registrada en la carpeta /pages
                dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path']))
                for page in dash.page_registry.values()
            ],
            brand="Asistente Inclusivo 🚀",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4" # Margen inferior
        ),

        # --- 2. CONTENEDOR DE PÁGINA ---
        # Aquí es donde Dash cargará Perfil.py, Asistente_IA.py, etc.
        dash.page_container,

        # --- 3. ALMACÉN DE SESIÓN (SESSION STORAGE) ---
        # Este es el "cerebro" que guarda el perfil del usuario entre páginas
        # storage_type='session' = Se borra cuando el usuario cierra la pestaña
        dcc.Store(id='session-storage', storage_type='session'),

        # --- 4. FOOTER PERSONALIZADO ---
        html.Footer(
            html.Div(
                [
                    html.A("Términos y Condiciones", href="#"), 
                    " | ",
                    html.A("Política de Privacidad", href="#")
                ], 
                className="footer"
            )
        )
    ],
    fluid=True # Usar todo el ancho de la pantalla
)

if __name__ == '__main__':
    app.run(debug=True)