import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
from PIL import Image

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
if 'df_asistencia' not in st.session_state: st.session_state.df_asistencia = pd.DataFrame()
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now(zona_colombia).strftime("%I:%M %p")

# --- 2. CSS AVANZADO (DISEÑO, MARCA DE AGUA Y CAMUFLAJE) ---
st.markdown("""
<style>
    /* Ocultar elementos de desarrollo de Streamlit (Gato, menú derecho) */
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    footer { visibility: hidden !important; }
    
    /* Asegurar que el botón del menú lateral (hamburguesa) sea visible y blanco */
    [data-testid="collapsedControl"] {
        background-color: #0d1b2a !important;
        border-radius: 5px !important;
        display: flex !important;
    }
    [data-testid="collapsedControl"] svg { fill: white !important; }

    /* Diseño General */
    .stApp { background-color: #ffffff; }
    .stApp::before {
        content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    
    /* Sidebar Estilo Militar */
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; font-weight: bold; }
    
    /* Títulos y Contenedores */
    .titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
    .titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
    .asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}
    
    /* Gráficos */
    [data-testid="stPlotlyChart"] { transition: transform 0.3s ease; border-radius: 12px; background: white; border: 2px solid #000; }
    [data-testid="stPlotlyChart"]:hover { transform: scale(1.02); }

    /* Colores Institucionales en Inputs */
    p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000; }
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; font-family: 'Arial Black';}
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
        try: st.image("logo.png", width=250)
        except: pass
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px;"><h3 style="color:#000000; font-family:'Arial Black'; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        u = st.text_input("👤 Usuario", placeholder="Ej: admin")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••")
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
                except: st.error("🚨 Error de conexión satelital.")
    st.stop()

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.image("logo.png", width=120)
    st.markdown(f"### 👤 {st.session_state.nombre_completo_usuario}")
    st.markdown(f"<p style='color:#d4af37;'>Rango: {st.session_state.rol}</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #d4af37; padding:10px; border-radius:5px;'>🕒 INICIO: {st.session_state.hora_inicio}</div>", unsafe_allow_html=True)
    st.markdown("---")
    opciones_menu = ["🏠 Inicio", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin":
        opciones_menu.insert(1, "🛡️ Bitácora y Backup")
        opciones_menu.insert(1, "👑 Centro de Mando")
    menu = st.radio("SECCIONES:", opciones_menu)
    
    # Filtros
    usuario_activo = st.session_state.usuario_actual
    cursos = ["TODOS"] if st.session_state.rol == "Admin" else ASIGNACIONES_DOCENTES.get(usuario_activo, {}).get("grados", ["Sin asignación"])
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
msg_dict = {"🏠 Inicio": "Sistema persistente y sincronizado exitosamente.", "✍️ Digitar Notas": "Rango válido: 1.0 a 10.0. Use punto para decimales."}
msg_bot = msg_dict.get(menu, "Módulo activo y operando.")
st.markdown(f"<div class='asistente-box'><img src='https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png' width='30' style='margin-right:15px;'><span>Génesis: \"{msg_bot}\"</span></div>", unsafe_allow_html=True)

# --- 6. CARGA DE DATOS ---
if st.session_state.df_maestro is None:
    with st.spinner("📡 Sincronizando notas..."):
        try:
            df_notas = conn.read(worksheet='NOTAS_CONSOLIDADAS', ttl=0).rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo', 'ASIGNATURA': 'Materia', 'LOGROS': 'LOGRO'})
            df_estud = conn.read(worksheet='DATA_ESTUDIANTES', ttl=0).rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo'})
            st.session_state.df_maestro = pd.merge(df_notas, df_estud[['Nombre_Completo', 'Grado']], on='Nombre_Completo', how='left')
            st.session_state.df_logros = conn.read(worksheet='DB_LOGROS', ttl=0)
            st.session_state.df_asistencia = conn.read(worksheet='DB_ASISTENCIA', ttl=0)
        except: st.error("Error cargando datos.")

df_m = st.session_state.df_maestro
if df_m is not None:
    for c in ['P1', 'P2', 'P3', 'P4']: df_m[c] = pd.to_numeric(df_m[c], errors='coerce').fillna(0.0).round(1)
    df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
    df = df_m.copy()
    if str(curso_sel) != "TODOS": df = df[df['Grado'].astype(str) == str(curso_sel)]
    if str(materia_sel) != "TODAS": df = df[df['Materia'].astype(str) == str(materia_sel)]
else: st.stop()

# --- 7. LÓGICA DE SECCIONES (Simplificada para estabilidad) ---
if menu == "🏠 Inicio":
    st.markdown("### Bienvenidos a la Excelencia")
    st.image("logo.png", width=300)
    st.info("Misión: Formar líderes con tecnología de vanguardia.")

elif menu == "✍️ Digitar Notas":
    col_save, _ = st.columns([2, 8])
    with col_save:
        if st.button("💾 GUARDAR CAMBIOS", type="primary"):
            st.session_state.df_maestro = st.session_state.temp_edit
            try:
                df_save = st.session_state.df_maestro.drop(columns=['Grado']) if 'Grado' in st.session_state.df_maestro.columns else st.session_state.df_maestro
                conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_save)
                st.success("✅ Sincronizado con Drive")
            except: st.warning("Error en Drive, guardado localmente.")
    
    config_n = {c: st.column_config.NumberColumn(c, min_value=1.0, max_value=10.0, step=0.1) for c in ['P1', 'P2', 'P3', 'P4']}
    st.session_state.temp_edit = st.data_editor(df, use_container_width=True, column_config=config_n, height=400)

elif menu == "📜 Boletines":
    alumno = st.selectbox("👤 Seleccione Estudiante:", sorted(df['Nombre_Completo'].unique()))
    if st.button("🖨️ Generar Vista de Impresión"):
        st.write(f"Generando boletín para {alumno}...")
        # Aquí va su lógica de boletín HTML que ya funciona bien

# --- PIE DE PÁGINA ---
st.markdown(f"<div class='footer-legal'>Génesis AGH © {datetime.now().year} | Ley 1581 de 2012 Protección de Datos</div>", unsafe_allow_html=True)
