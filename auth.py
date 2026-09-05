"""Login simplificado de un solo usuario.

A diferencia de Visión Digital (múltiples roles, sesión recordada por cookie),
aquí solo existe una cuenta para toda la empresa. La primera vez que alguien
abre la plataforma y todavía no hay ningún usuario creado, se muestra un
formulario para crearlo (usuario + contraseña). De ahí en adelante, se pide
ese usuario y contraseña para entrar.
"""

import streamlit as st

import database as db
from config import EMPRESA_NOMBRE, LOGO_PATH


def current_user():
    return st.session_state.get("user")


def do_login(username: str, password: str) -> bool:
    usuario = db.get_usuario()
    if not usuario:
        return False
    if usuario["username"].strip().lower() != username.strip().lower():
        return False
    if not db.check_password(password, usuario["password_hash"]):
        return False
    st.session_state["user"] = {"username": usuario["username"]}
    return True


def do_logout():
    st.session_state.pop("user", None)


def _render_logo():
    try:
        st.image(LOGO_PATH, width=220)
    except Exception:
        pass


def _formulario_crear_usuario():
    st.info(
        "👋 Bienvenido — esta es la primera vez que se usa la plataforma. "
        "Crea el usuario y la contraseña con los que vas a entrar de ahora en adelante."
    )
    with st.form("sgh_crear_usuario_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        password2 = st.text_input("Confirmar contraseña", type="password")
        enviado = st.form_submit_button("Crear usuario", use_container_width=True)
        if enviado:
            if not username.strip() or not password:
                st.error("Completa el usuario y la contraseña.")
            elif password != password2:
                st.error("Las contraseñas no coinciden.")
            else:
                db.crear_usuario_inicial(username, password)
                st.success("Usuario creado. Ahora inicia sesión abajo.")
                st.rerun()


def _formulario_login():
    with st.form("sgh_login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Iniciar sesión", use_container_width=True)
        if enviado:
            if do_login(username, password):
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")


def require_login():
    """Si ya hay una sesión activa, la devuelve. Si no, muestra el
    formulario de creación de usuario (primera vez) o de login, y detiene
    la ejecución de la página (st.stop())."""
    user = current_user()
    if user:
        return user

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        _render_logo()
        st.markdown(
            f"<h3 style='text-align:center;'>{EMPRESA_NOMBRE}</h3>",
            unsafe_allow_html=True,
        )
        if db.get_usuario() is None:
            _formulario_crear_usuario()
        else:
            _formulario_login()

    st.stop()
