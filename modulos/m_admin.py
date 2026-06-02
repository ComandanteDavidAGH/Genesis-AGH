import streamlit as st
import pandas as pd
import io
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

def render_mando(df, periodo_sel, conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Mando | Nivel Rectoría</h3>", unsafe_allow_html=True)
    
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else 0
    promedio_colegio = df[col_n].mean() if not df.empty and col_n in df.columns else 0
    
    est_en_riesgo = df[df[col_n] < 6.0]['Nombre_Completo'].nunique() if not df.empty and col_n in df.columns else 0
    porcentaje_riesgo = (est_en_riesgo / total_estudiantes * 100) if total_estudiantes > 0 else 0
    eficiencia_interna = 100 - porcentaje_riesgo
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Estudiantes</p><p class='metric-value'>{total_estudiantes}</p></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio Institucional</p><p class='metric-value'>{promedio_colegio:.1f}</p></div>", unsafe_allow_html=True)
    with col3: 
        color_e = "#00994c" if eficiencia_interna > 85 else "#cc8800"
        st.markdown(f"<div class='metric-card' style='border-top-color:{color_e}'><p class='metric-label'>Índice de Eficiencia</p><p class='metric-value' style='color:{color_e}'>{eficiencia_interna:.1f}%</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔐 Gestión de Seguridad de Periodos")
    st.info("Desde aquí puede cerrar los periodos para que ningún docente pueda modificar notas.")
    
    try:
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.read(worksheet="Configuracion", ttl=600)
        
        df_config = st.session_state.df_config_seguridad.copy()
        
        col_1, col_2 = st.columns(2)
        nuevos_estados = []

        for i, fila in df_config.iterrows():
            with col_1 if i < 2 else col_2:
                bloqueado = st.toggle(f"Cerrar {fila['Periodo']}", value=(fila['Estado'] == "Cerrado"))
                nuevos_estados.append("Cerrado" if bloqueado else "Abierto")

        if st.button("🔴 APLICAR BLOQUEO GENERAL", type="primary"):
            with st.spinner("🚀 Transmitiendo órdenes de seguridad al satélite..."):
                try:
                    df_config['Estado'] = nuevos_estados
                    conn.update(worksheet="Configuracion", data=df_config)
                    st.session_state.df_config_seguridad = df_config
                    st.cache_data.clear()
                    st.success("✅ Protocolo actualizado. Los periodos han sido configurados.")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🔐 Modificó la seguridad de periodos")
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 FALLA DE CONEXIÓN: {e}")
    except Exception as e:
        st.error(f"❌ Error al leer la configuración. {e}")

def render_backup(conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
    
    def guardar_como_tabla(df_export, writer_obj, sheet_name):
        if df_export is None or df_export.empty: return
        df_export.columns = df_export.columns.astype(str) 
        df_export.to_excel(writer_obj, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer_obj.sheets[sheet_name]
        (max_row, max_col) = df_export.shape
        column_settings = [{'header': col} for col in df_export.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'style': 'Table Style Medium 4'})
        for i in range(max_col): worksheet.set_column(i, i, 25) 

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        guardar_como_tabla(st.session_state.df_maestro, writer, 'NOTAS_CONSOLIDADAS')
        guardar_como_tabla(st.session_state.df_logros, writer, 'DB_LOGROS')
        guardar_como_tabla(st.session_state.df_asistencia, writer, 'DB_ASISTENCIA')
        if st.session_state.bitacora: 
            guardar_como_tabla(pd.DataFrame(st.session_state.bitacora), writer, 'BITACORA')
    
    st.download_button(label="📥 DESCARGAR BACKUP EXCEL", data=buffer.getvalue(), file_name=f"Backup_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.ms-excel", type="primary", use_container_width=True)
    
    # ---------------------------------------------------------
    # 🚀 MOTOR DE TELETRANSPORTACIÓN A SQL SUPABASE
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("<div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#cc0000; text-align:center; font-family:Arial Black; margin-top:0;'>⚠️ OPERACIÓN MIGRA-SQL</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:black; font-weight:bold; text-align:center;'>Este botón copiará TODOS los datos de su Google Sheets actual hacia la nueva base de datos PostgreSQL en Supabase. Oprímalo UNA SOLA VEZ.</p>", unsafe_allow_html=True)
    
    if st.button("⚡ INICIAR TELETRANSPORTACIÓN DE DATOS ⚡", use_container_width=True):
        with st.spinner("Estableciendo enlace satelital con Supabase... (Por favor no cierre esta ventana)"):
            try:
                from sqlalchemy import create_engine
                
                # 1. Conectar al motor SQL usando las llaves ocultas
                cadena_sql = st.secrets["connections"]["postgresql"]["url"]
                motor_sql = create_engine(cadena_sql)
                
                # 2. Descargar todos los Excel al mismo tiempo
                st.info("Descargando información de Google Sheets...")
                df_usu = conn.read(worksheet="DATA_USUARIOS", ttl=0)
                df_not = conn.read(worksheet="NOTAS_CONSOLIDADAS", ttl=0)
                df_log = conn.read(worksheet="DB_LOGROS", ttl=0)
                
                try: df_asi = conn.read(worksheet="DB_ASISTENCIA", ttl=0)
                except: df_asi = pd.DataFrame()
                
                try: df_hor = conn.read(worksheet="DB_HORARIOS", ttl=0)
                except: df_hor = pd.DataFrame()

                # Limpieza rápida para alinear con SQL
                df_not.columns = ["NOMBRE_COMPLETO", "ASIGNATURA", "P1", "P2", "P3", "P4", "LOGROS"]
                df_not = df_not.fillna(0.0)
                
                df_log.columns = ["NIVEL", "MATERIA", "DESEMPEÑO", "LOGRO_TEXTO"]
                df_usu = df_usu[["USUARIO", "PASSWORD", "ESTADO", "ROL", "Nombre_Completo"]]

                if not df_hor.empty: df_hor.columns = ["DOCENTE", "DÍA", "BLOQUE_HORARIO", "MATERIA", "GRADO"]

                # 3. Disparar a SQL
                st.info("Inyectando Usuarios...")
                df_usu.to_sql('data_usuarios', motor_sql, if_exists='append', index=False)
                
                st.info("Inyectando Notas...")
                df_not.to_sql('notas_consolidadas', motor_sql, if_exists='append', index=False)
                
                st.info("Inyectando Logros...")
                df_log.to_sql('db_logros', motor_sql, if_exists='append', index=False)
                
                if not df_asi.empty:
                    st.info("Inyectando Asistencia...")
                    df_asi.to_sql('db_asistencia', motor_sql, if_exists='append', index=False)
                    
                if not df_hor.empty:
                    st.info("Inyectando Horarios...")
                    df_hor.to_sql('db_horarios', motor_sql, if_exists='append', index=False)

                st.success("✅ ¡MIGRACIÓN EXITOSA! TODOS LOS DATOS ESTÁN AHORA EN SUPABASE.")
                st.balloons()
                
            except Exception as e:
                st.error(f"🚨 ERROR EN LA TELETRANSPORTACIÓN: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
