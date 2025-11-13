import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import google.generativeai as genai
import os
import json
import markdown2
import io
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Registrar esta página
dash.register_page(__name__, name='Asistente IA', order=2)

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
                    dcc.RadioItems(id="ia-select-tipo-plan-crear", value='Anual-Primaria'), # Se actualiza por callback
                    
                    html.Hr(),
                    
                    # --- NUEVO: Acordeón para organizar los inputs ---
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(title="Detalles de Año y Aula", children=[
                                dbc.Label("Materia Específica:"),
                                dbc.Input(id="ia-materia", placeholder="Ej: Matemática, Biología"),
                                
                                dbc.Label("Año/Grado:", className="mt-2"),
                                dbc.Input(id="ia-ano-grado", placeholder="Ej: 5to Grado, 3er Año"),
                                
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
                                dbc.Label("Selecciona los desafíos a considerar:"),
                                # NUEVO: Lista de inclusión ampliada
                                dbc.Checklist(
                                    id="ia-inclusion-crear", 
                                    options=[
                                        {'label': 'TDAH (Déficit de Atención con Hiperactividad)', 'value': 'TDAH'},
                                        {'label': 'Dislexia', 'value': 'Dislexia'},
                                        {'label': 'TDA (Déficit de Atención sin Hiperactividad)', 'value': 'TDA'},
                                        {'label': 'TEA (Trastorno del Espectro Autista Leve)', 'value': 'TEA'},
                                        {'label': 'Discalculia (Dificultad Matemática)', 'value': 'Discalculia'},
                                        {'label': 'Altas Capacidades', 'value': 'Altas Capacidades'},
                                    ], 
                                    inline=False,
                                    labelStyle={'display': 'block', 'margin-bottom': '5px'}
                                ),
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
                    dbc.Checklist(
                        id="ia-accion-analizar",
                        options=[
                            {'label': 'Generar Rúbricas de Evaluación', 'value': 'rubricas'},
                            {'label': 'Resumir para Suplente (detectar temas clave)', 'value': 'resumen'},
                            {'label': 'Sugerir Adaptaciones de Inclusión', 'value': 'adaptar-doc'},
                        ],
                        value=['rubricas']
                    ),
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
    State('ia-materia', 'value'),         # NUEVO
    State('ia-ano-grado', 'value'),       # NUEVO
    State('ia-cant-alumnos', 'value'),    # NUEVO
    State('ia-dias-clase-crear', 'value'),
    State('ia-cant-eval-crear', 'value'),
    State('ia-cant-tps-crear', 'value'),  # NUEVO
    State('ia-inclusion-crear', 'value'),
    State('ia-plan-base-crear', 'value'),
    State('ia-dias-patios', 'value'),     # (del input dinámico)
    State('ia-libro-matriz', 'value'),    # (del input dinámico)
    State('ia-contexto-general', 'value'),# (del input dinámico)
    
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
                                   tipo_plan_crear, materia, ano_grado, cant_alumnos, 
                                   dias_clase, cant_eval, cant_tps, inclusion_crear, 
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
        
        inclusion_str = ", ".join(inclusion_crear) if inclusion_crear else "ninguno"
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
        **Tarea:** CREAR una "{tipo_plan_crear}" para la materia {materia}, en el año/grado {ano_grado}.
        
        **Contexto del Aula y Plan:**
        * Días de clase: {dias_clase}
        * Cantidad de Alumnos: {cant_alumnos}
        * Carga evaluativa: {cant_eval} evaluaciones y {cant_tps} trabajos prácticos.
        * Contexto del Nivel: {contexto_nivel_str}
        * Desafíos de Inclusión (para plan y rúbricas): {inclusion_str}
        
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


# --- Callback 6: Descargar el PDF (Versión Final con xhtml2pdf) ---
@callback(
    Output('download-pdf', 'data'),
    Input('btn-download-pdf', 'n_clicks'),
    State('ia-output-div-unificado', 'children'),
    prevent_initial_call=True
)
def download_pdf(n_clicks, markdown_text):
    if n_clicks == 0:
        return dash.no_update

    # --- MODO DE PRUEBA ---
    sample_markdown = """
¡Hola, Nahuel! Soy Guidia, tu asesora pedagógica. Es un gusto volver a conectar y ponernos a
trabajar en la planificación para tu 5to año en la Técnica República Italiana. Matemática en este
nivel es clave y prepararemos una propuesta sólida, interesante y, sobre todo, inclusiva para tus
estudiantes.
Dado que no tenemos un input base, he diseñado una propuesta completa desde cero, centrada en
el eje de **"Análisis de Funciones"**, un tema fundamental en 5to año que sienta las bases para
estudios superiores. He puesto especial atención en la adaptación para estudiantes con TDAH,
integrando estrategias en las actividades y, fundamentalmente, en las rúbricas de evaluación.
Aquí tienes la propuesta. ¡Revisémosla juntos!
---
### **PLANIFICACIÓN MENSUAL-SECUNDARIA: MATEMÁTICA 5to AÑO**
* **Docente:** Nahuel
* **Escuela:** Escuela Técnica República Italiana
* **Espacio Curricular:** Matemática
* **Curso:** 5to Año
* **Duración:** 44 días de clase (Aprox. 8-9 semanas)
* **Cantidad de Alumnos:** 30
* **Eje Temático:** El Estudio de las Funciones: De los Polinomios a los Modelos Exponenciales.
---
#### **1. Fundamentación Pedagógica**
La presente unidad busca consolidar y expandir el concepto de función, una de las ideas más
potentes de la matemática. Partiendo de los conocimientos previos sobre funciones lineales y
cuadráticas, los estudiantes explorarán el comportamiento de funciones polinómicas, racionales,
exponenciales y logarítmicas. El enfoque estará puesto en el desarrollo del pensamiento crítico, la
capacidad de modelización y la resolución de problemas aplicados a contextos reales y técnicos.
**Adaptación Inclusiva (TDAH):** La planificación se estructura en secuencias cortas y dinámicas,
alternando la instrucción directa con el trabajo práctico y colaborativo. Se priorizará el uso de
organizadores gráficos, software (GeoGebra) y rutinas claras para facilitar la organización, el
enfoque y la gestión del tiempo, atendiendo a las necesidades de los estudiantes con TDAH. La
evaluación se centrará tanto en el producto final como en el proceso, valorando el esfuerzo y las
estrategias utilizadas.
#### **2. Objetivos de Aprendizaje**
Al finalizar la unidad, se espera que los estudiantes logren:
* Analizar y graficar funciones polinómicas, identificando raíces, multiplicidad y comportamiento.
* Resolver ecuaciones e inecuaciones aplicando los conceptos de funciones.
* Interpretar el comportamiento de funciones racionales, reconociendo asíntotas y dominios.
* Comprender y aplicar las propiedades de las funciones exponenciales y logarítmicas.
* Modelizar situaciones problemáticas del mundo real y técnico utilizando las funciones
estudiadas.
* Utilizar herramientas tecnológicas como GeoGebra para la visualización y el análisis de
funciones.
#### **3. Cronograma Detallado (44 clases)**
| Semana | Días | Contenidos Principales | Actividades y Evaluaciones Clave | Estrategias para TDAH |
| :--- | :--- | :--- | :--- | :--- |
| **1** | 1-5 | **Unidad 1: Funciones Polinómicas.** Repaso. Definición, grado, raíces. Teorema del Resto y Regla de Ruffini. | Diagnóstico rápido. Clases expositivas dialogadas. Ejercicios guiados paso a paso. | *Chunking* (dividir la info en partes). Instrucciones claras y numeradas. Refuerzo positivo. |
| **2** | 6-10 | Factorización de polinomios. Teorema de Gauss para raíces racionales. | Trabajo en pares para factorizar polinomios. Lluvia de ideas guiada. **Lanzamiento del TP N°1.** | Listas de verificación (checklist) para el TP. Posibilidad de entregas parciales del avance. |
| **3** | 11-15 | Análisis completo de funciones polinómicas: multiplicidad de las raíces, conjuntos de positividad y negatividad. Gráficos aproximados. | Uso de GeoGebra para visualizar cómo la multiplicidad afecta el gráfico. "Galería de gráficos" en el aula. | Fuerte apoyo visual (colores para C+ y C-). Actividad con movimiento (caminar y observar gráficos). |
| **4** | 16-20 | Cierre de Unidad 1. Clase de consulta y repaso. | **Entrega y defensa del TP N°1.** Práctica intensiva tipo prueba. **Evaluación Sumativa N°1.** | Tiempo extra opcional para la evaluación. Espacio de trabajo con pocas distracciones. |
| **5** | 21-25 | **Unidad 2: Funciones Racionales.** Definición. Dominio. Asíntotas verticales y horizontales. Análisis y gráfico. | Descubrimiento guiado de asíntotas con GeoGebra. Ejercicios de "caza de errores" en gráficos. **Lanzamiento del TP N°2.** | Foco en una sola tarea a la vez. Mapas conceptuales para conectar ideas (dominio, asíntota). |
| **6** | 26-30 | **Unidad 3: Funciones Exponenciales.** Definición. Gráficos. Análisis del parámetro "base". Problemas de crecimiento. | Modelización de problemas: interés compuesto, crecimiento de bacterias. Uso de calculadoras científicas. | Conexión con temas de interés (videojuegos, finanzas). Problemas con datos claros y relevantes. |
| **7** | 31-35 | **Función Logarítmica.** Definición como inversa de la exponencial. Propiedades de los logaritmos. Ecuaciones. | Trabajo en estaciones: una estación de propiedades, otra de ecuaciones, otra de gráficos. **Lanzamiento del TP N°3.** | Variedad de actividades para mantener el interés. Grupos pequeños para fomentar la participación. |
| **8** | 36-40 | Cierre de Unidad 2 y 3. Aplicaciones integradoras. | **Entrega y defensa del TP N°2 y TP N°3.** Clase de repaso general con "gamificación" (Kahoot!, Quizizz). | La gamificación aumenta el engagement. Feedback inmediato. |
| **9** | 41-44 | Repaso final integrador de toda la unidad. | Simulación de examen. Espacio de consulta abierto. **Evaluación Sumativa N°2 (Integradora).** | Modelar la resolución de un problema complejo paso a paso. Fomentar la autoevaluación. |
#### **4. Detalle de Evaluaciones**
1. **Trabajo Práctico N°1: "Análisis Forense de una Función Polinómica"**: Los estudiantes reciben una función y deben realizar un análisis completo (raíces, C+, C-, gráfico) presentando un informe detallado.
2. **Trabajo Práctico N°2: "Modelizando el Mundo Real"**: En grupos, eligen una situación (ej. velocidad de internet según usuarios, dilución de una sustancia) que pueda modelizarse con una función racional o exponencial y la analizan.
3. **Trabajo Práctico N°3: "Crecimiento y Decaimiento"**: Resolución de una guía de problemas aplicados sobre funciones exponenciales y logarítmicas (ej. datación con Carbono-14, interés compuesto).
4. **Evaluación Sumativa N°1**: Prueba escrita individual sobre Funciones Polinómicas.
5. **Evaluación Sumativa N°2**: Prueba escrita individual integradora de toda la unidad.
---
### **5. RÚBRICAS DE EVALUACIÓN (ADAPTADAS PARA TDAH)**
La clave de estas rúbricas es **separar el contenido matemático de las habilidades de organización y presentación**, y valorar explícitamente el proceso.
#### **Rúbrica para Trabajo Práctico N°1: "Análisis Forense de una Función Polinómica"**
| Criterio | **Logrado (4 puntos)** | **Satisfactorio (3 puntos)** | **En Proceso (2 puntos)** | **Inicial (1 punto)** |
| :--- | :--- | :--- | :--- | :--- |
| **Comprensión Conceptual** (Dominio del tema) | Identifica correctamente todas las raíces, su multiplicidad, los conjuntos C+ y C- y la ordenada al origen, justificando sus hallazgos. | Identifica la mayoría de los elementos clave con justificaciones correctas, pero comete errores menores. | Identifica algunos elementos (ej. raíces) pero tiene dificultades con conceptos más complejos (ej. multiplicidad). | La identificación de los elementos es mayormente incorrecta o está ausente. |
| **Procedimiento Matemático** (Cálculo y aplicación) | Aplica los métodos (Ruffini, Gauss) de forma precisa y eficiente. Los cálculos son correctos y están bien fundamentados. | Aplica los métodos correctamente pero comete pequeños errores de cálculo que no afectan el concepto general. | Intenta aplicar los métodos pero muestra errores conceptuales en el procedimiento o en los cálculos. | No logra aplicar los métodos solicitados de forma coherente. |
| **Representación Gráfica** (Visualización) | El gráfico es coherente con el análisis, respetando las raíces, su comportamiento (rebota/atraviesa) y los intervalos de positividad. Es claro y prolijo. | El gráfico es mayormente coherente con el análisis, aunque puede tener imprecisiones menores en la forma o escala. | El gráfico muestra los puntos clave (raíces) pero no representa correctamente el comportamiento general de la función. | El gráfico no se corresponde con el análisis realizado. |
| **Organización y Claridad del Proceso** <br>**(Adaptación TDAH)** | El trabajo está estructurado. Muestra los pasos de forma secuencial y es fácil seguir el razonamiento, aunque no sea perfectamente prolijo. **Se valora el esfuerzo por organizar el pensamiento.** | El trabajo presenta la información necesaria, pero la estructura es algo desordenada, requiriendo que el lector conecte las partes. **Se reconocen los componentes correctos.** | El trabajo es desorganizado y los pasos del razonamiento son difíciles de seguir. Hay saltos lógicos o falta de conexión entre cálculo y conclusión. | El trabajo carece de estructura y es incomprensible. |
---
#### **Rúbrica para Evaluación Sumativa Escrita (Aplicable a ambas)**
Aquí, la adaptación no está solo en la rúbrica sino en el diseño de la prueba: problemas cortos, espacio delimitado para cada respuesta y la opción de solicitar una hoja de ruta o checklist de los pasos a seguir.
| Criterio | **Excelente (3 puntos)** | **Bueno (2 puntos)** | **A mejorar (1 punto)** |
| :--- | :--- | :--- | :--- |
| **Planteo y Estrategia** (Comprensión del problema) | Identifica correctamente los datos y la incógnita. Elige una estrategia de resolución pertinente y eficiente para el problema. | Identifica los datos y la incógnita. La estrategia elegida es pertinente, aunque podría no ser la más eficiente. | Tiene dificultades para identificar los datos clave o la estrategia elegida no es adecuada para resolver el problema. |
| **Desarrollo y Procedimiento** <br>**(Adaptación TDAH)** | El desarrollo es claro, muestra todos los pasos lógicos y los cálculos intermedios. **Incluso con un error de cálculo final, se valora el proceso correcto.** | Muestra los pasos principales del desarrollo, pero puede omitir algunos cálculos intermedios o presentar el trabajo de forma algo desorganizada. | El desarrollo es incompleto o presenta errores conceptuales significativos en el procedimiento. |
| **Precisión y Resultado Final** (Exactitud) | El resultado final es correcto, se presenta con las unidades adecuadas y responde claramente a la pregunta del problema. | El resultado final es incorrecto debido a un error de cálculo menor, pero el procedimiento es mayormente correcto. | El resultado final es incorrecto debido a errores conceptuales en el desarrollo. |
| **Feedback Formativo (Sin puntaje)** | **Gestión de la Tarea:** Logra abordar todos/casi todos los problemas. **Verificación:** Revisa sus respuestas. | **Gestión de la Tarea:** Se concentra en algunos problemas y deja otros sin hacer. **Verificación:** Realiza una revisión parcial. | **Gestión de la Tarea:** Dificultad para iniciar o completar los problemas. **Verificación:** No hay evidencia de revisión. |
---
Nahuel, espero que esta propuesta te sirva como un excelente punto de partida. Es un plan
ambicioso pero totalmente realizable. Lo más importante es que es flexible. si ves que el grupo
necesita más tiempo en un tema, podemos ajustar el cronograma.
Mi recomendación es que presentes la rúbrica a los chicos desde el primer día. Que sepan qué se
espera de ellos y cómo el esfuerzo en el proceso es tan valorado como el resultado final. Esto
puede ser un gran motivador, especialmente para aquellos que luchan con la atención y la
organización.
Quedo a tu disposición para charlar sobre cualquier punto, modificar actividades o pensar juntos en
más estrategias. ¡Excelente trabajo el que estás haciendo!
Saludos cordiales,
**Guidia**
Asesora Pedagógica
Nivel Secundario
"""
    markdown_text = sample_markdown
    # --- FIN MODO DE PRUEBA ---

    if not markdown_text:
        return dash.no_update

    try:
        # Convertir Markdown a HTML
        html_body = markdown2.markdown(markdown_text, extras=["tables"])

        # Envolver el HTML en una estructura completa con estilos
        # Usamos @font-face para asegurar que la fuente Arial se use desde los assets
        # y definimos los estilos para los encabezados y las tablas.
        source_html = f"""
        <html>
        <head>
            <style>
                @font-face {{
                    font-family: 'Arial';
                    src: url('assets/arial.ttf');
                }}
                @font-face {{
                    font-family: 'Arial';
                    font-weight: bold;
                    src: url('assets/arialbd.ttf');
                }}
                @font-face {{
                    font-family: 'Arial';
                    font-style: italic;
                    src: url('assets/ariali.ttf');
                }}
                @font-face {{
                    font-family: 'Arial';
                    font-weight: bold;
                    font-style: italic;
                    src: url('assets/arialbi.ttf');
                }}
                body {{
                    font-family: 'Arial';
                    font-size: 12px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #04294b;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Crear el PDF en memoria
        result = io.BytesIO()
        # La función link_callback es crucial para que xhtml2pdf encuentre los archivos locales (fuentes)
        pdf = pisa.CreatePDF(
                io.StringIO(source_html),
                dest=result,
                link_callback=lambda uri, rel: os.path.join(os.getcwd(), uri.replace('/', os.sep)))

        if not pdf.err:
            return dcc.send_bytes(result.getvalue(), "Guidia_Planificacion.pdf")
        else:
            print(f"Error al generar PDF con xhtml2pdf: {pdf.err}")
            return dash.no_update

    except Exception as e:
        print(f"Error crítico al generar PDF: {e}")
        import traceback
        traceback.print_exc()
        return dash.no_update