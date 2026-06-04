import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
from xhtml2pdf import pisa
import base64

# 📋 MATRIZ DE MANDO: ASIGNACIONES ACADÉMICAS IE GÉNESIS 2026
ASIGNACIONES_DOCENTES = {
    "Priscila Pacheco": {"grados": ["5°"], "materias": "TODAS"},
    "Celeste Conrrado": {"grados": ["1°"], "materias": "TODAS"},
    "Maria Narvaez": {"grados": ["2°"], "materias": "TODAS"},
    "Ana Soler": {"grados": ["3°"], "materias": "TODAS"},
    "Daniel Quintero": {"grados": ["4°"], "materias": "TODAS"},
    "Sugeydis Pacheco": {"grados": ["10°", "11°"], "materias": ["Física", "Matemáticas"]},
    "Rafael Martínez": {"grados": ["10°", "11°"], "materias": ["Química"]},
    "Ludis Barrios": {"grados": ["10°", "11°"], "materias": ["Filosofía", "Ética"]},
    "Arnaldo Tilano": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Matemáticas"]},
    "Jorge Pacheco": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Lenguaje"]},
    "Sandra Bolaño": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Sociales", "Constitución"]},
    "Melquisedec Pacheco": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Inglés"]},
    "Nellys Martínez": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Ciencias Naturales"]},
    "USUARIO_ESPECIALIDADES": {"grados": ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Educación Física", "Artística", "Informática", "Religión"]}
}

MATERIAS_PRIMARIA = ["Matemáticas", "Lenguaje", "Ciencias Naturales", "Sociales", "Inglés", "Educación Física", "Ética", "Artística", "Informática", "Religión"]

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

ocultar_elementos = """
<style>
[data-testid="stToolbarActions"] { display: none !important; }
.viewerBadge_container { display: none !important; visibility: hidden !important; opacity: 0 !important; }
div[class^="viewerBadge"] { display: none !important; }
footer { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: visible; }
</style>
"""
st.markdown(ocultar_elementos, unsafe_allow_html=True)

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

# --- 2. CSS AVANZADO ---
st.markdown("""
<style>
.stApp { background-color: #ffffff; }
.stApp::before {
    content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
    background-size: 350px; background-repeat: no-repeat; background-position: center;
    opacity: 0.15; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
}
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
[data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
[data-testid="stSidebar"] * { color: white !important; font-weight: bold; }

.titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
.titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
.asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}

[data-testid="stPlotlyChart"] { transition: all 0.3s ease-out; border-radius: 12px; padding: 5px; background: white; border: 2px solid #000; will-change: transform; }
[data-testid="stPlotlyChart"]:hover { transform: translateY(-6px) scale(1.015); box-shadow: 0 15px 30px rgba(212, 175, 55, 0.6); z-index: 10; }

@keyframes pulso-rojo { 0% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 0, 0, 1), inset 0 0 10px rgba(255, 0, 0, 0.5); } 100% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } }
@keyframes pulso-naranja { 0% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 153, 0, 1), inset 0 0 10px rgba(255, 153, 0, 0.5); } 100% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } }
@keyframes pulso-verde { 0% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 153, 51, 1), inset 0 0 10px rgba(0, 153, 51, 0.5); } 100% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } }

.tarjeta-roja { animation: pulso-rojo 1.5s infinite; border: 3px solid #cc0000; border-left: 10px solid #cc0000; background:#ffe6e6; padding:15px; border-radius:8px; color: #000; }
.tarjeta-naranja { animation: pulso-naranja 2s infinite; border: 3px solid #cc8800; border-left: 10px solid #cc8800; background:#fff4e6; padding:15px; border-radius:8px; color: #000; }
.tarjeta-verde { animation: pulso-verde 2.5s infinite; border: 3px solid #00994c; border-left: 10px solid #00994c; background:#e6ffe6; padding:15px; border-radius:8px; color: #000; }

p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000; }

div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
div[data-baseweb="select"] > div * { color: #000000 !important; font-family: 'Arial Black', sans-serif !important; }
ul[role="listbox"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; }
ul[role="listbox"] li { background-color: #ffffff !important; color: #000000 !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; }
ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] { background-color: #d4af37 !important; color: #000000 !important; }

div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { background-color: #ffffff !important; color: #000000 !important; font-family: 'Arial', sans-serif !important; caret-color: #cc0000 !important; font-weight: bold; }

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] * { color: #ffffff !important; }
button[kind="primary"] * { color: #ffffff !important; }
button[kind="secondary"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; border-radius: 8px !important; }
button[kind="secondary"] * { color: #0d1b2a !important; font-weight: bold !important; }
button[kind="secondary"]:hover { background-color: #0d1b2a !important; }
button[kind="secondary"]:hover * { color: #d4af37 !important; }

div[data-baseweb="calendar"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; }
div[data-baseweb="calendar"] * { color: #000000 !important; background-color: transparent !important; }
div[data-baseweb="calendar"] div[role="button"]:hover { background-color: #f0f2f6 !important; }
div[data-baseweb="calendar"] div[aria-selected="true"] { background-color: #d4af37 !important; color: #0d1b2a !important; font-weight: bold !important; }

.stTabs [data-baseweb="tab-list"] button { font-family: 'Arial Black'; color: #0d1b2a; border-bottom: 2px solid transparent; }
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { border-bottom: 3px solid #d4af37; color: #d4af37; background-color: #0d1b2a; border-radius: 5px 5px 0 0; }

.metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
.metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
.metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
.footer-legal { font-size: 10px; color: #888888; text-align: center; margin-top: 50px; border-top: 1px solid #eeeeee; padding-top: 10px; font-family: 'Arial', sans-serif; }

[data-testid="stExpander"] { background-color: #ffffff !important; border: 2px solid #d4af37 !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { background-color: #ffffff !important; }
[data-testid="stExpander"] summary:hover { background-color: #f0f0f0 !important; }
[data-testid="stExpander"] summary * { color: #000000 !important; font-weight: bold !important; }
[data-testid="stExpanderDetails"] { background-color: #ffffff !important; }
[data-testid="stExpanderDetails"] * { color: #000000 !important; }
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

def generar_pdf(html_contenido):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_contenido.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

# --- 3. LOGIN SEGURO ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        from PIL import Image
        try: st.image(Image.open("logo.png"), width=250)
        except: pass 
          
        st.markdown("""div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px; margin-top: -10px;"><h3 style="color:#000000; font-family:'Arial Black'; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        
        u = st.text_input("👤 Usuario", placeholder="Ej: admin", label_visibility="collapsed")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 INGRESAR", use_container_width=True):
            with st.spinner("Validando en Bóveda Satelital..."):
                try:
                    if u == "admin":
                        clave_secreta = st.secrets.get("CLAVE_MAESTRA", "Genesis2026*") 
                        if p == clave_secreta:
                            st.session_state.logueado = True
                            st.session_state.rol = "Admin"
                            st.session_state.usuario_actual = u
                            st.session_state.nombre_completo_usuario = "Comandante Supremo"
                            registrar_bitacora(u, "Admin", "✅ Ingreso Comandante")
                            st.rerun()
                        else:
                            st.error("🚨 Acceso Denegado: Llave maestra incorrecta.")
                            st.stop()
                            
                    df_usuarios = conn.read(worksheet='DATA_USUARIOS', ttl=0) 
                    acceso = df_usuarios[(df_usuarios['USUARIO'] == u) & (df_usuarios['PASSWORD'] == p)]
                    
                    if not acceso.empty:
                        estado = str(acceso['ESTADO'].iloc[0]).strip().upper()
                        rol = str(acceso['ROL'].iloc[0]).strip().capitalize()
                        if estado == "ACTIVO":
                            st.session_state.logueado = True
                            st.session_state.rol = rol
                            st.session_state.usuario_actual = u
                            if 'Nombre_Completo' in df_usuarios.columns:
                                st.session_state.nombre_completo_usuario = str(acceso['Nombre_Completo'].iloc[0]).strip()
                            else:
                                st.session_state.nombre_completo_usuario = u
                            registrar_bitacora(u, rol, "✅ Ingreso Exitoso")
                            st.rerun()
                        else: st.error("🚨 Acceso Denegado: Cuenta inactiva.")
                    else: st.error("🚨 Acceso Denegado: Credenciales incorrectas.")
                except Exception as e:
                    st.error("🚨 Error de conexión con la base de datos satelital.")
    st.stop() 

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.image("logo.png", width=120)
    nombre_mostrar = st.session_state.nombre_completo_usuario if st.session_state.nombre_completo_usuario else st.session_state.usuario_actual.upper()
    st.markdown(f"<h3 style='color:white; margin-top:0;'>👤 {nombre_mostrar}</h3><p style='color:#d4af37; font-weight:bold; margin-top:-15px;'>Rango: {st.session_state.rol}</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style='background:rgba(212, 175, 55, 0.1); border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center; margin-bottom:15px;'>
            <p style='color:#d4af37; font-size:12px; margin:0;'>🕒 HORA DE INICIO</p>
            <p style='color:white; font-size:18px; font-weight:bold; margin:0;'>{st.session_state.hora_inicio}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    opciones_menu = ["🏠 Inicio", "🕒 Horarios y Asignaciones", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": 
        opciones_menu.insert(1, "🛡️ Bitácora y Backup")
        opciones_menu.insert(1, "👑 Centro de Mando")
    if st.session_state.rol == "Docente":
        if "📜 Boletines" in opciones_menu: opciones_menu.remove("📜 Boletines")
    menu = st.radio("SECCIONES:", opciones_menu)
    
    usuario_activo = st.session_state.usuario_actual
    cursos = ["TODOS"] if st.session_state.rol == "Admin" else (ASIGNACIONES_DOCENTES[usuario_activo]["grados"] if usuario_activo in ASIGNACIONES_DOCENTES else ["Sin asignación"])

    st.markdown("---")
    curso_sel = st.selectbox("🎓 GRADO:", cursos)
    
    if st.session_state.rol == "Admin":
        materias_permitidas = ["TODAS"]
        if st.session_state.df_maestro is not None and 'Materia' in st.session_state.df_maestro.columns:
            materias_permitidas += sorted(st.session_state.df_maestro['Materia'].dropna().unique().astype(str).tolist())
    else:
        materias_permitidas = ["TODAS"] + (MATERIAS_PRIMARIA if ASIGNACIONES_DOCENTES.get(usuario_activo, {}).get("materias") == "TODAS" else ASIGNACIONES_DOCENTES.get(usuario_activo, {}).get("materias", ["Sin asignación"]))

    materia_sel = st.selectbox("📚 MATERIA:", materias_permitidas)
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if st.button("🔴 Salir"): 
        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🚪 Salida")
        st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = False, "", ""
        st.rerun()

# --- 5. ENCABEZADO FIJO ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h1></div>", unsafe_allow_html=True)

msg_dict = {
    "🏠 Inicio": "Sistema persistente y sincronizado con éxito.",
    "🕒 Horarios y Asignaciones": "Radar de cuadrícula temporal activo. Cero colisiones.",
    "👑 Centro de Mando": "Visión satelital activada. Datos exclusivos de Rectoría.",
    "🛡️ Bitácora y Backup": "Descargue aquí el Excel con el historial de trabajo.",
    "📊 Inteligencia Académica": "Análisis de pelotón en español activo.",
    "📈 Dashboard Estudiantil": "Radar táctico de rendimiento individual activo.",
    "🚦 Semáforo Académico": "Balizas de alerta en tiempo real.",
    "✍️ Digitar Notas": "El sistema protege las notas. Rango válido: 1.0 a 10.0",
    "📚 Logros": "Diccionario protegido.",
    "📝 Asistencias y Reportes": "Registre fallas y observaciones disciplinarias.",
    "📜 Boletines": "Generador de impresión VIP activo.",
    "📖 Manual de Usuario": "Módulos de información listos.",
    "📸 Eventos Institucionales": "Módulos de información listos."
}
msg_bot = msg_dict.get(menu, "Módulo en línea y operando.")
    
st.markdown(f"""
<div class="asistente-box">
   <img src="https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png" width="30" style="margin-right:15px;">
   <div style="display:flex; align-items:center;">
       <span style="color:#000000; font-weight:900; margin-right:10px;">Génesis:</span>
       <span style="color:#000000; font-size:14px; font-weight:bold; font-style:italic;">"{msg_bot}"</span>
   </div>
</div>
""", unsafe_allow_html=True)

# --- 6. ZONA DE TRABAJO ---
if 'df_maestro' not in st.session_state or st.session_state.df_maestro is None or st.session_state.df_maestro.empty:
    with st.spinner("📡 Descargando notas de la base satelital..."):
        df_notas = conn.read(worksheet='NOTAS_CONSOLIDADAS', ttl=600)
        df_notas = df_notas.rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo', 'ASIGNATURA': 'Materia', 'LOGROS': 'LOGRO'})
        df_estud = conn.read(worksheet='DATA_ESTUDIANTES', ttl=600)
        if 'Nombre_Completo' not in df_estud.columns and 'NOMBRE_COMPLETO' in df_estud.columns:
            df_estud = df_estud.rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo'})
        df_grados = df_estud[['Nombre_Completo', 'Grado']].drop_duplicates()
        st.session_state.df_maestro = pd.merge(df_notas, df_grados, on='Nombre_Completo', how='left')
        
if 'df_logros' not in st.session_state or st.session_state.df_logros is None or st.session_state.df_logros.empty:
    with st.spinner("📡 Descargando logros de la base satelital..."):
        st.session_state.df_logros = conn.read(worksheet='DB_LOGROS', ttl=600)
        
df_m = st.session_state.df_maestro
df_l = st.session_state.df_logros
 
if df_m is not None and not df_m.empty:
    df_m['Grado'] = df_m['Grado'].fillna("Sin Grado") 
    for col_nota in ['P1', 'P2', 'P3', 'P4']:
        if col_nota in df_m.columns:
            df_m[col_nota] = pd.to_numeric(df_m[col_nota], errors='coerce').fillna(0.0).round(1)
    if all(c in df_m.columns for c in ['P1', 'P2', 'P3', 'P4']):
        df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
    df_temp = df_m.copy()
    if str(curso_sel) != "TODOS":
        df_temp = df_temp[df_temp['Grado'].astype(str) == str(curso_sel)]
    if str(materia_sel) != "TODAS" and str(materia_sel) != "Sin asignación" and 'Materia' in df_temp.columns:
        df_temp = df_temp[df_temp['Materia'].astype(str) == str(materia_sel)]
    df = df_temp.copy()
else:
    st.error("📡 Interferencia satelital.")
    st.stop()
    
if menu == "🏠 Inicio":
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.markdown("""<div style="background:rgba(255,255,255,0.95); padding:15px; border-radius:10px; border-left:6px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#000; margin-bottom:15px; border:2px solid #000;">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif;">¡Bienvenido a la PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026!</h3>
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
        try: st.image("logo.png", width=400)
        except: pass
 
elif menu == "👑 Centro de Mando":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Mando | Nivel Rectoría</h3>", unsafe_allow_html=True)
    
    # --- AJUSTE: CORRECCIÓN DE KPI DE FILAS A ESTUDIANTES REALES ---
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else 0
    promedio_colegio = df[col_n].mean() if not df.empty else 0
    
    # Cálculo preciso agrupando por alumno único
    df_grupo_unicos = df.groupby('Nombre_Completo')[col_n].mean().reset_index()
    est_en_riesgo = len(df_grupo_unicos[df_grupo_unicos[col_n] < 6.0])
    porcentaje_riesgo = (est_en_riesgo / total_estudiantes * 100) if total_estudiantes > 0 else 0
    eficiencia_interna = 100 - porcentaje_riesgo
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Estudiantes Actuales</p><p class='metric-value'>{total_estudiantes}</p></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio Selección</p><p class='metric-value'>{promedio_colegio:.1f}</p></div>", unsafe_allow_html=True)
    with col3: 
        color_e = "#00994c" if eficiencia_interna > 85 else "#cc8800"
        st.markdown(f"<div class='metric-card' style='border-top-color:{color_e}'><p class='metric-label'>Índice de Eficiencia</p><p class='metric-value' style='color:{color_e}'>{eficiencia_interna:.1f}%</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if eficiencia_interna < 80:
        st.warning(f"⚠️ Alerta de Rectoría: El {porcentaje_riesgo:.1f}% de la población estudiantil presenta riesgo de reprobación.")
 
    st.markdown("---")
    st.subheader("🔐 Gestión de Seguridad de Periodos")
    try:
        df_config = conn.read(worksheet="Configuracion", ttl=0)
        col_1, col_2 = st.columns(2)
        nuevos_estados = []
        for i, fila in df_config.iterrows():
            with col_1 if i < 2 else col_2:
                bloqueado = st.toggle(f"Cerrar {fila['Periodo']}", value=(fila['Estado'] == "Cerrado"))
                nuevos_estados.append("Cerrado" if bloqueado else "Abierto")
        if st.button("🔴 APLICAR BLOQUEO / APERTURA GENERAL", type="primary"):
            with st.spinner("🚀 Transmitiendo órdenes de seguridad..."):
                df_config['Estado'] = nuevos_estados
                conn.update(worksheet="Configuracion", data=df_config)
                st.success("✅ Protocolo actualizado.")
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🔐 Modificó la seguridad de los periodos")
                st.balloons()
                st.rerun()
    except Exception as e:
        st.error(f"❌ Error en 'Configuracion': {e}")
   
elif menu == "🛡️ Bitácora y Backup":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
    def guardar_como_tabla(df_export, writer_obj, sheet_name):
        if df_export is None or df_export.empty: return
        df_export.columns = df_export.columns.astype(str) 
        df_export.to_excel(writer_obj, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer_obj.sheets[sheet_name]
        (max_row, max_col) = df_export.shape
        column_settings = [{'header': col} for col in df_export.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'style': 'Table Style Medium 4'})
        for i in range(max_col): worksheet.set_column(i, i, 25) 
 
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        guardar_como_tabla(st.session_state.df_maestro, writer, 'NOTAS_CONSOLIDADAS')
        guardar_como_tabla(st.session_state.df_logros, writer, 'DB_LOGROS')
        guardar_como_tabla(st.session_state.df_asistencia, writer, 'DB_ASISTENCIA')
        if st.session_state.bitacora: guardar_como_tabla(pd.DataFrame(st.session_state.bitacora), writer, 'BITACORA')
    
    st.download_button(label="📥 DESCARGAR BASE DE DATOS ACTUALIZADA (EXCEL)", data=buffer.getvalue(), file_name=f"Backup_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.ms-excel", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>🇨🇴 Módulo de Exportación SIMAT (MEN)</h4>", unsafe_allow_html=True)
    if not df_m.empty and 'Nombre_Completo' in df_m.columns:
        columnas_simat = [c for c in ['ID_Est', 'Nombre_Completo', 'Grado'] if c in df_m.columns]
        df_simat = df_m[columnas_simat].drop_duplicates().copy()
        df_simat['ESTADO_MATRICULA'] = "MATRICULADO"
        df_simat['FECHA_REPORTE'] = datetime.now(zona_colombia).strftime("%Y-%m-%d")
        buffer_simat = io.BytesIO()
        with pd.ExcelWriter(buffer_simat, engine='xlsxwriter') as writer: guardar_como_tabla(df_simat, writer, 'REPORTE_SIMAT')
        st.download_button(label="📄 DESCARGAR PLANTILLA SIMAT OFICIAL", data=buffer_simat.getvalue(), file_name=f"SIMAT_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d')}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
    
    st.markdown("---")
    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>Registro Histórico de Usuarios</h4>", unsafe_allow_html=True)
    if st.session_state.bitacora: st.dataframe(pd.DataFrame(st.session_state.bitacora).iloc[::-1].reset_index(drop=True), use_container_width=True)

elif menu == "🕒 Horarios y Asignaciones":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🕒 Matriz de Horarios Oficiales</h3>", unsafe_allow_html=True)
    try:
        df_horarios = conn.read(worksheet="DB_HORARIOS", ttl=0).dropna(subset=['DÍA', 'BLOQUE_HORARIO'])
    except:
        st.error("🚨 Falla Crítica: No se encontró la pestaña 'DB_HORARIOS'.")
        st.stop()
    df_horarios = df_horarios.fillna("")
    for col in df_horarios.columns: df_horarios[col] = df_horarios[col].astype(str).str.strip()
    if st.session_state.rol == "Admin":
        tipo_vista = st.radio("Seleccione el Modo de Radar:", ["🧑‍🏫 Vista por Docente", "🎓 Vista por Grado"], horizontal=True)
        if tipo_vista == "🧑‍🏫 Vista por Docente":
            docentes_lista = sorted([str(d) for d in df_horarios['DOCENTE'].unique() if str(d).upper() not in ['N/A', 'NAN', '']])
            objetivo = st.selectbox("🔍 Seleccione el Docente a Inspeccionar:", docentes_lista)
            df_filtro = df_horarios[df_horarios['DOCENTE'] == objetivo].copy()
            df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#666; font-size:12px;'>(" + df_filtro['GRADO'] + ")</span>"
        else:
            grados_lista = sorted([str(g) for g in df_horarios['GRADO'].unique() if str(g).upper() not in ['N/A', 'NAN', '']])
            objetivo = st.selectbox("🔍 Seleccione el Grado a Inspeccionar:", grados_lista)
            df_filtro = df_horarios[df_horarios['GRADO'] == objetivo].copy()
            df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#0d1b2a; font-size:11px;'>[" + df_filtro['DOCENTE'] + "]</span>"
    else:
        df_filtro = df_horarios[df_horarios['DOCENTE'].str.upper() == st.session_state.usuario_actual.upper()].copy()
        df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#666; font-size:12px;'>(" + df_filtro['GRADO'] + ")</span>"
    
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    df_filtro['DÍA'] = pd.Categorical(df_filtro['DÍA'].str.capitalize(), categories=dias_orden, ordered=True)
    matriz = df_filtro.pivot_table(index='BLOQUE_HORARIO', columns='DÍA', values='CELDA', aggfunc=lambda x: '<hr style="margin:5px 0;">'.join(x.astype(str))).fillna("")
    import re
    matriz['sort_key'] = matriz.index.map(lambda b: re.search(r'\((\d{2}:\d{2})', str(b)).group(1) if re.search(r'\((\d{2}:\d{2})', str(b)) else str(b))
    matriz = matriz.sort_values('sort_key').drop(columns=['sort_key'])
    
    html_tabla = "<table style='width:100%; border-collapse: collapse; text-align:center; border:3px solid #0d1b2a; margin-top:15px;'>"
    html_tabla += "<tr style='background-color:#0d1b2a; color:#d4af37;'><th style='padding:12px; border:1px solid #d4af37; width:15%; font-family:Arial Black;'>HORARIO</th>"
    for d in dias_orden:
        if d in matriz.columns: html_tabla += f"<th style='padding:12px; border:1px solid #d4af37; font-family:Arial Black;'>{d.upper()}</th>"
    html_tabla += "</tr>"
    for bloque, row in matriz.iterrows():
        if "DESCANSO" in bloque.upper():
            html_tabla += f"<tr style='background-color:#f0f2f6;'><td style='padding:10px; font-weight:bold; border:1px solid #ccc; color:#0d1b2a;'>{bloque}</td>"
            for d in dias_orden:
                if d in matriz.columns: html_tabla += f"<td style='padding:10px; color:#888; font-style:italic; border:1px solid #ccc; font-weight:bold;'>🥪 RECESO</td>"
            html_tabla += "</tr>"
        else:
            html_tabla += f"<tr><td style='padding:10px; font-weight:bold; background-color:#fafafa; border:1px solid #ccc; color:#0d1b2a;'>{bloque}</td>"
            for d in dias_orden:
                if d in matriz.columns:
                    val = row[d]
                    if val == "": html_tabla += f"<td style='padding:10px; background-color:white; border:1px solid #ccc;'></td>"
                    else:
                        bg_color = "#ffe6e6" if "<hr" in val else ("#e6ffe6" if st.session_state.rol != "Admin" or tipo_vista == "🧑‍🏫 Vista por Docente" else "#e6f2ff")
                        borde_fuerte = "border:2px solid #cc0000;" if "<hr" in val else "border:1px solid #ccc;"
                        html_tabla += f"<td style='padding:10px; background-color:{bg_color}; {borde_fuerte} font-weight:bold; color:#000;'>{val}</td>"
            html_tabla += "</tr>"
    html_tabla += "</table>"
    st.markdown(html_tabla, unsafe_allow_html=True)
    if "<hr" in html_tabla: st.error("🚨 ALERTA DE COLISIÓN.")

elif menu == "📊 Inteligencia Académica":
    config_espanol = {'locale': 'es', 'displaylogo': False}
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; border:2px solid #d4af37;'>Rendimiento por Materia ({periodo_sel})</div>", unsafe_allow_html=True)
        df_promedios = df.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
        fig1 = px.bar(df_promedios, x=col_n, y='Materia', text_auto='.1f', color='Materia', orientation='h')
        fig1.update_layout(height=260, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        fig1.update_yaxes(tickfont=dict(size=14, color='#000000', family="Arial Black"), automargin=True) 
        st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
    with c2: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; border:2px solid #d4af37;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
        df['DESEMPEÑO_FILTRO'] = df[col_n].apply(lambda n: 'BAJO' if n < 6.0 else ('BÁSICO' if n < 7.6 else ('ALTO' if n < 9.1 else 'SUPERIOR')))
        fig2 = px.pie(df, names='DESEMPEÑO_FILTRO', hole=0.4, color_discrete_map={'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'})
        fig2.update_traces(textinfo='percent+label', textfont=dict(color="#000", family="Arial Black"))
        fig2.update_layout(height=260, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config=config_espanol)

elif menu == "📈 Dashboard Estudiantil":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Radar Táctico Individual</h3>", unsafe_allow_html=True)
    lista_alumnos_dash = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
    alumno_analisis = st.selectbox("🎯 Seleccione Estudiante a Inspeccionar:", lista_alumnos_dash)
    if alumno_analisis:
        df_alum = df[df['Nombre_Completo'] == alumno_analisis]
        promedio_global = df_alum[col_n].mean()
        des_global = 'BAJO 🔴' if promedio_global < 6.0 else ('BÁSICO 🟡' if promedio_global < 7.6 else ('ALTO 🟢' if promedio_global < 9.1 else 'SUPERIOR 🌟'))
        novedades_count = len(st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_analisis]) if st.session_state.df_asistencia is not None else 0
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio ({periodo_sel})</p><p class='metric-value'>{promedio_global:.1f}</p></div>", unsafe_allow_html=True)
        with col_m2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Nivel Actual</p><p class='metric-value'>{des_global}</p></div>", unsafe_allow_html=True)
        with col_m3: st.markdown(f"<div class='metric-card'><p class='metric-label'>Novedades / Faltas</p><p class='metric-value'>{novedades_count}</p></div>", unsafe_allow_html=True)
        col_r1, col_r2 = st.columns([1.2, 1])
        with col_r1:
            fig_radar = px.line_polar(df_alum, r=col_n, theta='Materia', line_close=True, range_r=[0,10], text=col_n)
            fig_radar.update_traces(fill='toself', fillcolor='rgba(212, 175, 55, 0.4)', line_color='#0d1b2a', mode='lines+markers+text', textfont=dict(color='#000000', family='Arial Black'))
            st.plotly_chart(fig_radar, use_container_width=True, config={'displaylogo': False})
        with col_r2:
            if novedades_count > 0: st.dataframe(st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_analisis][['FECHA', 'ESTADO', 'OBSERVACIONES']], use_container_width=True, hide_index=True)
            else: st.info("✅ Sin reportes disciplinarios.")

elif menu == "🚦 Semáforo Académico":
    st.markdown(f"<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Semáforo de Riesgo Académico - Grado {curso_sel} ({periodo_sel})</h3>", unsafe_allow_html=True)
    df_estudiantes = df.groupby(['Nombre_Completo', 'Grado'])[col_n].mean().reset_index()
    df_estudiantes['ESTADO'] = df_estudiantes[col_n].apply(lambda n: '🔴 CRÍTICO' if n < 6.0 else ('🟡 ALERTA' if n < 7.6 else '🟢 ÓPTIMO'))
    criticos = df_estudiantes[df_estudiantes['ESTADO'] == '🔴 CRÍTICO']
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='tarjeta-roja'><h4>🔴 Riesgo Crítico</h4><h1>{len(criticos)}</h1></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='tarjeta-naranja'><h4>🟡 Alerta</h4><h1>{len(df_estudiantes[df_estudiantes['ESTADO'] == '🟡 ALERTA'])}</h1></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='tarjeta-verde'><h4>🟢 Óptimo</h4><h1>{len(df_estudiantes[df_estudiantes['ESTADO'] == '🟢 ÓPTIMO'])}</h1></div>", unsafe_allow_html=True)
    if not criticos.empty: st.dataframe(criticos[['Nombre_Completo', 'Grado', col_n]], use_container_width=True, hide_index=True)

elif menu == "✍️ Digitar Notas":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)
    try:
        df_conf_shield = conn.read(worksheet="Configuracion", ttl=0)
        if df_conf_shield[df_conf_shield['Periodo'] == periodo_sel]['Estado'].values[0] == "Cerrado":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO.")
            st.stop()
    except: pass
    config_notas = {'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1), 'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1), 'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1), 'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1), 'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True), 'Materia': st.column_config.TextColumn("Asignatura", disabled=True), 'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True)}
    col_btn, _ = st.columns([2, 8])
    with col_btn:
        if st.button("💾 GUARDAR EN EXCEL", type="primary", use_container_width=True):
            cambios = st.session_state.editor_notas.get('edited_rows', {})
            if cambios:
                for f, v in cambios.items():
                    idx = df.index[int(f)]
                    for c, val in v.items(): st.session_state.df_maestro.at[idx, c] = val
                st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                df_para_drive = st.session_state.df_maestro.copy().drop(columns=['Grado'], errors='ignore').rename(columns={'Nombre_Completo': 'NOMBRE_COMPLETO', 'Materia': 'ASIGNATURA', 'LOGRO': 'LOGROS'})
                conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_para_drive)
                st.success("✅ ¡SATÉLITE SINCRONIZADO!")
                st.balloons()
                st.rerun()
    st.data_editor(df, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)

elif menu == "📚 Logros":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📚 Diccionario Oficial de Logros</h3>", unsafe_allow_html=True)
    if st.session_state.rol == "Admin":
        col_btn, _ = st.columns([2, 8])
        with col_btn:
            if st.button("💾 GUARDAR LOGROS", type="primary", use_container_width=True):
                st.session_state.df_logros = st.session_state.df_l_temp
                conn.update(worksheet="DB_LOGROS", data=st.session_state.df_logros)
                st.success("✅ Logros asegurados.")
                st.rerun()
        st.session_state.df_l_temp = st.data_editor(df_l, use_container_width=True, num_rows="dynamic", height=300, key="editor_logros")
    else: st.dataframe(df_l, use_container_width=True, height=300, hide_index=True)

elif menu == "📝 Asistencias y Reportes":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Control de Asistencia y Observaciones</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["✍️ Registrar Novedad", "🖨️ Generar Observador Oficial"])
    with tab1:
        with st.form("form_novedad"):
            col1, col2, col3 = st.columns(3)
            with col1: alum_sel = st.selectbox("👤 Estudiante:", sorted(df['Nombre_Completo'].dropna().unique()))
            with col2: fecha_sel = st.date_input("📅 Fecha:")
            with col3: estado_sel = st.selectbox("🚦 Estado / Tipo:", ["Falla", "Retardo", "Excusa", "Llamado de Atención", "Felicitación"])
            obs_sel = st.text_area("📝 Observaciones:")
            if st.form_submit_button("💾 GUARDAR REPORTE", type="primary") and alum_sel:
                grado_alum = df[df['Nombre_Completo'] == alum_sel]['Grado'].iloc[0] if not df[df['Nombre_Completo'] == alum_sel].empty else "N/A"
                nuevo = pd.DataFrame([{'Nombre_Completo': alum_sel, 'GRADO': grado_alum, 'FECHA': fecha_sel.strftime("%Y-%m-%d"), 'ESTADO': estado_sel, 'OBSERVACIONES': obs_sel}])
                st.session_state.df_asistencia = pd.concat([st.session_state.df_asistencia, nuevo], ignore_index=True)
                conn.update(worksheet="DB_ASISTENCIA", data=st.session_state.df_asistencia)
                st.success("✅ Reporte guardado.")
        if st.session_state.df_asistencia is not None: st.dataframe(st.session_state.df_asistencia.iloc[::-1], use_container_width=True, hide_index=True)
    with tab2:
        alumno_obs = st.selectbox("👤 Buscar Estudiante:", sorted(df['Nombre_Completo'].dropna().unique()), key="sel_obs")
        if st.button("🖨️ PREPARAR OBSERVADOR", type="primary") and st.session_state.df_asistencia is not None:
            df_obs_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_obs]
            if not df_obs_alum.empty:
                html_obs = f"<html><body><h2>ACADEMIA GLOBAL HORIZONTE</h2><p><b>Estudiante:</b> {alumno_obs}</p><table border='1'>"
                for _, r in df_obs_alum.iterrows(): html_obs += f"<tr><td>{r['FECHA']}</td><td>{r['ESTADO']}</td><td>{r['OBSERVACIONES']}</td></tr>"
                html_obs += "</table></body></html>"
                components.html(html_obs, height=400)

# =========================================================
# 👑 TERMINAL ACADÉMICA VIP REESTRUCTURADA (MENÚ 8)
# =========================================================
elif menu == "📜 Boletines":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Central de Impresión VIP</h3>", unsafe_allow_html=True)
    
    # 🚀 PANEL DE CONTROL SUPER-COMPACTO NUEVO
    st.markdown("<div class='no-print' style='background:#f8f9fa; padding:12px; border-radius:8px; border: 2px solid #0d1b2a; margin-bottom:15px;'>", unsafe_allow_html=True)
    c_print_1, c_print_2 = st.columns([4, 6])
    with c_print_1:
        modo_impresion = st.radio("🛠️ Modo de Generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True)
    with c_print_2:
        opciones_p = ["P1", "P2", "P3", "P4", "FINAL"]
        def_p = ["P1", "P2", "P3", "P4", "FINAL"] if "CONSOLID" in str(periodo_sel).upper() else [periodo_sel]
        def_p = [p for p in def_p if p in opciones_p]
        if not def_p: def_p = ["FINAL"]
        # Selector dinámico de periodos para que el usuario elija
        periodos_print = st.multiselect("📊 Columnas a Imprimir en el Reporte:", opciones_p, default=def_p)
    st.markdown("</div>", unsafe_allow_html=True)

    if not periodos_print:
        st.warning("⚠️ Seleccione al menos un periodo para compilar.")
        st.stop()

    css_vip = """<style>
        body { font-family: Arial, sans-serif; background: white; color: black; } 
        .b-print { position: relative; padding: 30px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; } 
        .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: -1; pointer-events: none; } 
        .table-custom { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; z-index: 2; position: relative; } 
        .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 10px; font-family: 'Arial Black'; } 
        .table-custom td { border: 1px solid #000; padding: 8px; background-color: rgba(255, 255, 255, 0.85); text-align: center; } 
        .header-table { width: 100%; border: none; margin-bottom: 15px; z-index: 2; position: relative; } 
        .header-table td { border: none; } 
        .firmas-container { display: flex; justify-content: space-around; margin-top: 60px; font-size: 14px; z-index: 2; position: relative; page-break-inside: avoid; } 
        .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; } 
        @media print { 
            @page { size: legal portrait; margin: 10mm; } 
            body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } 
            .no-print { display: none !important; } 
            .b-print { border: none; box-shadow: none; padding: 0; } 
            .salto-pagina { page-break-after: always; } 
        }
    </style>"""   

    df_boletines_base = df_m.copy() if df_m is not None else pd.DataFrame()
    if curso_sel != "TODOS":
        df_boletines_base = df_boletines_base[df_boletines_base['Grado'].astype(str) == str(curso_sel)]
    
    # 🏆 MOTOR DE PUESTOS ACADÉMICOS (Algoritmo de unificación por promedio de periodo activo)
    df_boletines_base[col_n] = pd.to_numeric(df_boletines_base[col_n], errors='coerce').fillna(0.0)
    df_puestos_calc = df_boletines_base.groupby(['Grado', 'Nombre_Completo'])[col_n].mean().reset_index()
    df_puestos_calc['Puesto'] = df_puestos_calc.groupby('Grado')[col_n].rank(ascending=False, method='min').astype(int)
    df_puestos_calc['Total_Grado'] = df_puestos_calc.groupby('Grado')['Nombre_Completo'].transform('count')
    mapa_puestos = {row['Nombre_Completo']: f"{row['Puesto']} de {row['Total_Grado']}" for _, row in df_puestos_calc.iterrows()}

    diccionario_logros = {}
    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
        for _, l_row in st.session_state.df_logros.iterrows():
            try:
                k = (str(l_row.iloc[0]).strip().upper(), str(l_row.iloc[1]).strip().upper(), str(l_row.iloc[2]).strip().upper())
                diccionario_logros[k] = str(l_row.iloc[3])
            except: pass

    try:
        with open("logo.png", "rb") as img_file: b64_string = base64.b64encode(img_file.read()).decode()
        URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
    except: URL_LOGO_OFICIAL = ""

    # Dibuja los encabezados de las materias dinámicamente según la selección
    th_dinamico = "".join([f"<th>{p}</th>" for p in periodos_print])
    col_span_logro = len(periodos_print) + 2

    if modo_impresion == "👤 Individual":
        alumno = st.selectbox("👤 Estudiante:", sorted(df_boletines_base['Nombre_Completo'].dropna().unique()))
        if alumno:
            res = df_boletines_base[df_boletines_base['Nombre_Completo'] == alumno].drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0]
            
            promedios = [nota_limpia(x) for x in res[col_n]]
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
                logro_texto = diccionario_logros.get(llave_busqueda, row.get('LOGRO', 'Descriptor no encontrado en BD'))
                if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']: logro_texto = "Pendiente de registro."
                
                html_boletin += f"<tr><td colspan='{col_span_logro}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
            
            html_boletin += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div></body></html>"""
            
            pdf_data = generar_pdf(html_boletin)
            if pdf_data:
                _, col_boton_pequeno = st.columns([8, 2])
                with col_boton_pequeno:
                    st.download_button(label="📥 DESCARGAR PDF", data=pdf_data, file_name=f"Boletin_{alumno}_{periodo_sel}.pdf", mime="application/pdf", type="primary", use_container_width=True)
            
            components.html(html_boletin, height=650, scrolling=True)

    else:
        estudiantes = sorted(df_boletines_base['Nombre_Completo'].dropna().unique())
        st.warning(f"⚠️ Se generarán {len(estudiantes)} boletines VIP en formato LEGAL para el grado {curso_sel}.")
        
        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary", use_container_width=True):
            html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body><div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;"><button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR LOTE MASIVO</button></div>"""
            
            for i, alum in enumerate(estudiantes):
                res = df_boletines_base[df_boletines_base['Nombre_Completo'] == alum].drop_duplicates(subset=['Materia'])
                res = res[res['PROMEDIO'] > 0.0]
                if res.empty: continue
                
                promedios = [nota_limpia(x) for x in res[col_n]]
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
                    logro_texto = diccionario_logros.get(llave_busqueda, row.get('LOGRO', 'Descriptor no encontrado en BD'))
                    if str(logro_texto).strip().lower() in ['nan', 'none', '<na>', 'null', '']: logro_texto = "Pendiente de registro."
                    
                    html_masivo += f"<tr><td colspan='{col_span_logro}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
                
                html_masivo += """</table><div class='firmas-container'><div class='firma-box'>Firma Rectoría<br><span style='font-size:9px; font-weight:normal;'>Sello Institucional</span></div><div class='firma-box'>Firma Director de Grupo</div></div></div>"""
                
            html_masivo += "</body></html>"
            st.toast("✅ ¡Compilación Masiva Finalizada con Éxito!", icon="🚀")
            components.html(html_masivo, height=650, scrolling=True)

elif menu == "📖 Manual de Usuario":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📖 Manual de Operaciones Génesis AGH</h3>", unsafe_allow_html=True)
    with st.expander("🔐 1. ACCESO Y SEGURIDAD", expanded=True):
        st.write("""
        * **Ingreso:** Utilice sus credenciales asignadas. El sistema registra cada ingreso en la bitácora de seguridad.
        * **Habeas Data:** Al ingresar, usted acepta el tratamiento de datos personales bajo la Ley 1581 de 2012. 
        * **Cierre de Sesión:** Siempre use el botón 'Salir' para proteger la información de los menores.
        """)
    with st.expander("✍️ 2. GESTIÓN ACADÉMICA (NOTAS)"):
        st.write("""
        * **Rango:** El sistema solo permite notas entre 1.0 y 10.0.
        * **Guardado:** Es obligatorio presionar el botón azul **'GUARDAR'** después de digitar. Si no lo hace, el satélite no recibirá los datos.
        * **Escala MEN:** El sistema traduce automáticamente su nota numérica a la escala nacional (Bajo, Básico, Alto, Superior).
        """)
    with st.expander("📝 3. CONVIVENCIA Y ASISTENCIA"):
        st.write("""
        * **Registro:** En la pestaña 'Registrar Novedad' puede anotar fallas, retardos o felicitaciones.
        * **Observador Oficial:** En la pestaña 'Generar Observador', seleccione al alumno y presione 'Preparar Observador' para obtener el documento legal listo para firmas.
        * **Corrección:** Si comete un error, use el botón **'↩️ DESHACER'** inmediatamente.
        """)

elif menu == "📸 Eventos Institucionales":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📸 Memorias Institucionales</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    try:
        c1.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", caption="Feria Científica")
        c2.image("https://images.unsplash.com/photo-1523580494112-071d1694335c?q=80&w=800", caption="Ceremonia de Grados")
        c3.image("https://images.unsplash.com/photo-1511632765486-a01980e01a18?q=80&w=800", caption="Comunidad Estudiantil")
    except: pass

st.markdown(f"""
    <div class='footer-legal'>
        PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026 - Sistema Génesis AGH © {datetime.now().year}<br>
        Protección de Datos Personales: En cumplimiento de la Ley 1581 de 2012, el tratamiento de la información aquí registrada es de carácter estrictamente institucional y confidencial.
    </div>
""", unsafe_allow_html=True)
