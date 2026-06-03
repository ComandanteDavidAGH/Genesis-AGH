import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
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

def renderizar(df, conn):
    # 🚀 ENVOLTORIO EXTERNO PREMIUM PARA LAS TABLAS DE HISTORIAL
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
        padding: 2px !important;
        background-color: #f0f2f6 !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #0d1b2a !important;
        color: #d4af37 !important;
        font-family: 'Arial Black', sans-serif !important;
        font-size: 13px !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Control de Asistencia y Observaciones</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✍️ Registrar Novedad", "🖨️ Generar Observador Oficial"])
    
    with tab1:
        with st.form("form_novedad"):
            st.markdown("<p style='font-weight:bold;'>Registrar Nueva Novedad:</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            lista_alumnos = sorted(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else []
            with col1: alum_sel = st.selectbox("👤 Estudiante:", lista_alumnos)
            with col2: fecha_sel = st.date_input("📅 Fecha:")
            with col3: estado_sel = st.selectbox("🚦 Estado / Tipo:", ["Falla", "Retardo", "Excusa", "Llamado de Atención", "Felicitación"])
            obs_sel = st.text_area("📝 Observaciones o Detalles:")
            submit_btn = st.form_submit_button("💾 GUARDAR REPORTE", type="primary")
            
            if submit_btn and alum_sel:
                grado_alum = df[df['Nombre_Completo'] == alum_sel]['Grado'].iloc[0] if not df[df['Nombre_Completo'] == alum_sel].empty else "N/A"
                nuevo_registro = pd.DataFrame([{'Nombre_Completo': alum_sel, 'GRADO': grado_alum, 'FECHA': fecha_sel.strftime("%Y-%m-%d"), 'ESTADO': estado_sel, 'OBSERVACIONES': obs_sel}])
                
                if st.session_state.df_asistencia is None: st.session_state.df_asistencia = pd.DataFrame()
                st.session_state.df_asistencia = pd.concat([st.session_state.df_asistencia, nuevo_registro], ignore_index=True)
                
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, f"📝 Reporte: {alum_sel}")
                
                # ⚡ ESCRITURA DIRECTA A SUPABASE (SQL)
                try: 
                    st.session_state.df_asistencia.to_sql('db_asistencia', con=conn.engine, if_exists='replace', index=False)
                    st.success(f"✅ Reporte guardado y asegurado en la Bóveda SQL.")
                    st.cache_data.clear() # Limpia caché para lectura fresca
                except Exception as e: 
                    st.error(f"🚨 Falla en el satélite SQL: {e}")
        
        st.markdown("---")
        col_h1, col_h2 = st.columns([7, 3])
        with col_h1:
            st.markdown("<h4 style='color:#000000; font-family:Arial Black;'>Historial de Novedades</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                if st.button("↩️ DESHACER ÚLTIMO REPORTE", help="Elimina el último registro guardado por error"):
                    st.session_state.df_asistencia = st.session_state.df_asistencia.iloc[:-1] 
                    
                    # ⚡ ESCRITURA DIRECTA A SUPABASE (SQL)
                    try: 
                        st.session_state.df_asistencia.to_sql('db_asistencia', con=conn.engine, if_exists='replace', index=False)
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "↩️ Revirtió último reporte")
                        st.cache_data.clear() # Limpia caché
                        st.rerun()
                    except Exception as e: 
                        st.error(f"🚨 Falla en el satélite SQL: {e}")
                        
        if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty: 
            st.dataframe(st.session_state.df_asistencia.iloc[::-1], use_container_width=True, hide_index=True)
        else: 
            st.info("No hay registros disciplinarios almacenados.")

    with tab2:
        st.markdown("<p style='font-weight:bold;'>Seleccione un estudiante para imprimir su hoja de vida disciplinaria:</p>", unsafe_allow_html=True)
        lista_alumnos_obs = sorted(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else []
        if lista_alumnos_obs:
            alumno_obs = st.selectbox("👤 Buscar Estudiante:", lista_alumnos_obs, key="sel_obs")
            
            if st.button("🖨️ PREPARAR OBSERVADOR", type="primary"):
                if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                    df_obs_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_obs]
                    if not df_obs_alum.empty:
                        css_obs = "<style>body { font-family: Arial, sans-serif; background: white; color: black; } .b-print { padding: 30px; border: 2px solid #000; } .table-obs { width: 100%; border-collapse: collapse; margin-top: 15px; } .table-obs th, .table-obs td { border: 1px solid #000; padding: 8px; text-align: left; } .table-obs th { background-color: #f0f0f0; } .firmas-box { display: flex; justify-content: space-between; margin-top: 60px; } .firma-linea { border-top: 1px solid #000; width: 30%; text-align: center; font-weight: bold; font-size: 12px; padding-top: 5px; } @media print { .no-print { display: none !important; } } </style>"
                        
                        html_observador = f"<html><head><script>function imprimirObs() {{ window.print(); }}</script>{css_obs}</head><body><div class='no-print' style='text-align:right; margin-bottom:10px;'><button onclick='imprimirObs()' style='background:#0d1b2a; color:#d4af37; padding:10px; font-weight:bold; cursor:pointer;'>🖨️ IMPRIMIR OBSERVADOR</button></div><div class='b-print'><h2 style='text-align:center; margin:0;'>ACADEMIA GLOBAL HORIZONTE</h2><h4 style='text-align:center; margin:5px 0;'>OBSERVADOR DEL ALUMNO (HOJA DE VIDA)</h4><hr style='border-top:2px solid #000;'><p><b>Estudiante:</b> {alumno_obs} &nbsp;&nbsp;&nbsp; <b>Grado:</b> {df_obs_alum['GRADO'].iloc[0] if 'GRADO' in df_obs_alum.columns else 'N/A'}</p><table class='table-obs'><tr><th>Fecha</th><th>Tipo / Estado</th><th>Observación Detallada</th></tr>"
                        
                        for _, row in df_obs_alum.iterrows():
                            html_observador += f"<tr><td>{row['FECHA']}</td><td><b>{row['ESTADO']}</b></td><td>{row['OBSERVACIONES']}</td></tr>"
                            
                        html_observador += "</table><div class='firmas-box'><div class='firma-linea'>Firma del Estudiante</div><div class='firma-linea'>Firma del Acudiente</div><div class='firma-linea'>Firma del Docente / Coordinador</div></div></div></body></html>"
                        
                        components.html(html_observador, height=600, scrolling=True)
                    else:
                        st.success(f"✅ El estudiante {alumno_obs} tiene una hoja de vida intachable. Cero reportes.")
                else:
                    st.warning("No hay base de datos disciplinaria registrada aún.")
