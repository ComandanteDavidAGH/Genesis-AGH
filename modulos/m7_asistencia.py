import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import base64
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
    # 🚀 ENVOLTORIO EXTERNO PREMIUM PARA LAS TABLAS Y PANELES
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
    .panel-registro {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #0d1b2a;
        border-top: 5px solid #d4af37;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📝 Control de Novedades y Observador</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✍️ Registrar Novedad", "🖨️ Generar Observador Oficial"])
    
    with tab1:
        st.markdown("<div class='panel-registro'>", unsafe_allow_html=True)
        with st.form("form_novedad"):
            st.markdown("<p style='font-family:Arial Black; color:#0d1b2a; margin-top:0;'>NUEVA ENTRADA DISCIPLINARIA / ACADÉMICA:</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            lista_alumnos = sorted(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else []
            
            with col1: alum_sel = st.selectbox("👤 Estudiante:", lista_alumnos)
            with col2: fecha_sel = st.date_input("📅 Fecha de la Incidencia:")
            with col3: estado_sel = st.selectbox("🚦 Gravedad / Tipo:", ["Falla", "Retardo", "Excusa", "Llamado de Atención", "Felicitación", "Suspensión"])
            
            obs_sel = st.text_area("📝 Detalles del Evento (Máxima Precisión):")
            
            # Botón alineado a la derecha
            col_espacio, col_btn = st.columns([7, 3])
            with col_btn:
                submit_btn = st.form_submit_button("💾 ASEGURAR REPORTE", type="primary", use_container_width=True)
            
            if submit_btn and alum_sel:
                grado_alum = df[df['Nombre_Completo'] == alum_sel]['Grado'].iloc[0] if not df[df['Nombre_Completo'] == alum_sel].empty else "N/A"
                nuevo_registro = pd.DataFrame([{'Nombre_Completo': alum_sel, 'GRADO': grado_alum, 'FECHA': fecha_sel.strftime("%Y-%m-%d"), 'ESTADO': estado_sel, 'OBSERVACIONES': obs_sel}])
                
                if st.session_state.df_asistencia is None: st.session_state.df_asistencia = pd.DataFrame()
                st.session_state.df_asistencia = pd.concat([st.session_state.df_asistencia, nuevo_registro], ignore_index=True)
                
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, f"📝 Reporte: {alum_sel} ({estado_sel})")
                
                # ⚡ ESCRITURA DIRECTA A SUPABASE (SQL)
                try: 
                    st.session_state.df_asistencia.to_sql('db_asistencia', con=conn.engine, if_exists='replace', index=False)
                    st.toast(f"✅ Reporte asegurado en la Bóveda SQL.", icon="🛡️")
                    st.cache_data.clear() # Limpia caché
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e: 
                    st.error(f"🚨 Falla en el satélite SQL: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        col_h1, col_h2 = st.columns([7, 3])
        with col_h1:
            st.markdown("<h4 style='color:#000000; font-family:Arial Black;'>📜 Bitácora Histórica Institucional</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                if st.button("↩️ DESHACER ÚLTIMO REPORTE", help="Elimina el último registro guardado por error", use_container_width=True):
                    st.session_state.df_asistencia = st.session_state.df_asistencia.iloc[:-1] 
                    
                    try: 
                        st.session_state.df_asistencia.to_sql('db_asistencia', con=conn.engine, if_exists='replace', index=False)
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "↩️ Revirtió último reporte")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e: 
                        st.error(f"🚨 Falla en el satélite SQL: {e}")
                        
        if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty: 
            # 🎨 MOTOR DE PINTURA PANDAS STYLER
            def color_novedad(val):
                v = str(val).upper()
                if any(p in v for p in ['FALLA', 'RETARDO', 'LLAMADO', 'SUSPENSIÓN']): return 'color: #cc0000; font-weight: bold; background-color: #ffe6e6;'
                elif any(p in v for p in ['FELICITACIÓN', 'EXCELENCIA']): return 'color: #00994c; font-weight: bold; background-color: #e6ffe6;'
                elif 'EXCUSA' in v: return 'color: #cc8800; font-weight: bold; background-color: #fffef0;'
                return 'color: #0d1b2a; font-weight: bold;'
                
            df_historial = st.session_state.df_asistencia.iloc[::-1]
            st.dataframe(df_historial.style.map(color_novedad, subset=['ESTADO']), use_container_width=True, hide_index=True)
        else: 
            st.info("No hay registros disciplinarios almacenados en la bóveda.")

    with tab2:
        st.markdown("<p style='font-weight:bold;'>Seleccione un estudiante para inspeccionar e imprimir su Hoja de Vida:</p>", unsafe_allow_html=True)
        lista_alumnos_obs = sorted(df['Nombre_Completo'].dropna().unique()) if not df.empty and 'Nombre_Completo' in df.columns else []
        
        if lista_alumnos_obs:
            col_busq, col_esp = st.columns([5, 5])
            with col_busq:
                alumno_obs = st.selectbox("👤 Buscar Estudiante:", lista_alumnos_obs, key="sel_obs")
            
            if st.button("🖨️ PREPARAR OBSERVADOR OFICIAL", type="primary"):
                if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                    df_obs_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_obs]
                    if not df_obs_alum.empty:
                        
                        try:
                            with open("logo.png", "rb") as img_file:
                                b64_string = base64.b64encode(img_file.read()).decode()
                                URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
                        except:
                            URL_LOGO_OFICIAL = ""
                            
                        # 👑 ESTILOS VIP PARA EL DOCUMENTO IMPRESO
                        css_obs = """<style>
                            body { font-family: Arial, sans-serif; background: white; color: black; } 
                            .b-print { position: relative; padding: 30px; border: 3px solid #0d1b2a; border-radius: 10px; z-index: 1; } 
                            .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: -1; pointer-events: none; }
                            .table-obs { width: 100%; border-collapse: collapse; margin-top: 20px; } 
                            .table-obs th, .table-obs td { border: 1px solid #000; padding: 10px; text-align: left; font-size: 12px; } 
                            .table-obs th { background-color: #0d1b2a !important; color: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: 'Arial Black'; } 
                            .firmas-box { display: flex; justify-content: space-between; margin-top: 80px; } 
                            .firma-linea { border-top: 1px solid #000; width: 30%; text-align: center; font-weight: bold; font-size: 11px; padding-top: 5px; } 
                            @media print { 
                                .no-print { display: none !important; } 
                                .b-print { border: none !important; padding: 0 !important; }
                            } 
                        </style>"""
                        
                        html_observador = f"""<html><head><script>function imprimirObs() {{ window.print(); }}</script>{css_obs}</head><body>
                        <div class='no-print' style='text-align:right; margin-bottom:15px;'>
                            <button onclick='imprimirObs()' style='background:#0d1b2a; color:#d4af37; padding:10px 20px; font-weight:bold; cursor:pointer; border:2px solid #d4af37; border-radius:5px;'>🖨️ IMPRIMIR DOCUMENTO</button>
                        </div>
                        <div class='b-print'>
                            <img src="{URL_LOGO_OFICIAL}" class="watermark">
                            <table style="width:100%; border:none; margin-bottom:20px;">
                                <tr>
                                    <td style="width:15%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                                    <td style="text-align:center;">
                                        <h2 style='margin:0; color:#0d1b2a; font-family:Arial Black;'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                                        <h4 style='margin:5px 0; color:#d4af37; font-family:Arial Black;'>OBSERVADOR DEL ALUMNO (HOJA DE VIDA)</h4>
                                    </td>
                                    <td style="width:15%;"></td>
                                </tr>
                            </table>
                            <div style="border: 2px solid #000; padding: 10px; background-color: #f8f9fa;">
                                <b>ESTUDIANTE:</b> {alumno_obs} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>GRADO ACTUAL:</b> {df_obs_alum['GRADO'].iloc[0] if 'GRADO' in df_obs_alum.columns else 'N/A'}
                            </div>
                            <table class='table-obs'>
                                <tr><th style="width:15%;">FECHA</th><th style="width:20%;">TIPO DE NOVEDAD</th><th>OBSERVACIÓN DETALLADA</th></tr>"""
                        
                        for _, row in df_obs_alum.iterrows():
                            # Se pone en negrilla el estado para resaltar
                            html_observador += f"<tr><td>{row['FECHA']}</td><td><b>{row['ESTADO']}</b></td><td>{row['OBSERVACIONES']}</td></tr>"
                            
                        html_observador += """</table>
                            <div class='firmas-box'>
                                <div class='firma-linea'>Firma del Estudiante</div>
                                <div class='firma-linea'>Firma del Acudiente</div>
                                <div class='firma-linea'>Sello de Coordinación</div>
                            </div>
                        </div></body></html>"""
                        
                        components.html(html_observador, height=800, scrolling=True)
                    else:
                        st.success(f"✅ El estudiante {alumno_obs} tiene una hoja de vida intachable. Cero reportes registrados.")
                else:
                    st.warning("No hay base de datos disciplinaria registrada aún.")
