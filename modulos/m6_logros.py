import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def registrar_bitacora(usuario, rol, accion):
    if 'bitacora' not in st.session_state:
        st.session_state.bitacora = []
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

def renderizar(conn):
    # 🚀 ENVOLTORIO EXTERNO PREMIUM PARA LAS TABLAS Y FILTROS
    st.markdown("""
    <style>
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
        padding: 2px !important;
        background-color: #f0f2f6 !important;
    }
    .filtro-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #d4af37;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #dee2e6;
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

    # Configuración de ancho para evitar que se corten los textos
    config_columnas = {
        "LOGRO": st.column_config.TextColumn("Descripción del Logro", width="large"),
        "LOGROS": st.column_config.TextColumn("Descripción del Logro", width="large"),
        "DESCRIPCIÓN": st.column_config.TextColumn("Descripción del Logro", width="large")
    }

    if st.session_state.rol == "Admin":
        st.info("💡 Modo Edición: Como Comandante, usted tiene autorización para modificar el diccionario oficial.")
        
        # Botón alineado a la derecha como en el módulo de Notas
        col_vacia, col_btn = st.columns([7, 3])
        with col_btn:
            if st.button("💾 GUARDAR EN BASE DE DATOS", type="primary", use_container_width=True):
                df_editado = st.session_state.editor_logros
                
                with st.spinner("🚀 Transmitiendo al Satélite SQL..."):
                    try: 
                        # ⚡ ESCRITURA DIRECTA A SUPABASE
                        df_editado.to_sql('db_logros', con=conn.engine, if_exists='replace', index=False)
                        st.session_state.df_logros = df_editado.copy()
                        
                        st.toast("✅ ¡Diccionario de Logros asegurado en la bóveda SQL!", icon="🚀")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Diccionario de Logros")
                        st.cache_data.clear() # Limpiamos RAM para que los boletines tomen los nuevos logros
                        
                        import time
                        time.sleep(1)
                        st.rerun()
                    except Exception as e: 
                        st.error(f"🚨 FALLA DE ESCRITURA SQL: {e}")
        
        df_pintado = df_l.style.map(pintar_niveles, subset=['DESEMPEÑO'] if 'DESEMPEÑO' in df_l.columns else [])
        st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:5px; letter-spacing:1px;'>MATRIZ DE DESCRIPTORES EDITABLE</div>", unsafe_allow_html=True)
        
        st.session_state.editor_logros = st.data_editor(df_pintado, use_container_width=True, num_rows="dynamic", height=500, key="editor_logros", column_config=config_columnas)
    
    else:
        # --- MODO DOCENTE (LECTURA Y BÚSQUEDA TÁCTICA) ---
        st.info("👁️ Modo Lectura: Busque y consulte los logros institucionales. Solo Rectoría está autorizada para modificarlos.")
        
        # Inyección del Buscador Táctico
        st.markdown("<div class='filtro-box'>", unsafe_allow_html=True)
        st.markdown("<p style='font-family:Arial Black; color:#0d1b2a; margin-top:0;'>🔍 Búsqueda Rápida de Logros</p>", unsafe_allow_html=True)
        cf1, cf2, cf3 = st.columns(3)
        
        # Filtros dinámicos basados en las columnas existentes
        df_filtro = df_l.copy()
        
        col_nivel = next((c for c in df_filtro.columns if c.upper() in ['NIVEL', 'GRADO']), None)
        col_asig = next((c for c in df_filtro.columns if c.upper() in ['ASIGNATURA', 'MATERIA']), None)
        col_des = next((c for c in df_filtro.columns if c.upper() in ['DESEMPEÑO', 'DESEMPEÑO']), None)
        
        with cf1:
            if col_nivel:
                opciones_nivel = ["TODOS"] + sorted(df_filtro[col_nivel].dropna().unique().tolist())
                sel_nivel = st.selectbox("Nivel:", opciones_nivel)
                if sel_nivel != "TODOS": df_filtro = df_filtro[df_filtro[col_nivel] == sel_nivel]
        with cf2:
            if col_asig:
                opciones_asig = ["TODAS"] + sorted(df_filtro[col_asig].dropna().unique().tolist())
                sel_asig = st.selectbox("Asignatura:", opciones_asig)
                if sel_asig != "TODAS": df_filtro = df_filtro[df_filtro[col_asig] == sel_asig]
        with cf3:
            if col_des:
                opciones_des = ["TODOS", "BAJO", "BÁSICO", "ALTO", "SUPERIOR"]
                sel_des = st.selectbox("Desempeño:", opciones_des)
                if sel_des != "TODOS": df_filtro = df_filtro[df_filtro[col_des].astype(str).str.upper() == sel_des]
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Renderizado final
        if df_filtro.empty:
            st.warning("No hay logros que coincidan con la búsqueda actual.")
        else:
            df_pintado = df_filtro.style.map(pintar_niveles, subset=[col_des] if col_des else [])
            st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:5px; letter-spacing:1px;'>DICCIONARIO INSTITUCIONAL FILTRADO</div>", unsafe_allow_html=True)
            st.dataframe(df_pintado, use_container_width=True, height=500, hide_index=True, column_config=config_columnas)
