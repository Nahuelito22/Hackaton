import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import google.generativeai as genai
import os
import json

# Registrar esta página
dash.register_page(__name__, name='Asistente IA')

# --- Configurar la API de Gemini ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
    API_CONFIGURADA = True
except Exception as e:
    API_CONFIGURADA = False

# --- 1. Layout de la Página ---
layout = dbc.Container([
    html.H2("🤖 Asistente de Planificación Inclusiva"),
    
    # Este Div mostrará un saludo o una advertencia
    html.Div(id="ia-welcome-message"),
    
    dbc.Row([
        # --- Columna Izquierda (Contexto y Acción) ---
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Paso 1: ¿Qué quieres hacer hoy?"),
                dbc.CardBody([
                    # --- NUEVO: EL SELECTOR DE ACCIÓN PRINCIPAL ---
                    dcc.RadioItems(
                        id='selector-accion-principal',
                        options=[
                            {'label': ' Crear una nueva Planificación (Anual/Mensual)', 'value': 'crear'},
                            {'label': ' Analizar un Plan existente / Generar Rúbricas', 'value': 'analizar'},
                            {'label': ' Adaptar una Actividad Diaria (Inclusión Rápida)', 'value': 'adaptar'},
                        ],
                        value='crear', # Valor por defecto
                        labelStyle={'display': 'block', 'margin-bottom': '10px'}
                    )
                ])
            ]),
            html.Br(),
            
            # --- Contenedor de Contexto (Se muestra siempre) ---
            dbc.Card([
                dbc.CardHeader("Paso 2: Define tu Contexto"),
                dbc.CardBody([
                    dbc.Label("¿Para qué institución estás planificando?"),
                    dcc.Dropdown(id="ia-select-escuela", placeholder="Cargando escuelas..."),
                    
                    dbc.Label("¿Para qué nivel?", className="mt-2"),
                    dcc.Dropdown(id="ia-select-nivel", placeholder="Selecciona una escuela primero..."),
                    
                    dbc.Label("Contexto de la Escuela:", className="mt-2"),
                    dbc.Input(id="ia-contexto-escuela", disabled=True) # Se rellena solo
                ])
            ]),

        ], width=4), # Fin Columna Izquierda
        
        # --- Columna Derecha (Formularios Dinámicos) ---
        dbc.Col([
            
            # --- Formulario para "CREAR PLANIFICACIÓN" ---
            dbc.Card(id="card-crear-plan", children=[
                dbc.CardHeader("Paso 3: Detalles para CREAR Planificación"),
                dbc.CardBody([
                    dbc.Label("Tipo de Plan a Crear:"),
                    dcc.RadioItems(id="ia-select-tipo-plan-crear", value='Anual'),
                    
                    html.Hr(),
                    dbc.Label("Detalles Específicos (según Nivel):"),
                    html.Div(id="ia-contexto-nivel-crear"), # Se rellena dinámicamente
                    
                    dbc.Label("Cantidad de Evaluaciones (TPs, Pruebas):", className="mt-2"),
                    dbc.Input(id="ia-cant-eval-crear", type="number", value=2, min=0, step=1),
                    
                    dbc.Label("Cantidad de Días de Clase (aprox):", className="mt-2"),
                    dbc.Input(id="ia-dias-clase-crear", type="number", value=20, min=1, step=1),

                    dbc.Label("Input Base (Pega los temas, parrilla anterior, libro matriz, etc.):"),
                    dbc.Textarea(id="ia-plan-base-crear", rows=10),
                    
                    dbc.Label("Desafíos de Inclusión (para adaptar rúbricas):", className="mt-2"),
                    dbc.Checklist(id="ia-inclusion-crear", options=[
                        {'label': 'TDAH', 'value': 'TDAH'}, {'label': 'Dislexia', 'value': 'Dislexia'}
                    ], inline=True),
                ])
            ], style={'display': 'block'}), # Visible por defecto

            # --- Formulario para "ANALIZAR DOCUMENTO" ---
            dbc.Card(id="card-analizar-doc", children=[
                dbc.CardHeader("Paso 3: Detalles para ANALIZAR Planificación"),
                dbc.CardBody([
                    dbc.Label("¿Qué quieres que haga la IA con este documento?"),
                    dbc.Checklist(
                        id="ia-accion-analizar",
                        options=[
                            {'label': 'Generar Rúbricas de Evaluación', 'value': 'rubricas'},
                            {'label': 'Resumir para Suplente (detectar temas clave)', 'value': 'resumen'},
                            {'label': 'Sugerir Adaptaciones de Inclusión', 'value': 'adaptar-doc'},
                        ],
                        value=['rubricas'] # Valor por defecto
                    ),
                    html.Hr(),
                    # --- AQUÍ ESTÁ EL COMPROMISO (TEXTAREA, NO PDF) ---
                    dbc.Label("Pega aquí la Planificación (Anual, Mensual, etc.) a ANALIZAR:"),
                    dbc.Textarea(id="ia-plan-base-analizar", rows=20,
                                 placeholder="Pega aquí el documento completo (PDF, Word, etc.)..."),
                ])
            ], style={'display': 'none'}), # Oculto por defecto

            # --- Formulario para "ADAPTACIÓN RÁPIDA" ---
            dbc.Card(id="card-adaptar-diaria", children=[
                dbc.CardHeader("Paso 3: Adaptación Rápida de Clase Diaria"),
                dbc.CardBody([
                    dbc.Label("Pega aquí tu borrador de actividad de clase:"),
                    dbc.Textarea(id="ia-plan-base-adaptar", rows=10),
                    
                    dbc.Label("Desafíos de Inclusión a adaptar:", className="mt-2"),
                    dbc.Checklist(id="ia-inclusion-adaptar", options=[
                        {'label': 'TDAH', 'value': 'TDAH'}, {'label': 'Dislexia', 'value': 'Dislexia'}
                    ], inline=True, value=['TDAH']),
                ])
            ], style={'display': 'none'}), # Oculto por defecto
            
            # --- Botón de Generar (Unificado) ---
            dbc.Button("Generar Respuesta IA", 
                     id="ia-generar-btn-unificado", 
                     color="primary", 
                     className="mt-3 w-100", 
                     n_clicks=0),
            
            # --- Output (Unificado) ---
            html.Hr(),
            dbc.Label("Resultados Generados por la IA:"),
            dcc.Loading(
                dcc.Markdown(id="ia-output-div-unificado", style={'border': '1px solid #ddd', 'padding': '10px', 'min-height': '200px'})
            )
            
        ], width=8) # Fin Columna Derecha
    ]) # Fin Fila
])

