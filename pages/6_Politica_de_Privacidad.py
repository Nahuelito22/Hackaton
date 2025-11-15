import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/politica-de-privacidad', name='Política de Privacidad', order=5)

layout = dbc.Container([
    html.H1("Política de Privacidad", className="my-4"),

    html.H4("1. Información que Recopilamos"),
    html.P("La aplicación 'Asistente de Planificación Inclusiva' recopila la información que usted proporciona directamente para configurar su perfil de usuario. Esto incluye:"),
    html.Ul([
        html.Li("Nombre y Apellido."),
        html.Li("Correo electrónico."),
        html.Li("Información sobre las instituciones educativas donde trabaja (nombre, niveles, contexto)."),
    ]),
    html.P("Esta información se almacena localmente en la sesión de su navegador utilizando el componente dcc.Store de Dash. No se almacena en ninguna base de datos central ni en nuestros servidores."),

    html.H4("2. Uso de la Información"),
    html.P("La información de su perfil se utiliza exclusivamente para personalizar la experiencia dentro de la Aplicación. Los datos contextuales de su escuela y nivel se envían a la API de Google Generative AI como parte de los prompts para generar planificaciones y rúbricas relevantes. No utilizamos su información personal para ningún otro propósito."),

    html.H4("3. Almacenamiento y Seguridad de los Datos"),
    html.P("Como se mencionó, todos los datos de su perfil se guardan en el almacenamiento de sesión de su navegador. Esto significa que los datos se eliminan cuando cierra la pestaña o el navegador. No tenemos acceso a esta información. La seguridad de estos datos depende de la seguridad de su propio dispositivo y navegador."),

    html.H4("4. Intercambio de Información con Terceros"),
    html.P("No vendemos, intercambiamos ni transferimos de ningún otro modo su información de identificación personal a terceros. La única información que se comparte es el contenido no personal y contextual de los prompts enviados a la API de Google Generative AI para el procesamiento del lenguaje natural. Le recomendamos revisar la política de privacidad de Google."),

    html.H4("5. Cookies"),
    html.P("La Aplicación utiliza componentes de Dash que pueden emplear cookies para gestionar el estado de la sesión y la funcionalidad. Estas son cookies funcionales y esenciales para el funcionamiento de la aplicación."),

    html.H4("6. Consentimiento"),
    html.P("Al utilizar nuestra Aplicación, usted consiente nuestra política de privacidad."),

], fluid=True, className="p-5")
