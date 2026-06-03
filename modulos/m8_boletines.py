import streamlit as st
import pandas as pd
import unicodedata

def limpiar_texto(txt):
    """ Estandariza cadenas para realizar cruces perfectos entre Notas y Logros """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 👑 INYECTOR DE ESTILOS PREMIUM: Réplica exacta del Boletín Insignia y ocultamiento de controles
    st.markdown("""
        <style>
            @media print {
                header, [data-testid="stSidebar"], [data-testid="stHeader"], 
                .stRadio, .stSelectbox, .no-print, .stButton, div.block-container button,
                div[data-testid="stVerticalBlock"] > div.no-print {
                    display: none !important;
                }
                .main .block-container {
                    padding-top: 0px !important;
                    padding-bottom: 0px !important;
                }
                .boletin-insignia-box {
                    border: none !important;
                    box-shadow: none !important;
                    margin: 0px !important;
                    padding: 0px !important;
                    width: 100% !important;
                }
            }
            
            .barra-comandos {
                display: flex;
                gap: 15px;
                margin-top: -10px;
                margin-bottom: 25px;
            }
            
            .btn-premium-print {
                background-color: #0d1b2a;
                color: white !important;
                font-family: 'Arial Black', sans-serif;
                font-size: 13px;
                padding: 10px 22px;
                border: 2px solid #d4af37;
                border-radius: 6px;
                cursor: pointer;
                text-decoration: none;
                box-shadow: 3px 3px 0px #0d1b2a;
                font-weight: bold;
            }
            .btn-premium-print:hover {
                background-color: #1e3551;
                box-shadow: 3px 3px 0px #d4af37;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📜 Expedición de Boletines Oficiales</h3>", unsafe_allow_html=True)
    
    # 🔄 TRACKER DE SINCRONIZACIÓN: Detectar periodo desde los argumentos de app.py o desde la barra lateral global
    df_notas = None
    periodo_sel = "P1"
    conn_sql = None

    if len(args) >= 1: df_notas = args[0] if isinstance(args[0], pd.DataFrame) else None
    if len(args) >= 2 and args[1]: periodo_sel = str(args[1]).upper().strip()
    if len(args) >= 3: conn_sql = args[2]

    # Escudo de acople para interceptar el selector de periodo de la barra lateral izquierda de Streamlit
    for key in st.session_state.keys():
        if "PERIOD" in key.upper() or key.lower() == "periodo":
            periodo_sel = str(st.session_state[key]).upper().strip()
            break

    # Ajuste de nombre visual para periodos consolidados
    periodo_visual = "CONSOLIDADO FINAL" if "CONSOLID" in periodo_sel or "TODO" in periodo_sel else f"PERIODO {periodo_sel}"

    # Enlace de contingencia a la base satelital
    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    # Enlace de la tabla de logros
    df_logros = pd.DataFrame()
    if conn_sql is not None:
        try: df_logros = conn_sql.query("SELECT * FROM db_logros;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    # Estandarización de las columnas de calificaciones
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    col_materia = next((c for c in df_trabajo.columns if c in ['MATERIA', 'ASIGNATURA']), None)
    
    # Mapeo dinámico de la columna de notas alineada con el filtro lateral
    col_p = None
    if periodo_sel in df_trabajo.columns:
        col_p = periodo_sel
    else:
        for c in df_trabajo.columns:
            if limpiar_texto(c) == limpiar_texto(periodo_sel):
                col_p = c
                break
    if not col_p:
        col_p = next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'DEF', 'NOTA', 'P1', 'P2', 'P3', 'P4']), df_trabajo.columns[-1])

    # ⚡ OPERACIÓN REJILLA HORIZONTAL: Ajuste de filtros pequeños uno al lado del otro
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
            st.markdown("<p style='margin-top:28px; font-weight:bold; color:#0d1b2a;'>📦 Lote Masivo Activo</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Preparación de la matriz de logros si existe
    if not df_logros.empty:
        df_logros.columns = [str(c).upper().strip() for c in df_logros.columns]
        col_log_mat = next((c for c in df_logros.columns if c in ['MATERIA', 'ASIGNATURA']), None)
        col_log_grad = next((c for c in df_logros.columns if c in ['GRADO', 'CURSO']), None)
        col_log_txt = next((c for c in df_logros.columns if c in ['LOGRO', 'DESCRIPCION', 'TEXTO']), None)
        
        if col_log_mat and col_log_txt:
            df_logros['MAT_CLEAN'] = df_logros[col_log_mat].apply(limpiar_texto)
            if col_log_grad:
                df_logros['GRAD_CLEAN'] = df_logros[col_log_grad].astype(str).str.strip()

    # Despliegue en cadena de los Boletines Insignias
    for estudiante in df_alumnos:
        df_est = df_trabajo[df_trabajo[col_nombre] == estudiante].copy()
        if df_est.empty: continue
        
        df_est[col_p] = pd.to_numeric(df_est[col_p], errors='coerce').fillna(0.0)
        promedio_general = df_est[col_p].mean()
        grado_est = df_est[col_grado].iloc[0] if col_grado in df_est.columns else "N/A"

        # Barra de botones ejecutivos de impresión
        if modo == "👤 Individual":
            st.markdown(f"""
                <div class="barra-comandos no-print">
                    <button class="btn-premium-print" onclick="window.print();">🖨️ IMPRIMIR INFORME ACADÉMICO</button>
                    <button class="btn-premium-print" onclick="window.print();" style="background-color:#cc8800;">📥 GUARDAR COMO PDF</button>
                </div>
            """, unsafe_allow_html=True)

        # 👑 RÉPLICA IDÉNTICA DE SU BOLETÍN INSIGNIA CON ESCUDO VECTORIAL EMBEBIDO
        html_boletin = f"""
        <div class="boletin-insignia-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:30px; margin-top:10px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.08);">
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="width:15%; text-align:left; vertical-align:middle;">
                        <svg width="85" height="85" viewBox="0 0 100 100" style="display:block;">
                            <path d="M50,5 L90,25 L90,65 C90,80 50,95 50,95 C50,95 10,80 10,65 L10,25 Z" fill="#0d1b2a" stroke="#d4af37" stroke-width="3"/>
                            <path d="M50,12 L82,28 L82,62 C82,74 50,86 50,86 C50,86 18,74 18,62 L18,28 Z" fill="none" stroke="#d4af37" stroke-width="1.5" stroke-dasharray="3,3"/>
                            <polygon points="50,25 54,37 67,37 57,45 60,57 50,50 40,57 43,45 33,37 46,37" fill="#d4af37"/>
                            <path d="M30,65 Q50,55 70,65" fill="none" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
                            <text x="50" y="77" font-family="'Arial Black', sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle">PEGO</text>
                        </svg>
                    </td>
                    <td style="width:65%; text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black'; font-size:21px; letter-spacing:0.5px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <h4 style="margin:6px 0 0 0; color:#cc8800; font-family:'Arial'; font-weight:bold; font-size:13px; text-transform:uppercase; letter-spacing:1px;">INFORME ACADÉMICO OFICIAL: {periodo_visual}</h4>
                    </td>
                    <td style="width:20%; text-align:right; vertical-align:middle;">
                        <div style="border:3px solid #0d1b2a; border-radius:8px; padding:6px 12px; background-color:#f8f9fa; text-align:center; display:inline-block; min-width:110px; box-shadow: 3px 3px 0px #0d1b2a;">
                            <div style="font-size:10px; font-family:'Arial Black'; color:#0d1b2a; letter-spacing:0.5px; text-transform:uppercase;">PROMEDIO</div>
                            <div style="font-size:24px; font-family:'Arial Black'; color:#cc8800; font-weight:900; margin-top:1px;">{promedio_general:.1f}</div>
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
            
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif; border: 2px solid #0d1b2a;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a;">
                        <th style="padding:12px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black'; font-size:12px;">MATERIA</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:15%;">{periodo_sel}</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:25%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, fila in df_est.iterrows():
            materia_nom = str(fila[col_materia]).strip()
            nota_val = float(fila[col_p])
            
            # Clasificación de Desempeños Institucionales
            if nota_val >= 9.0: des_txt = "SUPERIOR"
            elif nota_val >= 7.6: des_txt = "ALTO"
            elif nota_val >= 6.0: des_txt = "BÁSICO"
            else: des_txt = "BAJO"
            
            color_nota = "#cc0000" if nota_val < 6.0 else "#000000"
            color_des = "#cc0000" if nota_val < 6.0 else ("#00994c" if nota_val >= 7.6 else "#cc8800")
            
            # Búsqueda automatizada del Logro en la base de datos SQL
            logro_render = "No se ha registrado descriptor de logro para esta asignatura en la base de datos satelital."
            if not df_logros.empty:
                mat_clean = limpiar_texto(materia_nom)
                grad_clean = str(grado_est).strip()
                
                condicion = (df_logros['MAT_CLEAN'] == mat_clean)
                if 'GRAD_CLEAN' in df_logros.columns:
                    condicion = condicion & (df_logros['GRAD_CLEAN'] == grad_clean)
                    
                match_logro = df_logros[condicion]
                if not match_logro.empty:
                    logro_render = str(match_logro[col_log_txt].iloc[0]).strip()

            # 📅 FILA 1: Datos Métricos de la Materia
            html_boletin += f"""
                <tr style="background-color:#ffffff;">
                    <td style="padding:10px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0; font-size:13px; padding-bottom:4px;">{materia_nom}</td>
                    <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:900; color:{color_nota}; border-right:1px solid #e0e0e0; font-size:14px; padding-bottom:4px;">{nota_val:.1f}</td>
                    <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:bold; color:{color_des}; border-right:1px solid #0d1b2a; font-size:12px; padding-bottom:4px;">{des_txt}</td>
                </tr>
                <tr style="background-color:#ffffff;">
                    <td colspan="3" style="padding:6px 12px 10px 12px; font-style:italic; font-size:11.5px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; line-height:1.3; background-color:#fafafa;">
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
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase; letter-spacing:0.5px;">RECTORÍA INSTITUCIONAL</div>
                </div>
                <div style="text-align:center; width:40%;">
                    <div style="border-bottom:2px solid #0d1b2a; width:100%; height:35px;"></div>
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase; letter-spacing:0.5px;">COORDINACIÓN ACADÉMICA</div>
                </div>
            </div>
            
        </div>
        <br class="no-print">
        <hr style="border:1px dashed #b0b0b0;" class="no-print">
        <br class="no-print">
        """
        st.html(html_boletin)
