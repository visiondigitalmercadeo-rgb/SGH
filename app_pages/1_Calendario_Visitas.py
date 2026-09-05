from datetime import date, datetime, time

import pandas as pd
import streamlit as st

import auth
import database as db
from utils import download_excel_button, sidebar_user_box

user = auth.current_user()
sidebar_user_box()

st.title("🗓️ Calendario de visitas")
st.caption("Registra y consulta las visitas programadas.")

# ---------------------------------------------------------------------------
# Formulario para agregar una visita
# ---------------------------------------------------------------------------
with st.form("form_nueva_visita", clear_on_submit=True):
    col_fecha, col_hora = st.columns(2)
    fecha = col_fecha.date_input("Fecha", value=date.today())
    hora = col_hora.time_input("Hora", value=time(9, 0))
    motivo = st.text_area("Motivo o tipo de visita")

    enviado = st.form_submit_button("➕ Agregar visita", use_container_width=True)
    if enviado:
        if not motivo.strip():
            st.error("Escribe el motivo o tipo de visita.")
        else:
            fecha_hora_str = datetime.combine(fecha, hora).strftime("%Y-%m-%d %H:%M")
            db.create_visita(fecha_hora_str, motivo)
            st.success("Visita agregada.")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Listado: próximas vs. ya pasadas
# ---------------------------------------------------------------------------
visitas = db.list_visitas()
ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M")

proximas = [v for v in visitas if (v.get("fecha_hora") or "") >= ahora_str]
pasadas = [v for v in visitas if (v.get("fecha_hora") or "") < ahora_str]

tab_proximas, tab_pasadas = st.tabs([
    f"📅 Próximas ({len(proximas)})", f"✅ Pasadas ({len(pasadas)})",
])


def _tabla(rows):
    return pd.DataFrame([{
        "Fecha y hora": r.get("fecha_hora"),
        "Motivo": r.get("motivo"),
    } for r in rows])


with tab_proximas:
    if not proximas:
        st.info("No hay visitas próximas registradas.")
    else:
        st.dataframe(_tabla(proximas), use_container_width=True, hide_index=True)
        download_excel_button(_tabla(proximas), "visitas_proximas.xlsx", key="visitas_proximas_excel")

with tab_pasadas:
    if not pasadas:
        st.info("Todavía no hay visitas pasadas.")
    else:
        st.dataframe(_tabla(pasadas), use_container_width=True, hide_index=True)
        download_excel_button(_tabla(pasadas), "visitas_pasadas.xlsx", key="visitas_pasadas_excel")

st.divider()

# ---------------------------------------------------------------------------
# Editar / eliminar una visita existente
# ---------------------------------------------------------------------------
if visitas:
    st.markdown("##### ✏️ Editar o eliminar una visita")
    opciones = {
        f"{v.get('fecha_hora')} — {v.get('motivo')}": v["id"] for v in visitas
    }
    seleccion = st.selectbox("Selecciona una visita", list(opciones.keys()), index=None,
                              key="visita_seleccion_editar")
    if seleccion:
        visita_sel = next(v for v in visitas if v["id"] == opciones[seleccion])
        fecha_actual, hora_actual = visita_sel["fecha_hora"].split(" ")
        with st.form("form_editar_visita"):
            col_fecha_e, col_hora_e = st.columns(2)
            nueva_fecha = col_fecha_e.date_input(
                "Fecha", value=datetime.strptime(fecha_actual, "%Y-%m-%d").date(),
                key="editar_fecha",
            )
            nueva_hora = col_hora_e.time_input(
                "Hora", value=datetime.strptime(hora_actual, "%H:%M").time(),
                key="editar_hora",
            )
            nuevo_motivo = st.text_area("Motivo o tipo de visita", value=visita_sel["motivo"],
                                         key="editar_motivo")
            col_guardar, col_eliminar = st.columns(2)
            guardar = col_guardar.form_submit_button("💾 Guardar cambios", use_container_width=True)
            eliminar = col_eliminar.form_submit_button("🗑️ Eliminar visita", use_container_width=True)

            if guardar:
                nueva_fecha_hora = datetime.combine(nueva_fecha, nueva_hora).strftime("%Y-%m-%d %H:%M")
                db.update_visita(visita_sel["id"], nueva_fecha_hora, nuevo_motivo)
                st.success("Visita actualizada.")
                st.rerun()
            if eliminar:
                db.delete_visita(visita_sel["id"])
                st.success("Visita eliminada.")
                st.rerun()
