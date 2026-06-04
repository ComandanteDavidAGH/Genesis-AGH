import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def registrar_bitacora(usuario, rol, accion):
    if 'bitacora' not in st.session_state: st.session_state.bitacora = []
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario, "Rol": rol, "Acción": accion
    })

def renderizar(conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📚 Diccionario Oficial de Logros</h3>", unsafe_allow_html=True)
    
    # 🚀 MOTOR VISUAL 3D Y FUSIÓN DE CONTORNOS
    st.markdown("""
    <style>
    /* Fusión perfecta entre el encabezado negro y la tabla */
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        border: 3px solid #0d1b2a !important;
        border-top: none !important; /* Para que encaje con la caja del título */
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
        margin-top: -15px !important; /* 🎯 TRUCO MAESTRO: Succiona la tabla hacia arriba */
        position: relative;
        z-index: 10;
    }
    
    /* Eliminar borde gris fantasma interno de Streamlit */
    [data-testid="stDataFrameResizable"] {
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'df_logros' not in st.session_state or st.session_state.df_logros is None:
        st.error("No se pudo cargar la base de datos de logros.")
        return

    df_l = st.session_state.df_logros

    if st.session_state.rol == "Admin":
        st.info("💡 Modo Edición: Como Comandante, usted tiene autorización para modificar el diccionario oficial.")
        col_vacia, col_btn = st.columns([7, 3])
        with col_btn:
            if st.button("💾 GUARDAR LOGROS", type="primary", use_container_width=True):
                with st.spinner("Sincronizando al Satélite SQL..."):
                    try:
                        st.session_state.df_logros = st.session_state.df_l_temp
                        df_para_sql = st.session_state.df_logros.copy()
                        df_para_sql.to_sql('db_logros', con=conn.engine, if_exists='replace', index=False)
                        st.toast("✅ ¡Logros sincronizados exitosamente!", icon="🚀")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Diccionario de Logros")
                        st.cache_data.clear()
                        import time
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 Error SQL: {e}")

        # 🎯 EL TÍTULO QUE SE FUNDE CON LA TABLA
        st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-radius:8px 8px 0 0; position:relative; z-index:11; letter-spacing:1px;'>MATRIZ DE DESCRIPTORES EDITABLE</div>", unsafe_allow_html=True)
        
        st.session_state.df_l_temp = st.data_editor(df_l, use_container_width=True, num_rows="dynamic", height=500, key="editor_logros")
    
    else:
        st.info("👁️ Modo Lectura: Como docente, puede consultar los logros. Solo Rectoría está autorizada para modificarlos.")
        
        # 🎯 EL TÍTULO QUE SE FUNDE CON LA TABLA
        st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-radius:8px 8px 0 0; position:relative; z-index:11; letter-spacing:1px;'>MATRIZ DE DESCRIPTORES INSTITUCIONALES</div>", unsafe_allow_html=True)
        
        st.dataframe(df_l, use_container_width=True, height=500, hide_index=True)
