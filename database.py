"""Capa de acceso a datos (Firestore) para la plataforma SGH.

Sigue el mismo patrón de 3 niveles usado en Visión Digital:
1. `st.secrets["firebase"]`      -> producción, cuando corre en Streamlit Cloud.
2. `serviceAccountKey.json` local -> desarrollo local (el archivo NO se sube a git).
3. `fake_firestore` en memoria     -> "modo de práctica" si no hay ninguna
   credencial configurada todavía, para poder explorar la app sin Firebase.

A diferencia de Visión Digital, aquí se usa la base de datos POR DEFECTO del
proyecto de Firebase (sin `database_id` especial), ya que esta es una
plataforma nueva sin el problema histórico que forzó ese ajuste allá.
"""

import os

import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore

import fake_firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

_client = None
MODO_PRACTICA = False


# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------
def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Conexión a Firestore
# ---------------------------------------------------------------------------
def _cargar_credenciales():
    try:
        import streamlit as st
        if "firebase" in st.secrets:
            return credentials.Certificate(dict(st.secrets["firebase"]))
    except Exception as e:
        import traceback
        print("ERROR AL CARGAR CREDENCIALES DE FIREBASE:", e)
        traceback.print_exc()
    if os.path.exists(SERVICE_ACCOUNT_PATH):
        return credentials.Certificate(SERVICE_ACCOUNT_PATH)
    return None


def get_client():
    global _client, MODO_PRACTICA
    if _client is not None:
        return _client
    cred = _cargar_credenciales()
    if cred is not None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _client = firestore.client()
        MODO_PRACTICA = False
    else:
        _client = fake_firestore.FakeFirestoreClient()
        MODO_PRACTICA = True
    return _client


# ---------------------------------------------------------------------------
# Usuario único (modelo de un solo usuario/login)
# ---------------------------------------------------------------------------
_ID_USUARIO_UNICO = "principal"


def get_usuario():
    """Devuelve el único usuario configurado, o None si todavía no se ha
    creado (primer arranque de la plataforma)."""
    db = get_client()
    snap = db.collection("usuarios").document(_ID_USUARIO_UNICO).get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    data["id"] = snap.id
    return data


def crear_usuario_inicial(username: str, password: str):
    """Crea el usuario único. Solo debe llamarse una vez, la primera vez que
    se usa la plataforma (si ya existe uno, no hace nada)."""
    if get_usuario() is not None:
        return
    db = get_client()
    db.collection("usuarios").document(_ID_USUARIO_UNICO).set({
        "username": username.strip(),
        "password_hash": hash_password(password),
    })


def cambiar_password(password_nuevo: str):
    db = get_client()
    db.collection("usuarios").document(_ID_USUARIO_UNICO).update({
        "password_hash": hash_password(password_nuevo),
    })


# ---------------------------------------------------------------------------
# Visitas (Calendario de visitas)
# ---------------------------------------------------------------------------
def create_visita(fecha_hora: str, motivo: str):
    """`fecha_hora` en formato 'YYYY-MM-DD HH:MM'."""
    db = get_client()
    db.collection("visitas").add({
        "fecha_hora": fecha_hora,
        "motivo": motivo.strip(),
    })


def list_visitas():
    """Todas las visitas, ordenadas por fecha y hora (ascendente)."""
    db = get_client()
    rows = []
    for snap in db.collection("visitas").stream():
        data = snap.to_dict()
        data["id"] = snap.id
        rows.append(data)
    rows.sort(key=lambda r: r.get("fecha_hora") or "")
    return rows


def update_visita(visita_id: str, fecha_hora: str, motivo: str):
    db = get_client()
    db.collection("visitas").document(visita_id).update({
        "fecha_hora": fecha_hora,
        "motivo": motivo.strip(),
    })


def delete_visita(visita_id: str):
    db = get_client()
    db.collection("visitas").document(visita_id).delete()
