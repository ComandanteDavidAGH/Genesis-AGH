import streamlit as st
import pandas as pd
import io
import base64
from xhtml2pdf import pisa

# 🚀 CACHÉ PARA LOGO (Solo para el PDF)
@st.cache_data
def get_logo_base64():
    try:
        with open("logo.png", "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except: return ""

def generar_pdf(html_contenido):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_contenido.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def nota_limpia(valor):
    try:
        n = float(valor)
        return 0.0 if pd.isna(n) else n
    except: return 0.0

def renderizar(df, curso_sel, periodo_sel):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Central de Impresión VIP</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No hay datos para generar boletines en este filtro.")
        return

    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    modo_impresion = st.radio("Seleccione el modo de generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True)
    
    # 🛑 CLAVE DEL RENDIMIENTO: Separar la imagen de la pantalla y la imagen del PDF
    URL_LOGO_PDF = get_logo_base64()
    URL_LOGO_PREVIEW = "https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png"

    # CSS SEGURO PARA PANTALLA (Renderizado ultrarrápido)
    css_preview = """<style> .b-print { position: relative; padding: 20px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; background: white; color: black; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); font-family: Arial, sans-serif; overflow: hidden; } .watermark-img { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: 0; pointer-events: none; } .table-custom { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; z-index: 2; position: relative; } .table-custom th { background-color: #0d1b2a !important; color: #d4af37 !important; border: 1px solid #000; padding: 10px; font-family: 'Arial Black'; } .table-custom td { border: 1px solid #000; padding: 8px; text-align: center; color: black; } .header-table { width: 100%; border: none; margin-bottom: 15px; z-index: 2; position: relative; } .header-table td { border: none; } .firmas-container { display: flex; justify-content: space-around; margin-top: 50px; font-size: 14px; z-index: 2; position: relative; } .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; } </style>"""

    # 🚀 DICCIONARIO O(1) PARA VELOCIDAD EXTREMA EN LOS LOGROS
    dict_logros = {}
    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
        try:
            df_l = st.session_state.df_logros.copy()
            df_l.iloc[:,0] = df_l.iloc[:,0].astype(str).str.strip().str.upper()
            df_l.iloc[:,1] = df_l.iloc[:,1].astype(str).str.strip().str.upper()
            df_l.iloc[:,2] = df_l.iloc[:,2].astype(str).str.strip().str.upper()
            df_l.iloc[:,3] = df_l.iloc[:,3].astype(str)
            dict_logros = df_l.set_index([df_l.columns[0], df_l.columns[1], df_l.columns[2]])[df_l.columns[3]].to_dict()
        except: pass

    if modo_impresion == "👤 Individual":
        lista_alumnos = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
        alumno = st.selectbox("👤 Estudiante:", lista_alumnos)
        
        if alumno:
            res = df[df['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0] if 'PROMEDIO' in res.columns else res
            
            promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else []
            p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
            
            th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
            
            html_cuerpo = f"""
            <div class="b-print">
                <img src="__LOGO_URL__" class="watermark-img">
                <table class="header-table">
                    <tr>
                        <td style="width:15%;"><img src="__LOGO_URL__" width="90"></td>
                        <td style="text-align:center;">
                            <h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL OMEGA 2026</h2>
                            <p style="margin:0; font-size:14px; color:#d4af37; font-family:'Arial Black';">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                        </td>
                        <td style="text-align:right; width:15%;">
                            <div style="border:3px solid #0d1b2a; padding:8px; background:#f0f2f6; text-align:center; border-radius:8px;">
                                <b style="font-size:12px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                            </div>
                        </td>
                    </tr>
                </table>
                <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; position: relative; z-index: 2;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""
            
            grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
            es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
            nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"

            for index, row in res.iterrows():
                nota_final = nota_limpia(row.get(col_n, 0))
                if nota_final >= 9.1: desp = "SUPERIOR"
                elif nota_final >= 7.6: desp = "ALTO"
                elif nota_final >= 6.0: desp = "BÁSICO"
                else: desp = "BAJO"

                color = "#155724" if nota_final >= 6.0 else "#721c24"
                
                if periodo_sel == "CONSOLIDADO FINAL":
                    p1 = nota_limpia(row.get('P1', 0)); p2 = nota_limpia(row.get('P2', 0))
                    p3 = nota_limpia(row.get('P3', 0)); p4 = nota_limpia(row.get('P4', 0))
                    prom = nota_limpia(row.get('PROMEDIO', 0))
                    td = f"<td style='color:black;'>{p1:.1f}</td><td style='color:black;'>{p2:.1f}</td><td style='color:black;'>{p3:.1f}</td><td style='color:black;'>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                    col_span = 7
                else:
                    td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                    col_span = 3
                
                html_cuerpo += f"<tr><td style='text-align:left; color:black;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"                    
                
                # Búsqueda ultra rápida en el diccionario
                llave_logro = (nivel_alumno, str(row['Materia']).strip().upper(), desp)
                logro_texto = dict_logros.get(llave_logro, "Logro no registrado")

                html_cuerpo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa; color:black;'><b>LOGRO:</b> {logro_texto}</td></tr>"
            
            html_cuerpo += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div>"""

            # 🎯 DIBUJO INSTANTÁNEO EN LA PANTALLA (Reemplaza la etiqueta con URL web ligera)
            html_pantalla = html_cuerpo.replace("__LOGO_URL__", URL_LOGO_PREVIEW)
            st.markdown(css_preview + html_pantalla, unsafe_allow_html=True)
            
            # 🎯 GENERADOR DE PDF (Reemplaza la etiqueta con el código Base64 pesado)
            with st.expander("📥 Generar Archivo PDF Descargable"):
                if st.button("Generar archivo .pdf (Toma unos segundos)"):
                    with st.spinner("Compilando Documento PDF Oficial..."):
                        html_para_pdf = html_cuerpo.replace("__LOGO_URL__", URL_LOGO_PDF)
                        css_para_pdf = css_preview.replace(".b-print {", ".b-print { border:none; box-shadow:none; padding:0;").replace("position: relative;", "")
                        html_completo_pdf = f"<html><head><style>@page {{ size: legal portrait; margin: 10mm; }} {css_para_pdf.replace('<style>','').replace('</style>','')}</style></head><body style='background:white;'>{html_para_pdf}</body></html>"
                        
                        pdf_data = generar_pdf(html_completo_pdf)
                        if pdf_data:
                            st.download_button(label="📥 DESCARGAR PDF AHORA", data=pdf_data, file_name=f"Boletin_{alumno}_{periodo_sel}.pdf", mime="application/pdf", type="primary", use_container_width=True)
            
    else:
        # MODO MASIVO EXACTAMENTE IGUAL OPTIMIZADO
        estudiantes = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
        st.warning(f"⚠️ Se generarán {len(estudiantes)} boletines VIP para el grado {curso_sel}.")
        
        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary"):
            with st.spinner("Construyendo lote masivo ultrarrápido..."):
                th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
                
                html_masivo = ""
                for i, alum in enumerate(estudiantes):
                    res = df[df['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                    res = res[res['PROMEDIO'] > 0.0] if 'PROMEDIO' in res.columns else res
                    promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else []
                    p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
                    salto = "<div style='page-break-after: always;'></div>" if i < len(estudiantes) - 1 else ""
                    
                    html_masivo += f"""<div class="b-print">
                    <img src="__LOGO_URL__" class="watermark-img">
                    <table class="header-table"><tr><td style="width:15%;"><img src="__LOGO_URL__" width="90"></td>
                    <td style="text-align:center;"><h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL OMEGA 2026</h2>
                    <p style="margin:0; font-size:14px; color:#d4af37; font-family:'Arial Black';">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p></td>
                    <td style="text-align:right; width:15%;"><div style="border:3px solid #0d1b2a; padding:8px; background:#f0f2f6; text-align:center; border-radius:8px;">
                    <b style="font-size:12px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b></div></td></tr></table>
                    <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px; position: relative; z-index: 2;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span></div>
                    <table class="table-custom"><tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""
                    
                    grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
                    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
                    nivel_alumno = "PRIMARIA" if es_primaria else "BACHILLERATO"

                    for _, row in res.iterrows():
                        nota_final = nota_limpia(row.get(col_n, 0))
                        if nota_final >= 9.1: desp = "SUPERIOR"
                        elif nota_final >= 7.6: desp = "ALTO"
                        elif nota_final >= 6.0: desp = "BÁSICO"
                        else: desp = "BAJO"
                        color = "#155724" if nota_final >= 6.0 else "#721c24"

                        if periodo_sel == "CONSOLIDADO FINAL":
                            p1 = nota_limpia(row.get('P1', 0)); p2 = nota_limpia(row.get('P2', 0))
                            p3 = nota_limpia(row.get('P3', 0)); p4 = nota_limpia(row.get('P4', 0))
                            prom = nota_limpia(row.get('PROMEDIO', 0))
                            td = f"<td style='color:black;'>{p1:.1f}</td><td style='color:black;'>{p2:.1f}</td><td style='color:black;'>{p3:.1f}</td><td style='color:black;'>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                            col_span = 7
                        else:
                            td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                            col_span = 3

                        html_masivo += f"<tr><td style='text-align:left; color:black;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
                        
                        llave_logro = (nivel_alumno, str(row['Materia']).strip().upper(), desp)
                        logro_texto = dict_logros.get(llave_logro, "Logro no registrado")
                            
                        html_masivo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa; color:black;'><b>LOGRO:</b> {logro_texto}</td></tr>"
                        
                    html_masivo += f"</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div>{salto}"
                    
                html_para_pdf = html_masivo.replace("__LOGO_URL__", URL_LOGO_PDF)
                css_para_pdf = css_preview.replace(".b-print {", ".b-print { border:none; box-shadow:none; padding:0;").replace("position: relative;", "")
                html_pdf = f"<html><head><style>@page {{ size: legal portrait; margin: 10mm; }} {css_para_pdf.replace('<style>','').replace('</style>','')}</style></head><body style='background:white;'>{html_para_pdf}</body></html>"
                
                pdf_data = generar_pdf(html_pdf)
                if pdf_data:
                    st.download_button(label="📥 DESCARGAR LOTE EN PDF", data=pdf_data, file_name=f"Boletines_Masivos_{curso_sel}_{periodo_sel}.pdf", mime="application/pdf", type="primary", use_container_width=True)
