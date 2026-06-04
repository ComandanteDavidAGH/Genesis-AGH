import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import unicodedata
import base64
import time

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
                val_logro = str(fila.iloc[3]).strip()
                if val_logro.lower() in ['nan', 'none', '<na>', 'null', '']:
                    continue
                clave = (
                    str(fila.iloc[0]).strip().upper(), 
                    str(fila.iloc[1]).strip().upper(), 
                    str(fila.iloc[2]).strip().upper()
                )
                dict_logros[clave] = val_logro
    return dict_logros

# --- 2. MOTOR DE RENDERIZADO ULTRALIVIANO ---

def render_individual(df_curso, alumno, periodo_sel, col_n, dict_logros, nivel_alumno, URL_LOGO, css_vip, periodos_print, info_puesto):
    res = df_curso[df_curso['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
    res = res[res['PROMEDIO'] > 0.0]
    
    if res.empty:
        st.info("El estudiante seleccionado no tiene registros de notas mayores a 0.0.")
        return

    promedios = [float(x) for x in res[col_n] if pd.notna(x)]
    p_prom = sum(promedios) / len(promedios) if promedios else 0.0

    th = "".join([f"<th>{p}</th>" for p in periodos_print])
    col_span_logro = len(periodos_print) + 2

    html_filas = []
    for _, row in res.iterrows():
        nota_final = float(row.get(col_n, 0)) if pd.notna(row.get(col_n, 0)) else 0.0
        
        if nota_final >= 9.1: desp = "SUPERIOR"
        elif nota_final >= 7.6: desp = "ALTO"
        elif nota_final >= 6.0: desp = "BÁSICO"
        else: desp = "BAJO"

        color = "#006600" if nota_final >= 6.0 else "#cc0000"

        td = ""
        for p in periodos_print:
            if p == "FINAL":
                val = float(row.get('PROMEDIO', 0)) if pd.notna(row.get('PROMEDIO', 0)) else 0.0
                td += f"<td style='color:{color}; font-weight:bold;'>{val:.1f}</td>"
            else:
                val = float(row.get(p, 0)) if pd.notna(row.get(p, 0)) else 0.0
                td += f"<td style='font-weight:bold;'>{val:.1f}</td>"

        html_filas.append(f"<tr><td class='materia-title'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>")
        
        materia_limpia = str(row['Materia']).strip().upper()
        clave_busqueda = (nivel_alumno, materia_limpia, desp)
        logro_texto = dict_logros.get(clave_busqueda, str(row.get('LOGRO', '')))
        
        if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']:
            logro_texto = "Pendiente de registro."
            
        html_filas.append(f"<tr class='logro-row'><td colspan='{col_span_logro}'><b>LOGRO:</b> {logro_texto}</td></tr>")

    img_watermark = f'<img src="{URL_LOGO}" class="watermark">' if URL_LOGO else ""
    img_logo = f'<img src="{URL_LOGO}" width="70">' if URL_LOGO else ""

    html_boletin = f"""<html><head><script>function imprimirBoletin() {{ window.print(); }}</script>{css_vip}</head><body>
    <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:12px; right:20px; z-index:99;">
        <button onclick="imprimirBoletin()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black'; transition: 0.2s;">🖨️ IMPRIMIR / PDF</button>
    </div>
    <div class="b-print">
        {img_watermark}
        <table class="header-table">
            <tr>
                <td style="width:12%; text-align:left;">{img_logo}</td>
                <td style="text-align:center; vertical-align:middle;">
                    <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                    <p style="margin:2px 0 0 0; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                </td>
                <td style="text-align:right; width:15%; vertical-align:middle;">
                    <div style="border:2px solid #0d1b2a; padding:4px; background:#f0f2f6; text-align:center; border-radius:6px;">
                        <b style="font-size:9px; color:#000;">PROMEDIO</b><br><b style="font-size:16px; color:#d4af37;">{p_prom:.1f}</b>
                    </div>
                </td>
            </tr>
        </table>
        <div class="info-box">
            <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span>
            <span><b style="color:#0d1b2a;">GRADO:</b> {df_curso['Grado'].iloc[0] if not df_curso.empty else ''}</span>
            <span><b style="color:#0d1b2a;">PUESTO:</b> <span style="color:#cc0000; font-weight:900;">{info_puesto}</span></span>
        </div>
        <table class="table-custom">
            <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>
            {"".join(html_filas)}
        </table>
        <div class='firmas-container'>
            <div class='firma-box'>Firma Rectoría<br><span style='font-size:8px; font-weight:normal;'>Sello Institucional</span></div>
            <div class='firma-box'>Firma Director de Grupo</div>
        </div>
    </div></body></html>"""

    components.html(html_boletin, height=800, scrolling=True)


# --- 3. CONTROLADOR PRINCIPAL ---
def renderizar(df_filtrado, curso_sel, periodo_sel):
    df_base = st.session_state.df_maestro if ('df_maestro' in st.session_state and st.session_state.df_maestro is not None) else df_filtrado

    if str(curso_sel) != "TODOS":
        df_curso = df_base[df_base['Grado'].astype(str) == str(curso_sel)].copy()
    else:
        df_curso = df_base.copy()

    # 🚀 PANEL DE CONTROL
    st.markdown("<div class='no-print' style='background:#f8f9fa; padding:10px 15px; border-radius:8px; border: 2px solid #0d1b2a; border-left: 5px solid #d4af37; margin-bottom: 20px;'>", unsafe_allow_html=True)
    col_modo, col_per, col_vacia = st.columns([3, 3, 4])
    
    with col_modo:
        modo_impresion = st.radio("🛠️ Modo de Generación:", ["👤 Individual", "🖨️ Masiva"], horizontal=True)
    
    with col_per:
        opciones_p = ["P1", "P2", "P3", "P4", "FINAL"]
        def_p = ["P1", "P2", "P3", "P4", "FINAL"] if "CONSOLID" in str(periodo_sel).upper() else [periodo_sel]
        def_p = [p for p in def_p if p in opciones_p]
        if not def_p: def_p = ["FINAL"]
        periodos_print = st.multiselect("📊 Columnas a Imprimir:", opciones_p, default=def_p)
        
    st.markdown("</div>", unsafe_allow_html=True)

    if not periodos_print:
        st.warning("⚠️ Debe seleccionar al menos una columna para poder generar el boletín.")
        return

    col_n = "PROMEDIO" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else periodo_sel
    grado_str = str(curso_sel).upper()
    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
    nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"
    
    URL_LOGO_OFICIAL = obtener_logo_b64_cached("logo.png")
    dict_logros = construir_mapa_logros(st.session_state.get('df_logros', pd.DataFrame()))

    # 🏆 CÁLCULO DE PUESTOS ACADÉMICOS
    df_curso[col_n] = pd.to_numeric(df_curso[col_n], errors='coerce')
    df_agrupado = df_curso.groupby(['Grado', 'Nombre_Completo'])[col_n].mean().reset_index()
    df_agrupado['Puesto'] = df_agrupado.groupby('Grado')[col_n].rank(ascending=False, method='min').fillna(0).astype(int)
    df_agrupado['Total_Grado'] = df_agrupado.groupby('Grado')['Nombre_Completo'].transform('count')
    dict_puestos = {row['Nombre_Completo']: f"{row['Puesto']} de {row['Total_Grado']}" for _, row in df_agrupado.iterrows()}

    # 🎨 NÚCLEO CSS DE COMPRESIÓN TÁCTICA EXTREMA
    css_vip = """<style>
        body { font-family: Arial, sans-serif; background: white; color: black; margin: 0; padding: 0; }
        
        /* Contenedor en Pantalla */
        .b-print { position: relative; padding: 20px; border: 3px solid #0d1b2a; border-radius: 10px; background: white; z-index: 1; margin-bottom: 25px; page-break-inside: avoid !important; }
        .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.04; width: 60%; z-index: -1; pointer-events: none; }
        
        /* Tablas en Pantalla */
        .table-custom { width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 8px; z-index: 2; position: relative; }
        .table-custom th { background-color: #0d1b2a !important; color: white !important; border: 1px solid #000; padding: 4px; font-family: 'Arial Black'; font-size: 11px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .table-custom td { border: 1px solid #000; padding: 4px; text-align: center; font-size: 11px; }
        .materia-title { text-align: left !important; background-color: #f8f9fa !important; font-size: 11px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .logro-row td { text-align: justify !important; font-size: 10px !important; font-style: italic; border-bottom: 1.5px solid #000; background-color: #ffffff !important; padding: 2px 8px !important; font-weight: normal !important; line-height: 1.1 !important; }
        
        .header-table { width: 100%; border: none; margin-bottom: 8px; z-index: 2; position: relative; }
        .header-table td { border: none; padding: 0; }
        .header-table h2 { font-size: 17px !important; }
        .header-table p { font-size: 11px !important; }
        
        .info-box { border: 2px solid #0d1b2a; padding: 6px 10px; background: #f8f9fa !important; display: flex; justify-content: space-between; margin-bottom: 8px; border-radius: 5px; font-size: 11px; -webkit-print-color-adjust: exact; print-color-adjust: exact; box-shadow: 2px 2px 0px #0d1b2a; }
        
        .firmas-container { display: flex; justify-content: space-around; margin-top: 25px; font-size: 11px; z-index: 2; position: relative; page-break-inside: avoid !important; }
        .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 4px; font-weight: bold; color: #0d1b2a; }
        
        /* 🚀 REGLAS DE IMPRESIÓN (APLASTAMIENTO TOTAL) */
        @media print { 
            /* El margin: 0 mata los textos de Fecha y Link de Chrome */
            @page { size: letter portrait; margin: 0 !important; } 
            
            /* Le devolvemos el aire interno para que no quede pegado al borde del papel */
            body { background: white; margin: 0; padding: 8mm 12mm !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; } 
            .no-print { display: none !important; } 
            .b-print { border: none !important; box-shadow: none !important; padding: 0 !important; width: 100% !important; margin: 0 !important; } 
            .salto-pagina { page-break-after: always !important; page-break-inside: avoid !important; } 
            
            /* Compresión Atómica */
            .header-table { margin-bottom: 3px !important; }
            .header-table h2 { font-size: 14px !important; margin: 0 !important; }
            .header-table p { font-size: 10px !important; margin: 0 !important; }
            .info-box { padding: 4px 8px !important; font-size: 10px !important; margin-bottom: 4px !important; border-width: 1.5px !important;}
            .table-custom { margin-top: 0 !important; margin-bottom: 0 !important; }
            .table-custom th { padding: 2px !important; font-size: 9px !important; }
            .table-custom td { padding: 2px !important; font-size: 9.5px !important; }
            .materia-title { font-size: 9.5px !important; }
            .logro-row td { padding: 1px 6px !important; font-size: 8.5px !important; line-height: 1 !important; border-bottom: 1.5px solid #000 !important; }
            .firmas-container { margin-top: 15px !important; font-size: 10px !important; }
            .firma-box { padding-top: 2px !important; }
        }
    </style>"""

    if modo_impresion == "👤 Individual":
        estudiantes = sorted(df_curso['Nombre_Completo'].dropna().unique())
        col_esp1, col_est, col_esp2 = st.columns([1, 8, 1])
        with col_est:
            alumno = st.selectbox("👤 Seleccione el Estudiante para Inspección:", estudiantes, key="sb_alumno_vip")
        
        if alumno:
            puesto_info = dict_puestos.get(alumno, "N/A")
            render_individual(df_curso, alumno, periodo_sel, col_n, dict_logros, nivel_alumno, URL_LOGO_OFICIAL, css_vip, periodos_print, puesto_info)

    else:
        # --- MODO MASIVO ---
        estudiantes = sorted(df_curso['Nombre_Completo'].dropna().unique())
        col_esp1, col_est, col_esp2 = st.columns([1, 8, 1])
        with col_est:
            st.info(f"⚠️ Se compilarán {len(estudiantes)} boletines oficiales. El documento incluirá las siguientes columnas: **{', '.join(periodos_print)}**")

            if st.button("🖨️ INICIAR COMPILACIÓN MASIVA VIP", type="primary", use_container_width=True):
                progress_text = "Preparando motores de compilación..."
                barra_progreso = st.progress(0, text=progress_text)
                
                html_masivo = [f"<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body>",
                               "<div class=\"no-print\" style=\"position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;\">",
                               "    <button onclick=\"imprimirLote()\" style=\"background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black'; transition: 0.2s;\">🖨️ IMPRIMIR LOTE MASIVO COMPLETO</button>",
                               "</div>"]

                img_watermark = f'<img src="{URL_LOGO_OFICIAL}" class="watermark">' if URL_LOGO_OFICIAL else ""
                img_logo = f'<img src="{URL_LOGO_OFICIAL}" width="70">' if URL_LOGO_OFICIAL else ""

                total_alumnos = len(estudiantes)
                th_masivo = "".join([f"<th>{p}</th>" for p in periodos_print])
                col_span_logro = len(periodos_print) + 2

                for i, alum in enumerate(estudiantes):
                    porcentaje = (i + 1) / total_alumnos
                    barra_progreso.progress(porcentaje, text=f"Compilando expediente: {alum} ({i+1}/{total_alumnos})")
                    
                    res = df_curso[df_curso['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                    res = res[res['PROMEDIO'] > 0.0]
                    if res.empty: continue

                    promedios = [float(x) for x in res[col_n] if pd.notna(x)]
                    p_prom = sum(promedios) / len(promedios) if promedios else 0.0
                    salto = "salto-pagina" if i < total_alumnos - 1 else ""
                    
                    puesto_info = dict_puestos.get(alum, "N/A")

                    html_masivo.append(f"""<div class="b-print {salto}">
                    {img_watermark}
                    <table class="header-table">
                        <tr>
                            <td style="width:12%; text-align:left;">{img_logo}</td>
                            <td style="text-align:center; vertical-align:middle;">
                                <h2 style="margin:0; color:#0d1b2a; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                                <p style="margin:2px 0 0 0; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                            </td>
                            <td style="text-align:right; width:15%; vertical-align:middle;">
                                <div style="border:2px solid #0d1b2a; padding:4px; background:#f0f2f6; text-align:center; border-radius:6px;">
                                    <b style="font-size:9px; color:#000;">PROMEDIO</b><br><b style="font-size:16px; color:#d4af37;">{p_prom:.1f}</b>
                                </div>
                            </td>
                        </tr>
                    </table>
                    <div class="info-box">
                        <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span>
                        <span><b style="color:#0d1b2a;">GRADO:</b> {curso_sel}</span>
                        <span><b style="color:#0d1b2a;">PUESTO:</b> <span style="color:#cc0000; font-weight:900;">{puesto_info}</span></span>
                    </div>
                    <table class="table-custom">
                        <tr><th>MATERIA</th>{th_masivo}<th>DESEMPEÑO</th></tr>""")

                    for _, row in res.iterrows():
                        nota_final = float(row.get(col_n, 0)) if pd.notna(row.get(col_n, 0)) else 0.0
                        if nota_final >= 9.1: desp = "SUPERIOR"
                        elif nota_final >= 7.6: desp = "ALTO"
                        elif nota_final >= 6.0: desp = "BÁSICO"
                        else: desp = "BAJO"

                        color = "#006600" if nota_final >= 6.0 else "#cc0000"

                        td_masivo = ""
                        for p in periodos_print:
                            if p == "FINAL":
                                val = float(row.get('PROMEDIO', 0)) if pd.notna(row.get('PROMEDIO', 0)) else 0.0
                                td_masivo += f"<td style='color:{color}; font-weight:bold;'>{val:.1f}</td>"
                            else:
                                val = float(row.get(p, 0)) if pd.notna(row.get(p, 0)) else 0.0
                                td_masivo += f"<td style='font-weight:bold;'>{val:.1f}</td>"

                        html_masivo.append(f"<tr><td class='materia-title'><b>{row['Materia']}</b></td>{td_masivo}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>")

                        materia_limpia = str(row['Materia']).strip().upper()
                        clave_busqueda = (nivel_alumno, materia_limpia, desp)
                        logro_texto = dict_logros.get(clave_busqueda, str(row.get('LOGRO', '')))
                        
                        if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']:
                            logro_texto = "Pendiente de registro."

                        html_masivo.append(f"<tr class='logro-row'><td colspan='{col_span_logro}'><b>LOGRO:</b> {logro_texto}</td></tr>")

                    html_masivo.append("""</table>
                        <div class='firmas-container'>
                            <div class='firma-box'>Firma Rectoría<br><span style='font-size:8px; font-weight:normal;'>Sello Institucional</span></div>
                            <div class='firma-box'>Firma Director de Grupo</div>
                        </div>
                    </div>""")

                html_masivo.append("</body></html>")
                
                barra_progreso.empty()
                st.toast("✅ ¡Compilación Masiva Finalizada con Éxito!", icon="🚀")
                components.html("".join(html_masivo), height=800, scrolling=True)
