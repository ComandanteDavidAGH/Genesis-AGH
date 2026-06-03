import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import unicodedata
import base64
import os

def limpiar_texto(txt):
    """ Estandariza cadenas para realizar cruces perfectos """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 🔄 ANCLAJE DE RADAR: Recibir variables exactas enviadas desde app.py o Supabase
    df_notas = args[0] if len(args) >= 1 and isinstance(args[0], pd.DataFrame) else None
    periodo_sel = str(args[1]).upper().strip() if len(args) >= 2 and args[1] else "P1"
    conn_sql = args[2] if len(args) >= 3 else None

    # Sincronización de respaldo con la barra lateral por si hay retraso en los argumentos
    for key, value in st.session_state.items():
        if "period" in key.lower() or key.lower() == "periodo":
            periodo_sel = str(value).upper().strip()
            break

    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible en este cuadrante.**")
        return

    # Estandarización de columnas según la trampa detectada
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]

    # Mapeo de columnas fijas del archivo de producción
    col_nombre = "NOMBRE_COMPLETO"
    col_materia = "MATERIA"
    col_grado = "GRADO"
    
    # Asignamos la columna de nota activa según el periodo del menú
    col_n = "PROMEDIO" if "CONSOLID" in periodo_sel or "FINAL" in periodo_sel else periodo_sel

    # 👑 HOJA DE ESTILOS VIP ORIGINAL DE SU PLATAFORMA
    css_vip = """<style>
        body { font-family: Arial, sans-serif; background: white; color: black; margin: 0; padding: 0; }
        .b-print { position: relative; padding: 25px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; }
        .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 55%; z-index: -1; pointer-events: none; }
        .table-custom { width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 12px; z-index: 2; position: relative; }
        .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 8px; font-family: 'Arial Black'; font-size: 11px; }
        .table-custom td { border: 1px solid #000; padding: 6px; background-color: rgba(255, 255, 255, 0.85); text-align: center; font-size: 11.5px; }
        .header-table { width: 100%; border: none; margin-bottom: 12px; z-index: 2; position: relative; }
        .header-table td { border: none; }
        .firmas-container { display: flex; justify-content: space-around; margin-top: 45px; font-size: 13px; z-index: 2; position: relative; page-break-inside: avoid; }
        .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; }
        @media print { 
            @page { size: legal portrait; margin: 8mm 10mm 8mm 10mm; } 
            body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } 
            .no-print { display: none !important; } 
            .b-print { border: none; box-shadow: none; padding: 0; width: 100% !important; } 
            .salto-pagina { page-break-after: always; } 
        }
    </style>"""

    def nota_limpia(valor):
        try:
            n = float(valor)
            return 0.0 if pd.isna(n) else n
        except:
            return 0.0

    # ⚡ SECCIÓN DE FILTROS PEQUEÑOS HORIZONTALES PARA PANTALLA EXCLUSIVA
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_grad, c_est = st.columns([1.2, 1.5, 3.3])
    
    with c_modo:
        modo_impresion = st.selectbox("Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"])
    
    lista_grados = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
    with c_grad:
        curso_sel = st.selectbox("📂 Grado:", lista_grados)
    df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == curso_sel]

    if modo_impresion == "👤 Individual":
        lista_estudiantes = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            alumno = st.selectbox("👤 Estudiante:", lista_estudiantes)
        df_alumnos = [alumno]
    else:
        df_alumnos = sorted(df_trabajo[col_nombre].dropna().unique().tolist())
        with c_est:
            st.text_input("Estado de Lote:", f"📦 {len(df_alumnos)} Boletines VIP listos para compilar", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Convertidor Base64 para el Escudo de Armas oficial
    try:
        with open("logo.png", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
            URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
    except:
        URL_LOGO_OFICIAL = ""

    # 👑 CONSTRUCCIÓN DEL DOCUMENTO EN LA MEMORIA ACUMULATIVA
    th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if "CONSOLID" in periodo_sel or "FINAL" in periodo_sel else f"<th>{periodo_sel}</th>"
    
    if modo_impresion == "👤 Individual":
        if not df_alumnos: return
        res = df_trabajo[df_trabajo[col_nombre] == df_alumnos[0]].drop_duplicates(subset=[col_materia])
        
        promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
        p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0

        html_boletin = f"""<html><head><script>function imprimirBoletin() {{ window.print(); }}</script>{css_vip}</head><body>
        <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:12px; right:25px; z-index:99;">
            <button onclick="imprimirBoletin()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:9px 18px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black'; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">🖨️ IMPRIMIR / GUARDAR PDF</button>
        </div>
        <div class="b-print">
            <img src="{URL_LOGO_OFICIAL}" class="watermark">
            <table class="header-table">
                <tr>
                    <td style="width:12%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                    <td style="text-align:center; vertical-align:middle;">
                        <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                        <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_visual if 'periodo_visual' in locals() else periodo_sel}</p>
                    </td>
                    <td style="text-align:right; width:15%; vertical-align:middle;">
                        <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px; box-shadow: 2px 2px 0px #0d1b2a;">
                            <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:20px; color:#d4af37;">{p_prom:.1f}</b>
                        </div>
                    </td>
                </tr>
            </table>
            <div style="border:2px solid #0d1b2a; padding:8px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; font-size:12px;">
                <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {df_alumnos[0]}</span><span><b style="color:#0d1b2a;">GRADO:</b> {curso_sel}</span>
            </div>
            <table class="table-custom">
                <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""

        for index, row in res.iterrows():
            nota_final = nota_limpia(row.get(col_n, 0)) if col_n in res.columns else 0.0
            
            if nota_final >= 9.1: desp = "SUPERIOR"
            elif nota_final >= 7.6: desp = "ALTO"
            elif nota_final >= 6.0: desp = "BÁSICO"
            else: desp = "BAJO"

            color = "#155724" if nota_final >= 6.0 else "#721c24"
            
            if "CONSOLID" in periodo_sel or "FINAL" in periodo_sel:
                p1 = nota_limpia(row.get('P1', 0))
                p2 = nota_limpia(row.get('P2', 0))
                p3 = nota_limpia(row.get('P3', 0))
                p4 = nota_limpia(row.get('P4', 0))
                prom = nota_limpia(row.get('PROMEDIO', 0))
                td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                col_span = 7
            else:
                td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                col_span = 3
            
            html_boletin += f"<tr><td style='text-align:left;'><b>{row[col_materia]}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
            logro_texto = str(row.get('LOGRO', 'Descriptor de logro oficial registrado en la bitácora escolar.'))
            html_boletin += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px;'><b>LOGRO:</b> {logro_texto}</td></tr>"

        html_boletin += f"""</table>
            <div class='firmas-container'>
                <div class='firma-box'>RECTORÍA INSTITUCIONAL<br><span style='font-size:9px; font-weight:normal;'>Sello Oficial</span></div>
                <div class='firma-box'>COORDINACIÓN ACADÉMICA</div>
            </div>
        </div></body></html>"""

        # Despliegue nativo encapsulado en iframe
        components.html(html_boletin, height=650, scrolling=True)

    else:
        # MODO LOTE MASIVO VIP
        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary", use_container_width=True):
            html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body>
            <div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;">
                <button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR LOTE MASIVO COMPLETO</button>
            </div>"""

            for i, alum in enumerate(df_alumnos):
                res = df_trabajo[df_trabajo[col_nombre] == alum].drop_duplicates(subset=[col_materia])
                promedos_m = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
                p_prom = sum(promedos_m) / len(promedos_m) if len(promedos_m) > 0 else 0.0
                salto = "salto-pagina" if i < len(df_alumnos) - 1 else ""

                html_masivo += f"""<div class="b-print {salto}">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table">
                    <tr>
                        <td style="width:12%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                        <td style="text-align:center; vertical-align:middle;">
                            <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                            <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black';">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                        </td>
                        <td style="text-align:right; width:15%; vertical-align:middle;">
                            <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px; box-shadow: 2px 2px 0px #0d1b2a;">
                                <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:20px; color:#d4af37;">{p_prom:.1f}</b>
                            </div>
                        </td>
                    </tr>
                </table>
                <div style="border:2px solid #0d1b2a; padding:8px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; font-size:12px;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {curso_sel}</span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""

                for _, row in res.iterrows():
                    nota_final = nota_limpia(row.get(col_n, 0)) if col_n in res.columns else 0.0
                    if nota_final >= 9.1: desp = "SUPERIOR"
                    elif nota_final >= 7.6: desp = "ALTO"
                    elif nota_final >= 6.0: desp = "BÁSICO"
                    else: desp = "BAJO"

                    color = "#155724" if nota_final >= 6.0 else "#721c24"

                    if "CONSOLID" in periodo_sel or "FINAL" in periodo_sel:
                        p1 = nota_limpia(row.get('P1', 0))
                        p2 = nota_limpia(row.get('P2', 0))
                        p3 = nota_limpia(row.get('P3', 0))
                        p4 = nota_limpia(row.get('P4', 0))
                        prom = nota_limpia(row.get('PROMEDIO', 0))
                        td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                        col_span = 7
                    else:
                        td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                        col_span = 3

                    html_masivo += f"<tr><td style='text-align:left;'><b>{row[col_materia]}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
                    logro_texto = str(row.get('LOGRO', 'Descriptor de logro oficial registrado en la bitácora escolar.'))
                    html_masivo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px;'><b>LOGRO:</b> {logro_texto}</td></tr>"

                html_masivo += """</table>
                    <div class='firmas-container'>
                        <div class='firma-box'>RECTORÍA INSTITUCIONAL<br><span style='font-size:9px; font-weight:normal;'>Sello Oficial</span></div>
                        <div class='firma-box'>COORDINACIÓN ACADÉMICA</div>
                    </div>
                </div>"""

            html_masivo += "</body></html>"
            components.html(html_masivo, height=650, scrolling=True)
