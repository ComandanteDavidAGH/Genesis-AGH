import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import io
from xhtml2pdf import pisa

# =========================================================
# ⚡ ACELERADORES DE MEMORIA EXTREMA (Evita congelamientos)
# =========================================================
@st.cache_data
def construir_mapa_logros(df_logros_raw):
    """Procesa los logros una sola vez y los guarda en la memoria caché"""
    diccionario = {}
    if df_logros_raw is not None and not df_logros_raw.empty:
        for _, l_row in df_logros_raw.iterrows():
            try:
                k = (str(l_row.iloc[0]).strip().upper(), str(l_row.iloc[1]).strip().upper(), str(l_row.iloc[2]).strip().upper())
                diccionario[k] = str(l_row.iloc[3])
            except: pass
    return diccionario

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
    except:
        return 0.0

# =========================================================
# 👑 MOTOR PRINCIPAL DE BOLETINES
# =========================================================
def renderizar(df_m, curso_sel, periodo_sel):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Central de Impresión VIP</h3>", unsafe_allow_html=True)
    
    # --- PANEL DE CONTROL ---
    st.markdown("<div class='no-print' style='background:#f8f9fa; padding:12px; border-radius:8px; border: 2px solid #0d1b2a; margin-bottom:15px;'>", unsafe_allow_html=True)
    c_print_1, c_print_2 = st.columns([4, 6])
    with c_print_1:
        modo_impresion = st.radio("🛠️ Modo de Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True)
    with c_print_2:
        col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
        opciones_p = ["P1", "P2", "P3", "P4", "FINAL"]
        def_p = ["P1", "P2", "P3", "P4", "FINAL"] if "CONSOLID" in str(periodo_sel).upper() else [periodo_sel]
        def_p = [p for p in def_p if p in opciones_p]
        if not def_p: def_p = ["FINAL"]
        periodos_print = st.multiselect("📊 Columnas a Imprimir en el Reporte:", opciones_p, default=def_p)
    st.markdown("</div>", unsafe_allow_html=True)

    if not periodos_print:
        st.warning("⚠️ Seleccione al menos un periodo para compilar.")
        st.stop()

    # --- CSS ESTABLE (TAMAÑO LEGAL / OFICIO) ---
    css_vip = """<style>body { font-family: Arial, sans-serif; background: white; color: black; } .b-print { position: relative; padding: 30px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; } .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: -1; pointer-events: none; } .table-custom { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; z-index: 2; position: relative; } .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 10px; font-family: 'Arial Black'; } .table-custom td { border: 1px solid #000; padding: 8px; background-color: rgba(255, 255, 255, 0.85); text-align: center; } .header-table { width: 100%; border: none; margin-bottom: 15px; z-index: 2; position: relative; } .header-table td { border: none; } .firmas-container { display: flex; justify-content: space-around; margin-top: 60px; font-size: 14px; z-index: 2; position: relative; page-break-inside: avoid; } .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; } @media print { @page { size: legal portrait; margin: 10mm; } body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } .no-print { display: none !important; } .b-print { border: none; box-shadow: none; padding: 0; } .salto-pagina { page-break-after: always; } }</style>"""   

    # --- CARGA DE DATOS ---
    df_boletines_base = df_m.copy() if df_m is not None else pd.DataFrame()
    if str(curso_sel) != "TODOS":
        df_boletines_base = df_boletines_base[df_boletines_base['Grado'].astype(str) == str(curso_sel)]
    
    # Motor de Puestos Matemáticos
    mapa_puestos = {}
    if not df_boletines_base.empty and col_n in df_boletines_base.columns:
        df_boletines_base[col_n] = pd.to_numeric(df_boletines_base[col_n], errors='coerce').fillna(0.0)
        df_puestos_calc = df_boletines_base.groupby(['Grado', 'Nombre_Completo'])[col_n].mean().reset_index()
        df_puestos_calc['Puesto'] = df_puestos_calc.groupby('Grado')[col_n].rank(ascending=False, method='min').astype(int)
        df_puestos_calc['Total_Grado'] = df_puestos_calc.groupby('Grado')['Nombre_Completo'].transform('count')
        mapa_puestos = {row['Nombre_Completo']: f"{row['Puesto']} de {row['Total_Grado']}" for _, row in df_puestos_calc.iterrows()}

    # 🚀 USO DE CACHÉ Y URL PARA MAXIMIZAR VELOCIDAD
    diccionario_logros = construir_mapa_logros(st.session_state.get('df_logros', pd.DataFrame()))
    
    # 🎯 EL SALVAVIDAS: Usamos el enlace web del logo en vez de incrustarlo
    URL_LOGO_OFICIAL = "https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png"

    th_dinamico = "".join([f"<th>{p}</th>" for p in periodos_print])
    col_span_logro = len(periodos_print) + 2

    # ==========================================
    # 👤 MODO INDIVIDUAL
    # ==========================================
    if modo_impresion == "👤 Individual":
        estudiantes_lista = sorted(df_boletines_base['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df_boletines_base.columns else []
        alumno = st.selectbox("👤 Estudiante:", estudiantes_lista)
        
        if alumno:
            res = df_boletines_base[df_boletines_base['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0]
            
            promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
            p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
            puesto_estudiante = mapa_puestos.get(alumno, "N/A")
            
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
                            <h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                            <p style="margin:0; font-size:14px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                        </td>
                        <td style="text-align:right; width:15%;">
                            <div style="border:3px solid #0d1b2a; padding:8px; background:#f0f2f6; text-align:center; border-radius:8px;">
                                <b style="font-size:12px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                            </div>
                        </td>
                    </tr>
                </table>
                <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px;">
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alumno}</span>
                    <span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span>
                    <span><b style="color:#0d1b2a;">PUESTO:</b> <span style="color:#cc0000; font-weight:bold;">{puesto_estudiante}</span></span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th_dinamico}<th>DESEMPEÑO</th></tr>"""
            
            grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
            es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
            nivel_alumno = "Primaria" if es_primaria else "Bachillerato"

            for index, row in res.iterrows():
                nota_final = nota_limpia(row.get(col_n, 0))
                desp = "SUPERIOR" if nota_final >= 9.1 else ("ALTO" if nota_final >= 7.6 else ("BÁSICO" if nota_final >= 6.0 else "BAJO"))
                color = "#155724" if nota_final >= 6.0 else "#721c24"
                
                td_dinamico = ""
                for p in periodos_print:
                    if p == "FINAL":
                        val_p = nota_limpia(row.get('PROMEDIO', 0))
                        td_dinamico += f"<td style='color:{color}; font-weight:bold;'>{val_p:.1f}</td>"
                    else:
                        val_p = nota_limpia(row.get(p, 0))
                        td_dinamico += f"<td>{val_p:.1f}</td>"
                
                html_boletin += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td_dinamico}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
                
                llave_busqueda = (nivel_alumno.upper(), str(row['Materia']).strip().upper(), desp.upper())
                logro_texto = diccionario_logros.get(llave_busqueda, str(row.get('LOGRO', '')))
                if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']: logro_texto = "Pendiente de registro."
                
                html_boletin += f"<tr><td colspan='{col_span_logro}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
            
            html_boletin += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div></body></html>"""
            
            # --- ZONA DE DESCARGAS OPTIMIZADA ---
            col_info, col_btn_prep, col_btn_down = st.columns([5, 3, 3])
            with col_info:
                st.info("💡 Use **'🖨️ IMPRIMIR REPORTE'** dentro del boletín para máxima calidad inmediata.")
            with col_btn_prep:
                if st.button("⚙️ Procesar Archivo PDF (.pdf)", use_container_width=True):
                    with st.spinner("Construyendo el archivo PDF pesado..."):
                        st.session_state[f'pdf_generado_{alumno}'] = generar_pdf(html_boletin)
            with col_btn_down:
                if f'pdf_generado_{alumno}' in st.session_state:
                    st.download_button(label="📥 DESCARGAR PDF", data=st.session_state[f'pdf_generado_{alumno}'], file_name=f"Boletin_{alumno}_{periodo_sel}.pdf", mime="application/pdf", type="primary", use_container_width=True)
            
            # Muestra el HTML
            components.html(html_boletin, height=750, scrolling=True)

    # ==========================================
    # 🖨️ MODO MASIVO
    # ==========================================
    else:
        estudiantes = sorted(df_boletines_base['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df_boletines_base.columns else []
        st.warning(f"⚠️ Se compilarán {len(estudiantes)} boletines en formato LEGAL para el grado {curso_sel}.")
        
        if st.button("🖨️ INICIAR COMPILACIÓN MASIVA VIP", type="primary", use_container_width=True):
            with st.spinner("Generando documentos oficiales... La velocidad dependerá del tamaño del grupo."):
                html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body><div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;"><button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR LOTE MASIVO</button></div>"""
                
                for i, alum in enumerate(estudiantes):
                    res = df_boletines_base[df_boletines_base['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                    res = res[res['PROMEDIO'] > 0.0]
                    if res.empty: continue
                    
                    promedios = [nota_limpia(x) for x in res[col_n]] if col_n in res.columns else [0.0]
                    p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
                    salto = "salto-pagina" if i < len(estudiantes) - 1 else ""
                    puesto_estudiante = mapa_puestos.get(alum, "N/A")
                    
                    html_masivo += f"""<div class="b-print {salto}">
                    <img src="{URL_LOGO_OFICIAL}" class="watermark">
                    <table class="header-table">
                        <tr>
                            <td style="width:15%;"><img src="{URL_LOGO_OFICIAL}" width="90"></td>
                            <td style="text-align:center;">
                                <h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h2>
                                <p style="margin:0; font-size:14px; color:#d4af37; font-family:'Arial Black'; text-transform:uppercase;">INFORME ACADÉMICO OFICIAL: {periodo_sel}</p>
                            </td>
                            <td style="text-align:right; width:15%;">
                                <div style="border:3px solid #0d1b2a; padding:8px; background:#f0f2f6; text-align:center; border-radius:8px;">
                                    <b style="font-size:12px; color:#000;">PROMEDIO</b><br><b style="font-size:18px; color:#d4af37;">{p_prom:.1f}</b>
                                </div>
                            </td>
                        </tr>
                    </table>
                    <div style="border:2px solid #0d1b2a; padding:10px; background:rgba(255,255,255,0.9); display:flex; justify-content:space-between; margin-bottom:10px; border-radius:5px;">
                        <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span>
                        <span><b style="color:#0d1b2a;">PUESTO:</b> <span style="color:#cc0000; font-weight:bold;">{puesto_estudiante}</span></span>
                    </div>
                    <table class="table-custom">
                        <tr><th>MATERIA</th>{th_dinamico}<th>DESEMPEÑO</th></tr>"""
                    
                    grado_str = str(res['Grado'].iloc[0]).upper() if not res.empty else ""
                    es_primaria = any(k in grado_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in grado_str for k in ["10", "11", "DECIMO", "ONCE"])
                    nivel_alumno = "Primaria" if es_primaria else "Bachillerato"
                    
                    for _, row in res.iterrows():
                        nota_final = nota_limpia(row.get(col_n, 0))
                        desp = "SUPERIOR" if nota_final >= 9.1 else ("ALTO" if nota_final >= 7.6 else ("BÁSICO" if nota_final >= 6.0 else "BAJO"))
                        color = "#155724" if nota_final >= 6.0 else "#721c24"
                        
                        td_dinamico = ""
                        for p in periodos_print:
                            if p == "FINAL":
                                val_p = nota_limpia(row.get('PROMEDIO', 0))
                                td_dinamico += f"<td style='color:{color}; font-weight:bold;'>{val_p:.1f}</td>"
                            else:
                                val_p = nota_limpia(row.get(p, 0))
                                td_dinamico += f"<td>{val_p:.1f}</td>"
                        
                        html_masivo += f"<tr><td style='text-align:left;'><b>{row['Materia']}</b></td>{td_dinamico}<td style='color:{color}; font-weight:bold;'>{desp}</td></tr>"
                        
                        llave_busqueda = (nivel_alumno.upper(), str(row['Materia']).strip().upper(), desp.upper())
                        logro_texto = diccionario_logros.get(llave_busqueda, str(row.get('LOGRO', '')))
                        if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']: logro_texto = "Pendiente de registro."
                        
                        html_masivo += f"<tr><td colspan='{col_span_logro}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
                    
                    html_masivo += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div>"""
                    
                html_masivo += "</body></html>"
                
                components.html(html_masivo, height=750, scrolling=True)
                st.toast("✅ ¡Compilación Masiva Finalizada con Éxito!", icon="🚀")
