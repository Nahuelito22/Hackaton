import dash
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
import json # Usaremos json para guardar los datos

# Registrar esta página
dash.register_page(__name__, path='/', name='Perfil', order=1)

# --- Layout de la Página de Perfil (V2 - Dinámico) ---
layout = dbc.Container([
    html.H2("Perfil del Docente"),
    html.P("Completa tu perfil para personalizar la experiencia. Este perfil se guarda en tu navegador."),
    
    dbc.Row([
        dbc.Col(dbc.Label("Nombre:"), width=2),
        dbc.Col(dbc.Input(type="text", id="perfil-nombre", placeholder="Ej. Nahuel"), width=10)
    ], className="mb-3"),
    
    dbc.Row([
        dbc.Col(dbc.Label("Apellido:"), width=2),
        dbc.Col(dbc.Input(type="text", id="perfil-apellido", placeholder="Ej. Ghilardi"), width=10)
    ], className="mb-3"),
    
    dbc.Row([
        dbc.Col(dbc.Label("Correo (Opcional):"), width=2),
        dbc.Col(dbc.Input(type="email", id="perfil-correo", placeholder="Para notificaciones..."), width=10)
    ], className="mb-3"),
    
    html.Hr(),
    
    html.H4("Tus Instituciones"),
    dbc.Row([
        dbc.Col(dbc.Label("¿En cuántas instituciones trabajas?"), width=4),
        dbc.Col(dbc.Input(type="number", id="cuantas-escuelas", min=1, step=1, value=1), width=2)
    ], className="mb-3"),

    # Aquí es donde Dash creará los campos dinámicamente
    html.Div(id="escuelas-container"),
    
    dbc.Button("Guardar Perfil", id="guardar-perfil-btn", color="primary", className="mt-3", n_clicks=0),
    
    dbc.Alert(id="guardar-output", is_open=False, duration=4000) # Mensaje de éxito/error

], className="mb-4")


# --- Callback 1: Generar campos de escuela dinámicamente ---
# Este callback se dispara CADA VEZ que el número de escuelas cambia
@callback(
    Output('escuelas-container', 'children'),
    Input('cuantas-escuelas', 'value')
)
def generar_campos_escuela(n_escuelas):
    if n_escuelas is None or n_escuelas < 1:
        return []

    # Creamos una "tarjeta" de inputs para cada escuela
    cards = []
    for i in range(n_escuelas):
        card = dbc.Card([
            dbc.CardHeader(f"Institución #{i + 1}"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(dbc.Label("Nombre de la Institución:"), width=4),
                    dbc.Col(dbc.Input(type="text", 
                                     placeholder=f"Ej. Escuela 4-123",
                                     # ¡LA CLAVE! ID de tipo "diccionario"
                                     id={'type': 'escuela-nombre', 'index': i}), 
                            width=8)
                ], className="mb-2"),
                
                dbc.Row([
                    dbc.Col(dbc.Label("Nivel/es en esta institución:"), width=4),
                    dbc.Col(dbc.Checklist(
                        options=[
                            {'label': 'Nivel Inicial', 'value': 'Inicial'},
                            {'label': 'Nivel Primario', 'value': 'Primario'},
                            {'label': 'Nivel Secundario', 'value': 'Secundario'},
                        ],
                        id={'type': 'escuela-niveles', 'index': i},
                        inline=True
                    ), width=8)
                ], className="mb-2"),

                dbc.Row([
                    dbc.Col(dbc.Label("Contexto:"), width=4),
                    dbc.Col(dbc.RadioItems(
                        options=[
                            {'label': 'Urbana', 'value': 'Urbana'},
                            {'label': 'Rural', 'value': 'Rural'},
                            {'label': 'Urbano-Marginal', 'value': 'Urbano-Marginal'},
                        ],
                        id={'type': 'escuela-contexto', 'index': i},
                        inline=True,
                        value='Urbana' # Valor por defecto
                    ), width=8)
                ])
            ])
        ], className="mb-3")
        cards.append(card)
    
    return cards


# --- Callback 2: Guardar el perfil completo en la sesión ---
# Este callback usa "ALL" (Pattern-Matching) para encontrar todos
# los campos dinámicos que acabamos de crear.
@callback(
    Output('guardar-output', 'children'),
    Output('guardar-output', 'is_open'),
    Output('guardar-output', 'color'),
    Output('session-storage', 'data'), # Guardamos en el almacén de sesión
    Input('guardar-perfil-btn', 'n_clicks'),
    State('perfil-nombre', 'value'),
    State('perfil-apellido', 'value'),
    State('perfil-correo', 'value'),
    State({'type': 'escuela-nombre', 'index': ALL}, 'value'),  # Lee TODOS los nombres
    State({'type': 'escuela-niveles', 'index': ALL}, 'value'), # Lee TODOS los niveles
    State({'type': 'escuela-contexto', 'index': ALL}, 'value'),# Lee TODOS los contextos
    prevent_initial_call=True
)
def guardar_perfil_completo(n_clicks, nombre, apellido, correo, nombres_esc, niveles_esc, contextos_esc):
    if not nombre or not apellido:
        return "Error: Nombre y Apellido son requeridos.", True, "danger", dash.no_update

    # Construimos el objeto de perfil
    perfil_data = {
        'nombre_docente': nombre,
        'apellido_docente': apellido,
        'correo_docente': correo,
        'instituciones': []
    }

    # Procesamos las escuelas
    for i in range(len(nombres_esc)):
        if not nombres_esc[i]:
            return f"Error: Por favor, completa el nombre de la Institución #{i + 1}.", True, "danger", dash.no_update
        
        escuela = {
            'id': i,
            'nombre': nombres_esc[i],
            'niveles': niveles_esc[i] if niveles_esc[i] else [], # Manejar si no selecciona ninguno
            'contexto': contextos_esc[i]
        }
        perfil_data['instituciones'].append(escuela)

    # Devolvemos el mensaje de éxito y los nuevos datos
    # Usamos json.dumps para guardar el diccionario como un string en dcc.Store
    return f"¡Perfil de {nombre} guardado con {len(perfil_data['instituciones'])} escuela(s)!", True, "success", json.dumps(perfil_data)