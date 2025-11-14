import dash
from dash import dcc, html, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
import google.generativeai as genai
import os
import json
from fpdf import FPDF # Importar la biblioteca de PDF

# Registrar esta página
dash.register_page(__name__, name='Asistente IA', order=2)

# --- Constantes ---
DESAFIOS_INCLUSION = [
    'TDAH (Déficit de Atención con Hiperactividad)',
    'Dislexia',
    'TDA (Déficit de Atención sin Hiperactividad)',
    'TEA (Trastorno del Espectro Autista Leve)',
    'Discalculia (Dificultad Matemática)',
    'Altas Capacidades',
]

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
    
    html.Div(id="ia-welcome-message"),
    dcc.Download(id="download-pdf"),
    
    dbc.Row([
        # --- Columna Izquierda (Contexto y Acción) ---
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Paso 1: ¿Qué quieres hacer hoy?"),
                dbc.CardBody([
                    html.Div([
                        dcc.RadioItems(
                            id='selector-accion-principal',
                            options=[
                                {'label': ' Crear una nueva Planificación (Anual/Mensual)', 'value': 'crear'},
                                {'label': ' Analizar un Plan existente / Generar Rúbricas', 'value': 'analizar'},
                                {'label': ' Adaptar una Actividad Diaria (Inclusión Rápida)', 'value': 'adaptar'},
                            ],
                            value='crear',
                            labelStyle={'display': 'block', 'margin-bottom': '10px'}
                        )
                    ], className="control-group")
                ])
            ]),
            html.Br(),
            
            dbc.Card([
                dbc.CardHeader("Paso 2: Define tu Contexto"),
                dbc.CardBody([
                    dbc.Label("¿Para qué institución estás planificando?"),
                    dcc.Dropdown(id="ia-select-escuela", placeholder="Cargando escuelas..."),
                    
                    dbc.Label("¿Para qué nivel?", className="mt-2"),
                    dcc.Dropdown(id="ia-select-nivel", placeholder="Selecciona una escuela primero..."),
                    
                    dbc.Label("Contexto de la Escuela:", className="mt-2"),
                    dbc.Input(id="ia-contexto-escuela", disabled=True)
                ])
            ]),

        ], width=4), # Fin Columna Izquierda
        
        # --- Columna Derecha (Formularios Dinámicos) ---
        dbc.Col([
            
            # --- Formulario para "CREAR PLANIFICACIÓN" (NUEVA UI CON ACORDEÓN) ---
            dbc.Card(id="card-crear-plan", children=[
                dbc.CardHeader("Paso 3: Detalles para CREAR Planificación"),
                dbc.CardBody([
                    
                    dbc.Label("Tipo de Plan a Crear:"),
                    html.Div(
                        dcc.RadioItems(id="ia-select-tipo-plan-crear", value='Anual-Primaria'), # Se actualiza por callback
                        className="control-group"
                    ),
                    
                    html.Hr(),
                    
                    # --- NUEVO: Acordeón para organizar los inputs ---
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(title="Detalles de Año y Aula", children=[
                                dbc.Label("Materia Específica:"),
                                dbc.Input(id="ia-materia", placeholder="Ej: Matemática, Biología"),
                                
                                dbc.Label("Año/Grado:", className="mt-2"),
                                dbc.Input(id="ia-ano-grado", placeholder="Ej: 5to Grado, 3er Año"),
                                
                                # Campo de Mes, oculto por defecto
                                html.Div([
                                    dbc.Label("Mes a Planificar:", className="mt-2"),
                                    dbc.Input(id="ia-mes-plan", placeholder="Ej: Mayo, Junio"),
                                ], id="ia-mes-container", style={'display': 'none'}),

                                dbc.Label("Cantidad de Alumnos (aprox):", className="mt-2"),
                                dbc.Input(id="ia-cant-alumnos", type="number", value=30, min=1, step=1),
                            ]),
                            
                            dbc.AccordionItem(title="Detalles Específicos del Plan", children=[
                                # Este Div se rellena dinámicamente (Primaria vs Secundaria)
                                html.Div(id="ia-contexto-nivel-crear"),
                                
                                dbc.Label("Cantidad de Días de Clase (aprox):", className="mt-2"),
                                dbc.Input(id="ia-dias-clase-crear", type="number", value=20, min=1, step=1),
                                
                                dbc.Label("Cantidad de Evaluaciones Principales:", className="mt-2"),
                                dbc.Input(id="ia-cant-eval-crear", type="number", value=2, min=0, step=1),
                                
                                # NUEVO: Campo de TPs
                                dbc.Label("Cantidad de Trabajos Prácticos (TPs):", className="mt-2"),
                                dbc.Input(id="ia-cant-tps-crear", type="number", value=3, min=0, step=1),
                            ]),
                            
                            dbc.AccordionItem(title="Detalles de Inclusión (Adaptar Rúbricas)", children=[
                                dbc.Label("Indica la cantidad de alumnos por desafío:", className="mb-2"),
                                html.Div([
                                    dbc.Row([
                                        dbc.Col(html.Strong("Desafío de Inclusión"), width=8),
                                        dbc.Col(html.Strong("Cantidad"), width=4),
                                    ], className="mb-2"),
                                ] + [
                                    dbc.Row([
                                        dbc.Col(dbc.Label(desafio), width=8, style={'font-size': '0.9rem'}),
                                        dbc.Col(
                                            dbc.Input(
                                                id={'type': 'inclusion-cant', 'index': desafio},
                                                type='number',
                                                min=0,
                                                value=0,
                                            ),
                                            width=4
                                        ),
                                    ], className="mb-1 align-items-center") for desafio in DESAFIOS_INCLUSION
                                ], className="control-group")
                            ]),
                        ],
                        start_collapsed=False,
                        always_open=True
                    ),
                    
                    html.Hr(),
                    dbc.Label("Input Base (Pega los temas, parrilla anterior, libro matriz, etc.):"),
                    dbc.Textarea(id="ia-plan-base-crear", rows=8,
                                 placeholder="Si dejas esto vacío, la IA crea de cero. Si pegas texto (ej. temas del libro), la IA lo usa como base."),
                ])
            ], style={'display': 'block'}), # Visible por defecto

            # --- Formulario para "ANALIZAR DOCUMENTO" ---
            dbc.Card(id="card-analizar-doc", children=[
                dbc.CardHeader("Paso 3: Detalles para ANALIZAR Planificación"),
                dbc.CardBody([
                    dbc.Label("¿Qué quieres que haga la IA con este documento?"),
                    html.Div([
                        dbc.Checklist(
                            id="ia-accion-analizar",
                            options=[
                                {'label': 'Generar Rúbricas de Evaluación', 'value': 'rubricas'},
                                {'label': 'Resumir para Suplente (detectar temas clave)', 'value': 'resumen'},
                                {'label': 'Sugerir Adaptaciones de Inclusión', 'value': 'adaptar-doc'},
                            ],
                            value=['rubricas']
                        ),
                    ], className="control-group"),
                    html.Hr(),
                    dbc.Label("Pega aquí la Planificación (Anual, Mensual, etc.) a ANALIZAR:"),
                    dbc.Textarea(id="ia-plan-base-analizar", rows=20,
                                 placeholder="Pega aquí el documento completo..."),
                ])
            ], style={'display': 'none'}), # Oculto por defecto

            # --- Formulario para "ADAPTACIÓN RÁPIDA" ---
            dbc.Card(id="card-adaptar-diaria", children=[
                dbc.CardHeader("Paso 3: Adaptación Rápida de Clase Diaria"),
                dbc.CardBody([
                    dbc.Label("Pega aquí tu borrador de actividad de clase:"),
                    dbc.Textarea(id="ia-plan-base-adaptar", rows=10),
                    dbc.Label("Desafíos de Inclusión a adaptar:", className="mt-2"),
                    # NUEVO: Lista de inclusión ampliada
                    dbc.Checklist(
                        id="ia-inclusion-adaptar", 
                        options=[
                            {'label': 'TDAH', 'value': 'TDAH'},
                            {'label': 'Dislexia', 'value': 'Dislexia'},
                            {'label': 'TDA', 'value': 'TDA'},
                            {'label': 'TEA (Autismo Leve)', 'value': 'TEA'},
                            {'label': 'Discalculia', 'value': 'Discalculia'},
                        ], 
                        inline=True, value=['TDAH']),
                ])
            ], style={'display': 'none'}), # Oculto por defecto
            
            # --- Botones de Acción (Sin cambios) ---
            dbc.Row([
                dbc.Col(dbc.Button("Generar Respuesta IA", 
                                 id="ia-generar-btn-unificado", 
                                 color="primary", 
                                 className="w-100", 
                                 n_clicks=0), width=8),
                
                dbc.Col(dbc.Button("Descargar PDF",
                                 id="btn-download-pdf",
                                 color="secondary",
                                 outline=True, # Estilo secundario
                                 className="w-100",
                                 n_clicks=0), width=4),
            ], className="mt-3"),
            
            # --- Output (Unificado) (Sin cambios) ---
            html.Hr(),
            dbc.Label("Resultados Generados por la IA:"),
            dcc.Loading(
                dcc.Markdown(id="ia-output-div-unificado", 
                             style={'border': '1px solid #ddd', 'padding': '10px', 'min-height': '200px', 'background-color': '#fff'})
            )
            
        ], width=8) # Fin Columna Derecha
    ]) # Fin Fila
])

