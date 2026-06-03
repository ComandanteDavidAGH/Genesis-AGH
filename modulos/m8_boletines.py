import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import unicodedata
import base64

# --- 1. OPTIMIZACIÓN DE MEMORIA Y CACHÉ ---
# Al usar st.cache_data, Streamlit guarda en memoria el logo. Solo se procesa una vez en la vida de la app.
@st.cache_data
def obtener_logo_b64_cached(ruta_imagen="logo.png"):
    try:
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{b64_string}"
    except Exception:
        return ""

# Almacenamos el diccionario de logros en caché para no reconstruirlo en cada clic
@st.cache_data
def construir_mapa_logros(df_logros_raw):
    dict_logros = {}
    if df_logros_raw is not None and not df_logros_raw.empty:
        for _, fila in df_logros_raw.iterrows():
            if len(fila) >= 4:
                # Clave: (NIVEL, MATERIA, DESEMPEÑO) en mayúsculas y sin espacios
                clave = (
                    str(fila.iloc[0]).strip().upper(), 
                    str(fila.iloc[1]).strip().upper(), 
                    str(fila.iloc[2]).strip().upper()
                )
                dict_logros[clave] = str(fila.iloc[3])
    return dict_logros

def limpiar_texto(txt):
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def nota_limpia(valor):
    try:
        n = float(valor)
        return 0.0 if pd.isna(n) else n
    except:
        return 0.0

