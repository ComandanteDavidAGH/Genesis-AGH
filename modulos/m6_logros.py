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
    # 🚀 ENVOLTORIO EXTERNO PREMIUM PARA LAS TABLAS (stDataEditor / stDataFrame)
    st.markdown("""
    <style>
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
        padding: 2px !important;
        background-color: #f0f2f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📚 Diccionario Oficial de Logros</h3>", unsafe_allow_html=True)
    
    df_l = st.session_state.df_logros.copy() if st.session_state.df_logros is not None else pd.DataFrame()

    # ⚡ MOTOR DE PINTURA PANDAS STYLER (Resalta el nivel de desempeño)
    def pintar_niveles(val):
        try:
            texto = str(val).strip().upper()
            if texto == 'BAJO': return 'color: #cc0000; font-weight: bold; background-color: #ffe6e6;'
            elif texto == 'SUPERIOR': return 'color: #00994c; font-weight: bold; background-color: #e6ffe6;'
            elif texto == 'ALTO': return 'color: #0066cc; font-weight: bold; background-color: #e6f2ff;'
            elif texto == 'BÁSICO': return 'color: #0d1b2a; font-weight: bold; background-color: #e0e0e0;'
            return ''
        except: return ''

    if st.session_state.rol == "Admin":
        st.info("💡 Modo Edición: Como Comandante, usted tiene autorización para modificar el diccionario oficial.")
        col_btn, col_espacio = st.columns([2, 8])
        with col_btn:
            if st.button("💾 GUARDAR EN BD", type="primary", use_container_width=True):
                # Capturamos la tabla temporal editada
                df_editado = st.session_state.editor_logros
                
                with st.spinner("🚀 Transmitiendo al Satélite SQL..."):
                    try: 
                        # ⚡ ESCRITURA DIRECTA A SUPABASE
                        df_editado.to_sql('db_logros', con=conn.engine, if_exists='replace', index=False)
                        st.session_state.df_logros = df_editado.copy()
                        
                        st.success("✅ Logros asegurados en el Satélite SQL.")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Diccionario de Logros")
                        st.cache_data.clear() # Limpiamos RAM para que los boletines tomen los nuevos logros
                        st.rerun()
                    except Exception as e: 
                        st.error(f"🚨 FALLA DE ESCRITURA SQL: {e}")
        
        # Aplicamos la pintura y ponemos el encabezado VIP
        df_pintado = df_l.style.map(pintar_niveles, subset=['DESEMPEÑO'] if 'DESEMPEÑO' in df_l.columns else [])
        st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ DE DESCRIPTORES EDITABLE</div>", unsafe_allow_html=True)
        
        # Renderizamos el editor
        st.session_state.editor_logros = st.data_editor(df_pintado, use_container_width=True, num_rows="dynamic", height=450, key="editor_logros")
    
    else:
        st.info("👁️ Modo Lectura: Como docente, puede consultar los logros institucionales. Solo Rectoría está autorizada para modificarlos.")
        
        # Aplicamos la pintura y ponemos el encabezado VIP
        df_pintado = df_l.style.map(pintar_niveles, subset=['DESEMPEÑO'] if 'DESEMPEÑO' in df_l.columns else [])
        st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>DICCIONARIO INSTITUCIONAL (LECTURA)</div>", unsafe_allow_html=True)
        
        # Renderizamos tabla estática
        st.dataframe(df_pintado, use_container_width=True, height=450, hide_index=True)
