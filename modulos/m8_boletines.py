import streamlit as st
import pandas as pd

def renderizar(*args, **kwargs):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📜 Expedición de Boletines Oficiales</h3>", unsafe_allow_html=True)
    
    # 👑 INYECTOR DE REGLAS DE IMPRESIÓN Y BOTONES PREMIUM
    st.markdown("""
        <style>
            /* 🖨️ ESCUDO DE IMPRESIÓN RECTÓRICO: Oculta la app y deja solo el boletín */
            @media print {
                header, [data-testid="stSidebar"], [data-testid="stHeader"], 
                .stRadio, .stSelectbox, .no-print, .stButton, div.block-container button {
                    display: none !important;
                }
                .main .block-container {
                    padding-top: 0px !important;
                    padding-bottom: 0px !important;
                }
                .boletin-print-box {
                    border: none !important;
                    box-shadow: none !important;
                    margin: 0px !important;
                    padding: 0px !important;
                    width: 100% !important;
                }
            }
            
            /* Estilos de la barra de acciones en pantalla */
            .barra-acciones-boletin {
                display: flex;
                gap: 15px;
                margin-top: 10px;
                margin-bottom: 15px;
            }
            
            .btn-accion-print {
                background-color: #0d1b2a;
                color: white !important;
                font-family: 'Arial Black', sans-serif;
                font-size: 13px;
                padding: 10px 20px;
                border: 2px solid #d4af37;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                box-shadow: 3px 3px 0px #d4af37;
                transition: all 0.2s ease;
            }
            .btn-accion-print:hover {
                transform: translate(-1px, -1px);
                box-shadow: 4px 4px 0px #0d1b2a;
                background-color: #1e3551;
            }
        </style>
    """, unsafe_allow_html=True)

    # Desempaquetado seguro de los datos enviados por app.py
    df_notas = None
    periodo_sel = "P1"
    conn_sql = None

    if len(args) >= 1: df_notas = args[0] if isinstance(args[0], pd.DataFrame) else None
    if len(args) >= 2: periodo_sel = args[1] if isinstance(args[1], str) else None
    if len(args) >= 3: conn_sql = args[2]

    # Recuperación autónoma en caso de desconexión temporal
    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    col_materia = next((c for c in df_trabajo.columns if c in ['MATERIA', 'ASIGNATURA']), None)
    
    col_p = str(periodo_sel).upper().strip()
    if col_p not in df_trabajo.columns:
        col_p = next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'DEF', 'NOTA']), None)

    # Selectores de Configuración en Pantalla
    modo = st.radio("Seleccione el modo de generación:", ["👤 Individual", "📦 Masivo (Todo el Grado)"], horizontal=True)
    
    if col_grado:
        lista_grados = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
        grado_sel = st.selectbox("📂 Seleccione el Grado:", lista_grados)
        df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    if modo == "👤 Individual":
        lista_estudiantes = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        estudiante_sel = st.selectbox("👤 Estudiante:", lista_estudiantes)
        df_alumnos = [estudiante_sel]
    else:
        df_alumnos = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        st.info(f"Se procesará un lote consolidado de {len(df_alumnos)} boletines para el grado seleccionado.")

    if not df_alumnos:
        st.info("No hay registros para la selección actual.")
        return

    # Proceso de renderizado para los alumnos seleccionados
    for estudiante in df_alumnos:
        df_est = df_trabajo[df_trabajo[col_nombre] == estudiante].copy()
        if df_est.empty: continue
        
        df_est[col_p] = pd.to_numeric(df_est[col_p], errors='coerce').fillna(0.0)
        promedio_general = df_est[col_p].mean()
        grado_est = df_est[col_grado].iloc[0] if col_grado in df_est.columns else "N/A"

        # 👑 RENDERIZACIÓN DE LOS BOTONES DE IMPRESIÓN (Sólo visibles en modo individual y no salen en el papel)
        if modo == "👤 Individual":
            st.markdown(f"""
                <div class="barra-acciones-boletin no-print">
                    <button class="btn-accion-print" onclick="window.print();">🖨️ IMPRIMIR INFORME ACADÉMICO</button>
                    <button class="btn-accion-print" onclick="window.print();" style="background-color:#cc8800; box-shadow: 3px 3px 0px #0d1b2a;">📥 GUARDAR COMO PDF</button>
                </div>
            """, unsafe_allow_html=True)

        # 👑 MAQUETACIÓN ESTRUCTURAL DEL BOLETÍN DEL COLEGIO
        html_boletin = f"""
        <div class="boletin-print-box" style="background-color:#ffffff; border:3px solid #0d1b2a; border-radius:12px; padding:30px; margin-top:10px; font-family:'Arial', sans-serif; box-shadow: 4px 4px 15px rgba(0,0,0,0.08); position:relative;">
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="width:15%; text-align:left; vertical-align:middle;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2211/2211571.png" style="width:80px; height:80px;">
                    </td>
                    <td style="width:65%; text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black'; font-size:22px; letter-spacing:1px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <h4 style="margin:5px 0 0 0; color:#cc8800; font-family:'Arial'; font-weight:bold; font-size:14px; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</h4>
                    </td>
                    <td style="width:20%; text-align:right; vertical-align:middle;">
                        <div style="border:3px solid #0d1b2a; border-radius:8px; padding:8px; background-color:#f8f9fa; text-align:center; min-width:100px;">
                            <div style="font-size:10px; font-family:'Arial Black'; color:#0d1b2a; text-transform:uppercase;">PROMEDIO</div>
                            <div style="font-size:22px; font-family:'Arial Black'; color:#cc8800; font-weight:900; margin-top:2px;">{promedio_general:.1f}</div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:25px; border:2px solid #0d1b2a; background-color:#f8f9fa;">
                <tr>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:12px; color:#0d1b2a; width:15%;">ESTUDIANTE:</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:13px; color:#000000; width:55%;">{estudiante}</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial Black'; font-size:12px; color:#0d1b2a; width:12%;">GRADO:</td>
                    <td style="padding:10px; border:1px solid #0d1b2a; font-family:'Arial'; font-weight:bold; font-size:13px; color:#000000; width:18%; text-align:center;">{grado_est}</td>
                </tr>
            </table>
            
            <table style="width:100%; border-collapse:collapse; font-family:'Arial', sans-serif;">
                <thead>
                    <tr style="background-color:#0d1b2a; color:white; border:2px solid #0d1b2a;">
                        <th style="padding:12px; border:1px solid #d4af37; text-align:left; font-family:'Arial Black'; font-size:12px;">MATERIA / JORNADA</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:15%;">{periodo_sel}</th>
                        <th style="padding:12px; border:1px solid #d4af37; text-align:center; font-family:'Arial Black'; font-size:12px; width:25%;">DESEMPEÑO</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, fila in df_est.iterrows():
            materia_nom = str(fila[col_materia]).strip()
            nota_val = float(fila[col_p])
            
            # Clasificador de Desempeños Institucionales
            if nota_val >= 9.0: des_txt = "SUPERIOR"
            elif nota_val >= 7.6: des_txt = "ALTO"
            elif nota_val >= 6.0: des_txt = "BÁSICO"
            else: des_txt = "BAJO"
            
            color_nota = "#cc0000" if nota_val < 6.0 else "#000000"
            color_des = "#cc0000" if nota_val < 6.0 else ("#00994c" if nota_val >= 7.6 else "#cc8800")
            
            html_boletin += f"""
                <tr style="border-bottom:1px solid #e0e0e0;">
                    <td style="padding:10px; font-weight:bold; color:#0d1b2a; border-left:2px solid #0d1b2a; border-right:1px solid #e0e0e0; font-size:13px;">{materia_nom}</td>
                    <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:900; color:{color_nota}; border-right:1px solid #e0e0e0; font-size:14px;">{nota_val:.1f}</td>
                    <td style="padding:10px; text-align:center; font-family:'Arial Black'; font-weight:bold; color:{color_des}; border-right:2px solid #0d1b2a; font-size:12px;">{des_txt}</td>
                </tr>
            """
            
        html_boletin += """
                </tbody>
            </table>
            
            <div style="margin-top:60px; display:flex; justify-content:space-between; padding:0 40px;" class="page-break-avoid">
                <div style="text-align:center; width:40%;">
                    <div style="border-bottom:2px solid #0d1b2a; width:100%; height:40px;"></div>
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase;">RECTORÍA INSTITUCIONAL</div>
                </div>
                <div style="text-align:center; width:40%;">
                    <div style="border-bottom:2px solid #0d1b2a; width:100%; height:40px;"></div>
                    <div style="font-size:11px; font-family:'Arial Black'; color:#0d1b2a; margin-top:8px; text-transform:uppercase;">COORDINACIÓN ACADÉMICA</div>
                </div>
            </div>
            
        </div>
        <br class="no-print">
        <hr style="border:1px dashed #b0b0b0;" class="no-print">
        <br class="no-print">
        """
        st.html(html_boletin)
