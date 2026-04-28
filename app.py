import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Persistent Core", layout="wide", page_icon="🎓")

if 'logueado' not in st.session_state: st.session_state.logueado = False
if 'rol' not in st.session_state: st.session_state.rol = ""
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'bitacora' not in st.session_state: st.session_state.bitacora = []
if 'df_maestro' not in st.session_state: st.session_state.df_maestro = None
if 'df_logros' not in st.session_state: st.session_state.df_logros = None
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now().strftime("%H:%M:%S")

# --- 2. CSS AVANZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .stApp::before {
        content: ""; background-image: url('https://cdn-icons-png.flaticon.com/512/2231/2231644.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stTextInput"] div[data-baseweb="input"] input { height: 35px !important; min-height: 35px !important; padding: 5px 10px !important; font-size: 13px !important; border-radius: 4px !important; }
    .titulo-Agh { color: #0d1b2a !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
    .asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.05); display: flex; align-items: center; border: 1px solid #ddd; margin-bottom: 15px; }
    
    [data-testid="stPlotlyChart"] { transition: transform 0.3s ease, box-shadow 0.3s ease; border-radius: 12px; padding: 5px; background: white; }
    [data-testid="stPlotlyChart"]:hover { transform: scale(1.03); box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4); z-index: 10; }
    .colchon { height: 300px; width: 100%; }

    @keyframes pulso-rojo { 0% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 51, 51, 0.8), inset 0 0 10px rgba(255, 51, 51, 0.2); } 100% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } }
    @keyframes pulso-naranja { 0% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 170, 0, 0.8), inset 0 0 10px rgba(255, 170, 0, 0.2); } 100% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } }
    @keyframes pulso-verde { 0% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 204, 102, 0.8), inset 0 0 10px rgba(0, 204, 102, 0.2); } 100% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } }
    .tarjeta-roja { animation: pulso-rojo 1.5s infinite; border-left:6px solid #ff3333; background:#ffe6e6; padding:15px; border-radius:8px; }
    .tarjeta-naranja { animation: pulso-naranja 2s infinite; border-left:6px solid #ffaa00; background:#fff4e6; padding:15px; border-radius:8px; }
    .tarjeta-verde { animation: pulso-verde 2.5s infinite; border-left:6px solid #00cc66; background:#e6ffe6; padding:15px; border-radius:8px; }
    </style>
""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

# --- 3. LOGIN ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=800&auto=format&fit=crop", use_container_width=True)
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-top: -10px;"><h3 style="color:#0d1b2a; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        u = st.text_input("👤 Usuario", placeholder="Ej: admin", label_visibility="collapsed")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 INGRESAR", use_container_width=True):
            if u == "admin" and p == "agh2024": 
                st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, "Admin", u
                registrar_bitacora(u, "Admin", "✅ Ingreso")
                st.rerun()
            elif u == "docente" and p == "profe2024": 
                st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, "Docente", u
                registrar_bitacora(u, "Docente", "✅ Ingreso")
                st.rerun()
            else: st.error("Error de credenciales")
    st.stop()

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2231/2231644.png", width=70)
    st.markdown(f"**👤 {st.session_state.usuario_actual.upper()} ({st.session_state.rol})**")
    st.markdown("---")
    
    opciones_menu = ["🏠 Inicio", "📊 Inteligencia Académica", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": opciones_menu.insert(1, "🛡️ Bitácora y Backup")
    menu = st.radio("SECCIONES:", opciones_menu)
    
    cursos = ["TODOS"]
    if st.session_state.df_maestro is not None:
        cursos += sorted(st.session_state.df_maestro['Grado'].dropna().unique().astype(str).tolist())
    st.markdown("---")
    curso_sel = st.selectbox("📚 GRADO:", cursos)
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if st.button("🔴 Salir"): 
        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🚪 Salida")
        st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = False, "", ""
        st.rerun()

# --- 5. ENCABEZADO FIJO ---
st.markdown("<h1 class='titulo-Agh'>ACADEMIA GLOBAL HORIZONTE</h1>", unsafe_allow_html=True)

if st.session_state.df_maestro is None: msg_bot = "Comandante, Backup Master activado. Suba el Excel." if st.session_state.rol == "Admin" else "Esperando datos."
else:
    if menu == "🏠 Inicio": msg_bot = "Sistema persistente y operativo."
    elif menu == "🛡️ Bitácora y Backup": msg_bot = "NUEVO: Aquí puede descargar el Excel con todo el trabajo guardado de los docentes."
    elif menu == "📊 Inteligencia Académica": msg_bot = "Análisis en español activo."
    elif menu == "🚦 Semáforo Académico": msg_bot = "Balizas en tiempo real."
    elif menu == "✍️ Digitar Notas": msg_bot = "Recuerde guardar sus avances para que queden en el Backup."
    elif menu == "📚 Logros": msg_bot = "Diccionario protegido."
    elif menu == "📜 Boletines": msg_bot = "Generador de impresión activo."
    elif menu in ["📖 Manual de Usuario", "📸 Eventos Institucionales"]: msg_bot = "Módulos de información."

st.markdown(f"""
<div class="asistente-box">
    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" width="30" style="margin-right:15px;">
    <div style="display:flex; align-items:center;">
        <span style="color:#0d1b2a; font-weight:bold; margin-right:10px;">Génesis:</span>
        <span style="color:#444; font-size:14px; font-style:italic;">"{msg_bot}"</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. ZONA DE TRABAJO ---
if st.session_state.df_maestro is None:
    if st.session_state.rol == "Admin":
        archivo = st.file_uploader("📥 Sincronizar Base Maestra", type=["xlsm", "xlsx"])
        if archivo:
            xls = pd.ExcelFile(archivo)
            df_n = pd.read_excel(xls, sheet_name='NOTAS_CONSOLIDADAS')
            df_e = pd.read_excel(xls, sheet_name='DATA_ESTUDIANTES') if 'DATA_ESTUDIANTES' in xls.sheet_names else pd.DataFrame()
            df = pd.merge(df_n, df_e[['ID_Estudiante', 'Grado']], left_on='ID_Est', right_on='ID_Estudiante', how='left') if not df_e.empty else df_n
            st.session_state.df_maestro = df.fillna(0)
            st.session_state.df_logros = pd.read_excel(xls, sheet_name='DB_LOGROS') if 'DB_LOGROS' in xls.sheet_names else pd.DataFrame()
            st.rerun()
else:
    df_m = st.session_state.df_maestro
    df_l = st.session_state.df_logros
    df = df_m[df_m['Grado'].astype(str) == curso_sel].copy() if curso_sel != "TODOS" else df_m.copy()

    if menu == "🏠 Inicio":
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown(f"""<div style="background:rgba(255,255,255,0.9); padding:20px; border-radius:10px; border-left:6px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#333; margin-bottom:15px;">
                <h3 style="margin-top:0; color:#0d1b2a;">¡Bienvenido a la Academia Global Horizonte!</h3>
                <p style="font-size:1rem; color:#555;"><i>"Seguridad, Control y Excelencia Educativa."</i></p></div>""", unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1470&auto=format&fit=crop", use_container_width=True)

    # --- NUEVO: MÓDULO DE BITÁCORA Y BACKUP (SOLO ADMIN) ---
    elif menu == "🛡️ Bitácora y Backup":
        st.markdown("<h3 style='color:#0d1b2a; border-bottom:2px solid #d4af37; padding-bottom:5px;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
        
        # EL CEREBRO DEL BACKUP: Genera un Excel con las notas actuales y la bitácora
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.df_maestro.to_excel(writer, sheet_name='NOTAS_CONSOLIDADAS', index=False)
            st.session_state.df_logros.to_excel(writer, sheet_name='DB_LOGROS', index=False)
            if st.session_state.bitacora:
                pd.DataFrame(st.session_state.bitacora).to_excel(writer, sheet_name='BITACORA', index=False)
        
        st.info("Comandante, aquí puede descargar todo el trabajo que los docentes han realizado en el sistema. Es su copia de seguridad física.")
        
        st.download_button(
            label="📥 DESCARGAR BASE DE DATOS ACTUALIZADA (EXCEL)",
            data=buffer.getvalue(),
            file_name=f"Backup_AGH_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.ms-excel",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### Registro Histórico de Usuarios")
        if st.session_state.bitacora:
            df_bitacora = pd.DataFrame(st.session_state.bitacora).iloc[::-1].reset_index(drop=True)
            st.dataframe(df_bitacora, use_container_width=True)

    elif menu == "📊 Inteligencia Académica":
        config_espanol = {'locale': 'es', 'displaylogo': False}
        c1, c2 = st.columns(2)
        with c1: 
            st.markdown(f"<div style='background:#0d1b2a; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold; margin-bottom:15px;'>Rendimiento por Asignatura ({periodo_sel})</div>", unsafe_allow_html=True)
            df_promedios = df.groupby('ASIGNATURA')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
            fig1 = px.bar(df_promedios, x=col_n, y='ASIGNATURA', text_auto='.1f', color='ASIGNATURA', orientation='h')
            fig1.update_layout(height=350, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            fig1.update_yaxes(title_text="", visible=True, tickmode='linear', dtick=1, tickfont=dict(size=14, color='#000000'), automargin=True) 
            fig1.update_xaxes(title_text="Promedio")
            fig1.update_traces(hovertemplate='<b>%{y}</b><br>Promedio: %{x:.1f}<extra></extra>')
            st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
            
        with c2: 
            st.markdown(f"<div style='background:#0d1b2a; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold; margin-bottom:15px;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
            def evaluar_filtro(nota):
                if nota < 6.0: return 'BAJO'
                elif nota < 7.6: return 'BÁSICO'
                elif nota < 9.1: return 'ALTO'
                else: return 'SUPERIOR'
            df['DESEMPEÑO_FILTRO'] = df[col_n].apply(evaluar_filtro)
            colores_vivos = {'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'}
            fig2 = px.pie(df, names='DESEMPEÑO_FILTRO', hole=0.4, color='DESEMPEÑO_FILTRO', color_discrete_map=colores_vivos)
            fig2.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Porcentaje: %{percent}<extra></extra>')
            fig2.update_layout(height=350, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, config=config_espanol)

    elif menu == "🚦 Semáforo Académico":
        st.markdown(f"<h3 style='color:#0d1b2a; border-bottom:2px solid #d4af37; padding-bottom:5px;'>Semáforo de Riesgo Académico - Grado {curso_sel} ({periodo_sel})</h3>", unsafe_allow_html=True)
        df_estudiantes = df.groupby(['NOMBRE_COMPLETO', 'Grado'])[col_n].mean().reset_index()
        def color_semaforo(nota):
            if nota < 6.0: return '🔴 CRÍTICO'
            elif nota < 7.6: return '🟡 ALERTA'
            else: return '🟢 ÓPTIMO'
        df_estudiantes['ESTADO'] = df_estudiantes[col_n].apply(color_semaforo)
        df_estudiantes = df_estudiantes.sort_values(by=col_n, ascending=True)
        criticos = df_estudiantes[df_estudiantes['ESTADO'] == '🔴 CRÍTICO']
        alertas = df_estudiantes[df_estudiantes['ESTADO'] == '🟡 ALERTA']
        optimos = df_estudiantes[df_estudiantes['ESTADO'] == '🟢 ÓPTIMO']
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='tarjeta-roja'><h4 style='margin:0; color:#cc0000;'>🔴 Riesgo Crítico (< 6.0)</h4><h1 style='margin:0; color:#cc0000;'>{len(criticos)}</h1></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='tarjeta-naranja'><h4 style='margin:0; color:#cc8800;'>🟡 Alerta (6.0 - 7.5)</h4><h1 style='margin:0; color:#cc8800;'>{len(alertas)}</h1></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='tarjeta-verde'><h4 style='margin:0; color:#00994c;'>🟢 Óptimo (>= 7.6)</h4><h1 style='margin:0; color:#00994c;'>{len(optimos)}</h1></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if not criticos.empty:
            st.error("🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO")
            df_criticos_mostrar = criticos[['NOMBRE_COMPLETO', 'Grado', col_n]].rename(columns={col_n: 'PROMEDIO'})
            st.dataframe(df_criticos_mostrar.style.format({'PROMEDIO': '{:.1f}'}), use_container_width=True, hide_index=True)

    elif menu == "✍️ Digitar Notas":
        col_btn, col_espacio = st.columns([1.5, 8.5])
        with col_btn:
            if st.button("💾 GUARDAR", type="primary", use_container_width=True):
                for c in ['P1', 'P2', 'P3', 'P4']: st.session_state.df_temp_n[c] = pd.to_numeric(st.session_state.df_temp_n[c], errors='coerce').fillna(0).round(1)
                st.session_state.df_temp_n['PROMEDIO'] = st.session_state.df_temp_n[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                st.session_state.df_temp_n['DESEMPEÑO'] = st.session_state.df_temp_n['PROMEDIO'].apply(lambda x: 'BAJO' if x<6 else ('BÁSICO' if x<7.6 else ('ALTO' if x<9.1 else 'SUPERIOR')))
                st.session_state.df_maestro = st.session_state.df_temp_n
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Notas")
                st.success("✅ Guardado"); st.rerun()
        st.session_state.df_temp_n = st.data_editor(df, use_container_width=True, num_rows="dynamic", height=300, key="editor_notas")

    elif menu == "📚 Logros":
        col_btn, col_espacio = st.columns([1.5, 8.5])
        with col_btn:
            if st.button("💾 GUARDAR", type="primary", use_container_width=True):
                st.session_state.df_logros = st.session_state.df_l_temp
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Logros")
                st.success("✅ Guardado"); st.rerun()
        st.session_state.df_l_temp = st.data_editor(df_l, use_container_width=True, num_rows="dynamic", height=300, key="editor_logros")

    elif menu == "📜 Boletines":
        st.markdown("<h3 style='color:#0d1b2a; border-bottom:2px solid #d4af37; padding-bottom:5px;'>Central de Impresión</h3>", unsafe_allow_html=True)
        modo_impresion = st.radio("Seleccione el modo de generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True)
        
        if modo_impresion == "👤 Individual":
            alumno = st.selectbox("👤 Estudiante:", sorted(df['NOMBRE_COMPLETO'].dropna().unique()))
            if alumno:
                res = df[df['NOMBRE_COMPLETO'] == alumno]; p_prom = res[col_n].mean()
                th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
                html_boletin = f"""
                <html><head><script>function imprimirBoletin() {{ window.print(); }}</script>
                <style>body {{ font-family: Arial, sans-serif; background: white; }} .b-print {{ padding: 20px; border: 2px solid #0d1b2a; color: black; font-size: 12px; }} @media print {{ @page {{ size: letter portrait; margin: 10mm; }} body {{ background: white; margin: 0; }} .no-print {{ display: none !important; }} .b-print {{ border: none; padding: 0; }} table {{ width: 100%; border-collapse: collapse; }} th, td {{ border: 1px solid black; padding: 5px; }} }}</style></head><body>
                <div class="no-print" style="text-align:right; margin-bottom:10px;"><button onclick="imprimirBoletin()" style="background:#0d1b2a; color:white; border:none; padding:8px 15px; cursor:pointer; border-radius:4px; font-weight:bold;">🖨️ IMPRIMIR</button></div>
                <div class="b-print">
                    <table style="width:100%; border:none; margin-bottom:10px;"><tr><td style="border:none; width:15%;"><img src="https://cdn-icons-png.flaticon.com/512/2231/2231644.png" width="60"></td><td style="border:none; text-align:center;"><h2 style="margin:0; color:#0d1b2a; font-size:18px;">ACADEMIA GLOBAL HORIZONTE</h2><p style="margin:0; font-size:11px; color:#555;">INFORME ACADÉMICO: {periodo_sel}</p></td><td style="border:none; text-align:right; width:15%;"><div style="border:1px solid #0d1b2a; padding:5px; background:#f0f4f8; text-align:center;"><b>PROM: {p_prom:.1f}</b></div></td></tr></table><br><br>
                    <div style="border:1px solid #eee; padding:8px; background:#f9f9f9; display:flex; justify-content:space-between; margin-bottom:10px;"><span><b>ESTUDIANTE:</b> {alumno}</span><span><b>GRADO:</b> {res['Grado'].iloc[0]}</span></div>
                    <table style="width:100%; border-collapse:collapse; text-align:center; border:1px solid #ccc;"><tr style="background:#0d1b2a; color:white;"><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>
                """
                for _, row in res.iterrows():
                    td = f"<td>{row['P1']:.1f}</td><td>{row['P2']:.1f}</td><td>{row['P3']:.1f}</td><td>{row['P4']:.1f}</td><td>{row['PROMEDIO']:.1f}</td>" if periodo_sel == "CONSOLIDADO FINAL" else f"<td>{row[col_n]:.1f}</td>"
                    html_boletin += f"<tr style='background:#f2f2f2;'><td style='text-align:left; padding:5px; border:1px solid #ccc;'>{row['ASIGNATURA']}</td>{td}<td>{row['DESEMPEÑO']}</td></tr><tr><td colspan='{7 if periodo_sel == 'CONSOLIDADO FINAL' else 3}' style='padding:8px; text-align:justify; font-style:italic; border:1px solid #ccc;'><b>LOGRO:</b> {row['LOGROS']}</td></tr>"
                html_boletin += "</table><br><br><br><div style='display:flex; justify-content:space-around; margin-top:50px; font-size:12px; color:black;'><div style='text-align:center; width:40%; border-top:1px solid black; padding-top:5px;'><b>Firma Rectoría</b></div><div style='text-align:center; width:40%; border-top:1px solid black; padding-top:5px;'><b>Firma Director de Grupo</b></div></div></div></body></html>"
                components.html(html_boletin, height=500, scrolling=True)
                
        else:
            estudiantes = sorted(df['NOMBRE_COMPLETO'].dropna().unique())
            st.warning(f"⚠️ Se generarán {len(estudiantes)} boletines para el grado {curso_sel}.")
            if st.button("🚀 COMPILAR LOTE MASIVO", type="primary"):
                th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
                html_masivo = f"""
                <html><head><script>function imprimirLote() {{ window.print(); }}</script>
                <style>body {{ font-family: Arial, sans-serif; background: white; }} @media print {{ @page {{ size: letter portrait; margin: 10mm; }} body {{ background: white; margin: 0; }} .no-print {{ display: none !important; }} .salto-pagina {{ page-break-after: always; }} table {{ width: 100%; border-collapse: collapse; }} th, td {{ border: 1px solid black; padding: 5px; }} }} .b-print {{ padding: 20px; border: 2px solid #0d1b2a; color: black; font-size: 12px; margin-bottom: 20px; }}</style></head><body>
                <div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; border-bottom: 2px solid #d4af37; text-align:right; margin-bottom:15px; z-index:9999;"><button onclick="imprimirLote()" style="background:#0d1b2a; color:white; border:none; padding:10px 20px; cursor:pointer; border-radius:4px; font-weight:bold; font-size:14px;">🖨️ IMPRIMIR LOS {len(estudiantes)} BOLETINES</button></div>
                """
                for i, alum in enumerate(estudiantes):
                    res = df[df['NOMBRE_COMPLETO'] == alum]; p_prom = res[col_n].mean()
                    salto = "salto-pagina" if i < len(estudiantes) - 1 else ""
                    html_masivo += f"""
                    <div class="b-print {salto}">
                        <table style="width:100%; border:none; margin-bottom:10px;"><tr><td style="border:none; width:15%;"><img src="https://cdn-icons-png.flaticon.com/512/2231/2231644.png" width="60"></td><td style="border:none; text-align:center;"><h2 style="margin:0; color:#0d1b2a; font-size:18px;">ACADEMIA GLOBAL HORIZONTE</h2><p style="margin:0; font-size:11px; color:#555;">INFORME ACADÉMICO: {periodo_sel}</p></td><td style="border:none; text-align:right; width:15%;"><div style="border:1px solid #0d1b2a; padding:5px; background:#f0f4f8; text-align:center;"><b>PROM: {p_prom:.1f}</b></div></td></tr></table><br><br>
                        <div style="border:1px solid #eee; padding:8px; background:#f9f9f9; display:flex; justify-content:space-between; margin-bottom:10px;"><span><b>ESTUDIANTE:</b> {alum}</span><span><b>GRADO:</b> {res['Grado'].iloc[0]}</span></div>
                        <table style="width:100%; border-collapse:collapse; text-align:center; border:1px solid #ccc;"><tr style="background:#0d1b2a; color:white;"><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>
                    """
                    for _, row in res.iterrows():
                        td = f"<td>{row['P1']:.1f}</td><td>{row['P2']:.1f}</td><td>{row['P3']:.1f}</td><td>{row['P4']:.1f}</td><td>{row['PROMEDIO']:.1f}</td>" if periodo_sel == "CONSOLIDADO FINAL" else f"<td>{row[col_n]:.1f}</td>"
                        html_masivo += f"<tr style='background:#f2f2f2;'><td style='text-align:left; padding:5px; border:1px solid #ccc;'>{row['ASIGNATURA']}</td>{td}<td>{row['DESEMPEÑO']}</td></tr><tr><td colspan='{7 if periodo_sel == 'CONSOLIDADO FINAL' else 3}' style='padding:8px; text-align:justify; font-style:italic; border:1px solid #ccc;'><b>LOGRO:</b> {row['LOGROS']}</td></tr>"
                    html_masivo += "</table><br><br><br><div style='display:flex; justify-content:space-around; margin-top:50px; font-size:12px; color:black;'><div style='text-align:center; width:40%; border-top:1px solid black; padding-top:5px;'><b>Firma Rectoría</b></div><div style='text-align:center; width:40%; border-top:1px solid black; padding-top:5px;'><b>Firma Director de Grupo</b></div></div></div>"
                html_masivo += "</body></html>"
                components.html(html_masivo, height=600, scrolling=True)

    elif menu in ["📖 Manual de Usuario", "📸 Eventos Institucionales"]:
        st.info("Módulos de información listos para contenido.")
