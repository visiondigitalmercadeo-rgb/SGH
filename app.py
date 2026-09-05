"""Punto de entrada de la plataforma SGH.

Versión mínima: un solo usuario, una sola pestaña (Calendario de visitas).
Cuando quieras agregar más pestañas, cada una es un archivo dentro de la
carpeta app_pages/ (Streamlit las detecta solo por estar ahí).
"""

import streamlit as st

import auth
from config import EMPRESA_NOMBRE

st.set_page_config(page_title=EMPRESA_NOMBRE, page_icon="🗓️", layout="wide")

auth.require_login()

pagina_visitas = st.Page(
    "app_pages/1_Calendario_Visitas.py",
    title="Calendario de visitas",
    icon="🗓️",
    default=True,
)

pg = st.navigation([pagina_visitas])
pg.run()
