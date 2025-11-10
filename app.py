import streamlit as st
import google.generativeai as genai
import time

# --- 1. Configuración de Página y API ---

# Configurar la página (¡debe ser el primer comando de Streamlit!)
st.set_page_config(
    page_title="Asistente de Planificación Inclusiva",
    page_icon="🚀",
    layout="wide", # Usar todo el ancho
)

# Configurar la API de Google (lee la clave de secrets.toml)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # Usar el modelo Flash (rápido y capaz)
except Exception as e:
    st.error(f"Error al configurar la API de Gemini: {e}")
    st.error("Asegúrate de haber creado el archivo .streamlit/secrets.toml con tu GOOGLE_API_KEY")
    st.stop()


# --- 2. El "Prompt Maestro" (El Cerebro) ---
# Esta es la parte más importante. La separamos en una función.

def generar_prompt_maestro(rol, alumnos, desafios, planificacion):
    """
    Genera el prompt detallado que se enviará a la IA.
    """
    # Convertir la lista de desafíos en un string legible
    desafios_str = ", ".join(desafios)
    if not desafios_str:
        desafios_str = "ninguno en particular"

    # El prompt es el "alma" de tu app. Es tu "investigación" de esta semana.
    prompt = f"""
    **Rol:** Eres un Asesor Pedagógico experto en inclusión y didáctica, con amplio conocimiento de la 
    legislación educativa y los desafíos en las aulas de Mendoza. Tu misión es ayudar a un docente
    a ahorrar tiempo y mejorar su enseñanza.

    **Contexto del Docente:**
    * **Rol:** {rol}
    * **Tamaño del Grupo:** {alumnos} alumnos
    * **Desafíos de Inclusión detectados:** {desafios_str}

    **Planificación Base del Docente (Input):**
    ---
    {planificacion}
    ---

    **Tu Tarea (Output):**
    Analiza la planificación base en el contexto dado y genera dos (2) secciones de salida CLARAS 
    y CONCISAS en formato Markdown. NO añadas introducciones ni despedidas, solo las dos secciones.

    **### 1. Planificación Adaptada (Sugerencias Clave)**
    (Ofrece 2-3 sugerencias prácticas y accionables para adaptar la planificación a los desafíos de inclusión 
    mencionados. Sé específico. Ej: "Para TDAH, divide la actividad 'X' en bloques de 10 min...")

    **### 2. Párrafo para Informe (GEI / Familias)**
    (Escribe un párrafo profesional, en tono formal, listo para "copiar y pegar" en un informe de GEI
    o en un comunicado a las familias. Este párrafo debe resumir las adaptaciones realizadas,
    justificando *por qué* se hacen (para el proceso de aprendizaje), tal como lo pidieron los padres
    en las encuestas.)
    """
    return prompt

# --- 3. Interfaz de Usuario (Streamlit) ---

# Título Principal
st.title("Asistente de Planificación Inclusiva 🚀")
st.markdown("Valido por 99 docentes y padres de Mendoza. Ahorra tiempo y potencia tu enseñanza.")

# --- Barra Lateral (Inputs) ---
st.sidebar.header("1. Contexto del Aula")
rol_docente = st.sidebar.selectbox("Mi Rol:", ["Docente Titular", "Docente Suplente", "Estudiante de Práctica"], key="rol")
cantidad_alumnos = st.sidebar.number_input("Cantidad de Alumnos:", min_value=1, max_value=50, value=30, key="alumnos")
desafios_aula = st.sidebar.multiselect(
    "Desafíos de Inclusión:",
    ["TDAH", "Dislexia", "TDA", "Autismo Leve", "Discalculia"],
    key="desafios"
)

st.sidebar.header("2. Input del Docente")
planificacion_base = st.sidebar.text_area(
    "Pega aquí tu planificación base:", 
    height=200, 
    key="plan_base",
    placeholder="Ej: Clase de 45 min sobre 'La Célula'. Actividad: leer el texto y responder preguntas..."
)

# Botón "Mágico"
generar_button = st.sidebar.button("¡Generar Adaptación e Informe!", type="primary")


# --- 4. Lógica de Generación (Outputs) ---

# El área principal se usa para los resultados
st.header("Resultados Generados")

if generar_button:
    # Validar que los campos no estén vacíos
    if not planificacion_base:
        st.error("Por favor, pega tu planificación base en la barra lateral.")
    elif not desafios_aula:
        st.error("Por favor, selecciona al menos un desafío de inclusión.")
    else:
        try:
            # Mostrar un "cargando..." amigable
            with st.spinner("🧠 Pensando... La IA está adaptando tu planificación..."):
                
                # 1. Crear el Prompt
                prompt_final = generar_prompt_maestro(rol_docente, cantidad_alumnos, desafios_aula, planificacion_base)
                
                # 2. Llamar a la IA
                response = model.generate_content(prompt_final)
                
                # 3. Mostrar los resultados
                st.success("¡Resultados generados!")
                
                # Usamos st.markdown para que reconozca el formato ###
                st.markdown(response.text)

                # (Opcional) Mostrar el prompt para debuggear
                with st.expander("Ver el prompt maestro enviado a la IA (Debug)"):
                    st.text(prompt_final)

        except Exception as e:
            st.error(f"Ha ocurrido un error al contactar la IA: {e}")
            st.error("Verifica tu API Key o la conexión a internet.")
else:
    st.info("Completa los datos en la barra lateral izquierda y presiona 'Generar'.")