import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

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

.metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
.metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
.metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
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
        except Exception as e: pass 
          
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
                    st.error("🚨 Error de conexión con la base de datos satelital.")
    st.stop() 

# --- 4. PANEL LATERAL ---
with st.sidebar:
    try: st.image("logo.png", width=120)
    except: pass
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
        if "📜 Boletines" in opciones_menu:
            opciones_menu.remove("📜 Boletines")
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
                materias_permitidas = ["TODAS"] + MATERIAS_PRIMARIA
            else:
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
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h1></div>", unsafe_allow_html=True)

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
    

# =========================================================================
# 🔀 ENRUTADOR MODULAR (AQUÍ SE DEFINE QUÉ MOSTRAR SEGÚN EL MENÚ)
# =========================================================================
if menu == "🏠 Inicio":
    st.info("Módulo de inicio en línea.")
    
elif menu == "👑 Centro de Mando":
    st.info("Centro de Mando en línea.")
    
elif menu == "🛡️ Bitácora y Backup":
    st.info("Bitácora en línea.")

elif menu == "🕒 Horarios y Asignaciones":
    st.info("Horarios en línea.")

elif menu == "📊 Inteligencia Académica":
    st.info("Inteligencia en línea.")

elif menu == "📈 Dashboard Estudiantil":
    st.info("Dashboard en línea.")
        
elif menu == "🚦 Semáforo Académico":
    st.info("Semáforo en línea.")

elif menu == "✍️ Digitar Notas":
    st.info("Editor de notas en línea.")
                
elif menu == "📚 Logros":
    st.info("Logros en línea.")
 
elif menu == "📝 Asistencias y Reportes":
    st.info("Asistencias en línea.")
                
elif menu == "📜 Boletines":
    # ⚠️ LLAMADA EXCLUSIVA AL MÓDULO EXTERNO DE FORMA CORRECTA Y SEGURA
    import modulos.m8_boletines as m8
    m8.renderizar(df, curso_sel, periodo_sel)

elif menu == "📖 Manual de Usuario":
    st.info("Manual en línea.")

elif menu == "📸 Eventos Institucionales":
    st.info("Eventos en línea.")

# --- PIE DE PÁGINA ---
st.markdown(f"""
    <div class='footer-legal'>
        PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026 - Sistema Génesis AGH © {datetime.now().year}<br>
        Protección de Datos Personales: En cumplimiento de la Ley 1581 de 2012, el tratamiento de la información aquí registrada es de carácter estrictamente institucional y confidencial.
    </div>
""", unsafe_allow_html=True)
