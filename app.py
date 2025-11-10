import streamlit as st
import google.generativeai as genai
import time
from streamlit_option_menu import option_menu # NUEVO: Importar el menú

# --- 1. Configuración de Página y API ---
# Configuración de página ANCHA para el menú superior
st.set_page_config(
    page_title="Asistente Inclusivo",
    page_icon="🚀",
    layout="wide" # 'Wide' es clave para el menú superior
)

# Configurar la API de Google
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
except Exception as e:
    st.error("Error de API Key. Asegúrate de tenerla en .streamlit/secrets.toml")
    st.stop()

# --- NUEVO: Inyección de CSS (para Footer y estética) ---
st.markdown("""
<style>
    /* Ocultar el footer nativo de Streamlit */
    footer { visibility: hidden; }

    /* Estilo del footer personalizado */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #e0e0e0;
    }
    .footer a {
        color: #0068C9;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)


# --- NUEVO: Estado de Sesión (Session State) ---
# Lo inicializamos todo al principio
if 'docente_nombre' not in st.session_state:
    st.session_state.docente_nombre = ""
if 'docente_apellido' not in st.session_state:
    st.session_state.docente_apellido = ""
if 'docente_escuela' not in st.session_state:
    st.session_state.docente_escuela = ""
if 'contexto_guardado' not in st.session_state:
    st.session_state.contexto_guardado = False


# --- NUEVO: Menú de Navegación Superior ---
selected = option_menu(
    menu_title=None, # No queremos un título de menú
    options=["Perfil", "Asistente IA", "Sobre Nosotros"], # Tus nombres de página
    icons=["person-fill", "robot", "info-circle-fill"], # Íconos de Bootstrap
    menu_icon="cast", # Ícono del menú (opcional)
    default_index=0, # Empezar en la página "Perfil"
    orientation="horizontal", # ¡La clave!
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#0068C9", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#0068C9", "color": "white"},
    }
)

# --- 2. Definición de la Página "Perfil" ---
def page_perfil():
    st.header("Tu Perfil de Docente")
    st.markdown("Completa tu contexto para personalizar las respuestas de la IA.")

    # Formulario de "Perfil"
    with st.form(key="perfil_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Tu Nombre", value=st.session_state.docente_nombre)
        with col2:
            apellido = st.text_input("Tu Apellido", value=st.session_state.docente_apellido)
        
        escuela = st.text_input("Escuela/Institución", 
                                value=st.session_state.docente_escuela,
                                placeholder="Ej. IES 9-023 Maipú")
        
        submit_button = st.form_submit_button(label="Guardar Contexto")

    # Lógica de Guardado
    if submit_button:
        if nombre and apellido and escuela:
            st.session_state.docente_nombre = nombre
            st.session_state.docente_apellido = apellido
            st.session_state.docente_escuela = escuela
            st.session_state.contexto_guardado = True
            st.success(f"¡Contexto guardado! Hola, {nombre}. Ahora puedes ir al 'Asistente IA'.")
            st.balloons()
        else:
            st.error("Por favor, completa todos los campos del perfil.")

# --- 3. Definición de la Página "Asistente IA" ---
def page_asistente():
    
    # Verificar si el perfil está completo
    if not st.session_state.get('contexto_guardado', False):
        st.warning("Por favor, ve a la página 'Perfil' y completa tus datos antes de usar el asistente.")
        st.stop()

    st.header(f"🤖 Asistente de Planificación Inclusiva")
    st.markdown(f"Hola **{st.session_state.docente_nombre}**, estás planificando para **{st.session_state.docente_escuela}**.")
    
    # Usaremos st.container para el layout
    input_container = st.container(border=True)
    output_container = st.container()

    with input_container:
        st.subheader("1. Completa los detalles de tu planificación")
        
        # Layout de 3 columnas para los inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_plan = st.selectbox(
                "Tipo de Planificación:", 
                ["Planificación de Clase Diaria", "Planificación Semanal", "Planificación Mensual", "Planificación Anual"], 
                key="tipo_plan"
            )
            
            if "Diaria" in tipo_plan:
                duracion_label = "Duración de la clase (minutos)"
                duracion_value = "45"
            else:
                duracion_label = "Período (Ej. 'Semana 1', '2026')"
                duracion_value = "Semana 1"
            
            duracion = st.text_input(duracion_label, duracion_value, key="duracion")

        with col2:
            materia = st.text_input("Materia:", "Ej. Biología", key="materia")
            cantidad_alumnos = st.number_input("Cantidad de Alumnos:", min_value=1, max_value=50, value=30, key="alumnos")

        with col3:
            desafios_aula = st.multiselect(
                "Desafíos de Inclusión (Requerido):",
                ["TDAH", "Dislexia", "TDA", "Autismo Leve", "Discalculia"],
                key="desafios"
            )
            
        planificacion_base = st.text_area(
            f"Pega aquí tu planificación base o tópicos para el plan {tipo_plan}:", 
            height=150, 
            key="plan_base",
            placeholder=f"Ej: Para el plan {tipo_plan} de {materia} quiero cubrir..."
        )
        
        generar_button = st.button("¡Generar Plan e Informe!", type="primary", use_container_width=True)

    with output_container:
        st.subheader("2. Resultados Generados por la IA")
        if generar_button:
            if not planificacion_base or not desafios_aula:
                st.error("Por favor, completa la planificación y los desafíos.")
            else:
                try:
                    with st.spinner("🧠 Analizando... La IA está generando tu plan..."):
                        # (Aquí va la función del prompt maestro)
                        prompt_final = generar_prompt_maestro(
                            docente_nombre=st.session_state.docente_nombre,
                            docente_escuela=st.session_state.docente_escuela,
                            tipo_plan=tipo_plan,
                            materia=materia,
                            duracion=duracion,
                            alumnos=cantidad_alumnos,
                            desafios=desafios_aula,
                            planificacion=planificacion_base
                        )
                        response = model.generate_content(prompt_final)
                        st.success("¡Resultados generados!")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"Ha ocurrido un error al contactar la IA: {e}")
        else:
            st.info("Completa todos los campos del paso 1 y presiona 'Generar'.")


# --- 4. Definición de la Página "Sobre Nosotros" ---
def page_sobre_nosotros():
    st.title("📊 Sobre Nosotros y el Proyecto")
    st.markdown("Esta herramienta fue creada para el **Hackaton EduTech 360** (Nov 2025).")

    st.header("Validación de Datos (Nuestras Encuestas)")
    st.markdown("No construimos una idea en el aire. Hablamos con **99 docentes y padres de Mendoza**.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("El Dolor del Docente")
        st.markdown("*(62 Encuestados)*")
        st.error("El 35.5% se siente 'Poco Preparado' para los desafíos reales del aula.")
        st.markdown("**Dolores Principales (menciones):**")
        st.markdown("* `29` Burocracia de GEI\n* `28` Informes y papeleo\n* `24` Planificar\n* `19` Inclusión (TDAH/Dislexia)")
    
    with col2:
        st.subheader("El Impacto en la Familia")
        st.markdown("*(37 Encuestados)*")
        st.error("El 43.2% se siente 'Confundido' con la información que recibe.")
        st.markdown("**Citas Clave de los Padres:**")
        st.warning("\"Quiero que se evalúe el proceso y no solo el resultado\"")
        st.info("\"Pido una aplicación de herramientas pedagógicas para acompañar dificultades\"")
    
    st.success("Nuestra solución ataca ambos problemas: ahorra **tiempo** al docente (burocracia) y da **claridad** al padre (proceso) con un solo clic.")
    
    st.header("El Equipo")
    st.markdown(f"""
    * **Nahuel Ghilardi** ({st.session_state.docente_nombre} {st.session_state.docente_apellido})
    * Mateo Gómez
    * Tomas Muñoz
    * Leandro Briceño
    * Franco
    """)


# --- 5. "Router" Principal ---
# (Este código decide qué función de página ejecutar)
if selected == "Perfil":
    page_perfil()
elif selected == "Asistente IA":
    page_asistente()
elif selected == "Sobre Nosotros":
    page_sobre_nosotros()

# --- 6. Footer (Siempre visible) ---
# NUEVO: El pie de página que pediste
st.markdown(f"""
<div class="footer">
    <p>Desarrollado por {st.session_state.get('docente_nombre', 'Nahu')} Ghilardi y Equipo - Hackaton EduTech 360</p>
    <p>
        <a href="#" target="_blank">Términos y Condiciones</a> | 
        <a href="#" target="_blank">Política de Privacidad</a>
    </p>
</div>
""", unsafe_allow_html=True)


# --- 7. (Oculto) Función del Prompt Maestro ---
# (La pegamos aquí al final para que no moleste)
def generar_prompt_maestro(docente_nombre, docente_escuela, tipo_plan, materia, duracion, alumnos, desafios, planificacion):
    
    desafios_str = ", ".join(desafios)
    if not desafios_str:
        desafios_str = "ninguno en particular"

    prompt = f"""
    **Rol:** Eres un Asesor Pedagógico experto en inclusión y didáctica, específico de Mendoza.

    **Contexto del Docente:**
    * **Nombre:** {docente_nombre}
    * **Institución:** {docente_escuela}
    * **Tipo de Planificación Requerida:** {tipo_plan}
    * **Materia:** {materia}
    * **Duración / Período:** {duracion}
    * **Tamaño del Grupo:** {alumnos} alumnos
    * **Desafíos de Inclusión detectados:** {desafios_str}

    **Planificación Base o Tópicos del Docente (Input):**
    ---
    {planificacion}
    ---

    **Tu Tarea (Output):**
    Analiza la planificación base en el contexto dado y genera dos (2) secciones de salida CLARAS 
    y CONCISAS en formato Markdown. NO añadas introducciones ni despedidas.

    **### 1. Planificación Adaptada ({tipo_plan})**
    (Ofrece sugerencias prácticas para adaptar la planificación a los desafíos de inclusión 
    mencionados, considerando el período '{tipo_plan}' y la materia '{materia}'. Sé específico.)

    **### 2. Párrafo para Informe (GEI / Familias)**
    (Escribe un párrafo profesional, listo para "copiar y pegar" en un informe de GEI
    para la institución '{docente_escuela}', firmado conceptualmente por {docente_nombre}. 
    Debe justificar las adaptaciones.)
    """
    return prompt