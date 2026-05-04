import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# 📋 MATRIZ DE MANDO: ASIGNACIONES ACADÉMICAS IE GÉNESIS 2026
ASIGNACIONES_DOCENTES = {
    # --- PRIMARIA (Carga Completa) ---
    "Priscila": {"grados": ["5°"], "materias": "TODAS"},
    "Celeste": {"grados": ["1°"], "materias": "TODAS"},
    "Maria": {"grados": ["2°"], "materias": "TODAS"},
    "Ana": {"grados": ["3°"], "materias": "TODAS"},
    "Juliana": {"grados": ["4°"], "materias": "TODAS"},

    # --- BACHILLERATO (Carga por Especialidad) ---
    "Daniel": {"grados": ["10°", "11°"], "materias": ["Física", "Matemáticas"]},
    "Rafael": {"grados": ["10°", "11°"], "materias": ["Química"]},
    "Ludis": {"grados": ["10°", "11°"], "materias": ["Filosofía", "Ética"]},
    "Arnaldo": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Matemáticas"]},
    
    # Profesores de área para toda la secundaria:
    "USUARIO_LENGUAJE": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Lenguaje"]},
    "USUARIO_SOCIALES": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Sociales", "Constitución"]},
    "USUARIO_INGLES": {"grados": ["6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Inglés"]},
    "USUARIO_CIENCIAS": {"grados": ["6°", "7°", "8°", "9°"], "materias": ["Ciencias Naturales"]},
    "USUARIO_ESPECIALIDADES": {"grados": ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "11°"], "materias": ["Educación Física", "Artística", "Informática", "Religión"]}
}

# Lista maestra de materias para Primaria (usada cuando dice "TODAS")
MATERIAS_PRIMARIA = ["Matemáticas", "Lenguaje", "Ciencias Naturales", "Sociales", "Inglés", "Educación Física", "Ética", "Artística", "Informática", "Religión"]

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")
# --- ARTILLERÍA PESADA: DESTRUCCIÓN DE MARCAS DE AGUA Y GATO GITHUB ---
arsenal_css = """
<style>
/* 1. Destruye el botón inferior derecho de "Gestionar Aplicación" y marca de agua */
.viewerBadge_container { display: none !important; visibility: hidden !important; opacity: 0 !important; }
div[class^="viewerBadge"] { display: none !important; }

/* 2. Destruye los botones de GitHub y Deploy de la barra superior */
[data-testid="stToolbarActions"] { display: none !important; visibility: hidden !important; }

/* 3. Destruye el footer (pie de página) que dice "Made with Streamlit" */
footer { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: visible; } /* Protege la hamburguesa */
</style>
"""
st.markdown(arsenal_css, unsafe_allow_html=True)

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

