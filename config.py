"""Constantes de configuración de la plataforma SGH.

EMPRESA_NOMBRE es el nombre que se muestra en la pantalla de login y en el
título de la app — es un simple texto, cámbialo aquí por el nombre real de
la empresa cuando quieras.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMPRESA_NOMBRE = "SGH"  # <-- cambia esto por el nombre real de la empresa

# Si agregas un archivo logo.png en esta misma carpeta y lo subes al repo,
# aparecerá automáticamente en la pantalla de login. Mientras no exista,
# la app simplemente no muestra logo (no da error).
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