# --- 2. Callbacks (La "Magia" de Dash) ---

# --- Callbacks 1 a 4 (Sin cambios) ---
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
        # Guardar el objeto entero como un string json
        opciones_escuela = [{'label': esc['nombre'], 'value': json.dumps(esc)} for esc in instituciones]
        mensaje_bienvenida = dbc.Alert(f"¡Hola {nombre_docente}! Selecciona tu contexto para comenzar.", color="success")
        return mensaje_bienvenida, opciones_escuela
    except Exception as e:
        return dbc.Alert(f"Error al cargar tu perfil: {e}", color="danger"), []

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
    # Seleccionar automáticamente el primer nivel si existe
    valor_nivel = opciones_nivel[0]['value'] if opciones_nivel else None
    
    return opciones_nivel, valor_nivel, contexto_de_la_escuela

@callback(
    Output('ia-contexto-nivel-crear', 'children'),
    Output('ia-select-tipo-plan-crear', 'options'),
    Input('ia-select-nivel', 'value')
)
def mostrar_contexto_especifico_crear(nivel_seleccionado):
    opciones_plan_crear = []
    
    # Definir estilos para mostrar/ocultar los inputs
    style_primario = {'display': 'none'}
    style_secundario = {'display': 'none'}
    style_otro = {'display': 'none'}

    if nivel_seleccionado == 'Primario':
        opciones_plan_crear = [
            {'label': 'Plan Anual (Parrilla)', 'value': 'Anual-Primaria'},
            {'label': 'Plan Mensual (Actividades y Rúbricas)', 'value': 'Mensual-Primaria'},
        ]
        style_primario = {'display': 'block'}
    elif nivel_seleccionado == 'Secundario':
        opciones_plan_crear = [
            {'label': 'Plan Anual (desde Libro Matriz)', 'value': 'Anual-Secundaria'},
            {'label': 'Plan Mensual (desde Anual)', 'value': 'Mensual-Secundaria'},
        ]
        style_secundario = {'display': 'block'}
    else:
        # Default o Nivel Inicial
        opciones_plan_crear = [{'label': 'Planificación de Actividades', 'value': 'Actividades'}]
        style_otro = {'display': 'block'}

    # Crear siempre todos los componentes, pero controlar su visibilidad.
    # Así, el callback principal siempre los encontrará en el layout.
    inputs_especificos = [
        html.Div([
            dbc.Label("Eventos Especiales / Días Patrios (Opcional):"),
            dbc.Textarea(id="ia-dias-patios", placeholder="Ej: 25 de Mayo, Día de la Bandera...", rows=2),
        ], style=style_primario),
        
        html.Div([
            dbc.Label("Libro Matriz / Temario General (Opcional):"),
            dbc.Textarea(id="ia-libro-matriz", placeholder="Ej: 'Capítulos 1-4 del libro Santillana...'", rows=2),
        ], style=style_secundario),

        html.Div([
            dbc.Label("Contexto General:"), 
            dbc.Textarea(id="ia-contexto-general", rows=2)
        ], style=style_otro)
    ]

    return inputs_especificos, opciones_plan_crear

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


