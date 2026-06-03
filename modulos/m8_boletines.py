import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import unicodedata
import base64

# --- 1. CACHÉ E INDEXACIÓN DE DATOS ---

@st.cache_data
def obtener_logo_b64_cached(ruta_imagen="logo.png"):
    try:
        with open(ruta_imagen, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception:
        return ""

@st.cache_data
def construir_mapa_logros(df_logros_raw):
    dict_logros = {}
    if df_logros_raw is not None and not df_logros_raw.empty:
        for _, fila in df_logros_raw.iterrows():
            if len(fila) >= 4:
                clave = (
                    str(fila.iloc[0]).strip().upper(), 
                    str(fila.iloc[1]).strip().upper(), 
                    str(fila.iloc[2]).strip().upper()
                )
                dict_logros[clave] = str(fila.iloc[3])
    return dict_logros

# --- 2. MOTOR DE RENDERIZADO ULTRALIVIANO ---

# Usamos la directiva de Streamlit para aislar el renderizado si está disponible (Opcional pero recomendado)
# @st.fragment 
def render_individual(df_curso, alumno, periodo_sel, col_n, dict_logros, nivel_alumno, URL_LOGO, css_vip, th):
    """ Función dedicada exclusivamente a procesar un solo alumno de forma aislada """
    # Operación de filtrado de alta velocidad
    res = df_curso[df_curso['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
    res = res[res['PROMEDIO'] > 0.0]
    
    if res.empty:
        st.info("El estudiante seleccionado no tiene registros de notas mayores a 0.0.")
        return

    promedios = [float(x) for x in res[col_n] if pd.notna(x)]
    p_prom = sum(promedios) / len(promedios) if promedios else 0.0
    es_consolidado = "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper()

    # Construcción limpia por bloques de strings (más eficiente que concatenar con += en bucles grandes)
    html_filas = []
    for _, row in res.iterrows():
        nota_final = float(row.get(col_n, 0)) if pd.notna(row.get(col_n, 0)) else 0.0
        
        if nota_final >= 9.1: desp = "SUPERIOR"
        elif nota_final >= 7.6: desp = "ALTO"
        elif nota_final >= 6.0: desp = "BÁSICO"
        else: desp = "BAJO"

        color = "#155724" if nota_final >= 6.0 else "#721c24"

        if es_consolidado:
            p1 = float(row.get('P1', 0)) if pd.notna(row.get('P1', 0)) else 0.0
            p2 = float(row.get('P2', 0)) if pd.notna(row.get('P2', 0)) else 0.0
            p3 = float(row.get('P3', 0)) if pd.notna(row.get('P3', 0)) else 0.0
            p4 = float(row.get('P4', 0)) if pd.notna(row.get('P4', 0)) else 0.0
            prom = float(row.get('PROMEDIO', 0)) if pd.notna(row.get('PROMEDIO', 0)) else 0.0
            td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
            col_span = 7
        else:
            td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
            col_span = 3

        # Estructura de fila de materia
        html_filas.append(f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>")
        
        # Logro indexado en memoria (O(1))
        materia_limpia = str(row['Materia']).strip().upper()
        clave_busqueda = (nivel_alumno, materia_limpia, desp)
        logro_texto = dict_logros.get(clave_busqueda, str(row.get('LOGRO', 'Sin registro')))
        
        html_filas.append(f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px; line-height:1.1;'><b>LOGRO:</b> {logro_texto}</td></tr>")

    # Unimos todo el árbol HTML de manera limpia
    html_boletin = f"""<html><head><script>function imprimirBoletin() {{ window.print(); }}</script>{css_vip}</head><body>
    <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:12px; right:20px; z-index:99;">
        <button onclick="imprimirBoletin()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR / PDF</button>
    </div>
    <div class="b-print">
        <img src="{URL_LOGO}" class="watermark">
        <table class="header-table">
            <tr>
                <td style="width:12%;"><img src="{URL_LOGO}" width="80"></td>
                <td style="text-align:center; vertical-align:middle;">
                    <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                    <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                </td>
                <td style="text-align:right; width:15%; vertical-align:middle;">
                    <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px;">
                        <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                    </div>
                </td>
            </tr>
        </table>
        <div style="border:2px solid #0d1b2a; padding:8px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; font-size:12px;">
            <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span><span><b style="color:#0d1b2a;">GRADO:</b> {df_curso['Grado'].iloc[0] if not df_curso.empty else ''}</span>
        </div>
        <table class="table-custom">
            <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>
            {"".join(html_filas)}
        </table>
        <div class='firmas-container'>
            <div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div>
            <div class='firma-box'>Firma Director de Grupo</div>
        </div>
    </div></body></html>"""

    components.html(html_boletin, height=750, scrolling=True)


# --- 3. CONTROLADOR PRINCIPAL ---
def renderizar(df_filtrado, curso_sel, periodo_sel):
    # Obtener DataFrame base de sesión de forma limpia sin duplicar memoria masivamente
    df_base = st.session_state.df_maestro if ('df_maestro' in st.session_state and st.session_state.df_maestro is not None) else df_filtrado

    # Filtrar el grado completo una sola vez al entrar a la función
    if str(curso_sel) != "TODOS":
        df_curso = df_base[df_base['Grado'].astype(str) == str(curso_sel)]
    else:
        df_curso = df_base

    # UI básica de selección en la barra superior
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_est = st.columns([3, 7])
    with c_modo:
        modo_impresion = st.radio("Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Variables de negocio estables
    col_n = "PROMEDIO" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else periodo_sel
    grado_str = str(curso_sel).upper()
    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
    nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"
    th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else f"<th>{periodo_sel}</th>"
    
    # Carga optimizada de recursos estáticos comunes
    URL_LOGO_OFICIAL = obtener_logo_b64_cached("logo.png")
    dict_logros = construir_mapa_logros(st.session_state.get('df_logros', pd.DataFrame()))

    css_vip = """<style>
        body { font-family: Arial, sans-serif; background: white; color: black; margin: 0; padding: 0; }
        .b-print { position: relative; padding: 25px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; overflow: hidden; page-break-inside: avoid !important; }
        .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.04; width: 55%; z-index: -1; pointer-events: none; }
        .table-custom { width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 12px; z-index: 2; position: relative; }
        .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 8px; font-family: 'Arial Black'; font-size: 11px; }
        .table-custom td { border: 1px solid #000; padding: 6px; background-color: rgba(255, 255, 255, 0.85); text-align: center; font-size: 11.5px; }
        .header-table { width: 100%; border: none; margin-bottom: 12px; z-index: 2; position: relative; }
        .header-table td { border: none; }
        .firmas-container { display: flex; justify-content: space-around; margin-top: 45px; font-size: 13px; z-index: 2; position: relative; page-break-inside: avoid !important; }
        .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; }
        @media print { 
            @page { size: legal portrait; margin: 8mm 10mm 8mm 10mm !important; } 
            body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } 
            .no-print { display: none !important; } 
            .b-print { border: none !important; box-shadow: none !important; padding: 0 !important; width: 100% !important; } 
            .salto-pagina { page-break-after: always !important; page-break-inside: avoid !important; } 
        }
    </style>"""

    if modo_impresion == "👤 Individual":
        # Extraer nombres es ultra veloz sobre el DataFrame del curso ya filtrado
        estudiantes = sorted(df_curso['Nombre_Completo'].dropna().unique())
        
        with c_est:
            alumno = st.selectbox("👤 Seleccione el Estudiante para Inspección:", estudiantes, key="sb_alumno_vip")
        
        if alumno:
            # Renderizamos llamando al sub-módulo optimizado
            render_individual(df_curso, alumno, periodo_sel, col_n, dict_logros, nivel_alumno, URL_LOGO_OFICIAL, css_vip, th)

    else:
        # --- MODO MASIVO (Totalmente aislado del flujo individual) ---
        estudiantes = sorted(df_curso['Nombre_Completo'].dropna().unique())
        with c_est:
            st.warning(f"⚠️ Se compilarán {len(estudiantes)} boletines oficiales oficiales para el grado {curso_sel}.")

        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary", use_container_width=True):
            html_masivo = [f"<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body>",
                           "<div class=\"no-print\" style=\"position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;\">",
                           "    <button onclick=\"imprimirLote()\" style=\"background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';\">🖨️ IMPRIMIR LOTE MASIVO COMPLETO</button>",
                           "</div>"]

            for i, alum in enumerate(estudiantes):
                res = df_curso[df_curso['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                res = res[res['PROMEDIO'] > 0.0]
                if res.empty: continue

                promedios = [float(x) for x in res[col_n] if pd.notna(x)]
                p_prom = sum(promedios) / len(promedios) if promedios else 0.0
                salto = "salto-pagina" if i < len(estudiantes) - 1 else ""

                html_masivo.append(f"""<div class="b-print {salto}">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table">
                    <tr>
                        <td style="width:12%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                        <td style="text-align:center; vertical-align:middle;">
                            <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                            <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                        </td>
                        <td style="text-align:right; width:15%; vertical-align:middle;">
                            <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px;">
                                <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                            </div>
                        </td>
                    </tr>
                </table>
                <div style="border:2px solid #0d1b2a; padding:8px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; font-size:12px;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {curso_sel}</span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>""")

                for _, row in res.iterrows():
                    nota_final = float(row.get(col_n, 0)) if pd.notna(row.get(col_n, 0)) else 0.0
                    if nota_final >= 9.1: desp = "SUPERIOR"
                    elif nota_final >= 7.6: desp = "ALTO"
                    elif nota_final >= 6.0: desp = "BÁSICO"
                    else: desp = "BAJO"

                    color = "#155724" if nota_final >= 6.0 else "#721c24"

                    if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper():
                        p1 = float(row.get('P1', 0)) if pd.notna(row.get('P1', 0)) else 0.0
                        p2 = float(row.get('P2', 0)) if pd.notna(row.get('P2', 0)) else 0.0
                        p3 = float(row.get('P3', 0)) if pd.notna(row.get('P3', 0)) else 0.0
                        p4 = float(row.get('P4', 0)) if pd.notna(row.get('P4', 0)) else 0.0
                        prom = float(row.get('PROMEDIO', 0)) if pd.notna(row.get('PROMEDIO', 0)) else 0.0
                        td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                        col_span = 7
                    else:
                        td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                        col_span = 3

                    html_masivo.append(f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>")

                    materia_limpia = str(row['Materia']).strip().upper()
                    clave_busqueda = (nivel_alumno, materia_limpia, desp)
                    logro_texto = dict_logros.get(clave_busqueda, str(row.get('LOGRO', 'Sin registro')))

                    html_masivo.append(f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px; line-height:1.1;'><b>LOGRO:</b> {logro_texto}</td></tr>")

                html_masivo.append("""</table>
                    <div class='firmas-container'>
                        <div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div>
                        <div class='firma-box'>Firma Director de Grupo</div>
                    </div>
                </div>""")

            html_masivo.append("</body></html>")
            components.html("".join(html_masivo), height=750, scrolling=True)
