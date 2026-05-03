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

# --- 2. CSS AVANZADO (OPERATIVIDAD TOTAL) ---
st.markdown("""
<style>
    /* 1. RESTAURAR INTERFAZ NATIVA PARA QUE APAREZCA EL MENÚ */
    /* No tocamos el header ni el toolbar para que el botón hamburguesa vuelva */
    
    /* 2. DISEÑO DE FONDO Y MARCA DE AGUA */
    .stApp { background-color: #ffffff; }
    .stApp::before {
        content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    
    /* 3. ESTILOS DE SU DISEÑO ORIGINAL */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; font-weight: bold; }
    .titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
    .titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
    .asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}
    
    /* Inputs y Tablas */
    p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
    footer { visibility: hidden !important; }
    .footer-legal { font-size: 10px; color: #888888; text-align: center; margin-top: 50px; border-top: 1px solid #eeeeee; padding-top: 10px; }
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
    st.markdown(f"### 👤 {nombre_mostrar}")
    st.markdown(f"<p style='color:#d4af37; font-weight:bold; margin-top:-15px;'>Rango: {st.session_state.rol}</p>", unsafe_allow_html=True)
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
            st.session_state.df_logros = conn.read(worksheet='DB_LOGROS', ttl=0)
            st.session_state.df_asistencia = conn.read(worksheet='DB_ASISTENCIA', ttl=0)
        except: st.error("Error de datos.")

df_m = st.session_state.df_maestro
if df_m is not None:
    for c in ['P1', 'P2', 'P3', 'P4']: df_m[c] = pd.to_numeric(df_m[c], errors='coerce').fillna(0.0).round(1)
    df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
    df = df_m.copy()
    if str(curso_sel) != "TODOS": df = df[df['Grado'].astype(str) == str(curso_sel)]
    if str(materia_sel) != "TODAS" and 'Materia' in df.columns: df = df[df['Materia'].astype(str) == str(materia_sel)]
else: st.stop()

# --- MÓDULOS ---
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

elif menu == "✍️ Digitar Notas":
    col_btn, _ = st.columns([1.5, 8.5])
    with col_btn:
        if st.button("💾 GUARDAR", type="primary"):
            st.session_state.df_maestro = st.session_state.df_temp_n
            conn.update(worksheet="NOTAS_CONSOLIDADAS", data=st.session_state.df_maestro.drop(columns=['Grado']))
            st.success("✅ Guardado.")
            st.rerun()
    config_notas = { c: st.column_config.NumberColumn(c, min_value=1.0, max_value=10.0, step=0.1) for c in ['P1', 'P2', 'P3', 'P4'] }
    st.session_state.df_temp_n = st.data_editor(df, use_container_width=True, num_rows="dynamic", height=400, column_config=config_notas)

# (Siguen el resto de sus módulos originales...)
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

# --- PIE DE PÁGINA ---
st.markdown(f"<div class='footer-legal'>Génesis AGH © {datetime.now().year} | Ley 1581 Protección de Datos</div>", unsafe_allow_html=True)
