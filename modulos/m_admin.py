import streamlit as st
import pandas as pd
import io
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

def render_mando(df, periodo_sel, conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Mando | Nivel Rectoría</h3>", unsafe_allow_html=True)
    
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else 0
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
    
    if 'df_config_seguridad' not in st.session_state or st.session_state.df_config_seguridad is None:
        try:
            st.session_state.df_config_seguridad = conn_sql.query("SELECT * FROM configuracion;")
        except Exception:
            st.session_state.df_config_seguridad = pd.DataFrame([
                {"Periodo": "P1", "Estado": "Abierto"},
                {"Periodo": "P2", "Estado": "Abierto"},
                {"Periodo": "P3", "Estado": "Abierto"},
                {"Periodo": "P4", "Estado": "Abierto"}
            ])
    
    df_config = st.session_state.df_config_seguridad.copy()
    
    col_1, col_2 = st.columns(2)
    nuevos_estados = []

    for i, fila in df_config.iterrows():
        with col_1 if i < 2 else col_2:
            bloqueado = st.toggle(f"Cerrar {fila['Periodo']}", value=(fila['Estado'] == "Cerrado"))
            nuevos_estados.append("Cerrado" if bloqueado else "Abierto")

    if st.button("🔴 APLICAR BLOQUEO GENERAL", type="primary"):
        st.session_state.df_config_seguridad = df_config
        st.success("✅ Protocolo actualizado en la sesión.")
        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🔐 Modificó la seguridad de periodos")
        st.rerun()

def render_backup(conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
    
    if st.session_state.get('df_maestro') is not None:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_maestro.to_excel(writer, sheet_name='NOTAS_CONSOLIDADAS', index=False)
        st.download_button(label="📥 DESCARGAR BACKUP EXCEL LOCAL", data=buffer.getvalue(), file_name=f"Backup_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.ms-excel", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("<div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#cc0000; text-align:center; font-family:Arial Black; margin-top:0;'>⚠️ OPERACIÓN MIGRA-SQL POR EXCEL</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:black; font-weight:bold; text-align:center;'>Suba el archivo de respaldo Excel (.xlsx) que descargó de su Google Drive para inyectar todas las tablas directamente en Supabase.</p>", unsafe_allow_html=True)
    
    archivo_excel = st.file_uploader("📂 Seleccione el archivo de respaldo Excel (.xlsx)", type=["xlsx"])
    
    if archivo_excel is not None:
        if st.button("⚡ INICIAR INYECCIÓN AUTOMÁTICA A SUPABASE ⚡", use_container_width=True):
            with st.spinner("Estableciendo enlace e inyectando datos al búnker..."):
                try:
                    from sqlalchemy import create_engine
                    cadena_sql = st.secrets["connections"]["postgresql"]["url"]
                    motor_sql = create_engine(cadena_sql)
                    
                    xls = pd.ExcelFile(archivo_excel)
                    pestanas = xls.sheet_names
                    
                    # Buscador flexible de nombres por si hay variaciones de mayúsculas o S
                    tablas_mapeo = [
                        (['DATA_USUARIOS', 'Data_Usuarios', 'data_usuarios'], 'data_usuarios'), 
                        (['NOTAS_CONSOLIDADAS', 'NOTAS_CONSOLIDADA', 'Notas_Consolidadas'], 'notas_consolidadas'), 
                        (['DB_LOGROS', 'Db_Logros', 'db_logros'], 'db_logros'), 
                        (['DB_ASISTENCIA', 'Db_Asistencia', 'db_asistencia'], 'db_asistencia'), 
                        (['DB_HORARIOS', 'Db_Horarios', 'db_horarios', 'Horarios'], 'db_horarios'), 
                        (['DATA_ESTUDIANTES', 'Data_Estudiantes', 'data_estudiantes'], 'data_estudiantes')
                    ]
                    
                    for listas_nombres, t_destino in tablas_mapeo:
                        p_encontrada = None
                        for nombre_posible in listas_nombres:
                            if nombre_posible in pestanas:
                                p_encontrada = nombre_posible
                                break
                        
                        if p_encontrada:
                            try:
                                df_origen = pd.read_excel(xls, p_encontrada)
                                # ⚡ MOTOR TURBO MULTI-BLOQUE ACTIVADO ⚡
                                df_origen.to_sql(t_destino, motor_sql, if_exists='replace', index=False, chunksize=500, method='multi')
                                st.success(f"✅ Tabla [{t_destino}] estructurada e inyectada desde pestaña '{p_encontrada}'.")
                            except Exception as e_tabla:
                                st.error(f"❌ Error en pestaña '{p_encontrada}': {e_tabla}")
                        else:
                            st.warning(f"⚠️ No se encontró ninguna pestaña equivalente para la tabla [{t_destino}].")
                    
                    df_conf_init = pd.DataFrame([{"Periodo": "P1", "Estado": "Abierto"}, {"Periodo": "P2", "Estado": "Abierto"}, {"Periodo": "P3", "Estado": "Abierto"}, {"Periodo": "P4", "Estado": "Abierto"}])
                    df_conf_init.to_sql('configuracion', motor_sql, if_exists='replace', index=False)
                    
                    st.success("🚀 ¡MIGRACIÓN COMPLETADA DE FORMA IMPECABLE! Todos los módulos están sincronizados.")
                    st.balloons()
                except Exception as e:
                    st.error(f"🚨 ERROR GENERAL EN LA INYECCIÓN SQL: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
