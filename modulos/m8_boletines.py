import streamlit as st
import pandas as pd
import unicodedata
import base64
import os

def limpiar_texto(txt):
    """ Estandariza cadenas para realizar cruces perfectos """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def obtener_desempeno_dinamico(nota):
    """ Calcula el desempeño institucional en tiempo real """
    try:
        val = float(nota)
        if val >= 9.0: return "SUPERIOR"
        elif val >= 7.6: return "ALTO"
        elif val >= 6.0: return "BÁSICO"
        else: return "BAJO"
    except Exception:
        return "BÁSICO"

def renderizar(*args, **kwargs):
    # 🛡️ EXTRACTOR DEL LOGO REAL DE LA APLICACIÓN (Conversión Base64)
    logo_base64 = ""
    if os.path.exists("logo.png"):
        try:
            with open("logo.png", "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode()
        except Exception:
            pass

    if logo_base64:
        escudo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width:75px; height:auto; filter: drop-shadow(1px 1px 3px rgba(0,0,0,0.15));">'
    else:
        escudo_html = '<div style="width:70px; height:70px; background-color:#0d1b2a; border:2px solid #d4af37; border-radius:50%;"></div>'

    # 👑 ESCUDO DE PRESIÓN RECTÓRICO: Ocultamiento absoluto de Streamlit y app.py
    st.markdown("""
        <style>
            @media print {
                /* 1. PULVERIZAR ABSOLUTAMENTE TODO ELEMENTO EXTERNO FUERA DEL BOLETÍN */
                header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], h3,
                .no-print, .stButton, div.block-container button, div.row-widget, .stSelectbox,
                iframe, .stMarkdown {
                    display: none !important;
                }
                
                /* 2. Ocultar todos los bloques sueltos de Streamlit (Títulos de app.py y espaciadores) */
                div.element-container, div[data-testid="stVerticalBlock"] > div {
                    display: none !important;
                }
                
                /* 3. Forzar que solo el contenedor del boletín insignia se mantenga visible y activo */
                div:has(> .boletin-insignia-box), .boletin-insignia-box, .boletin-insignia-box * {
                    display: block !important;
                    visibility: visible !important;
                }
                
                /* Re-renderizar las tablas en su formato nativo estructurado */
                .boletin-insignia-box table { display: table !important; width: 100% !important; margin-bottom: 8px !important; }
                .boletin-insignia-box tr { display: table-row !important; }
                .boletin-insignia-box th { display: table-cell !important; padding: 4px !important; font-size: 10.5px !important; background-color: #0d1b2a !important; color: white !important; }
                .boletin-insignia-box td { display: table-cell !important; padding: 3px 6px !important; font-size: 10px !important; line-height: 1.1 !important; }
                
                /* 4. PURGA DE MARCAS DE AGUA Y FONDOS PARÁSITOS DE LA RAM */
                body, .main, .block-container, div[data-testid="stAppViewContainer"] {
                    background-image: none !important;
                    background-color: #ffffff !important;
                    padding: 0px !important;
                    margin: 0px !important;
                    top: 0px !important;
                }
                
                /* 5. FIJACIÓN EN EL PUNTO CERO DEL PAPEL CARTA */
                .boletin-insignia-box {
                    position: absolute !important;
                    left: 0px !important;
                    top: 0px !important;
                    border: 3px solid #0d1b2a !important;
                    box-shadow: none !important;
                    margin: 0px auto !important;
                    padding: 20px !important;
                    width: 100% !important;
                    box-sizing: border-box !important;
                    page-break-inside: avoid !important;
                    page-break-after: avoid !important;
                }
                
                .boletin-insignia-box .logro-row-box { padding: 4px 10px 5px 10px !important; font-size: 9.5px !important; line-height: 1.2 !important; }
                .boletin-insignia-box .seccion-firmas { margin-top: 25px !important; display: flex !important; justify-content: space-between !important; }
                .boletin-insignia-box .seccion-firmas > div { display: block !important; width: 38% !important; }

                @page {
                    size: letter portrait;
                    margin: 0.4in !important;
                }
            }
            
            /* Estilización de los botones nativos en pantalla */
            div.stButton > button {
                background-color: #0d1b2a !important;
                color: white !important;
                font-family: 'Arial Black', sans-serif !important;
                font-size: 13px !important;
                font-weight: bold !important;
                border: 2px solid #d4af37 !important;
                border-radius: 6px !important;
                box-shadow: 3px 3px 0px #0d1b2a !important;
                transition: all 0.15s ease !important;
                height: 42px !important;
            }
            div.stButton > button:hover {
                background-color: #1e3551 !important;
                box-shadow: 3px 3px 0px #d4af37 !important;
                transform: translate(-1px, -1px) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 class='no-print' style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📜 Expedición de Boletines Oficiales</h3>", unsafe_allow_html=True)
    
    # 🔄 RECEPTOR EXCLUSIVO DE CALIFICACIONES
    df_notas = args[0] if len(args) >= 1 and isinstance(args[0], pd.DataFrame) else None
    conn_sql = args[2] if len(args) >= 3 else None

    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    col_nombre = "NOMBRE_COMPLETO"
    col_materia = "MATERIA"
    col_grado = "GRADO"

    # ⚡ SECCIÓN DE MANDOS COMPACTA HORIZONTAL CENTRAL ORIGINAL
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_per, c_grad, c_est = st.columns([1.1, 1.4, 1.1, 2.2])
    
    with c_modo:
        modo = st.selectbox("Generación:", ["👤 Individual", "📦 Masivo"])
        
    with c_per:
        lista_periodos_opt = ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"]
        periodo_activo = st.selectbox("⏱️ Periodo:", lista_periodos_opt)
        es_consolidado = (periodo_activo == "CONSOLIDADO FINAL")
    
    lista_grados = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
    with c_grad:
        grado_sel = st.selectbox("📂 Grado:", lista_grados)
    df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    if modo == "👤 Individual":
        lista_estudiantes = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            estudiante_sel = st.selectbox("👤 Seleccione el Estudiante:", lista_estudiantes)
        df_alumnos = [estudiante_sel]
    else:
        df_alumnos = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            st.text_input("Estado de Lote:", f"📦 Masivo: {len(df_alumnos)} Boletines listos", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 🖨️ CONTROL DE BOTONES NATIVOS DE IMPRESIÓN CON ACTIVADOR PARENT-LEVEL DE ALTA INSTANCIA
    if modo == "👤 Individual":
        st.markdown("<div class='no-print' style='margin-bottom: 20px;'>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🖨️ IMPRIMIR INFORME ACADÉMICO", use_container_width=True):
                st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)
        with col_btn2:
            if st.button("📥 GUARDAR COMO PDF", use_container_width=True):
                st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)
        st.markdown("</div>", unsafe_allow_html=True)

    # Renderizado final adaptado para contención vertical estricta
    for estudiante in df_alumnos:
        df_est = df_trabajo[df_trabajo[col_nombre] == estudiante].copy()
        if df_est.empty: continue
        
        grado_est = df_est[col_grado].iloc[0] if col_grado in df_est.columns else "N/A"

        for cp in ['P1', 'P2', 'P3', 'P4']:
            if cp in df_est.columns:
                df_est[cp] = pd.to_numeric(df_est[cp], errors='coerce').fillna(0.0)
            
        prom_col = "PROMEDIO"
        if prom_col in df_est.columns:
            df_est[prom_col] = pd.to_numeric(df_est[prom_col], errors='coerce').fillna(0.0)
            promedio_institucional = df_est[prom_col].mean()
        else:
            promedio_institucional = df_est[['P1', 'P2', 'P3', 'P4']].mean(axis=1).mean()

        html_boletin = f"""
        <div class="boletin-insignia-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:22px; margin-top:5px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.06);">
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:12px;">
                <tr>
                    <td style="width:12%; text-align:left; vertical-align:middle;">{escudo_html}</td>
                    <td style="width:68%; text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black'; font-size:18px; letter-spacing:0.5px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <h4 style="margin:4px 0 0 0; color:#cc8800; font-family:'Arial'; font-weight:bold; font-size:11px; text-transform:uppercase; letter-spacing:1px;">INFORME ACADÉMICO OFICIAL: {periodo_activo}</h4>
                    </td>
                    <td style="width:20%; text-align:right; vertical-align:middle;">
                        <div style="border:2.5px solid #0d1b2a; border-radius:8px; padding:4px 8px; background-color:#f8f9fa; text-align:center; display:inline-block; min-width:95px; box-shadow: 2px 2px 0px #0d1b2a;">
                            <div style="font-size:8px; font-family:'Arial Black'; color:#0d1b2a; text-transform:uppercase;">PROMEDIO</div>
                            <div style="font-size:20px; font-family:'Arial Black'; color:#cc8800; font-weight:900; margin-top:1px;">{promedio_institucional:.1f}</div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:12px; border:2px solid #0d1b2a; background-color:#f8f9fa; box-shadow: 2px 2px 0px #0d1b2a;">
                <tr>
                    <td style="padding:7px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:11px; color:#0d1b2a; width:15%;">ESTUDIANTE:</td>
                    <td style="padding:7px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:12px; color:#000000; width:55%;">{estudiante}</td>
                    <td style="padding:7px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:11px; color:#0d1b2a; width:12%;">GRADO:</td>
                    <td style="padding:7px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:12px; color:#000000; width:18%; text-align:center;">{grado_est}</td>
                </tr>
            </table>
        """

        if es_consolidated:
            html_boletin += """
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif; border: 2px solid #0d1b2a;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a; text-align:center; font-size:11px;">
                        <th style="padding:7px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black';">MATERIA</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:7%;">P1</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:7%;">P2</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:7%;">P3</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:7%;">P4</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:9%;">DEF</th>
                        <th style="padding:7px; border:1px solid #d4af37; font-family:'Arial Black'; width:16%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
            """
        else:
            html_boletin += f"""
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif; border: 2px solid #0d1b2a;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a; font-size:11px;">
                        <th style="padding:8px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black';">MATERIA</th>
                        <th style="padding:8px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; width:18%;">NOTA {periodo_activo}</th>
                        <th style="padding:8px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; width:22%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
            """

        for _, fila in df_est.iterrows():
            materia_nom = str(fila[col_materia]).strip()
            logro_render = str(fila['LOGRO']).strip() if 'LOGRO' in df_est.columns and not pd.isna(fila['LOGRO']) else "Descriptor de logro oficial registrado en la bitácora escolar."
            
            if es_consolidado:
                n_p1 = float(fila['P1']) if 'P1' in df_est.columns else 0.0
                n_p2 = float(fila['P2']) if 'P2' in df_est.columns else 0.0
                n_p3 = float(fila['P3']) if 'P3' in df_est.columns else 0.0
                n_p4 = float(fila['P4']) if 'P4' in df_est.columns else 0.0
                n_def = float(fila[prom_col]) if prom_col in df_est.columns else ((n_p1+n_p2+n_p3+n_p4)/4)

                des_txt = obtener_desempeno_dinamico(n_def)
                color_def = "#cc0000" if n_def < 6.0 else "#000000"
                color_des = "#cc0000" if n_def < 6.0 else ("#00994c" if "SUPER" in des_txt or "ALTO" in des_txt else "#cc8800")

                html_boletin += f"""
                    <tr style="text-align:center; background-color:#ffffff; font-size:11.5px;">
                        <td style="padding:5px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0; text-align:left;">{materia_nom}</td>
                        <td style="padding:5px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p1 < 6.0 else '#000000'}">{n_p1:.1f}</td>
                        <td style="padding:5px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p2 < 6.0 else '#000000'}">{n_p2:.1f}</td>
                        <td style="padding:5px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p3 < 6.0 else '#000000'}">{n_p3:.1f}</td>
                        <td style="padding:5px; border-right:1px solid #e0e0e0; color:{'#cc0000' if n_p4 < 6.0 else '#000000'}">{n_p4:.1f}</td>
                        <td style="padding:5px; font-family:'Arial Black'; font-weight:900; border-right:1px solid #e0e0e0; color:{color_def}">{n_def:.1f}</td>
                        <td style="padding:5px; font-family:'Arial Black'; font-weight:bold; border-right:1px solid #0d1b2a; color:{color_des}">{des_txt}</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td colspan="7" class="logro-row-box" style="padding:3px 10px 5px 10px; font-style:italic; font-size:10px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; background-color:#fafafa; line-height:1.2;">
                            <strong style="color:#cc8800;">LOGRO:</strong> {logro_render}
                        </td>
                    </tr>
                """
            else:
                col_p_verif = str(periodo_activo).upper().strip()
                nota_val = float(fila[col_p_verif]) if col_p_verif in df_est.columns else 0.0
                
                des_txt = obtener_desempeno_dinamico(nota_val)
                color_nota = "#cc0000" if nota_val < 6.0 else "#000000"
                color_des = "#cc0000" if nota_val < 6.0 else ("#00994c" if "SUPER" in des_txt or "ALTO" in des_txt else "#cc8800")

                html_boletin += f"""
                    <tr style="background-color:#ffffff; font-size:11.5px;">
                        <td style="padding:6px 10px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0;">{materia_nom}</td>
                        <td style="padding:6px 10px; text-align:center; font-family:'Arial Black'; font-weight:900; color:{color_nota}; border-right:1px solid #e0e0e0;">{nota_val:.1f}</td>
                        <td style="padding:6px 10px; text-align:center; font-family:'Arial Black'; font-weight:bold; color:{color_des}; border-right:1px solid #0d1b2a;">{des_txt}</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td colspan="3" class="logro-row-box" style="padding:3px 10px 5px 10px; font-style:italic; font-size:10px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; background-color:#fafafa; line-height:1.2;">
                            <strong style="color:#cc8800;">LOGRO:</strong> {logro_render}
                        </td>
                    </tr>
                """

        html_boletin += """
                </tbody>
            </table>
            
            <div class="seccion-firmas" style="margin-top:25px; display:flex; justify-content:space-between; padding:0 30px;" class="page-break-avoid">
                <div style="text-align:center; width:38%;">
                    <div style="border-bottom:1.5px solid #0d1b2a; width:100%; height:25px;"></div>
                    <div style="font-size:9.5px; font-family:'Arial Black'; color:#0d1b2a; margin-top:5px; text-transform:uppercase;">RECTORÍA INSTITUCIONAL</div>
                </div>
                <div style="text-align:center; width:38%;">
                    <div style="border-bottom:1.5px solid #0d1b2a; width:100%; height:25px;"></div>
                    <div style="font-size:9.5px; font-family:'Arial Black'; color:#0d1b2a; margin-top:5px; text-transform:uppercase;">COORDINACIÓN ACADÉMICA</div>
                </div>
            </div>
        </div>
        <br class="no-print"><hr style="border:1px dashed #b0b0b0;" class="no-print"><br class="no-print">
        """
        st.html(html_boletin)
