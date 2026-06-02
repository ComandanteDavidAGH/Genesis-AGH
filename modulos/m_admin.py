import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def render_mando(df, periodo_sel, conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Mando | Nivel Rectoría</h3>", unsafe_allow_html=True)
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else 0
    st.metric("Total Estudiantes", total_estudiantes)

def render_backup(conn_sheets, conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
    
    st.markdown("<div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#cc0000; text-align:center; font-family:Arial Black; margin-top:0;'>⚠️ TELETRANSPORTACIÓN AUTOMÁTICA DESDE DRIVE</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:black; font-weight:bold; text-align:center;'>Detectamos su base de datos sólida en Google Drive. Presione el botón inferior para clonar todos los datos directo al búnker SQL.</p>", unsafe_allow_html=True)
    
    if st.button("⚡ INICIAR TELETRANSPORTACIÓN EN LA NUBE ⚡", use_container_width=True):
        with st.spinner("Estableciendo comunicación multi-núcleo..."):
            try:
                from sqlalchemy import create_engine
                cadena_sql = st.secrets["connections"]["postgresql"]["url"]
                motor_sql = create_engine(cadena_sql)
                
                for origen, destino in [('DATA_USUARIOS', 'data_usuarios'), ('NOTAS_CONSOLIDADAS', 'notas_consolidadas'), ('DB_LOGROS', 'db_logros'), ('DB_ASISTENCIA', 'db_asistencia'), ('DATA_ESTUDIANTES', 'data_estudiantes')]:
                    try:
                        st.info(f"📥 Extrayendo y clonando [{origen}] desde Drive...")
                        df_origen = conn_sheets.read(worksheet=origen, ttl=0)
                        df_origen.to_sql(destino, motor_sql, if_exists='replace', index=False)
                    except Exception as err:
                        st.warning(f"⚠️ No se pudo migrar {origen}: {err}")
                
                # Inicializar tabla de configuración básica
                df_conf_init = pd.DataFrame([{"Periodo": "P1", "Estado": "Abierto"}, {"Periodo": "P2", "Estado": "Abierto"}, {"Periodo": "P3", "Estado": "Abierto"}, {"Periodo": "P4", "Estado": "Abierto"}])
                df_conf_init.to_sql('configuracion', motor_sql, if_exists='replace', index=False)
                
                st.success("🚀 ¡TELETRANSPORTACIÓN CLONADA CON ÉXITO DESDE DRIVE A SUPABASE!")
                st.balloons()
            except Exception as e:
                st.error(f"🚨 ERROR CRÍTICO EN ENLACE: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
