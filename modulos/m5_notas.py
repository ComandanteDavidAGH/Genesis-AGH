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

def renderizar(df, periodo_sel, conn):
    # 👑 ESTILOS GENERALES
    st.markdown("""
    <style>
    div[data-testid="stDataEditor"] { border: 3px solid #0d1b2a; border-radius: 8px; box-shadow: 4px 4px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    # 🛡️ ESCUDO DE SEGURIDAD
    try:
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.query("SELECT * FROM configuracion;", ttl=600)
            
        df_conf = st.session_state.df_config_seguridad
        filtro = df_conf[df_conf['periodo'].astype(str).str.upper() == str(periodo_sel).upper()]
        
        if not filtro.empty and str(filtro['estado'].values[0]).upper() == "CERRADO":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} está CERRADO.")
            st.stop()
    except:
        st.warning("⚠️ Módulo de seguridad desconectado.")

    if df.empty:
        st.warning("No hay estudiantes asignados.")
        return

    # 🎯 CONFIGURACIÓN DEL EDITOR (Columnas bloqueadas vs editables)
    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True, format="%.1f")
    }

    # 💾 LÓGICA DE GUARDADO (Mejorada)
    if st.button("💾 GUARDAR CAMBIOS EN BD", type="primary"):
        cambios = st.session_state.get('editor_notas', {}).get('edited_rows', {})
        
        if cambios:
            with st.spinner("🚀 Sincronizando..."):
                # Actualizamos df_maestro
                for fila, val in cambios.items():
                    idx = df.index[int(fila)]
                    for col, v in val.items():
                        st.session_state.df_maestro.at[idx, col] = v
                
                # Recalculamos promedios
                st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                
                # Sincronización SQL
                try:
                    df_to_sql = st.session_state.df_maestro.copy()
                    # Renombrar columnas para la BD si es necesario
                    df_to_sql.to_sql('notas_consolidadas', con=conn.engine, if_exists='replace', index=False)
                    st.success("✅ ¡Base de datos actualizada!")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Error SQL: {e}")
        else:
            st.warning("⚠️ No hay cambios pendientes.")

    # 🖨️ RENDERIZADO DEL EDITOR (Sin Styler)
    st.data_editor(df, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)
