import streamlit as st
import pandas as pd
import unicodedata

def limpiar_texto(txt):
    """ Estandariza cadenas para realizar cruces perfectos entre Notas y Logros """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 👑 INYECTOR DE REGLAS PREMIUM Y VISTA DE IMPRESIÓN OFICIAL
    st.markdown("""
        <style>
            @media print {
                header, [data-testid="stSidebar"], [data-testid="stHeader"], 
                .stRadio, .stSelectbox, .no-print, .stButton, div.block-container button,
                div[data-testid="stVerticalBlock"] > div.no-print, .trampa-box {
                    display: none !important;
                }
                .main .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }
                .boletin-insignia-box { border: none !important; box-shadow: none !important; margin: 0px !important; padding: 0px !important; width: 100% !important; }
            }
            .barra-comandos { display: flex; gap: 15px; margin-top: 5px; margin-bottom: 25px; }
            .btn-premium-print {
                background-color: #0d1b2a; color: white !important; font-family: 'Arial Black', sans-serif; font-size: 13px;
                padding: 10px 22px; border: 2px solid #d4af37; border-radius: 6px; cursor: pointer; text-decoration: none;
                box-shadow: 3px 3px 0px #0d1b2a; font-weight: bold;
            }
            .btn-premium-print:hover { background-color: #1e3551; box-shadow: 3px 3px 0px #d4af37; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📜 Expedición de Boletines Oficiales</h3>", unsafe_allow_html=True)
    
    # 🔄 RECEPTOR DINÁMICO DE ARGUMENTOS
    df_notas = None
    periodo_sidebar = "P1"
    conn_sql = None

    if len(args) >= 1: df_notas = args[0] if isinstance(args[0], pd.DataFrame) else None
    if len(args) >= 3: conn_sql = args[2]

    # Interceptar el selector de periodo global de la barra lateral izquierda
    for key in st.session_state.keys():
        if "PERIOD" in key.upper() or key.lower() == "periodo":
            periodo_sidebar = str(st.session_state[key]).upper().strip()
            break

    # Enlace de contingencia a Supabase
    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    # Enlace de logros
    df_logros = pd.DataFrame()
    if conn_sql is not None:
        try: df_logros = conn_sql.query("SELECT * FROM db_logros;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    # Estandarización absoluta de columnas de calificaciones
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    # 🪤 LA TRAMPA DE INSPECCIÓN SOLICITADA (Visible solo en pantalla para auditoría técnica)
    with st.expander("🪤 TRAMPA DE DETECCIÓN: ADN DE CALIFICACIONES", expanded=True):
        st.markdown("**Análisis de variables en tiempo real:**")
        st.write("⏱️ *Periodo detectado en la barra lateral:*", periodo_sidebar)
        st.write("📋 *Columnas reales de su archivo de notas:*", list(df_trabajo.columns))
        st.markdown("*Muestra de datos (Primeras 2 filas):*")
        st.dataframe(df_trabajo.head(2))

    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    col_materia = next((c for c in df_trabajo.columns if c in ['MATERIA', 'ASIGNATURA']), None)

    # Detectamos si estamos en modo Consolidado Final
    es_consolidado = "CONSOLID" in periodo_sidebar or "FINAL" in periodo_sidebar or "TODO" in periodo_sidebar

    # ⚡ CASILLAS PEQUEÑAS HORIZONTALES (Una al lado de la otra)
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_grad, c_est = st.columns([1.2, 1.8, 2.5])
    
    with c_modo:
        modo = st.radio("Generación:", ["👤 Individual", "📦 Masivo"], horizontal=False)
    
    if col_grado:
        lista_grados = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
        with c_grad:
            grado_sel = st.selectbox("📂 Seleccione el Grado:", lista_grados)
        df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    if modo == "👤 Individual":
        lista_estudiantes = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            estudiante_sel = st.selectbox("👤 Seleccione el Estudiante:", lista_estudiantes)
        df_alumnos = [estudiante_sel]
    else:
        df_alumnos = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            st.markdown(f"<p style='margin-top:28px; font-weight:bold; color:#0d1b2a;'>📦 Lote Masivo de {len(df_alumnos)} Alumnos</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Preparación de logros
    if not df_logros.empty:
        df_logros.columns = [str(c).upper().strip() for c in df_logros.columns]
        col_log_mat = next((c for c in df_logros.columns if c in ['MATERIA', 'ASIGNATURA']), None)
        col_log_txt = next((c for c in df_logros.columns if c in ['LOGRO', 'DESCRIPCION', 'TEXTO']), None)
        if col_log_mat and col_log_txt:
            df_logros['MAT_CLEAN'] = df_logros[col_log_mat].apply(limpiar_texto)

    # Renderizado de Boletines
    for estudiante in df_alumnos:
        df_est = df_trabajo[df_trabajo[col_nombre] == estudiante].copy()
        if df_est.empty: continue
        
        grado_est = df_est[col_grado].iloc[0] if col_grado in df_est.columns else "N/A"

        # Barra de botones de impresión
        if modo == "👤 Individual":
            st.markdown(f"""
                <div class="barra-comandos no-print">
                    <button class="btn-premium-print" onclick="window.print();">🖨️ IMPRIMIR INFORME ACADÉMICO</button>
                    <button class="btn-premium-print" onclick="window.print();" style="background-color:#cc8800;">📥 GUARDAR COMO PDF</button>
                </div>
            """, unsafe_allow_html=True)

        # 👑 CABECERA DEL INFORME CON ESCUDO HERÁLDICO HTML MAJESTUOSO COMPLETO
        escudo_html = """
        <div style="width:75px; height:85px; background-color:#0d1b2a; border:3px solid #d4af37; border-radius:10px 10px 50px 50px; box-shadow: 3px 3px 0px #0d1b2a; display:flex; align-items:center; justify-content:center; text-align:center; box-sizing:border-box;">
            <div style="font-family:'Arial Black', sans-serif; font-size:10px; font-weight:900; color:#ffffff; line-height:1.1; padding:2px;">P.E.G.O.<br><span style="color:#d4af37; font-size:8px;">2026</span></div>
        </div>
        """

        # Cálculo de Promedio General Dinámico
        columnas_periodos = [c for c in ['P1', 'P2', 'P3', 'P4'] if c in df_est.columns]
        if not columnas_periodos:
            columnas_periodos = [c for c in df_est.columns if c not in [col_nombre, col_grado, col_materia]]
        
        for cp in columnas_periodos:
            df_est[cp] = pd.to_numeric(df_est[cp], errors='coerce').fillna(0.0)
            
        df_est['FINAL_CALC'] = df_est[columnas_periodos].mean(axis=1)
        promedio_institucional = df_est['FINAL_CALC'].mean()

        # Renderizado de Cabecera del Boletín
        html_boletin = f"""
        <div class="boletin-insignia-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:30px; margin-top:10px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.08);">
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="width:15%; text-align:left; vertical-align:middle;">{escudo_html}</td>
                    <td style="width:65%; text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black'; font-size:20px; letter-spacing:0.5px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <h4 style="margin:6px 0 0 0; color:#cc8800; font-family:'Arial'; font-weight:bold; font-size:13px; text-transform:uppercase; letter-spacing:1px;">INFORME ACADÉMICO OFICIAL: {periodo_visual.upper()}</h4>
                    </td>
                    <td style="width:20%; text-align:right; vertical-align:middle;">
                        <div style="border:3px solid #0d1b2a; border-radius:8px; padding:6px 12px; background-color:#f8f9fa; text-align:center; display:inline-block; min-width:110px; box-shadow: 3px 3px 0px #0d1b2a;">
                            <div style="font-size:10px; font-family:'Arial Black'; color:#0d1b2a; text-transform:uppercase;">PROMEDIO</div>
                            <div style="font-size:24px; font-family:'Arial Black'; color:#cc8800; font-weight:900; margin-top:1px;">{promedio_institucional:.1f}</div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px; border:3px solid #0d1b2a; background-color:#f8f9fa; box-shadow: 2px 2px 0px #0d1b2a;">
                <tr>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:12px; color:#0d1b2a; width:15%;">ESTUDIANTE:</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:13px; color:#000000; width:55%;">{estudiante}</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:12px; color:#0d1b2a; width:12%;">GRADO:</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:13px; color:#000000; width:18%; text-align:center;">{grado_est}</td>
                </tr>
            </table>
        """

        # 👑 CONFIGURACIÓN DINÁMICA DE COLUMNAS MATRICIALES (4 PERIODOS EN PARALELO)
        if es_consolidado:
            html_boletin += """
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif; border: 2px solid #0d1b2a;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a; text-align:center;">
                        <th style="padding:10px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black'; font-size:12px;">MATERIA</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:8%;">P1</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:8%;">P2</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:8%;">P3</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:8%;">P4</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:10%;">DEF</th>
                        <th style="padding:10px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:12px; width:18%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
            """
        else:
            html_boletin += f"""
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif; border: 2px solid #0d1b2a;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a;">
                        <th style="padding:12px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black'; font-size:12px;">MATERIA</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:18%;">NOTA {periodo_sidebar}</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:25%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
            """

        # Inyección de filas de materias y logros
        for _, fila in df_est.iterrows():
            materia_nom = str(fila[col_materia]).strip()
            
            # Buscar logro
            logro_render = "No se ha registrado descriptor de logro para esta asignatura en la base de datos."
            if not df_logros.empty:
                match_logro = df_logros[df_logros['MAT_CLEAN'] == limpiar_texto(materia_nom)]
                if not match_logro.empty:
                    logro_render = str(match_logro[df_logros.columns[2]].iloc[0]).strip()

            if es_consolidado:
                # Extraemos las notas de cada uno de los 4 periodos de forma segura
                n_p1 = float(fila['P1']) if 'P1' in df_est.columns else 0.0
                n_p2 = float(fila['P2']) if 'P2' in df_est.columns else 0.0
                n_p3 = float(fila['P3']) if 'P3' in df_est.columns else 0.0
                n_p4 = float(fila['P4']) if 'P4' in df_est.columns else 0.0
                n_def = float(fila['FINAL_CALC'])

                if n_def >= 9.0: des_txt = "SUPERIOR"
                elif n_def >= 7.6: des_txt = "ALTO"
                elif n_def >= 6.0: des_txt = "BÁSICO"
                else: des_txt = "BAJO"

                color_def = "#cc0000" if n_def < 6.0 else "#000000"
                color_des = "#cc0000" if n_def < 6.0 else ("#00994c" if n_def >= 7.6 else "#cc8800")

                html_boletin += f"""
                    <tr style="text-align:center; background-color:#ffffff; font-size:13px;">
                        <td style="padding:8px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0; text-align:left;">{materia_nom}</td>
                        <td style="padding:8px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p1 < 6.0 else '#000000'}">{n_p1:.1f}</td>
                        <td style="padding:8px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p2 < 6.0 else '#000000'}">{n_p2:.1f}</td>
                        <td style="padding:8px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p3 < 6.0 else '#000000'}">{n_p3:.1f}</td>
                        <td style="padding:8px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p4 < 6.0 else '#000000'}">{n_p4:.1f}</td>
                        <td style="padding:8px; font-family:'Arial Black'; font-weight:900; border-right:1px solid #e0e0e0; color:{color_def}">{n_def:.1f}</td>
                        <td style="padding:8px; font-family:'Arial Black'; font-weight:bold; border-right:1px solid #0d1b2a; color:{color_des}">{des_txt}</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td colspan="7" style="padding:5px 12px 8px 12px; font-style:italic; font-size:11px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; background-color:#fafafa;">
                            <strong style="color:#cc8800;">LOGRO:</strong> {logro_render}
                        </td>
                    </tr>
                """
            else:
                nota_val = float(fila[col_p])
                if nota_val >= 9.0: des_txt = "SUPERIOR"
                elif nota_val >= 7.6: des_txt = "ALTO"
                elif nota_val >= 6.0: des_txt = "BÁSICO"
                else: des_txt = "BAJO"

                color_nota = "#cc0000" if nota_val < 6.0 else "#000000"
                color_des = "#cc0000" if nota_val < 6.0 else ("#00994c" if nota_val >= 7.6 else "#cc8800")

                html_boletin += f"""
                    <tr style="background-color:#ffffff;">
                        <td style="padding:10px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0; font-size:13px;">{materia_nom}</td>
                        <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:900; color:{color_nota}; border-right:1px solid #e0e0e0; font-size:14px;">{nota_val:.1f}</td>
                        <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:bold; color:{color_des}; border-right:1px solid #0d1b2a; font-size:12px;">{des_txt}</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td colspan="3" style="padding:5px 12px 8px 12px; font-style:italic; font-size:11px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; background-color:#fafafa;">
                            <strong style="color:#cc8800;">LOGRO:</strong> {logro_render}
                        </td>
                    </tr>
                """

        html_boletin += """
                </tbody>
            </table>
            
            <div style="margin-top:55px; display:flex; justify-content:space-between; padding:0 40px;" class="page-break-avoid">
                <div style="text-align:center; width:40%;">
                    <div style="border-bottom:2px solid #0d1b2a; width:100%; height:35px;"></div>
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase;">RECTORÍA INSTITUCIONAL</div>
                </div>
                <div style="text-align:center; width:40%;">
                    <div style="border-bottom:2px solid #0d1b2a; width:100%; height:35px;"></div>
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase;">COORDINACIÓN ACADÉMICA</div>
                </div>
            </div>
        </div>
        <br class="no-print"><hr style="border:1px dashed #b0b0b0;" class="no-print"><br class="no-print">
        """
        st.html(html_boletin)
