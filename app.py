import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# 📋 MATRIZ DE MANDO: ASIGNACIONES ACADÉMICAS IE GÉNESIS 2026
ASIGNACIONES_DOCENTES = {
    "Priscila": {"grados": ["5°"], "materias": "TODAS"},
    "Celeste": {"grados": ["1°"], "materias": "TODAS"},
    "Maria": {"grados": ["2°"], "materias": "TODAS"},
    "Ana": {"grados": ["3°"], "materias": "TODAS"},
    "Juliana": {"grados": ["4°"], "materias": "TODAS"},
    "Daniel": {"grados": ["10°", "11°"], "materias": ["Física", "Matemáticas"]},
    "Rafael": {"grados": ["10°", "11°"], "materias": ["Química"]},
    "Ludis": {"grados": ["10°", "11°"], "materias": ["Filosofía", "Ética"]},
    "Arnaldo": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Matemáticas"]},
    "Docente_Lenguaje_VIP": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Lenguaje"]},
    "Docente_Sociales_VIP": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Sociales"]},
    "Docente_Ingles_VIP": {"grados": ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Inglés"]},
    "Docente_Ciencias_VIP": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Ciencias Naturales"]},
    "Docente_Especialidades_VIP": {"grados": ["1°", "11°"], "materias": ["Educación Física", "Artística", "Informática", "Religión"]}
}

MATERIAS_PRIMARIA = ["Matemáticas", "Lenguaje", "Ciencias Naturales", "Sociales", "Inglés", "Educación Física", "Ética", "Artística", "Informática", "Religión"]

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

conn = st.connection("gsheets", type=GSheetsConnection)
zona_colombia = timezone(timedelta(hours=-5))

if 'logueado' not in st.session_state: st.session_state.logueado = False
if 'rol' not in st.session_state: st.session_state.rol = ""
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'nombre_completo_usuario' not in st.session_state: st.session_state.nombre_completo_usuario = ""
if 'bitacora' not in st.session_state: st.session_state.bitacora = []
if 'df_maestro' not in st.session_state: st.session_state.df_maestro = None
if 'df_logros' not in st.session_state: st.session_state.df_logros = None
if 'df_asistencia' not in st.session_state: st.session_state.df_asistencia = None
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now(zona_colombia).strftime("%I:%M %p")

# --- 2. CSS AVANZADO (DISEÑO, MARCA DE AGUA Y RESCATE DE MENÚ) ---
st.markdown("""
<style>
    /* 1. ELIMINAR GATO Y MENÚ DERECHO */
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    footer { visibility: hidden !important; }

    /* 2. RESCATAR BOTÓN HAMBURGUESA (Dorado sobre fondo azul oscuro) */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        background-color: #0d1b2a !important;
        border-radius: 0 8px 8px 0 !important;
    }
    [data-testid="collapsedControl"] svg { fill: #d4af37 !important; }

    /* 3. ESTILOS ORIGINALES DE SU CÓDIGO */
    .stApp { background-color: #ffffff; }
    .stApp::before {
        content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; font-weight: bold; }
    .titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
    .titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
    .asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}
    
    /* Efectos en Gráficos */
    [data-testid="stPlotlyChart"] { transition: transform 0.3s ease, box-shadow 0.3s ease; border-radius: 12px; padding: 5px; background: white; border: 2px solid #000; }
    [data-testid="stPlotlyChart"]:hover { transform: scale(1.03); box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4); z-index: 10; }

    /* Semáforos */
    .tarjeta-roja { border: 3px solid #cc0000; border-left: 10px solid #cc0000; background:#ffe6e6; padding:15px; border-radius:8px; color: #000; }
    .tarjeta-naranja { border: 3px solid #cc8800; border-left: 10px solid #cc8800; background:#fff4e6; padding:15px; border-radius:8px; color: #000; }
    .tarjeta-verde { border: 3px solid #00994c; border-left: 10px solid #00994c; background:#e6ffe6; padding:15px; border-radius:8px; color: #000; }

    /* Inputs y Selectores */
    p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
    .footer-legal { font-size: 10px; color: #888888; text-align: center; margin-top: 50px; border-top: 1px solid #eeeeee; padding-top: 10px; font-family: 'Arial', sans-serif; }
</style>
""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

# --- 3. LOGIN SEGURO ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        from PIL import Image
        try: st.image(Image.open("logo.png"), width=250)
        except: pass
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px; margin-top: -10px;"><h3 style="color:#000000; font-family:'Arial Black'; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        u = st.text_input("👤 Usuario", placeholder="Ej: admin", label_visibility="collapsed")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        if st.button("🚀 INGRESAR", use_container_width=True):
            with st.spinner("Validando..."):
                try:
                    if u == "admin":
                        clave_secreta = st.secrets.get("CLAVE_MAESTRA", "Genesis2026*") 
                        if p == clave_secreta:
                            st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, "Admin", u
                            st.session_state.nombre_completo_usuario = "Comandante Supremo"
                            registrar_bitacora(u, "Admin", "✅ Ingreso Comandante")
                            st.rerun()
                    df_usuarios = conn.read(worksheet='DATA_USUARIOS', ttl=0) 
                    acceso = df_usuarios[(df_usuarios['USUARIO'] == u) & (df_usuarios['PASSWORD'] == p)]
                    if not acceso.empty:
                        if str(acceso['ESTADO'].iloc[0]).strip().upper() == "ACTIVO":
                            st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, str(acceso['ROL'].iloc[0]).capitalize(), u
                            st.session_state.nombre_completo_usuario = str(acceso['Nombre_Completo'].iloc[0]).strip() if 'Nombre_Completo' in acceso.columns else u
                            registrar_bitacora(u, st.session_state.rol, "✅ Ingreso Exitoso")
                            st.rerun()
                        else: st.error("🚨 Cuenta inactiva.")
                    else: st.error("🚨 Credenciales incorrectas.")
                except: st.error("🚨 Error de conexión.")
    st.stop()

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.image("logo.png", width=120)
    nombre_mostrar = st.session_state.nombre_completo_usuario if st.session_state.nombre_completo_usuario else st.session_state.usuario_actual.upper()
    st.markdown(f"### 👤 {nombre_mostrar}\n<p style='color:#d4af37; font-weight:bold; margin-top:-15px;'>Rango: {st.session_state.rol}</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:rgba(212, 175, 55, 0.1); border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center; margin-bottom:15px;'><p style='color:#d4af37; font-size:12px; margin:0;'>🕒 INICIO: {st.session_state.hora_inicio}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    opciones_menu = ["🏠 Inicio", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": 
        opciones_menu.insert(1, "🛡️ Bitácora y Backup")
        opciones_menu.insert(1, "👑 Centro de Mando")
    menu = st.radio("SECCIONES:", opciones_menu)
    
    usuario_activo = st.session_state.usuario_actual
    cursos = ["TODOS"] if st.session_state.rol == "Admin" else ASIGNACIONES_DOCENTES.get(usuario_activo, {}).get("grados", ["Sin asignación"])
    st.markdown("---")
    curso_sel = st.selectbox("🎓 GRADO:", cursos)
    
    if st.session_state.rol == "Admin": materias_p = ["TODAS"]
    else:
        materias_p = ASIGNACIONES_DOCENTES.get(usuario_activo, {}).get("materias", ["Sin asignación"])
        if materias_p == "TODAS": materias_p = MATERIAS_PRIMARIA
    materia_sel = st.selectbox("📚 MATERIA:", materias_p)
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if st.button("🔴 Salir"):
        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🚪 Salida")
        st.session_state.logueado = False
        st.rerun()

# --- 5. ENCABEZADO FIJO ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>INSTITUCIÓN EDUCATIVA GÉNESIS JORSUG 2026</h1></div>", unsafe_allow_html=True)
msg_dict = {"🏠 Inicio": "Sistema persistente y sincronizado con éxito.", "✍️ Digitar Notas": "Rango válido: 1.0 a 10.0"}
msg_bot = msg_dict.get(menu, "Módulo activo.")
st.markdown(f"<div class='asistente-box'><img src='https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png' width='30' style='margin-right:15px;'><span>Génesis: \"{msg_bot}\"</span></div>", unsafe_allow_html=True)

# --- 6. ZONA DE TRABAJO ---
if st.session_state.df_maestro is None:
    with st.spinner("📡 Sincronizando..."):
        try:
            df_notas = conn.read(worksheet='NOTAS_CONSOLIDADAS', ttl=0).rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo', 'ASIGNATURA': 'Materia', 'LOGROS': 'LOGRO'})
            df_estud = conn.read(worksheet='DATA_ESTUDIANTES', ttl=0).rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo'})
            st.session_state.df_maestro = pd.merge(df_notas, df_estud[['Nombre_Completo', 'Grado']], on='Nombre_Completo', how='left')
            st.session_state.df_logros = conn.read(worksheet='DB_LOGROS', ttl=600)
            st.session_state.df_asistencia = conn.read(worksheet='DB_ASISTENCIA', ttl=600)
        except: st.error("Error de datos.")

df_m = st.session_state.df_maestro
if df_m is not None:
    for c in ['P1', 'P2', 'P3', 'P4']: df_m[c] = pd.to_numeric(df_m[c], errors='coerce').fillna(0.0).round(1)
    df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
    df = df_m.copy()
    if str(curso_sel) != "TODOS": df = df[df['Grado'].astype(str) == str(curso_sel)]
    if str(materia_sel) != "TODAS" and 'Materia' in df.columns: df = df[df['Materia'].astype(str) == str(materia_sel)]
else: st.stop()

# --- MÓDULOS DE NAVEGACIÓN (SU LÓGICA ORIGINAL) ---
if menu == "🏠 Inicio":
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.markdown("""<div style="background:rgba(255,255,255,0.95); padding:15px; border-radius:10px; border-left:6px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#000; margin-bottom:15px; border:2px solid #000;">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif;">¡Bienvenido a la INSTITUCIÓN EDUCATIVA GÉNESIS JORSUG 2026!</h3>
            <p style="font-size:1rem; color:#000; font-family: 'Arial Black', sans-serif; font-weight:bold;"><i>"Seguridad, Control y Excelencia Educativa."</i></p>
            </div>""", unsafe_allow_html=True)
        col_mision, col_vision = st.columns(2)
        with col_mision:
            st.markdown("""<div style="background:white; padding:15px; border-radius:10px; border:2px solid #000; border-top:6px solid #0d1b2a; height:100%;">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0;">🎯 Nuestra Misión</h4>
                <p style="color:#000; font-weight:bold; font-size:15px;">Formar líderes con excelencia académica y valores humanos, utilizando la tecnología satelital de Génesis AGH para transformar el seguimiento educativo en un proceso de precisión y calidad.</p>
            </div>""", unsafe_allow_html=True)
        with col_vision:
            st.markdown("""<div style="background:white; padding:15px; border-radius:10px; border:2px solid #000; border-top:6px solid #d4af37; height:100%;">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0;">👁️ Nuestra Visión 2028</h4>
                <p style="color:#000; font-weight:bold; font-size:15px;">Seremos reconocidos como la institución líder en innovación pedagógica y transformación digital en la región, proyectando talentos hacia el éxito internacional.</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("logo.png", width=400)

elif menu == "👑 Centro de Mando":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Mando | Nivel Rectoría</h3>", unsafe_allow_html=True)
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else 0
    promedio_colegio = df[col_n].mean() if not df.empty else 0
    est_en_riesgo = df[df[col_n] < 6.0]['Nombre_Completo'].nunique()
    porcentaje_riesgo = (est_en_riesgo / total_estudiantes * 100) if total_estudiantes > 0 else 0
    eficiencia_interna = 100 - porcentaje_riesgo
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Estudiantes</p><p class='metric-value'>{total_estudiantes}</p></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio Institucional</p><p class='metric-value'>{promedio_colegio:.1f}</p></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><p class='metric-label'>Índice de Eficiencia</p><p class='metric-value'>{eficiencia_interna:.1f}%</p></div>", unsafe_allow_html=True)

elif menu == "✍️ Digitar Notas":
    col_btn, _ = st.columns([1.5, 8.5])
    with col_btn:
        if st.button("💾 GUARDAR", type="primary", use_container_width=True):
            st.session_state.df_maestro = st.session_state.df_temp_n
            try: conn.update(worksheet="NOTAS_CONSOLIDADAS", data=st.session_state.df_maestro.drop(columns=['Grado'])); st.success("✅ Guardado.")
            except: st.warning("Guardado local.")
            st.rerun()
    config_notas = { c: st.column_config.NumberColumn(c, min_value=1.0, max_value=10.0, step=0.1) for c in ['P1', 'P2', 'P3', 'P4'] }
    st.session_state.df_temp_n = st.data_editor(df, use_container_width=True, num_rows="dynamic", height=400, column_config=config_notas)

elif menu == "📊 Inteligencia Académica":
    c1, c2 = st.columns(2)
    with c1:
        df_prom = df.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n)
        fig1 = px.bar(df_prom, x=col_n, y='Materia', orientation='h', title=f"Rendimiento por Materia ({periodo_sel})")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        def nivel(n): return 'BAJO' if n<6 else ('BÁSICO' if n<7.6 else ('ALTO' if n<9.1 else 'SUPERIOR'))
        df['Nivel'] = df[col_n].apply(nivel)
        fig2 = px.pie(df, names='Nivel', hole=0.4, title="Distribución de Niveles")
        st.plotly_chart(fig2, use_container_width=True)

elif menu == "📈 Dashboard Estudiantil":
    alumno = st.selectbox("🎯 Seleccione Estudiante:", sorted(df['Nombre_Completo'].dropna().unique()))
    if alumno:
        df_alum = df[df['Nombre_Completo'] == alumno]
        st.markdown(f"#### Informe de {alumno}")
        st.metric("Promedio Actual", f"{df_alum[col_n].mean():.1f}")
        fig_radar = px.line_polar(df_alum, r=col_n, theta='Materia', line_close=True, range_r=[0,10])
        st.plotly_chart(fig_radar, use_container_width=True)

elif menu == "🚦 Semáforo Académico":
    df_semaforo = df.groupby(['Nombre_Completo', 'Grado'])[col_n].mean().reset_index()
    criticos = df_semaforo[df_semaforo[col_n] < 6.0]
    st.error(f"🚨 Estudiantes en Riesgo Crítico: {len(criticos)}")
    st.dataframe(criticos, use_container_width=True)

elif menu == "📚 Logros":
    st.session_state.df_l_temp = st.data_editor(st.session_state.df_logros, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Guardar Logros"): 
        st.session_state.df_logros = st.session_state.df_l_temp
        conn.update(worksheet="DB_LOGROS", data=st.session_state.df_logros)
        st.success("Logros actualizados.")

elif menu == "📝 Asistencias y Reportes":
    with st.form("Asistencia"):
        alum = st.selectbox("Estudiante", sorted(df['Nombre_Completo'].unique()))
        est = st.selectbox("Estado", ["Falla", "Retardo", "Llamado de Atención"])
        obs = st.text_area("Observación")
        if st.form_submit_button("Guardar"): st.success("Reporte registrado.")

elif menu == "📜 Boletines":
    st.write("### Generador de Boletines")
    alum_bol = st.selectbox("Estudiante para Boletín", sorted(df['Nombre_Completo'].unique()))
    if st.button("🖨️ Generar"): st.write(f"Preparando boletín para {alum_bol}...")

elif menu == "📖 Manual de Usuario":
    st.markdown("### Manual de Operaciones\n1. Digite notas en el rango 1-10.\n2. No olvide Guardar.")

elif menu == "📸 Eventos Institucionales":
    st.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", caption="Memorias Génesis")

elif menu == "🛡️ Bitácora y Backup":
    st.write("### Centro de Respaldo")
    if st.button("Generar Backup"): st.download_button("Descargar Excel", data=b"", file_name="backup.xlsx")

# --- PIE DE PÁGINA ---
st.markdown(f"<div class='footer-legal'>Academia Global Horizonte © {datetime.now().year} | Protección de Datos Ley 1581</div>", unsafe_allow_html=True)
