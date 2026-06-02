import streamlit as st
import pandas as pd
import io
import base64
import streamlit.components.v1 as components
from xhtml2pdf import pisa

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
    
    css_vip = """<style>body { font-family: Arial, sans-serif; background: white; color: black; } .b-print { position: relative; padding: 30px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; } .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: -1; pointer-events: none; } .table-custom { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; z-index: 2; position: relative; } .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 10px; font-family: 'Arial Black'; } .table-custom td { border: 1px solid #000; padding: 8px; background-color: rgba(255, 255, 255, 0.85); text-align: center; } .header-table { width: 100%; border: none; margin-bottom: 15px; z-index: 2; position: relative; } .header-table td { border: none; } .firmas-container { display: flex; justify-content: space-around; margin-top: 60px; font-size: 14px; z-index: 2; position: relative; page-break-inside: avoid; } .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; } @media print { @page { size: legal portrait; margin: 10mm; } body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } .no-print { display: none !important; } .b-print { border: none; box-shadow: none; padding: 0; } .salto-pagina { page-break-after: always; } } </style>"""    
    
    try:
        with open("logo.png", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
    except: URL_LOGO_OFICIAL = ""

    if modo_impresion == "👤 Individual":
        lista_alumnos = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
        alumno = st.selectbox("👤 Estudiante:", lista_alumnos)
        
        if alumno:
            res = df[df['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0] if 'PROMEDIO' in res.columns else res
            
            promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else []
            p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
            
            th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
            
            html_boletin = f"""<html><head><script>function imprimirBoletin() {{ window.print(); }}</script>{css_vip}</head><body>
            <div class="no-print" style="text-align:right; margin-bottom:10px; position:absolute; top:20px; right:20px; z-index:99;">
                <button onclick="imprimirBoletin()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR REPORTE OFICIAL</button>
            </div>
            <div class="b-print">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table">
                    <tr>
                        <td style="width:15%;"><img src="{URL_LOGO_OFICIAL}" width="90"></td>
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
                <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""
            
            grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
            es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
            nivel_alumno = "Primaria" if es_primaria else "Bachillerato"

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
                    td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                    col_span = 7
                else:
                    td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                    col_span = 3
                
                html_boletin += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"                    
                
                logro_texto = 'Sin registro'
                try:
                    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
                        df_l = st.session_state.df_logros
                        filtro = df_l[(df_l.iloc[:, 0].astype(str).str.strip().str.upper() == nivel_alumno.upper()) & 
                                      (df_l.iloc[:, 1].astype(str).str.strip().str.upper() == str(row['Materia']).strip().upper()) & 
                                      (df_l.iloc[:, 2].astype(str).str.strip().str.upper() == desp.upper())]
                        if not filtro.empty: logro_texto = str(filtro.iloc[0, 3])
                        else: logro_texto = "Logro no encontrado en base de datos"
                except: logro_texto = row.get('LOGRO', 'Error al buscar logro')

                html_boletin += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
            
            html_boletin += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div></body></html>"""

            pdf_data = generar_pdf(html_boletin)
            if pdf_data:
                col_espacio_vacio, col_boton_pequeno = st.columns([8, 2])
                with col_boton_pequeno:
                    st.download_button(label="📥 DESCARGAR PDF", data=pdf_data, file_name=f"Boletin_{alumno}_{periodo_sel}.pdf", mime="application/pdf", type="primary", use_container_width=True)
            
            components.html(html_boletin, height=600, scrolling=True)
            
    else:
        estudiantes = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
        st.warning(f"⚠️ Se generarán {len(estudiantes)} boletines VIP para el grado {curso_sel}.")
        
        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary"):
            th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
            html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body><div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;"><button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR LOTE MASIVO</button></div>"""
            
            for i, alum in enumerate(estudiantes):
                res = df[df['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                res = res[res['PROMEDIO'] > 0.0] if 'PROMEDIO' in res.columns else res
                promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else []
                p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
                salto = "salto-pagina" if i < len(estudiantes) - 1 else ""
                
                html_masivo += f"""<div class="b-print {salto}">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table"><tr><td style="width:15%;"><img src="{URL_LOGO_OFICIAL}" width="90"></td>
                <td style="text-align:center;"><h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL OMEGA 2026</h2>
                <p style="margin:0; font-size:14px; color:#d4af37; font-family:'Arial Black';">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p></td>
                <td style="text-align:right; width:15%;"><div style="border:3px solid #0d1b2a; padding:8px; background:#f0f2f6; text-align:center; border-radius:8px;">
                <b style="font-size:12px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b></div></td></tr></table>
                <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px;">
                <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span></div>
                <table class="table-custom"><tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""
                
                grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
                es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
                nivel_alumno = "Primaria" if es_primaria else "Bachillerato"

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
                        td = f"<td>{p1:.1f}</td><td>{p2:.1f}</td><td>{p3:.1f}</td><td>{p4:.1f}</td><td style='color:{color}; font-weight:bold;'>{prom:.1f}</td>"
                        col_span = 7
                    else:
                        td = f"<td style='color:{color}; font-weight:bold;'>{nota_final:.1f}</td>"
                        col_span = 3

                    html_masivo += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
                    
                    logro_texto = 'Sin registro'
                    try:
                        if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
                            df_l = st.session_state.df_logros
                            filtro = df_l[(df_l.iloc[:, 0].astype(str).str.strip().str.upper() == nivel_alumno.upper()) & 
                                          (df_l.iloc[:, 1].astype(str).str.strip().str.upper() == str(row['Materia']).strip().upper()) & 
                                          (df_l.iloc[:, 2].astype(str).str.strip().str.upper() == desp.upper())]
                            if not filtro.empty: logro_texto = str(filtro.iloc[0, 3])
                    except: pass
                        
                    html_masivo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
                    
                html_masivo += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div>"""
                
            html_masivo += "</body></html>"
            components.html(html_masivo, height=600, scrolling=True)