# --- 2. CSS AVANZADO (ESTABILIDAD GARANTIZADA) ---
st.markdown("""
<style>
/* RENDICIÓN TÁCTICA: DEJAMOS EL ENCABEZADO TRANQUILO PARA QUE EL MENÚ FUNCIONE PERFECTO */

/* --- DISEÑO ORIGINAL COMPLETO --- */
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

[data-testid="stPlotlyChart"] { transition: transform 0.3s ease, box-shadow 0.3s ease; border-radius: 12px; padding: 5px; background: white; border: 2px solid #000; }
[data-testid="stPlotlyChart"]:hover { transform: scale(1.03); box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4); z-index: 10; }

@keyframes pulso-rojo { 0% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 0, 0, 1), inset 0 0 10px rgba(255, 0, 0, 0.5); } 100% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } }
@keyframes pulso-naranja { 0% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 153, 0, 1), inset 0 0 10px rgba(255, 153, 0, 0.5); } 100% { box-shadow: 0 0 0px rgba(255, 170, 0, 0.4); } }
@keyframes pulso-verde { 0% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 153, 51, 1), inset 0 0 10px rgba(0, 153, 51, 0.5); } 100% { box-shadow: 0 0 0px rgba(0, 204, 102, 0.4); } }

.tarjeta-roja { animation: pulso-rojo 1.5s infinite; border: 3px solid #cc0000; border-left: 10px solid #cc0000; background:#ffe6e6; padding:15px; border-radius:8px; color: #000; }
.tarjeta-naranja { animation: pulso-naranja 2s infinite; border: 3px solid #cc8800; border-left: 10px solid #cc8800; background:#fff4e6; padding:15px; border-radius:8px; color: #000; }
.tarjeta-verde { animation: pulso-verde 2.5s infinite; border: 3px solid #00994c; border-left: 10px solid #00994c; background:#e6ffe6; padding:15px; border-radius:8px; color: #000; }

p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000; }

/* MENÚS DESPLEGABLES NATIVOS Y CAJAS DE TEXTO */
div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
div[data-baseweb="select"] > div * { color: #000000 !important; font-family: 'Arial Black', sans-serif !important; }
div[data-baseweb="popover"] > div, div[data-baseweb="popover"] ul { background-color: #ffffff !important; }
ul[role="listbox"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; }
ul[role="listbox"] li { background-color: #ffffff !important; color: #000000 !important; font-family: 'Arial Black', sans-serif !important; font-weight: bold !important; }
ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] { background-color: #d4af37 !important; color: #000000 !important; }

div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { background-color: #ffffff !important; color: #000000 !important; font-family: 'Arial', sans-serif !important; caret-color: #cc0000 !important; font-weight: bold; }

/* --- PINTURA PARA BOTONES (PRIMARIOS Y SECUNDARIOS) --- */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] * { color: #ffffff !important; }
button[kind="primary"] * { color: #ffffff !important; }

button[kind="secondary"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; border-radius: 8px !important; }
button[kind="secondary"] * { color: #0d1b2a !important; font-weight: bold !important; }
button[kind="secondary"]:hover { background-color: #0d1b2a !important; }
button[kind="secondary"]:hover * { color: #d4af37 !important; }

div[data-baseweb="calendar"] { background-color: #ffffff !important; border: 2px solid #0d1b2a !important; }
div[data-baseweb="calendar"] * { color: #000000 !important; background-color: transparent !important; }
div[data-baseweb="calendar"] div[role="button"]:hover { background-color: #f0f0f0 !important; }
div[data-baseweb="calendar"] div[aria-selected="true"] { background-color: #d4af37 !important; color: #0d1b2a !important; font-weight: bold !important; }

.stTabs [data-baseweb="tab-list"] button { font-family: 'Arial Black'; color: #0d1b2a; border-bottom: 2px solid transparent; }
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { border-bottom: 3px solid #d4af37; color: #d4af37; background-color: #0d1b2a; border-radius: 5px 5px 0 0; }

.metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
.metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
.metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
.footer-legal { font-size: 10px; color: #888888; text-align: center; margin-top: 50px; border-top: 1px solid #eeeeee; padding-top: 10px; font-family: 'Arial', sans-serif; }

/* --- REPARACIÓN DE MENÚS DESPLEGABLES (EXPANDERS DEL MANUAL) --- */
[data-testid="stExpander"] { background-color: #ffffff !important; border: 2px solid #d4af37 !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { background-color: #ffffff !important; }
[data-testid="stExpander"] summary:hover { background-color: #f0f0f0 !important; }
[data-testid="stExpander"] summary * { color: #000000 !important; font-weight: bold !important; }
[data-testid="stExpanderDetails"] { background-color: #ffffff !important; }
[data-testid="stExpanderDetails"] * { color: #000000 !important; }
</style>
/* 🎯 FRANCOTIRADOR: ELIMINAR EL GATO DE GITHUB Y BOTÓN DE DEPLOY, SALVANDO LA HAMBURGUESA */
[data-testid="stToolbarActions"] {
    display: none !important;
}
.viewerBadge_container {
    display: none !important;
}

""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

# --- 3. LOGIN SEGURO (BLINDADO Y EN TIEMPO REAL) ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        from PIL import Image
        try:
            st.image(Image.open("logo.png"), width=250)
        except Exception as e:
            pass 
          
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px; margin-top: -10px;"><h3 style="color:#000000; font-family:'Arial Black'; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        
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
                        else:
                            st.error("🚨 Acceso Denegado: Cuenta inactiva.")
                    else:
                        st.error("🚨 Acceso Denegado: Credenciales incorrectas.")
                        
                except Exception as e:
                    st.error("🚨 Error de conexión con la base de datos satelital. Notifique a Rectoría.")
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
    
    opciones_menu = ["🏠 Inicio", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": 
        opciones_menu.insert(1, "🛡️ Bitácora y Backup")
        opciones_menu.insert(1, "👑 Centro de Mando")
        
    menu = st.radio("SECCIONES:", opciones_menu)
    
    usuario_activo = st.session_state.usuario_actual
    cursos = []

    if st.session_state.rol == "Admin":
        cursos = ["TODOS"]
        if st.session_state.df_maestro is not None:
            cursos += sorted(st.session_state.df_maestro['Grado'].dropna().unique().astype(str).tolist())
    else:
        if usuario_activo in ASIGNACIONES_DOCENTES:
            cursos = ASIGNACIONES_DOCENTES[usuario_activo]["grados"]
        else:
            cursos = ["Sin asignación"] 

    st.markdown("---")
    curso_sel = st.selectbox("🎓 GRADO:", cursos)
    
    materias_permitidas = []
    if st.session_state.rol == "Admin":
        materias_permitidas = ["TODAS"]
        if st.session_state.df_maestro is not None and 'Materia' in st.session_state.df_maestro.columns:
            materias_permitidas += sorted(st.session_state.df_maestro['Materia'].dropna().unique().astype(str).tolist())
    else:
        if usuario_activo in ASIGNACIONES_DOCENTES:
            if ASIGNACIONES_DOCENTES[usuario_activo]["materias"] == "TODAS":
                # SOLUCIÓN: Agregamos "TODAS" al inicio de la lista de Primaria
                materias_permitidas = ["TODAS"] + MATERIAS_PRIMARIA
            else:
                # SOLUCIÓN: También le damos la opción "TODAS" a los de Bachillerato
                materias_permitidas = ["TODAS"] + ASIGNACIONES_DOCENTES[usuario_activo]["materias"]
        else:
            materias_permitidas = ["Sin asignación"]

    materia_sel = st.selectbox("📚 MATERIA:", materias_permitidas)
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if st.button("🔴 Salir"): 
        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "🚪 Salida")
        st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = False, "", ""
        st.rerun()

# --- 5. ENCABEZADO FIJO ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>INSTITUCIÓN EDUCATIVA GÉNESIS JORSUG 2026</h1></div>", unsafe_allow_html=True)

if menu == "🏠 Inicio": msg_bot = "Sistema persistente y sincronizado con éxito."
elif menu == "👑 Centro de Mando": msg_bot = "Visión satelital activada. Datos exclusivos de Rectoría."
elif menu == "🛡️ Bitácora y Backup": msg_bot = "Descargue aquí el Excel con el historial de trabajo."
elif menu == "📊 Inteligencia Académica": msg_bot = "Análisis de pelotón en español activo."
elif menu == "📈 Dashboard Estudiantil": msg_bot = "Radar táctico de rendimiento individual activo."
elif menu == "🚦 Semáforo Académico": msg_bot = "Balizas de alerta en tiempo real."
elif menu == "✍️ Digitar Notas": msg_bot = "El sistema protege las notas. Rango válido: 1.0 a 10.0"
elif menu == "📚 Logros": msg_bot = "Diccionario protegido."
elif menu == "📝 Asistencias y Reportes": msg_bot = "Registre fallas y observaciones disciplinarias."
elif menu == "📜 Boletines": msg_bot = "Generador de impresión VIP activo."
elif menu in ["📖 Manual de Usuario", "📸 Eventos Institucionales"]: msg_bot = "Módulos de información listos."

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
        df_notas = df_notas.rename(columns={
            'NOMBRE_COMPLETO': 'Nombre_Completo', 
            'ASIGNATURA': 'Materia',
            'LOGROS': 'LOGRO'
        })
        
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
    
    curso_texto = str(curso_sel)
    if curso_texto != "TODOS":
        df_temp = df_temp[df_temp['Grado'].astype(str) == curso_texto]
        
    materia_texto = str(materia_sel)
    if materia_texto != "TODAS" and materia_texto != "Sin asignación" and 'Materia' in df_temp.columns:
        df_temp = df_temp[df_temp['Materia'].astype(str) == materia_texto]
        
    df = df_temp.copy()
else:
    st.error("📡 Interferencia satelital: No se pudo descargar la pestaña de notas.")
    st.stop()
    
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
    
    # --- RESTAURACIÓN DE LA REGLA DE ORO ---
    # Usamos "df" para que los totales respondan al grado que seleccione en la barra izquierda.
    total_estudiantes = len(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else 0
    promedio_colegio = df[col_n].mean() if not df.empty else 0
    
    est_en_riesgo = df[df[col_n] < 6.0]['Nombre_Completo'].nunique()
    porcentaje_riesgo = (est_en_riesgo / total_estudiantes * 100) if total_estudiantes > 0 else 0
    eficiencia_interna = 100 - porcentaje_riesgo
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Estudiantes</p><p class='metric-value'>{total_estudiantes}</p></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio Institucional</p><p class='metric-value'>{promedio_colegio:.1f}</p></div>", unsafe_allow_html=True)
    with col3: 
        color_e = "#00994c" if eficiencia_interna > 85 else "#cc8800"
        st.markdown(f"<div class='metric-card' style='border-top-color:{color_e}'><p class='metric-label'>Índice de Eficiencia</p><p class='metric-value' style='color:{color_e}'>{eficiencia_interna:.1f}%</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if eficiencia_interna < 80:
        st.warning(f"⚠️ Alerta de Rectoría: El {porcentaje_riesgo:.1f}% de la población estudiantil presenta riesgo de reprobación.")
        
elif menu == "🛡️ Bitácora y Backup":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Centro de Respaldo y Trazabilidad</h3>", unsafe_allow_html=True)
    
    # ⚡ OPERACIÓN VELOCIDAD: Optimizamos la creación del Excel
    def guardar_como_tabla(df_export, writer_obj, sheet_name):
        if df_export is None or df_export.empty: return
        df_export.columns = df_export.columns.astype(str) 
        df_export.to_excel(writer_obj, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer_obj.sheets[sheet_name]
        (max_row, max_col) = df_export.shape
        
        column_settings = [{'header': col} for col in df_export.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            'columns': column_settings, 
            'style': 'Table Style Medium 4' 
        })
        
        # 🛡️ BLINDAJE DE VELOCIDAD: Asignamos un ancho fijo (25) en vez de hacer que 
        # el sistema lea miles de celdas para calcular el ancho exacto.
        for i in range(max_col):
            worksheet.set_column(i, i, 25) 

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        guardar_como_tabla(st.session_state.df_maestro, writer, 'NOTAS_CONSOLIDADAS')
        guardar_como_tabla(st.session_state.df_logros, writer, 'DB_LOGROS')
        guardar_como_tabla(st.session_state.df_asistencia, writer, 'DB_ASISTENCIA')
        if st.session_state.bitacora: 
            guardar_como_tabla(pd.DataFrame(st.session_state.bitacora), writer, 'BITACORA')
    
    st.info("Comandante, aquí puede descargar todo el trabajo. Es su copia de seguridad física.")
    st.download_button(label="📥 DESCARGAR BASE DE DATOS ACTUALIZADA (EXCEL)", data=buffer.getvalue(), file_name=f"Backup_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.ms-excel", type="primary", use_container_width=True)
    st.markdown("---")

    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>🇨🇴 Módulo de Exportación SIMAT (MEN)</h4>", unsafe_allow_html=True)
    st.write("Genera la plantilla estructurada con los estudiantes activos para reportar al Ministerio de Educación Nacional.")
    
    if not df_m.empty and 'Nombre_Completo' in df_m.columns:
        columnas_simat = [c for c in ['ID_Est', 'Nombre_Completo', 'Grado'] if c in df_m.columns]
        df_simat = df_m[columnas_simat].drop_duplicates().copy()
        df_simat['ESTADO_MATRICULA'] = "MATRICULADO"
        df_simat['FECHA_REPORTE'] = datetime.now(zona_colombia).strftime("%Y-%m-%d")
        
        buffer_simat = io.BytesIO()
        with pd.ExcelWriter(buffer_simat, engine='xlsxwriter') as writer:
            guardar_como_tabla(df_simat, writer, 'REPORTE_SIMAT')
            
        st.download_button(label="📄 DESCARGAR PLANTILLA SIMAT OFICIAL", data=buffer_simat.getvalue(), file_name=f"SIMAT_AGH_{datetime.now(zona_colombia).strftime('%Y%m%d')}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
    else:
        st.warning("No hay datos de estudiantes para generar el SIMAT.")
    st.markdown("---")
    
    st.markdown("<h4 style='color:#000; font-family:Arial Black;'>Registro Histórico de Usuarios</h4>", unsafe_allow_html=True)
    if st.session_state.bitacora: st.dataframe(pd.DataFrame(st.session_state.bitacora).iloc[::-1].reset_index(drop=True), use_container_width=True)
    
elif menu == "📊 Inteligencia Académica":
    config_espanol = {'locale': 'es', 'displaylogo': False}
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Rendimiento por Materia ({periodo_sel})</div>", unsafe_allow_html=True)
        df_promedios = df.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
        fig1 = px.bar(df_promedios, x=col_n, y='Materia', text_auto='.1f', color='Materia', orientation='h')
        fig1.update_layout(height=260, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        fig1.update_yaxes(title_text="", visible=True, tickmode='linear', dtick=1, tickfont=dict(size=14, color='#000000', family="Arial Black"), automargin=True) 
        fig1.update_xaxes(title_text="Promedio", title_font=dict(color="#000", family="Arial Black"), tickfont=dict(color="#000", family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
    with c2: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
        def evaluar_filtro(nota):
            if nota < 6.0: return 'BAJO'
            elif nota < 7.6: return 'BÁSICO'
            elif nota < 9.1: return 'ALTO'
            else: return 'SUPERIOR'
        df['DESEMPEÑO_FILTRO'] = df[col_n].apply(evaluar_filtro)
        colores_vivos = {'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'}
        fig2 = px.pie(df, names='DESEMPEÑO_FILTRO', hole=0.4, color='DESEMPEÑO_FILTRO', color_discrete_map=colores_vivos)
        fig2.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color="#000", family="Arial Black"))
        fig2.update_layout(height=260, margin=dict(t=0, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config=config_espanol)

elif menu == "📈 Dashboard Estudiantil":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Radar Táctico Individual</h3>", unsafe_allow_html=True)
    lista_alumnos_dash = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
    alumno_analisis = st.selectbox("🎯 Seleccione Estudiante a Inspeccionar:", lista_alumnos_dash)
    
    if alumno_analisis:
        df_alum = df[df['Nombre_Completo'] == alumno_analisis]
        promedio_global = df_alum[col_n].mean()
        if promedio_global < 6.0: des_global = 'BAJO 🔴'
        elif promedio_global < 7.6: des_global = 'BÁSICO 🟡'
        elif promedio_global < 9.1: des_global = 'ALTO 🟢'
        else: des_global = 'SUPERIOR 🌟'
        
        novedades_count = 0
        df_hist_alum = pd.DataFrame()
        if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty and 'Nombre_Completo' in st.session_state.df_asistencia.columns:
            df_hist_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_analisis]
            novedades_count = len(df_hist_alum)
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio ({periodo_sel})</p><p class='metric-value'>{promedio_global:.1f}</p></div>", unsafe_allow_html=True)
        with col_m2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Nivel Actual</p><p class='metric-value'>{des_global}</p></div>", unsafe_allow_html=True)
        with col_m3: st.markdown(f"<div class='metric-card'><p class='metric-label'>Novedades / Faltas</p><p class='metric-value'>{novedades_count}</p></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns([1.2, 1])
        with col_r1:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>POLÍGONO DE DESEMPEÑO</p>", unsafe_allow_html=True)
            if not df_alum.empty:
                fig_radar = px.line_polar(df_alum, r=col_n, theta='Materia', line_close=True, range_r=[0,10], text=col_n)
                fig_radar.update_traces(fill='toself', fillcolor='rgba(212, 175, 55, 0.4)', line_color='#0d1b2a', line_width=3, mode='lines+markers+text', textfont=dict(color='#000000', size=13, family='Arial Black'), textposition='top center')
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color='black')), 
                        angularaxis=dict(type='category', tickfont=dict(color='black', size=13, family='Arial Black'))
                    ), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(l=60, r=60, t=30, b=30)
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={'displaylogo': False})
            else:
                st.info("📡 No hay datos suficientes para graficar el polígono.")
        with col_r2:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>HISTORIAL DISCIPLINARIO</p>", unsafe_allow_html=True)
            if novedades_count > 0: 
                st.dataframe(df_hist_alum[['FECHA', 'ESTADO', 'OBSERVACIONES']].sort_values(by='FECHA', ascending=False), use_container_width=True, hide_index=True)
            else: 
                st.info("✅ Sin reportes disciplinarios ni faltas.")
        
elif menu == "🚦 Semáforo Académico":
    st.markdown(f"<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Semáforo de Riesgo Académico - Grado {curso_sel} ({periodo_sel})</h3>", unsafe_allow_html=True)
    df_estudiantes = df.groupby(['Nombre_Completo', 'Grado'])[col_n].mean().reset_index()
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
    with col1: st.markdown(f"<div class='tarjeta-roja'><h4 style='margin:0; color:#cc0000; font-family:Arial Black;'>🔴 Riesgo Crítico (< 6.0)</h4><h1 style='margin:0; color:#cc0000; font-family:Arial Black;'>{len(criticos)}</h1></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='tarjeta-naranja'><h4 style='margin:0; color:#cc8800; font-family:Arial Black;'>🟡 Alerta (6.0 - 7.5)</h4><h1 style='margin:0; color:#cc8800; font-family:Arial Black;'>{len(alertas)}</h1></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='tarjeta-verde'><h4 style='margin:0; color:#00994c; font-family:Arial Black;'>🟢 Óptimo (>= 7.6)</h4><h1 style='margin:0; color:#00994c; font-family:Arial Black;'>{len(optimos)}</h1></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if not criticos.empty:
        st.error("🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO")
        st.dataframe(criticos[['Nombre_Completo', 'Grado', col_n]].rename(columns={col_n: 'PROMEDIO'}).style.format({'PROMEDIO': '{:.1f}'}), use_container_width=True, hide_index=True)

elif menu == "✍️ Digitar Notas":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)
    
    col_btn, col_espacio = st.columns([2, 8])
    
    # 1. Configuración visual del editor
    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True)
    }

    # 2. Mostramos el editor (Capturamos los cambios en tiempo real)
    # Usamos 'df' que ya está filtrado por el grado/materia que usted eligió
    notas_editadas = st.data_editor(df, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)

    with col_btn:
        if st.button("💾 GUARDAR EN EXCEL", type="primary", use_container_width=True):
            cambios = st.session_state.editor_notas.get('edited_rows', {})
            
            if cambios:
                with st.spinner("🚀 Transmitiendo datos a la Bóveda de Google Drive..."):
                    # 3. Aplicamos los cambios a la base maestra usando mapeo de índices reales
                    for fila_posicional, valores_nuevos in cambios.items():
                        # MAGIA TÁCTICA: Obtenemos el ID real de la fila en la base maestra (df_maestro)
                        idx_real = df.index[int(fila_posicional)]
                        
                        for columna, valor in valores_nuevos.items():
                            st.session_state.df_maestro.at[idx_real, columna] = valor
                    
                    # 4. Recalculamos promedios de las filas modificadas
                    st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)

                    # 5. TRADUCCIÓN PARA EXCEL: Ajustamos nombres para que coincidan con las columnas del Drive
                    df_para_drive = st.session_state.df_maestro.copy()
                    if 'Grado' in df_para_drive.columns: 
                        df_para_drive = df_para_drive.drop(columns=['Grado'])
                    
                    df_para_drive = df_para_drive.rename(columns={
                        'Nombre_Completo': 'NOMBRE_COMPLETO',
                        'Materia': 'ASIGNATURA',
                        'LOGRO': 'LOGROS'
                    })

                    try:
                        # 6. Envío final al satélite
                        conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_para_drive)
                        st.success("✅ ¡SATÉLITE SINCRONIZADO! Los cambios ya están en el Excel.")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas en Drive")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 FALLA DE CONEXIÓN: No se pudo escribir. ¿El Excel está compartido como EDITOR con la cuenta de servicio? Error: {e}")
            else:
                st.warning("⚠️ No has realizado ningún cambio en las notas todavía.")
                
elif menu == "📚 Logros":
    col_btn, col_espacio = st.columns([1.5, 8.5])
    with col_btn:
        if st.button("💾 GUARDAR", type="primary", use_container_width=True):
            st.session_state.df_logros = st.session_state.df_l_temp
            registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Actualizó Logros")
            try: conn.update(worksheet="DB_LOGROS", data=st.session_state.df_logros); st.success("✅ Logros subidos a Drive")
            except: st.warning("Guardado local.")
            st.rerun()
    st.session_state.df_l_temp = st.data_editor(df_l, use_container_width=True, num_rows="dynamic", height=300, key="editor_logros")

elif menu == "📝 Asistencias y Reportes":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Control de Asistencia y Observaciones</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✍️ Registrar Novedad", "🖨️ Generar Observador Oficial"])
    
    with tab1:
        with st.form("form_novedad"):
            st.markdown("<p style='font-weight:bold;'>Registrar Nueva Novedad:</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            lista_alumnos = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
            with col1: alum_sel = st.selectbox("👤 Estudiante:", lista_alumnos)
            with col2: fecha_sel = st.date_input("📅 Fecha:")
            with col3: estado_sel = st.selectbox("🚦 Estado / Tipo:", ["Falla", "Retardo", "Excusa", "Llamado de Atención", "Felicitación"])
            obs_sel = st.text_area("📝 Observaciones o Detalles:")
            submit_btn = st.form_submit_button("💾 GUARDAR REPORTE", type="primary")
            if submit_btn and alum_sel:
                grado_alum = df[df['Nombre_Completo'] == alum_sel]['Grado'].iloc[0] if not df[df['Nombre_Completo'] == alum_sel].empty else "N/A"
                nuevo_registro = pd.DataFrame([{'Nombre_Completo': alum_sel, 'GRADO': grado_alum, 'FECHA': fecha_sel.strftime("%Y-%m-%d"), 'ESTADO': estado_sel, 'OBSERVACIONES': obs_sel}])
                st.session_state.df_asistencia = pd.concat([st.session_state.df_asistencia, nuevo_registro], ignore_index=True)
                registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, f"📝 Reporte: {alum_sel}")
                try: conn.update(worksheet="DB_ASISTENCIA", data=st.session_state.df_asistencia); st.success(f"✅ Reporte guardado.")
                except: st.warning("Guardado localmente.")
        
        st.markdown("---")
        col_h1, col_h2 = st.columns([7, 3])
        with col_h1:
            st.markdown("<h4 style='color:#000000; font-family:Arial Black;'>Historial de Novedades</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                if st.button("↩️ DESHACER ÚLTIMO REPORTE", help="Elimina el último registro guardado por error"):
                    st.session_state.df_asistencia = st.session_state.df_asistencia.iloc[:-1] 
                    try: 
                        conn.update(worksheet="DB_ASISTENCIA", data=st.session_state.df_asistencia)
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "↩️ Revirtió último reporte")
                        st.rerun()
                    except: 
                        st.warning("No se pudo conectar con el satélite.")
                        
        if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty: 
            st.dataframe(st.session_state.df_asistencia.iloc[::-1], use_container_width=True, hide_index=True)
        else: 
            st.info("No hay registros disciplinarios almacenados.")

    with tab2:
        st.markdown("<p style='font-weight:bold;'>Seleccione un estudiante para imprimir su hoja de vida disciplinaria:</p>", unsafe_allow_html=True)
        alumno_obs = st.selectbox("👤 Buscar Estudiante:", sorted(df['Nombre_Completo'].dropna().unique()), key="sel_obs")
        
        if st.button("🖨️ PREPARAR OBSERVADOR", type="primary"):
            if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
                df_obs_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_obs]
                if not df_obs_alum.empty:
                    css_obs = """<style>body { font-family: Arial, sans-serif; background: white; color: black; } .b-print { padding: 30px; border: 2px solid #000; } .table-obs { width: 100%; border-collapse: collapse; margin-top: 15px; } .table-obs th, .table-obs td { border: 1px solid #000; padding: 8px; text-align: left; } .table-obs th { background-color: #f0f0f0; } .firmas-box { display: flex; justify-content: space-between; margin-top: 60px; } .firma-linea { border-top: 1px solid #000; width: 30%; text-align: center; font-weight: bold; font-size: 12px; padding-top: 5px; } @media print { .no-print { display: none !important; } } </style>"""
                    
                    html_observador = f"""<html><head><script>function imprimirObs() {{ window.print(); }}</script>{css_obs}</head><body>
                    <div class="no-print" style="text-align:right; margin-bottom:10px;"><button onclick="imprimirObs()" style="background:#0d1b2a; color:#d4af37; padding:10px; font-weight:bold; cursor:pointer;">🖨️ IMPRIMIR OBSERVADOR</button></div>
                    <div class="b-print">
                        <h2 style="text-align:center; margin:0;">ACADEMIA GLOBAL HORIZONTE</h2>
                        <h4 style="text-align:center; margin:5px 0;">OBSERVADOR DEL ALUMNO (HOJA DE VIDA)</h4>
                        <hr style="border-top:2px solid #000;">
                        <p><b>Estudiante:</b> {alumno_obs} &nbsp;&nbsp;&nbsp; <b>Grado:</b> {df_obs_alum['GRADO'].iloc[0] if 'GRADO' in df_obs_alum.columns else 'N/A'}</p>
                        <table class="table-obs">
                            <tr><th>Fecha</th><th>Tipo / Estado</th><th>Observación Detallada</th></tr>"""
                    
                    for _, row in df_obs_alum.iterrows():
                        html_observador += f"<tr><td>{row['FECHA']}</td><td><b>{row['ESTADO']}</b></td><td>{row['OBSERVACIONES']}</td></tr>"
                        
                    html_observador += """</table>
                        <div class="firmas-box">
                            <div class="firma-linea">Firma del Estudiante</div>
                            <div class="firma-linea">Firma del Acudiente</div>
                            <div class="firma-linea">Firma del Docente / Coordinador</div>
                        </div>
                    </div></body></html>"""
                    
                    components.html(html_observador, height=600, scrolling=True)
                else:
                    st.success(f"✅ El estudiante {alumno_obs} tiene una hoja de vida intachable. Cero reportes.")
            else:
                st.warning("No hay base de datos disciplinaria registrada aún.")
                
elif menu == "📜 Boletines":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>Central de Impresión VIP</h3>", unsafe_allow_html=True)
    modo_impresion = st.radio("Seleccione el modo de generación:", ["👤 Individual", "🖨️ Masiva (Todo el Grado)"], horizontal=True)
    css_vip = """<style>body { font-family: Arial, sans-serif; background: white; color: black; } .b-print { position: relative; padding: 30px; border: 3px solid #0d1b2a; border-radius: 12px; font-size: 13px; font-weight: bold; background: white; z-index: 1; margin-bottom: 25px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); overflow: hidden; } .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; width: 60%; z-index: -1; pointer-events: none; } .table-custom { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; z-index: 2; position: relative; } .table-custom th { background-color: #0d1b2a; color: #d4af37; border: 1px solid #000; padding: 10px; font-family: 'Arial Black'; } .table-custom td { border: 1px solid #000; padding: 8px; background-color: rgba(255, 255, 255, 0.85); text-align: center; } .header-table { width: 100%; border: none; margin-bottom: 15px; z-index: 2; position: relative; } .header-table td { border: none; } .firmas-container { display: flex; justify-content: space-around; margin-top: 60px; font-size: 14px; z-index: 2; position: relative; page-break-inside: avoid; } .firma-box { text-align: center; width: 40%; border-top: 2px solid #0d1b2a; padding-top: 5px; font-weight: bold; color: #0d1b2a; } @media print { @page { size: legal portrait; margin: 10mm; } body { background: white; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; } .no-print { display: none !important; } .b-print { border: none; box-shadow: none; padding: 0; } .salto-pagina { page-break-after: always; } } </style>"""    
    def nota_limpia(valor):
        try:
            n = float(valor)
            import pandas as pd
            return 0.0 if pd.isna(n) else n
        except:
            return 0.0

    if modo_impresion == "👤 Individual":
        alumno = st.selectbox("👤 Estudiante:", sorted(df['Nombre_Completo'].dropna().unique()))
        if alumno:
            import base64
            try:
                with open("logo.png", "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode()
                URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
            except:
                URL_LOGO_OFICIAL = ""

            res = df[df['Nombre_Completo'] == alumno]
            
            res = res.drop_duplicates(subset=['Materia'])
            res = res[res['PROMEDIO'] > 0.0]
            
            promedios = [nota_limpia(x) for x in res[col_n]]
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
                            <h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">INSTITUCION EDUCATIVA GÉNESIS JORSUG 2026</h2>
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
                    p1 = nota_limpia(row.get('P1', 0))
                    p2 = nota_limpia(row.get('P2', 0))
                    p3 = nota_limpia(row.get('P3', 0))
                    p4 = nota_limpia(row.get('P4', 0))
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
                        filtro = df_l[
                            (df_l.iloc[:, 0].astype(str).str.strip().str.upper() == nivel_alumno.upper()) & 
                            (df_l.iloc[:, 1].astype(str).str.strip().str.upper() == str(row['Materia']).strip().upper()) & 
                            (df_l.iloc[:, 2].astype(str).str.strip().str.upper() == desp.upper())
                        ]
                        if not filtro.empty:
                            logro_texto = str(filtro.iloc[0, 3])
                        else:
                            logro_texto = "Logro no encontrado en base de datos"
                    else:
                        logro_texto = "Base de logros vacía"
                except Exception as e:
                    logro_texto = row.get('LOGRO', 'Error al buscar logro')

                html_boletin += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
            
            html_boletin += """
                </table>
                <div class='firmas-container'>
                    <div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div>
                    <div class='firma-box'>Firma Director de Grupo</div>
                </div>
            </div></body></html>"""
            
            components.html(html_boletin, height=600, scrolling=True)
            
    else:
        estudiantes = sorted(df['Nombre_Completo'].dropna().unique())
        st.warning(f"⚠️ Se generarán {len(estudiantes)} boletines VIP para el grado {curso_sel}.")
        
        if st.button("🖨️ COMPILAR LOTE MASIVO VIP", type="primary"):
            import base64
            try:
                with open("logo.png", "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode()
                URL_LOGO_OFICIAL = f"data:image/png;base64,{b64_string}"
            except:
                URL_LOGO_OFICIAL = ""
                
            th = "<th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>FINAL</th>" if periodo_sel == "CONSOLIDADO FINAL" else f"<th>{periodo_sel}</th>"
            html_masivo = f"""<html><head><script>function imprimirLote() {{ window.print(); }}</script>{css_vip}</head><body><div class="no-print" style="position: sticky; top: 0; background: white; padding: 10px; z-index: 100; border-bottom: 2px solid #0d1b2a; text-align: right;"><button onclick="imprimirLote()" style="background:#0d1b2a; color:#d4af37; border:2px solid #d4af37; padding:10px 20px; cursor:pointer; border-radius:6px; font-weight:bold; font-family:'Arial Black';">🖨️ IMPRIMIR LOTE MASIVO</button></div>"""
            
            def nota_limpia(valor):
                try:
                    n = float(valor)
                    import pandas as pd
                    return 0.0 if pd.isna(n) else n
                except:
                    return 0.0

            for i, alum in enumerate(estudiantes):
                res = df[df['Nombre_Completo'] == alum]
                
                res = res.drop_duplicates(subset=['Materia'])
                res = res[res['PROMEDIO'] > 0.0]
                
                promedios = [nota_limpia(x) for x in res[col_n]]
                p_prom = sum(promedios) / len(promedios) if len(promedios) > 0 else 0.0
                salto = "salto-pagina" if i < len(estudiantes) - 1 else ""
                
                html_masivo += f"""<div class="b-print {salto}">
                <img src="{URL_LOGO_OFICIAL}" class="watermark">
                <table class="header-table">
                    <tr>
                        <td style="width:15%;"><img src="{URL_LOGO_OFICIAL}" width="90"></td>
                        <td style="text-align:center;">
                            <h2 style="margin:0; color:#0d1b2a; font-size:20px; font-family:'Arial Black';">INSTITUCION EDUCATIVA GÉNESIS JORSUG 2026</h2>
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
                    <span><b style="color:#0d1b2a;">ESTUDIANTE:</b> {alum}</span><span><b style="color:#0d1b2a;">GRADO:</b> {res['Grado'].iloc[0] if not res.empty else 'N/A'}</span>
                </div>
                <table class="table-custom">
                    <tr><th>MATERIA</th>{th}<th>DESEMPEÑO</th></tr>"""
                
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
                        p1 = nota_limpia(row.get('P1', 0))
                        p2 = nota_limpia(row.get('P2', 0))
                        p3 = nota_limpia(row.get('P3', 0))
                        p4 = nota_limpia(row.get('P4', 0))
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
                            filtro = df_l[
                                (df_l.iloc[:, 0].astype(str).str.strip().str.upper() == nivel_alumno.upper()) & 
                                (df_l.iloc[:, 1].astype(str).str.strip().str.upper() == str(row['Materia']).strip().upper()) & 
                                (df_l.iloc[:, 2].astype(str).str.strip().str.upper() == desp.upper())
                            ]
                            if not filtro.empty:
                                logro_texto = str(filtro.iloc[0, 3])
                            else:
                                logro_texto = "Logro no encontrado en base de datos"
                        else:
                            logro_texto = "Base de logros vacía"
                    except:
                        logro_texto = row.get('LOGRO', 'Error al buscar logro')
                        
                    html_masivo += f"<tr><td colspan='{col_span}' style='text-align:left; font-size:11px; font-style:italic; border-bottom:2px solid #000; background-color:#fafafa;'><b>LOGRO:</b> {logro_texto}</td></tr>"
                    
                html_masivo += """
                    </table>
                    <div class='firmas-container'>
                        <div class='firma-box'>Firma Rectoría<br><span style='font-size:10px; font-weight:normal;'>Sello Institucional</span></div>
                        <div class='firma-box'>Firma Director de Grupo</div>
                    </div>
                    </div>"""
                    
            html_masivo += "</body></html>"
            components.html(html_masivo, height=600, scrolling=True)
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

    with st.expander("📊 4. INTELIGENCIA Y REPORTES (EXCLUSIVO RECTORÍA)"):
        st.write("""
        * **Dashboard:** Visualice el 'Radar Táctico' para ver las fortalezas y debilidades de cada estudiante.
        * **SIMAT:** En el módulo de Backup, puede descargar el reporte listo para el Ministerio de Educación.
        * **Eficiencia:** Monitoree el medidor de eficiencia interna; si baja del 80%, el sistema emitirá una alerta de riesgo de reprobación masiva.
        """)
        
elif menu == "📸 Eventos Institucionales":
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📸 Memorias Institucionales</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", caption="Feria Científica")
    c2.image("https://images.unsplash.com/photo-1523580494112-071d1694335c?q=80&w=800", caption="Ceremonia de Grados")
    c3.image("https://images.unsplash.com/photo-1511632765486-a01980e01a18?q=80&w=800", caption="Comunidad Estudiantil")

# --- PIE DE PÁGINA LEGAL (Habeas Data) ---
st.markdown(f"""
    <div class='footer-legal'>
        Academia Global Horizonte - Sistema Génesis AGH © {datetime.now().year}<br>
        Protección de Datos Personales: En cumplimiento de la Ley 1581 de 2012, 
        el tratamiento de la información aquí registrada es de carácter estrictamente institucional y confidencial.
    </div>
""", unsafe_allow_html=True)
