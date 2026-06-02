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
    
    st.markdown("<br>", unsafe_allow_html=True)
    if eficiencia_interna < 80:
        st.warning(f"⚠️ Alerta de Rectoría: El {porcentaje_riesgo:.1f}% de la población estudiantil presenta riesgo de reprobación.")

    st.markdown("---")
    st.subheader("🔐 Gestión de Seguridad de Periodos")
    st.info("Desde aquí puede cerrar los periodos para que ningún docente pueda modificar notas.")
    
    try:
        df_config = conn.read(worksheet="Configuracion", ttl=0)
        col_1, col_2 = st.columns(2)
        nuevos_estados = []

        for i, fila in df_config.iterrows():
            with col_1 if i < 2 else col_2:
                bloqueado = st.toggle(f"Cerrar {fila['Periodo']}", value=(fila['Estado'] == "Cerrado"))
                nuevos_estados.append("Cerrado" if bloqueado else "Abierto")

        if st.button("🔴 APLICAR BLOQUEO / APERTURA GENERAL", type="primary"):
            with st.spinner("🚀 Transmitiendo órdenes de seguridad al satélite..."):
                try:
                    df_config['Estado'] = nuevos_estados
                    conn.update(worksheet="Configuracion", data=df_config)
                    st.success("✅ Protocolo actualizado. Los periodos han sido configurados.")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🔐 Modificó la seguridad de los periodos")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 FALLA DE CONEXIÓN AL SATÉLITE: {e}")
    except Exception as e:
        st.error(f"❌ Error al leer la pestaña 'Configuracion'. Verifique el Excel. Error: {e}")

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
    
    st.info("Comandante, aquí puede descargar todo el trabajo. Es su copia de seguridad física.")
    st.download_button(label="📥 DESCARGAR BASE DE DATOS ACTUALIZADA (EXCEL)", data=buffer.getvalue(), file_name=f"Backup_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.ms-excel", type="primary", use_container_width=True)
    st.markdown("---")

    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>🇨🇴 Módulo de Exportación SIMAT (MEN)</h4>", unsafe_allow_html=True)
    st.write("Genera la plantilla estructurada con los estudiantes activos para reportar al Ministerio de Educación Nacional.")
    
    df_m = st.session_state.df_maestro
    if df_m is not None and not df_m.empty and 'Nombre_Completo' in df_m.columns:
        columnas_simat = [c for c in ['ID_Est', 'Nombre_Completo', 'Grado'] if c in df_m.columns]
        df_simat = df_m[columnas_simat].drop_duplicates().copy()
        df_simat['ESTADO_MATRICULA'] = "MATRICULADO"
        df_simat['FECHA_REPORTE'] = datetime.now(zona_colombia).strftime("%Y-%m-%d")
        
        buffer_simat = io.BytesIO()
        with pd.ExcelWriter(buffer_simat, engine='xlsxwriter') as writer:
            guardar_como_tabla(df_simat, writer, 'REPORTE_SIMAT')
            
        st.download_button(label="📄 DESCARGAR PLANTILLA SIMAT OFICIAL", data=buffer_simat.getvalue(), file_name=f"SIMAT_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d')}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
    else:
        st.warning("No hay datos de estudiantes para generar el SIMAT.")
    
    st.markdown("---")
    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>Registro Histórico de Usuarios</h4>", unsafe_allow_html=True)
    if st.session_state.bitacora: st.dataframe(pd.DataFrame(st.session_state.bitacora).iloc[::-1].reset_index(drop=True), use_container_width=True)