# --- 2. Callbacks (La "Magia" de Dash) ---

# --- Callback 1: Cargar Perfil y poblar Dropdowns iniciales ---
@callback(
    Output('ia-welcome-message', 'children'),
    Output('ia-select-escuela', 'options'),
    Input('session-storage', 'data')
)
def cargar_perfil_y_escuelas(data_json):
    if not data_json:
        return dbc.Alert("Perfil no encontrado. Por favor, ve a 'Perfil' y guarda tus datos.", color="danger"), []
    try:
        data = json.loads(data_json)
        perfil = data.get('perfil', data)
        nombre_docente = perfil.get('nombre_docente', 'Docente')
        instituciones = perfil.get('instituciones', [])
        if not instituciones:
            return dbc.Alert("Tu perfil no tiene instituciones. Por favor, añade al menos una.", color="warning"), []
        opciones_escuela = [{'label': esc['nombre'], 'value': json.dumps(esc)} for esc in instituciones] # Guardar el objeto entero
        mensaje_bienvenida = dbc.Alert(f"¡Hola {nombre_docente}! Selecciona tu contexto para comenzar.", color="success")
        return mensaje_bienvenida, opciones_escuela
    except Exception as e:
        return dbc.Alert(f"Error al cargar tu perfil: {e}", color="danger"), []

