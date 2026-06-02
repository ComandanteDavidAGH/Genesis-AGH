import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

def renderizar(conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📚 Diccionario Oficial de Logros</h3>", unsafe_allow_html=True)
    
    df_l = st.session_state.df_logros if st.session_state.df_logros is not None else pd.DataFrame()

    if st.session_state.rol == "Admin":
        st.info("💡 Modo Edición: Como Comandante, usted tiene autorización para modificar el diccionario oficial.")
        col_btn, col_espacio = st.columns([2, 8])
        with col_btn:
            if st.button("💾 GUARDAR LOGROS", type="primary", use_container_width=True):
                st.session_state.df_logros = st.session_state.df_l_temp
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Diccionario de Logros")
                with st.spinner("Subiendo a la Bóveda..."):
                    try: 
                        conn.update(worksheet="DB_LOGROS", data=st.session_state.df_logros)
                        st.success("✅ Logros asegurados en el Satélite")
                    except: 
                        st.warning("⚠️ Error de conexión.")
                st.rerun()
        st.session_state.df_l_temp = st.data_editor(df_l, use_container_width=True, num_rows="dynamic", height=300, key="editor_logros")
    else:
        st.info("👁️ Modo Lectura: Como docente, puede consultar los logros institucionales. Solo Rectoría está autorizada para modificarlos.")
        st.dataframe(df_l, use_container_width=True, height=300, hide_index=True)
