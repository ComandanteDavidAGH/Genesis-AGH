import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
def renderizar(df, periodo_sel, conn):
    # Nombre exacto de tu tabla en la BD (Cámbialo aquí si es diferente)
    NOMBRE_TABLA_CONFIG = "configuracion" 

    st.markdown("""
    <style>
    div[data-testid="stDataEditor"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    # --- 🛡️ ESCUDO DE SEGURIDAD ---
    try:
        if 'df_config_seguridad' not in st.session_state:
            # Aquí es donde fallaba si el nombre de la tabla no coincidía
            st.session_state.df_config_seguridad = conn.query(f"SELECT * FROM {NOMBRE_TABLA_CONFIG};", ttl=600)
            
        df_conf_shield = st.session_state.df_config_seguridad
        filtro_estado = df_conf_shield[df_conf_shield['periodo'].astype(str).str.upper() == str(periodo_sel).upper()]
        
        if not filtro_estado.empty and str(filtro_estado['estado'].values[0]).strip().upper() == "CERRADO":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO.")
            st.stop()
    except Exception:
        # Si esto aparece, es que el query falló. Verifica el NOMBRE_TABLA_CONFIG arriba.
        st.warning("⚠️ Módulo de seguridad no detectado (Revisar nombre de tabla en BD).")

    if df.empty:
        st.warning("No hay estudiantes asignados.")
        return

    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True, format="%.1f")
    }

    if st.button("💾 GUARDAR EN BD", type="primary"):
        cambios = st.session_state.get('editor_notas', {}).get('edited_rows', {})
        if cambios:
            with st.spinner("🚀 Sincronizando..."):
                for fila_pos, valores in cambios.items():
                    idx_real = df.index[int(fila_pos)]
                    for col, val in valores.items():
                        st.session_state.df_maestro.at[idx_real, col] = val
                
                st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                
                try:
                    st.session_state.df_maestro.to_sql('notas_consolidadas', con=conn.engine, if_exists='replace', index=False)
                    st.success("✅ ¡Sincronizado!")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Error: {e}")
        else:
            st.warning("⚠️ Sin cambios.")

    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    # 1. Definimos la lógica de desempeño (ajusta los rangos según tu sistema de calificación)
def clasificar_desempeno(nota):
    # Por seguridad, si la nota es NaN, devolvemos "Sin definir"
    if pd.isna(nota): 
        return "Sin definir"
    
    # Aquí aplicamos tus reglas
    if nota < 6.0:
        return "BAJO"
    elif nota < 8.0:
        return "BÁSICO"
    elif nota < 9.5:
        return "ALTO"
    else:
        return "SUPERIOR"

# 2. Aplicamos esta lógica a la columna 'Definitiva' para llenar los vacíos
# Asegúrate de que 'Definitiva' sea numérica antes de procesar
df['Definitiva'] = pd.to_numeric(df['Definitiva'], errors='coerce')
df['DESEMPEÑO'] = df['Definitiva'].apply(clasificar_desempeno)
    st.data_editor(df, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)