# --- 2. FUNCIÓN DE RENDERIZADO OPTIMIZADA ---
def renderizar(df_filtrado, curso_sel, periodo_sel):
    # Traer base maestra de manera segura
    if 'df_maestro' in st.session_state and st.session_state.df_maestro is not None:
        df_base_boletines = st.session_state.df_maestro.copy()
    else:
        df_base_boletines = df_filtrado.copy()

    # Filtrado inicial por curso (Operación rápida)
    if str(curso_sel) != "TODOS":
        df_base_boletines = df_base_boletines[df_base_boletines['Grado'].astype(str) == str(curso_sel)]

    col_n = "PROMEDIO" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else periodo_sel

    # Carga ultra veloz del logo usando la caché
    URL_LOGO_OFICIAL = obtener_logo_b64_cached("logo.png")

    # Construcción ultra veloz del mapa de logros desde el session_state
    df_logros_raw = st.session_state.get('df_logros', pd.DataFrame())
    dict_logros = construir_mapa_logros(df_logros_raw)

    # Definición de estilos CSS (Se queda igual)
    css_vip = """<style>
        body { font-family: Arial, sans-serif; background: white; color: black; margin: 0; padding: 0; }
        .b-print { position: relative; padding: 25px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; page-break-inside: avoid !important; }
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
            .salto-pagina { page-break-after: always !always; page-break-inside: avoid !important; } 
        }
    </style>"""

    th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else f"<th>{periodo_sel}</th>"

    # Selector de Modo
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_est = st.columns([3, 7])
    with c_modo:
        modo_impresion = st.radio("Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Identificación del nivel escolar (Primaria / Bachillerato)
    grado_str = str(curso_sel).upper()
    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
    nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"

    if modo_impresion == "👤 Individual":
        # Obtener lista de estudiantes únicos de forma rápida
        lista_estudiantes = sorted(df_base_boletines['Nombre_Completo'].dropna().unique())
        
        with c_est:
            alumno = st.selectbox("👤 Seleccione el Estudiante para Inspección:", lista_estudiantes, key="sb_alumno_individual")
        
        if alumno:
            # Filtrado indexado ultrarrápido por el alumno seleccionado
            res = df_base_boletines[df_base_boletines['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0]
            
            if not res.empty:
                promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
                p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0

                html_boletin = f"""<html><head><script>function imprimirBoletin() {{ window.print(); }}</script>{css_vip}</head><body>
                <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:12px; right:20px; z-index:99;">
                    <button onclick="imprimirBoletin()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black'; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">🖨️ IMPRIMIR / GUARDAR PDF</button>
                </div>
                <div class="b-print">
                    <img src="{URL_LOGO_OFICIAL}" class="watermark">
                    <table class="header-table">
                        <tr>
                            <td style="width:12%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                            <td style="text-align:center; vertical-align:middle;">
                                <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                                <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                            </td>
                            <td style="text-align:right; width:15%; vertical-align:middle;">
                                <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px; box-shadow: 2px 2px 0px #0d1b2a;">
                                    <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                                </div>
                            </td>
                        </tr>
                    </table>
                    <div style="border:2px solid #0d1b2a; padding:8px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; font-size:12px;">
                        <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span><span><b style="color:#0d1b2a;">GRADO:</b> {curso_sel}</span>
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

                    if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper():
                        p1, p2, p3, p4 = [nota_limpia(row.get(p, 0)) for p in ['P1', 'P2', 'P3', 'P4']]
                        prom = nota_limpia(row.get('PROMEDIO', 0))
                        td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                        col_span = 7
                    else:
                        td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                        col_span = 3

                    html_boletin += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"

                    # 🚀 CRUCE EN O(1): Búsqueda instantánea en el diccionario de caché
                    materia_limpia = str(row['Materia']).strip().upper()
                    clave_busqueda = (nivel_alumno, materia_limpia, desp)
                    logro_texto = dict_logros.get(clave_busqueda, row.get('LOGRO', 'Logro no encontrado en base de datos'))

                    html_boletin += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px; line-height:1.1;'><b>LOGRO:</b> {logro_texto}</td></tr>"

                html_boletin += """
                    </table>
                    <div class='firmas-container'>
                        <div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div>
                        <div class='firma-box'>Firma Director de Grupo</div>
                    </div>
                </div></body></html>"""

                # Renderizado limpio en el iframe
                components.html(html_boletin, height=750, scrolling=True)

    else:
        # --- MODO MASIVO (Aislado para que no consuma recursos en modo individual) ---
        estudiantes = sorted(df_base_boletines['Nombre_Completo'].dropna().unique())
        with c_est:
            st.warning(f"⚠️ Se compilarán {len(estudiantes)} boletines oficiales para el grado {curso_sel}.")

        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary", use_container_width=True):
            html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body>
            <div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;">
                <button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black'; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">🖨️ IMPRIMIR LOTE MASIVO COMPLETO</button>
            </div>"""

            for i, alum in enumerate(estudiantes):
                res = df_base_boletines[df_base_boletines['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                res = res[res['PROMEDIO'] > 0.0]
                if res.empty: continue

                promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
                p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
                salto = "salto-pagina" if i < len(estudiantes) - 1 else ""

                html_masivo += f"""<div class="b-print {salto}">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table">
                    <tr>
                        <td style="width:12%;"><img src="{URL_LOGO_OFICIAL}" width="80"></td>
                        <td style="text-align:center; vertical-align:middle;">
                            <h2 style="margin:0; color:#0d1b2a; font-size:19px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                            <p style="margin:4px 0 0 0; font-size:13px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                        </td>
                        <td style="text-align:right; width:15%; vertical-align:middle;">
                            <div style="border:2.5px solid #0d1b2a; padding:6px; background:#f0f2f6; text-align:center; border-radius:8px; box-shadow: 2px 2px 0px #0d1b2a;">
                                <b style="font-size:10px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
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

                    if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper():
                        p1, p2, p3, p4 = [nota_limpia(row.get(p, 0)) for p in ['P1', 'P2', 'P3', 'P4']]
                        prom = nota_limpia(row.get('PROMEDIO', 0))
                        td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                        col_span = 7
                    else:
                        td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                        col_span = 3

                    html_masivo += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"

                    # 🚀 CRUCE EN O(1) PARA LOTE MASIVO
                    materia_limpia = str(row['Materia']).strip().upper()
                    clave_busqueda = (nivel_alumno, materia_limpia, desp)
                    logro_texto = dict_logros.get(clave_busqueda, row.get('LOGRO', 'Logro no encontrado'))

                    html_masivo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px; line-height:1.1;'><b>LOGRO:</b> {logro_texto}</td></tr>"

                html_masivo += """</table>
                    <div class='firmas-container'>
                        <div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div>
                        <div class='firma-box'>Firma Director de Grupo</div>
                    </div>
                </div>"""

            html_masivo += "</body></html>"
            components.html(html_masivo, height=750, scrolling=True)
