import streamlit as st
import pandas as pd
import unicodedata

def limpiar_texto(txt):
    """ Estandariza cadenas para realizar cruces perfectos entre Notas y Logros """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 👑 INYECTOR DE ESTILOS PREMIUM: Réplica exacta del Boletín Insignia
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
    
    # 🔄 DETECTOR AUTOMÁTICO DE MEMORIA (Escanea y separa Periodo, Grado y Base de datos)
    df_notas = None
    periodo_sel = "P1"
    conn_sql = None

    # 1. Escanear argumentos posicionales enviados por app.py
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            df_notas = arg
        elif hasattr(arg, 'query'):
            conn_sql = arg
        elif isinstance(arg, str):
            arg_clean = arg.upper().strip()
            if any(p in arg_clean for p in ["P1", "P2", "P3", "P4", "CONSOLIDADO", "FINAL"]):
                periodo_sel = arg_clean

    # 2. Escanear la memoria de sesión lateral global de Streamlit para sincronización en tiempo real
    for key in st.session_state.keys():
        val_str = str(st.session_state[key]).upper().strip()
        if any(p in val_str for p in ["P1", "P2", "P3", "P4", "CONSOLIDADO", "FINAL"]):
            periodo_sel = val_str

    # Ajuste de nombre visual para periodos consolidados
    periodo_visual = "CONSOLIDADO FINAL" if "CONSOLID" in periodo_sel or "FINAL" in periodo_sel else f"PERIODO {periodo_sel}"

    # Enlace de contingencia a Supabase
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
    
    # Mapeo dinámico e inteligente de la columna de notas real
    col_p = None
    p_buscar = "CONSOLIDADO" if "CONSOLID" in periodo_sel else periodo_sel
    for c in df_trabajo.columns:
        if p_buscar in limpiar_texto(c):
            col_p = c
            break
    if not col_p:
        col_p = next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'DEF', 'NOTA', 'P1', 'P2', 'P3', 'P4']), df_trabajo.columns[-1])

    # ⚡ DISEÑO DE CASILLAS PEQUEÑAS HORIZONTALES (Uno al lado de la otra)
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
            st.markdown(f"<p style='margin-top:28px; font-weight:bold; color:#0d1b2a;'>📦 Lote de {len(df_alumnos)} Boletines Activo</p>", unsafe_allow_html=True)
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

        # 👑 MAQUETACIÓN OFICIAL CON EL ESCUDO EMBEBIDO GARANTIZADO
        html_boletin = f"""
        <div class="boletin-insignia-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:30px; margin-top:10px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.08);">
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="width:15%; text-align:left; vertical-align:middle;">
                        <div style="width:80px; height:80px; background-color:#0d1b2a; border:3px solid #d4af37; border-radius:50%; box-shadow: 3px 3px 0px #0d1b2a; display:flex; align-items:center; justify-content:center; text-align:center;">
                            <div style="font-family:'Arial Black', sans-serif; font-size:12px; font-weight:900; color:#ffffff; letter-spacing:0.5px; line-height:1.1; padding:5px;">P.E.G.O.<br><span style="color:#d4af37; font-size:9px;">2026</span></div>
                        </div>
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
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:18%;">{periodo_visual}</th>
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