# --- Callback para mostrar/ocultar el campo de mes ---
@callback(
    Output('ia-mes-container', 'style'),
    Input('ia-select-tipo-plan-crear', 'value')
)
def toggle_mes_container(plan_type):
    if plan_type in ['Mensual-Primaria', 'Mensual-Secundaria']:
        return {'display': 'block'}
    return {'display': 'none'}



# --- Callback 5: Generar la respuesta de la IA (ACTUALIZADO CON TUS IDEAS) ---
@callback(
    Output('ia-output-div-unificado', 'children'),
    Input('ia-generar-btn-unificado', 'n_clicks'),
    # Estados de Contexto General
    State('session-storage', 'data'),
    State('selector-accion-principal', 'value'),
    State('ia-select-escuela', 'value'),
    State('ia-select-nivel', 'value'),
    State('ia-contexto-escuela', 'value'),
    
    # Estados de "Crear Planificación" (SECCIÓN ACTUALIZADA)
    State('ia-select-tipo-plan-crear', 'value'),
    State('ia-materia', 'value'),
    State('ia-ano-grado', 'value'),
    State('ia-mes-plan', 'value'),
    State('ia-cant-alumnos', 'value'),
    State('ia-dias-clase-crear', 'value'),
    State('ia-cant-eval-crear', 'value'),
    State('ia-cant-tps-crear', 'value'),
    State({'type': 'inclusion-cant', 'index': ALL}, 'value'), # NUEVO
    State('ia-plan-base-crear', 'value'),
    State('ia-dias-patios', 'value'),
    State('ia-libro-matriz', 'value'),
    State('ia-contexto-general', 'value'),
    
    # Estados de "Analizar Documento"
    State('ia-accion-analizar', 'value'),
    State('ia-plan-base-analizar', 'value'),
    
    # Estados de "Adaptación Rápida"
    State('ia-inclusion-adaptar', 'value'),
    State('ia-plan-base-adaptar', 'value'),
    prevent_initial_call=True
)
def generar_respuesta_ia_unificada(n_clicks, data_json, accion,
                                   esc_json, nivel, contexto,
                                   # Argumentos de "Crear"
                                   tipo_plan_crear, materia, ano_grado, mes_plan, cant_alumnos, 
                                   dias_clase, cant_eval, cant_tps, inclusion_cant, 
                                   plan_base_crear, dias_patios, libro_matriz, contexto_general,
                                   # Argumentos de "Analizar"
                                   accion_analizar, plan_base_analizar,
                                   # Argumentos de "Adaptar"
                                   inclusion_adaptar, plan_base_adaptar):
    
    if not API_CONFIGURADA: return "Error: API de IA no configurada."
    if not data_json: return "Error: Perfil no cargado."
    
    # --- Cargar Perfil ---
    data = json.loads(data_json)
    perfil = data.get('perfil', data)
    nombre_docente = perfil.get('nombre_docente', 'Docente')
    escuela = json.loads(esc_json) if esc_json else {}
    escuela_nombre = escuela.get('nombre', 'N/A')

    prompt_final = ""
    
    # --- 1. Lógica para "CREAR PLANIFICACIÓN" ---
    if accion == 'crear':
        if not all([materia, ano_grado, tipo_plan_crear]):
             return "Error: Faltan datos clave. Por favor, completa 'Materia', 'Año/Grado' y 'Tipo de Plan' en el acordeón."
        
        # Añadir el mes al tipo de plan si está definido
        plan_str = f"{tipo_plan_crear} para el mes de {mes_plan}" if mes_plan and 'Mensual' in tipo_plan_crear else tipo_plan_crear

        # Procesar los desafíos de inclusión
        desafios_con_cantidad = []
        for i, cant in enumerate(inclusion_cant):
            if cant and cant > 0:
                desafio_nombre = DESAFIOS_INCLUSION[i].split(' (')[0] # Tomar nombre corto
                desafios_con_cantidad.append(f"{desafio_nombre} ({cant} alumno/s)")
        
        inclusion_str = ", ".join(desafios_con_cantidad) if desafios_con_cantidad else "ninguno especificado"

        contexto_nivel_str = ""
        if nivel == 'Primario' and dias_patios:
            contexto_nivel_str = f"Eventos especiales a considerar (días patrios): {dias_patios}"
        elif nivel == 'Secundario' and libro_matriz:
            contexto_nivel_str = f"Temario / Libro Matriz de referencia: {libro_matriz}"
        elif contexto_general:
            contexto_nivel_str = f"Contexto general provisto: {contexto_general}"

        prompt_final = f"""
        **Rol:** Eres Guidia, un Asesor Pedagógico experto en Nivel {nivel} en una escuela {contexto} de Mendoza.
        **Cliente:** {nombre_docente} (Escuela: {escuela_nombre}).
        **Tarea:** CREAR una "{plan_str}" para la materia {materia}, en el año/grado {ano_grado}.
        
        **Contexto del Aula y Plan:**
        * Días de clase: {dias_clase}
        * Cantidad de Alumnos: {cant_alumnos}
        * Carga evaluativa: {cant_eval} evaluaciones y {cant_tps} trabajos prácticos.
        * Contexto del Nivel: {contexto_nivel_str}
        * Desafíos de Inclusión y cantidad de alumnos a considerar: {inclusion_str}
        
        **Input Base del Docente (Temas, Parrilla Anual, etc.):**
        ---
        {plan_base_crear}
        ---
        **Output Requerido:** Genera el plan detallado, actividades, y las RÚBRICAS de evaluación adaptadas 
        a los desafíos de inclusión mencionados. Si el Input Base está vacío, crea la planificación desde cero 
        basándote en el currículo estándar para {materia} en {ano_grado}.
        """

    # --- 2. Lógica para "ANALIZAR DOCUMENTO" ---
    elif accion == 'analizar':
        if not plan_base_analizar:
             return "Error: Por favor, pega el documento que quieres analizar."
        
        accion_str = ", ".join(accion_analizar)
        prompt_final = f"""
        **Rol:** Eres Guidia, un Asesor Pedagógico experto (para {nombre_docente} de {escuela_nombre}).
        **Tarea:** ANALIZAR el siguiente documento.
        **Acciones Requeridas:** {accion_str} (Ej. Generar Rúbricas, Resumir para suplente, Sugerir adaptaciones).
        **Input Base (Documento Pegado):**
        ---
        {plan_base_analizar}
        ---
        **Output Requerido:** Entrega un informe claro en Markdown que cumpla con las acciones pedidas. 
        Si se piden Rúbricas, genéralas. Si se pide Resumen, que sea claro y conciso.
        """

    # --- 3. Lógica para "ADAPTACIÓN RÁPIDA" ---
    elif accion == 'adaptar':
        if not plan_base_adaptar:
             return "Error: Por favor, pega la actividad que quieres adaptar."
             
        inclusion_str = ", ".join(inclusion_adaptar) if inclusion_adaptar else "ninguno"
        prompt_final = f"""
        **Rol:** Eres Guidia, un Asesor Pedagógico experto en adaptaciones rápidas.
        **Tarea:** ADAPTAR una actividad diaria para {nombre_docente} (Escuela: {escuela_nombre}).
        **Desafíos de Inclusión:** {inclusion_str}
        **Input Base (Actividad Diaria):**
        ---
        {plan_base_adaptar}
        ---
        **Output Requerido:** Genera 2-3 sugerencias de adaptación concretas y el párrafo para el informe de GEI.
        """
    else:
        return "Error: Acción no reconocida."

    # --- Llamar a la IA ---
    try:
        response = model.generate_content(prompt_final)
        # Reemplazar para que Markdown se vea mejor
        return response.text.replace('•', '  * ')
    except Exception as e:
        return f"Error al contactar la IA: {e}"


