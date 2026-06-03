import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import unicodedata
import base64

# --- FUNCIONES DE UTILIDAD PÚBLICA ---

def limpiar_texto(txt):
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def nota_limpia(valor):
    try:
        n = float(valor)
        return 0.0 if pd.isna(n) else n
    except (ValueError, TypeError): # 🔧 Mejor especificar la excepción
        return 0.0

def obtener_desempeno(nota):
    """ 🔧 Centralizamos la lógica del negocio de calificaciones """
    if nota >= 9.1: return "SUPERIOR", "#155724"
    if nota >= 7.6: return "ALTO", "#155724"
    if nota >= 6.0: return "BÁSICO", "#155724"
    return "BAJO", "#721c24"

def obtener_logo_b64(ruta_imagen="logo.png"):
    """ 🔧 Aislamos la carga de la imagen """
    try:
        with open(ruta_imagen, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        return ""

# --- MOTOR DE RENDERIZADO HTML ---

def construir_html_boletin_estudiante(df_estudiante, alumno, curso_sel, periodo_sel, col_n, css_vip, url_logo, dict_logros, es_primaria, salto_pagina=False):
    """ 🔧 Esta función hace una sola cosa: construir el HTML de UN estudiante """
    if df_estudiante.empty: return ""
    
    promedios = [nota_limpia(x) for x in df_estudiante[col_n]] if col_n in df_estudiante.columns else [0.0]
    p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
    
    nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"
    es_consolidado = "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper()
    
    th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if es_consolidado else f"<th>{periodo_sel}</th>"
    clase_salto = "salto-pagina" if salto_pagina else ""

    html = f"""
    <div class="b-print {clase_salto}">
        <img src="{url_logo}" class="watermark">
        <table class="header-table">
            <tr>
                <td style="width:12%;"><img src="{url_logo}" width="80"></td>
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
            <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>
    """

    for _, row in df_estudiante.iterrows():
        materia = str(row['Materia']).strip().upper()
        nota_final = nota_limpia(row.get(col_n, 0)) if col_n in df_estudiante.columns else 0.0
        desp, color = obtener_desempeno(nota_final)

        if es_consolidado:
            p1, p2, p3, p4 = [nota_limpia(row.get(p, 0)) for p in ['P1', 'P2', 'P3', 'P4']]
            prom = nota_limpia(row.get('PROMEDIO', 0))
            td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
            col_span = 7
        else:
            td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
            col_span = 3

        html += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"

        # 🚀 Búsqueda ultrarrápida usando el diccionario
        clave_logro = (nivel_alumno, materia, desp)
        logro_texto = dict_logros.get(clave_logro, row.get('LOGRO', 'Sin registro'))

        html += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:10.5px; font-style:italic; border-bottom:1.5px solid #000; background-color:#fafafa; padding:4px 8px; line-height:1.1;'><b>LOGRO:</b> {logro_texto}</td></tr>"

    html += """
        </table>
        <div class='firmas-container'>
            <div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div>
            <div class='firma-box'>Firma Director de Grupo</div>
        </div>
    </div>
    """
    return html

# --- FUNCIÓN PRINCIPAL DE INTERFAZ ---

def renderizar(df_filtrado, curso_sel, periodo_sel):
    
    # Manejo de la base
    df_base = st.session_state.get('df_maestro', df_filtrado).copy()
    if str(curso_sel) != "TODOS":
        df_base = df_base[df_base['Grado'].astype(str) == str(curso_sel)]

    col_n = "PROMEDIO" if "CONSOLID" in str(periodo_sel).upper() or "FINAL" in str(periodo_sel).upper() else periodo_sel
    grado_str = str(curso_sel).upper()
    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])

    # 🚀 OPTIMIZACIÓN: Crear diccionario de logros una sola vez para consultas en O(1)
    dict_logros = {}
    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
        df_l = st.session_state.df_logros
        for _, fila in df_l.iterrows():
            if len(fila) >= 4:
                # Clave: (NIVEL, MATERIA, DESEMPEÑO)
                clave = (str(fila.iloc[0]).strip().upper(), str(fila.iloc[1]).strip().upper(), str(fila.iloc[2]).strip().upper())
                dict_logros[clave] = str(fila.iloc[3])

    url_logo = obtener_logo_b64()
    
    # CSS VIP
    css_vip = """... (AQUÍ PONES EXACTAMENTE EL MISMO CSS QUE YA TENÍAS) ..."""

    # UI Controls
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    c_modo, c_est = st.columns([2, 8])
    with c_modo:
        modo_impresion = st.radio("Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Lógica de renderizado
    if modo_impresion == "👤 Individual":
        with c_est:
            alumno = st.selectbox("👤 Seleccione el Estudiante para Inspección:", sorted(df_base['Nombre_Completo'].dropna().unique()))
        
        if alumno:
            df_est = df_base[df_base['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            df_est = df_est[df_est['PROMEDIO'] > 0.0]
            
            cuerpo_html = construir_html_boletin_estudiante(df_est, alumno, curso_sel, periodo_sel, col_n, css_vip, url_logo, dict_logros, es_primaria)
            
            html_final = f"""<html><head><script>function imprimir() {{ window.print(); }}</script>{css_vip}</head><body>
            <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:12px; right:20px; z-index:99;">
                <button onclick="imprimir()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold;">🖨️ IMPRIMIR / GUARDAR PDF</button>
            </div>
            {cuerpo_html}</body></html>"""
            
            components.html(html_final, height=750, scrolling=True)

    else:
        estudiantes = sorted(df_base['Nombre_Completo'].dropna().unique())
        with c_est:
            st.warning(f"⚠️ Se compilarán {len(estudiantes)} boletines oficiales de rango Oficio para el grado {curso_sel}.")

        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary", use_container_width=True):
            html_final = f"""<html><head><script>function imprimir() {{ window.print(); }}</script>{css_vip}</head><body>
            <div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;">
                <button onclick="imprimir()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:8px 16px; cursor:pointer; border-radius:6px; font-weight:bold;">🖨️ IMPRIMIR LOTE MASIVO COMPLETO</button>
            </div>"""

            for i, alum in enumerate(estudiantes):
                df_est = df_base[df_base['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                df_est = df_est[df_est['PROMEDIO'] > 0.0]
                if df_est.empty: continue
                
                salto = True if i < len(estudiantes) - 1 else False
                html_final += construir_html_boletin_estudiante(df_est, alum, curso_sel, periodo_sel, col_n, css_vip, url_logo, dict_logros, es_primaria, salto_pagina=salto)
            
            html_final += "</body></html>"
            components.html(html_final, height=750, scrolling=True)
