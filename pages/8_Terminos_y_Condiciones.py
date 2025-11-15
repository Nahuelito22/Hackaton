import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/terminos-y-condiciones', name='Términos y Condiciones', order=4)

layout = dbc.Container([
    html.H1("Términos y Condiciones de Uso", className="my-4"),

    html.H4("1. Aceptación de los Términos"),
    html.P("Al acceder y utilizar la aplicación 'Asistente de Planificación Inclusiva' (en adelante, 'la Aplicación'), usted acepta cumplir y estar sujeto a los siguientes términos y condiciones de uso. Si no está de acuerdo con estos términos, por favor no utilice la Aplicación."),

    html.H4("2. Descripción del Servicio"),
    html.P("La Aplicación es una herramienta diseñada para ayudar a los docentes a crear, adaptar y analizar planificaciones educativas con un enfoque en la inclusión. Utiliza inteligencia artificial para generar contenido y rúbricas. El servicio se proporciona 'tal cual' y no garantizamos la exactitud o idoneidad del contenido generado para ningún propósito específico."),

    html.H4("3. Uso Aceptable"),
    html.P("Usted se compromete a no utilizar la Aplicación para ningún fin ilegal o no autorizado. Usted es el único responsable de la información que introduce y del contenido que genera. No debe utilizar la Aplicación para infringir derechos de autor, marcas registradas o cualquier otro derecho de propiedad intelectual."),

    html.H4("4. Propiedad Intelectual"),
    html.P("El contenido generado por la inteligencia artificial es para su uso personal y profesional. Sin embargo, la estructura, el diseño y el código de la Aplicación son propiedad de sus desarrolladores y no pueden ser copiados o redistribuidos sin permiso explícito."),

    html.H4("5. Limitación de Responsabilidad"),
    html.P("En ningún caso los desarrolladores de la Aplicación serán responsables por daños directos, indirectos, incidentales, especiales o consecuentes que resulten del uso o la incapacidad de usar la Aplicación. El contenido generado por la IA debe ser revisado y validado por un profesional docente antes de su implementación."),

    html.H4("6. Modificaciones a los Términos"),
    html.P("Nos reservamos el derecho de modificar estos términos y condiciones en cualquier momento. El uso continuado de la Aplicación después de dichas modificaciones constituirá su aceptación de los nuevos términos."),

], fluid=True, className="p-5")