# --- Callback 6: Descargar el PDF (Corregido) ---
@callback(
    Output('download-pdf', 'data'), # El output es el componente de descarga
    Input('btn-download-pdf', 'n_clicks'),
    State('ia-output-div-unificado', 'children'), # El input es el texto de Markdown
    prevent_initial_call=True
)
def download_pdf(n_clicks, markdown_text):
    if not markdown_text or n_clicks == 0:
        return dash.no_update

    # --- Intento 1: Usar write_html para texto con formato ---
    try:
        pdf = FPDF()
        pdf.add_page()
        # Añadir soporte para UTF-8, buscando la fuente en la carpeta assets
        pdf.add_font('Arial', '', 'assets/arial.ttf', uni=True)
        pdf.set_font("Arial", size=12)

        # Reemplazar saltos de línea de Markdown por <br> para que write_html los interprete
        html_text = markdown_text.replace('\n', '<br>')
        pdf.write_html(html_text)
        
        pdf_output = pdf.output()
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1')
        else:
            pdf_bytes = pdf_output
            
        # SOLUCIÓN: Convertir explícitamente a bytes() para dcc.send_bytes
        return dcc.send_bytes(bytes(pdf_bytes), "Guidia_Planificacion.pdf")

    except Exception as e1:
        print(f"Error con write_html, usando fallback a texto plano. Error: {e1}")
        
        # --- Intento 2: Fallback a texto plano si write_html falla ---
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('Arial', '', 'assets/arial.ttf', uni=True)
            pdf.set_font("Arial", size=12)
            
            pdf.multi_cell(0, 10, markdown_text)
            
            pdf_output = pdf.output()
            if isinstance(pdf_output, str):
                pdf_bytes = pdf_output.encode('latin-1')
            else:
                pdf_bytes = pdf_output

            # SOLUCIÓN: Convertir explícitamente a bytes() para dcc.send_bytes
            return dcc.send_bytes(bytes(pdf_bytes), "Guidia_Planificacion_TextoPlano.pdf")
            
        except Exception as e2:
            print(f"Error crítico al generar PDF de fallback: {e2}")
            import traceback
            traceback.print_exc()
            return dash.no_update