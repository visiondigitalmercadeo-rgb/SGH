"""Utilidades pequeñas y genéricas (nada de lógica de negocio)."""

import io

import pandas as pd
import streamlit as st

import auth


def sidebar_user_box():
    u = auth.current_user()
    with st.sidebar:
        _, col_refrescar = st.columns([5, 1])
        with col_refrescar:
            if st.button("🔄", key="btn_refrescar_datos", help="Actualizar datos (no cierra tu sesión)"):
                st.rerun()

        st.markdown("---")
        if u:
            st.caption(f"Sesión: **{u['username']}**")
        if st.button("Cerrar sesión", use_container_width=True):
            auth.do_logout()
            st.rerun()


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Datos") -> bytes:
    """Convierte un DataFrame a los bytes de un archivo .xlsx en memoria."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buffer.getvalue()


def download_excel_button(df: pd.DataFrame, filename: str, key: str,
                           label: str = "⬇️ Descargar Excel", sheet_name: str = "Datos"):
    st.download_button(
        label, data=to_excel_bytes(df, sheet_name=sheet_name), file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, key=key,
    )
