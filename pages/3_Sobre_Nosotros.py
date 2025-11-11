import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/sobre-nosotros', name='Sobre Nosotros', order=4)

# --- Datos Clave de Encuestas (Placeholder) ---
datos_encuestas = [
    {"porcentaje": "35.5%", "texto": "de los docentes se siente poco o nada preparado para adaptar sus planificaciones a estudiantes con necesidades especiales."},
    {"porcentaje": "43.2%", "texto": "de los padres y madres se sienten confundidos por las rúbricas y métodos de evaluación actuales."},
    {"porcentaje": "70%", "texto": "del tiempo administrativo de un docente se dedica a la planificación y documentación, restando tiempo para la enseñanza directa."}
]

# --- Miembros del Equipo (Placeholder) ---
miembros_equipo = [
    {"nombre": "Nombre Apellido 1", "rol": "Líder de Proyecto / Experto en Educación"},
    {"nombre": "Nombre Apellido 2", "rol": "Desarrollador Full-Stack / Experto en IA"},
    {"nombre": "Nombre Apellido 3", "rol": "Diseñador UX/UI / Especialista en Accesibilidad"},
]

def crear_card_miembro(miembro):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(miembro["nombre"], className="card-title"),
                html.P(miembro["rol"], className="card-text text-muted"),
            ]),
            className="text-center h-100"
        ),
        md=4,
        className="mb-4"
    )

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Nuestro Propósito", className="text-center my-4"),
            html.P(
                "Guidia nace de una necesidad real y validada en las aulas: "
                "dar a los docentes herramientas eficientes para crear planificaciones inclusivas y "
                "ofrecer a las familias claridad sobre el proceso evaluativo. "
                "Queremos transformar el tiempo burocrático en tiempo pedagógico de calidad.",
                className="lead text-center"
            ),
        ])
    ], className="mb-5"),

    dbc.Row([
        dbc.Col(html.H2("La Realidad en Cifras", className="text-center mb-4"), width=12)
    ] + [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H3(dato["porcentaje"], className="card-title text-primary"),
                    html.P(dato["texto"], className="card-text")
                ]),
                className="text-center h-100 shadow-sm"
            ),
            md=4,
            className="mb-4"
        ) for dato in datos_encuestas
    ], className="mb-5 justify-content-center"),

    dbc.Row([
        dbc.Col(html.H2("El Equipo Detrás de Guidia", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([crear_card_miembro(miembro) for miembro in miembros_equipo], className="justify-content-center")

], fluid=True, className="p-5")