# --- Callback 2: Actualizar Nivel y Contexto (cuando se elige escuela) ---
@callback(
    Output('ia-select-nivel', 'options'),
    Output('ia-select-nivel', 'value'),
    Output('ia-contexto-escuela', 'value'),
    Input('ia-select-escuela', 'value') # Se dispara cuando cambia la escuela
)
def actualizar_niveles_y_contexto(escuela_json):
    if not escuela_json:
        return [], None, ""
    
    escuela = json.loads(escuela_json) # Convertir el string JSON de vuelta a objeto
    niveles_de_la_escuela = escuela.get('niveles', [])
    contexto_de_la_escuela = escuela.get('contexto', 'Urbana')
    
    opciones_nivel = [{'label': nivel, 'value': nivel} for nivel in niveles_de_la_escuela]
    valor_nivel = opciones_nivel[0]['value'] if opciones_nivel else None
    
    return opciones_nivel, valor_nivel, contexto_de_la_escuela

# --- Callback 3: Actualizar Opciones (Primaria vs Secundaria) ---
# Se dispara cuando cambia el Nivel
@callback(
    Output('ia-contexto-nivel-crear', 'children'),
    Output('ia-select-tipo-plan-crear', 'options'),
    Input('ia-select-nivel', 'value')
)
def mostrar_contexto_especifico_crear(nivel_seleccionado):
    opciones_plan_crear = []
    inputs_especificos = []
    
    if nivel_seleccionado == 'Primario':
        opciones_plan_crear = [
            {'label': 'Plan Anual (Parrilla)', 'value': 'Anual-Primaria'},
            {'label': 'Plan Mensual (Actividades y Rúbricas)', 'value': 'Mensual-Primaria'},
        ]
        inputs_especificos = [
            dbc.Label("Eventos Especiales / Días Patrios (Opcional):"),
            dbc.Textarea(id="ia-dias-patios", placeholder="Ej: 25 de Mayo, Día de la Bandera...", rows=2),
        ]
    elif nivel_seleccionado == 'Secundario':
        opciones_plan_crear = [
            {'label': 'Plan Anual (desde Libro Matriz)', 'value': 'Anual-Secundaria'},
            {'label': 'Plan Mensual (desde Anual)', 'value': 'Mensual-Secundaria'},
        ]
        inputs_especificos = [
            dbc.Label("Libro Matriz / Temario General (Opcional):"),
            dbc.Textarea(id="ia-libro-matriz", placeholder="Ej: 'Capítulos 1-4 del libro Santillana...'", rows=2),
        ]
    
    return inputs_especificos, opciones_plan_crear

# --- Callback 4: Mostrar/Ocultar los Formularios Principales ---
@callback(
    Output('card-crear-plan', 'style'),
    Output('card-analizar-doc', 'style'),
    Output('card-adaptar-diaria', 'style'),
    Input('selector-accion-principal', 'value') # Se dispara con el RadioItems principal
)
def mostrar_formulario_principal(accion_seleccionada):
    style_crear = {'display': 'none'}
    style_analizar = {'display': 'none'}
    style_adaptar = {'display': 'none'}
    
    if accion_seleccionada == 'crear':
        style_crear = {'display': 'block'}
    elif accion_seleccionada == 'analizar':
        style_analizar = {'display': 'block'}
    elif accion_seleccionada == 'adaptar':
        style_adaptar = {'display': 'block'}
        
    return style_crear, style_analizar, style_adaptar

