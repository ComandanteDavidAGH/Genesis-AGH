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
    """ Calcula el desempeño institucional en tiempo real eliminando errores NAN """
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
        escudo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width:85px; height:auto; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.15));">'
    else:
        escudo_html = '<div style="width:80px; height:80px; background-color:#0d1b2a; border:2px solid #d4af37; border-radius:50%;"></div>'

    # 👑 INYECTOR DE REGLAS DE IMPRESIÓN OFICIAL CSS (Aísla el boletín en el papel)
    st.markdown("""
        <style>
            @media print {
                header, [data-testid="stSidebar"], [data-testid="stHeader"], 
                .stRadio, .stSelectbox, .no-print, .stButton, div.block-container button,
                div[data-testid="stVerticalBlock"] > div.no-print, .panel-ayuda-print {
                    display: none !important;
                }
                .main .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }
                .boletin-insignia-box { border: none !important; box-shadow: none !important; margin: 0px !important; padding: 0px !important; width: 100% !important; }
            }
            .panel-ayuda-print {
                background-color: #f8f9fa;
                border: 2px solid #0d1b2a;
                border-left: 6px solid #d4af37;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 3px 3px 10px rgba(0,0,0,0.05);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📜 Expedición de Boletines Oficiales</h3>", unsafe_allow_html=True)
    
    # 🔄 INTERCEPTOR DE FRECUENCIA: Escaneo prioritario y reactivo de la Barra Lateral Global
    periodo_seleccionado = "P1"
    for key, value in st.session_state.items():
        val_str = str(value).upper().strip()
        if val_str in ["P1", "P2", "P3", "P4"] or "CONSOLID" in val_str or "FINAL" in val_str:
            periodo_seleccionado = val_str
            break

    es_consolidado = "CONSOLID" in periodo_seleccionado or "FINAL" in periodo_seleccionado
    periodo_visual = "CONSOLIDADO FINAL" if es_consolidado else f"PERIODO {periodo_seleccionado}"

    # Desempaquetado seguro de los datos de app.py
    df_notas = args[0] if len(args) >= 1 and isinstance(args[0], pd.DataFrame) else None
    conn_sql = args[2] if len(args) >= 3 else None

    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    # Estandarización absoluta de columnas verificadas por la trampa
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    col_nombre = "NOMBRE_COMPLETO"
    col_materia = "MATERIA"
    col_grado = "GRADO"

    # ⚡ FILTROS COMPACTOS HORIZONTALES (Espacio Optimizado)
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_grad, c_est = st.columns([1.2, 1.5, 3.3])
    
    with c_modo:
        modo = st.selectbox("Generación:", ["👤 Individual", "📦 Masivo"])
    
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
            st.text_input("Estado de Lote:", f"📦 Masivo: {len(df_alumnos)} Boletines consolidados listos", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 🖨️ PANEL DE MANDO DE IMPRESIÓN PREMIUM (Garantiza el bypass de seguridad)
    if modo == "👤 Individual":
        st.markdown(f"""
            <div class="panel-ayuda-print no-print">
                <p style="margin:0; font-family:'Arial Black'; color:#0d1b2a; font-size:14px;">🖨️ CONTROL INSTITUCIONAL DE EXPEDICIÓN</p>
                <p style="margin:5px 0 0 0; font-size:12.5px; color:#333333; line-height:1.4;">
                    Para garantizar la máxima nitidez y activar el guardado oficial, use el comando universal del sistema: <br>
                    👉 Presione las teclas <strong>Ctrl + P</strong> (en Windows) o <strong>Cmd + P</strong> (en Mac). <br>
                    💡 <em>Nota de Rectoría:</em> En la ventana que se abrirá, cambie el 'Destino' a <strong>Guardar como PDF</strong> o seleccione su impresora física. El menú lateral y los botones se ocultarán automáticamente.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Renderizado en cadena de los Boletines Insignias
    for estudiante in df_alumnos:
        df_est = df_trabajo[df_trabajo[col_nombre] == estudiante].copy()
        if df_est.empty: continue
        
        grado_est = df_est[col_grado].iloc[0] if col_grado in df_est.columns else "N/A"

        # Asegurar formato numérico
        for cp in ['P1', 'P2', 'P3', 'P4']:
            if cp in df_est.columns:
                df_est[cp] = pd.to_numeric(df_est[cp], errors='coerce').fillna(0.0)
            
        prom_col = "PROMEDIO"
        if prom_col in df_est.columns:
            df_est[prom_col] = pd.to_numeric(df_est[prom_col], errors='coerce').fillna(0.0)
            promedio_institucional = df_est[prom_col].mean()
        else:
            promedio_institucional = df_est[['P1', 'P2', 'P3', 'P4']].mean(axis=1).mean()

        # Cabecera del Boletín Insignia
        html_boletin = f"""
        <div class="boletin-insignia-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:30px; margin-top:15px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.08);">
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="width:15%; text-align:left; vertical-align:middle;">{escudo_html}</td>
                    <td style="width:65%; text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black'; font-size:20px; letter-spacing:0.5px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <h4 style="margin:6px 0 0 0; color:#cc8800; font-family:'Arial'; font-weight:bold; font-size:13px; text-transform:uppercase; letter-spacing:1px;">INFORME ACADÉMICO OFICIAL: {periodo_visual}</h4>
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

        # 👑 CAMBIO MATRICIAL DINÁMICO COMPLETAMENTE CONECTADO AL MENÚ LATERAL
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
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:18%;">NOTA {periodo_seleccionado}</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:25%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
            """

        # Inyección de filas de materias y descriptores de logros
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
                col_p_verif = str(periodo_seleccionado).upper().strip()
                nota_val = float(fila[col_p_verif]) if col_p_verif in df_est.columns else 0.0
                
                des_txt = obtener_desempeno_dinamico(nota_val)
                color_nota = "#cc0000" if nota_val < 6.0 else "#000000"
                color_des = "#cc0000" if nota_val < 6.0 else ("#00994c" if "SUPER" in des_txt or "ALTO" in des_txt else "#cc8800")

                html_boletin += f"""
                    <tr style="background-color:#ffffff;">
                        <td style="padding:10px; font-weight:bold; color:#0d1b2a; border-left:1px solid #0d1b2a; border-right:1px solid #e0e0e0; font-size:13px;">{materia_nom}</td>
                        <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:900; color:{color_nota}; border-right:1px solid #e0e0e0; font-size:14px;">{nota_val:.1f}</td>
                        <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:bold; color:{color_des}; border-right:1px solid #0d1b2a; font-size:12px;">{des_txt}</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td colspan="3" style="padding:6px 12px 8px 12px; font-style:italic; font-size:11px; color:#4a4a4a; border-left:1px solid #0d1b2a; border-right:1px solid #0d1b2a; border-bottom:2px solid #0d1b2a; text-align:left; background-color:#fafafa;">
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