# --- Callback 5: Generar la respuesta de la IA (El Cerebro Unificado) ---
@callback(
    Output('ia-output-div-unificado', 'children'),
    Input('ia-generar-btn-unificado', 'n_clicks'),
    State('session-storage', 'data'),
    State('selector-accion-principal', 'value'),
    # Estados del Contexto
    State('ia-select-escuela', 'value'),
    State('ia-select-nivel', 'value'),
    State('ia-contexto-escuela', 'value'),
    # Estados de "Crear"
    State('ia-select-tipo-plan-crear', 'value'),
    State('ia-dias-clase-crear', 'value'),
    State('ia-cant-eval-crear', 'value'),
    State('ia-inclusion-crear', 'value'),
    State('ia-plan-base-crear', 'value'),
    # Estados de "Analizar"
    State('ia-accion-analizar', 'value'),
    State('ia-plan-base-analizar', 'value'),
    # Estados de "Adaptar"
    State('ia-inclusion-adaptar', 'value'),
    State('ia-plan-base-adaptar', 'value'),
    prevent_initial_call=True
)
def generar_respuesta_ia_unificada(n_clicks, data_json, accion,
                                   esc_json, nivel, contexto,
                                   tipo_plan_crear, dias_clase, cant_eval, inclusion_crear, plan_base_crear,
                                   accion_analizar, plan_base_analizar,
                                   inclusion_adaptar, plan_base_adaptar):
    
    if not API_CONFIGURADA: return "Error: API de IA no configurada."
    if not data_json: return "Error: Perfil no cargado."
    
    # Cargar datos del perfil
    data = json.loads(data_json)
    perfil = data.get('perfil', data)
    nombre_docente = perfil.get('nombre_docente', 'Docente')
    escuela = json.loads(esc_json) if esc_json else {}
    escuela_nombre = escuela.get('nombre', 'N/A')

    # Inicializar el prompt
    prompt_final = ""

    # --- Generar el Prompt según la ACCIÓN seleccionada ---
    
    if accion == 'crear':
        inclusion_str = ", ".join(inclusion_crear) if inclusion_crear else "ninguno"
        prompt_final = f"""
        **Rol:** Eres un Asesor Pedagógico experto en Nivel {nivel} en una escuela {contexto} de Mendoza.
        **Cliente:** {nombre_docente} (Escuela: {escuela_nombre}).
        **Tarea:** CREAR una "{tipo_plan_crear}".
        **Contexto:**
        * Días de clase: {dias_clase}
        * Evaluaciones: {cant_eval}
        * Desafíos de Inclusión (para plan y rúbricas): {inclusion_str}
        **Input Base (Temas/Libro):**
        {plan_base_crear}
        **Output Requerido:** Genera el plan detallado, actividades, y las RÚBRICAS de evaluación adaptadas.
        """

    elif accion == 'analizar':
        accion_str = ", ".join(accion_analizar)
        prompt_final = f"""
        **Rol:** Eres un Asesor Pedagógico experto (para {nombre_docente} de {escuela_nombre}).
        **Tarea:** ANALIZAR el siguiente documento.
        **Acciones Requeridas:** {accion_str} (Ej. Generar Rúbricas, Resumir para suplente).
        **Input Base (Documento Pegado):**
        {plan_base_analizar}
        **Output Requerido:** Entrega un informe claro que cumpla con las acciones pedidas. Si se piden rúbricas, genéralas. Si se pide resumen, que sea claro y conciso.
        """

    elif accion == 'adaptar':
        inclusion_str = ", ".join(inclusion_adaptar) if inclusion_adaptar else "ninguno"
        prompt_final = f"""
        **Rol:** Eres un Asesor Pedagógico experto en adaptaciones rápidas.
        **Tarea:** ADAPTAR una actividad diaria.
        **Desafíos de Inclusión:** {inclusion_str}
        **Input Base (Actividad Diaria):**
        {plan_base_adaptar}
        **Output Requerido:** Genera 2-3 sugerencias de adaptación concretas y el párrafo para el informe de GEI.
        """
    else:
        return "Error: Acción no reconocida."

    # --- Llamar a la IA ---
    try:
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Error al contactar la IA: {e}"