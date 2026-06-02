import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------
# 📋 1. MATRIZ DE MANDO: ASIGNACIONES ACADÉMICAS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# ⚙️ 2. CONFIGURACIÓN DEL NÚCLEO Y MEMORIA VISUAL
# ---------------------------------------------------------
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

st.markdown("""
<style>
[data-testid="stToolbarActions"] { display: none !important; }
.viewerBadge_container { display: none !important; visibility: hidden !important; opacity: 0 !important; }
footer { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: visible; }
.stApp { background-color: #ffffff; }
.stApp::before {
    content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
    background-size: 350px; background-repeat: no-repeat; background-position: center;
    opacity: 0.15; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
}
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
[data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; font-weight: bold; }
div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
div[data-baseweb="select"] > div * { color: #000000 !important; }
.metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
.metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
.metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
.titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
.titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
.asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}
.footer-legal { font-size: 10px; color: #888888; text-align: center; margin-top: 50px; border-top: 1px solid #eeeeee; padding-top: 10px; font-family: 'Arial', sans-serif; }
</style>
""", unsafe_allow_html=True)

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

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

# ---------------------------------------------------------
# 🔐 3. ENLACE EXCLUSIVO AL NÚCLEO SQL SUPABASE
# ---------------------------------------------------------
conn_sql = st.connection("postgresql", type="sql")

if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        try: st.image("logo.png", width=250)
        except: pass 
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px; margin-top: -10px;"><h3 style="color:#000000; font-family:'Arial Black'; margin-top:0; font-size:18px;">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        
        u = st.text_input("👤 Usuario", placeholder="Ej: admin", label_visibility="collapsed")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 INGRESAR", use_container_width=True):
            with st.spinner("Validando en Bóveda Satelital..."):
                try:
                    try:
                        df_usuarios = conn_sql.query("SELECT * FROM data_usuarios;")
                    except Exception:
                        df_usuarios = pd.DataFrame()
                    
                    if df_usuarios is None or df_usuarios.empty:
                        df_usuarios = pd.DataFrame([{"USUARIO": "Admin", "PASSWORD": "Genesis2026_Admin*", "ESTADO": "Activo", "ROL": "Admin", "Nombre_Completo": "Administrador de Emergencia"}])

                    acceso = df_usuarios[(df_usuarios['USUARIO'] == u) & (df_usuarios['PASSWORD'] == p)]
                    
                    if not acceso.empty:
                        estado = str(acceso['ESTADO'].iloc[0]).strip().upper()
                        rol = str(acceso['ROL'].iloc[0]).strip().capitalize()
                        if estado == "ACTIVO":
                            st.session_state.logueado = True
                            st.session_state.rol = rol
                            st.session_state.usuario_actual = u
                            st.session_state.nombre_completo_usuario = str(acceso['Nombre_Completo'].iloc[0]).strip() if 'Nombre_Completo' in df_usuarios.columns else u
                            registrar_bitacora(u, rol, "✅ Ingreso Exitoso")
                            st.rerun()
                        else: st.error("🚨 Acceso Denegado: Cuenta inactiva.")
                    else: st.error("🚨 Acceso Denegado: Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"🚨 Error de conexión. {e}")
    st.stop() 

# ---------------------------------------------------------
# Satélite: Descarga Segura desde SQL
# ---------------------------------------------------------
if 'df_maestro' not in st.session_state or st.session_state.df_maestro is None or st.session_state.df_maestro.empty:
    with st.spinner("📡 Descargando notas de la base satelital..."):
        try:
            df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;", ttl=600)
            df_notas = df_notas.rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo', 'ASIGNATURA': 'Materia', 'LOGROS': 'LOGRO'})
            df_estud = conn_sql.query("SELECT * FROM data_estudiantes;")
            df_grados = df_estud[['Nombre_Completo', 'Grado']].drop_duplicates() if not df_estud.empty else pd.DataFrame(columns=['Nombre_Completo', 'Grado'])
            st.session_state.df_maestro = pd.merge(df_notas, df_grados, on='Nombre_Completo', how='left')
        except Exception:
            st.session_state.df_maestro = pd.DataFrame(columns=["Nombre_Completo", "Materia", "P1", "P2", "P3", "P4", "LOGRO", "Grado"])

if 'df_logros' not in st.session_state or st.session_state.df_logros is None or st.session_state.df_logros.empty:
    try: st.session_state.df_logros = conn_sql.query("SELECT * FROM db_logros;")
    except Exception:
        st.session_state.df_logros = pd.DataFrame(columns=["NIVEL", "MATERIA", "DESEMPEÑO", "LOGRO_TEXTO"])
            
if 'df_asistencia' not in st.session_state or st.session_state.df_asistencia is None or st.session_state.df_asistencia.empty:
    try: st.session_state.df_asistencia = conn_sql.query("SELECT * FROM db_asistencia;")
    except Exception:
        st.session_state.df_asistencia = pd.DataFrame(columns=['Nombre_Completo', 'GRADO', 'FECHA', 'ESTADO', 'OBSERVACIONES'])

df_m = st.session_state.df_maestro
if df_m is not None and not df_m.empty:
    df_m['Grado'] = df_m['Grado'].fillna("Sin Grado") 
    for col_nota in ['P1', 'P2', 'P3', 'P4']:
        if col_nota in df_m.columns:
            df_m[col_nota] = pd.to_numeric(df_m[col_nota], errors='coerce').fillna(0.0).round(1)
    if all(c in df_m.columns for c in ['P1', 'P2', 'P3', 'P4']):
        df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)

# ---------------------------------------------------------
# 🧭 5. PANEL LATERAL Y FILTROS SEGURIZADOS
# ---------------------------------------------------------
with st.sidebar:
    try: st.image("logo.png", width=120)
    except: pass
    nombre_mostrar = st.session_state.nombre_completo_usuario if st.session_state.nombre_completo_usuario else st.session_state.usuario_actual.upper()
    st.markdown(f"<h3 style='color:white; margin-top:0;'>👤 {nombre_mostrar}</h3><p style='color:#d4af37; font-weight:bold; margin-top:-15px;'>Rango: {st.session_state.rol}</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:rgba(212, 175, 55, 0.1); border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center; margin-bottom:15px;'><p style='color:#d4af37; font-size:12px; margin:0;'>🕒 HORA DE INICIO</p><p style='color:white; font-size:18px; font-weight:bold; margin:0;'>{st.session_state.hora_inicio}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    opciones_menu = ["🏠 Inicio", "🕒 Horarios y Asignaciones", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": 
        opciones_menu.insert(1, "🛡️ Bitácora y Backup")
        opciones_menu.insert(1, "👑 Centro de Mando")
    menu = st.radio("SECCIONES:", opciones_menu)
    st.markdown("---")

    cursos = ["TODOS"]
    if st.session_state.df_maestro is not None and 'Grado' in st.session_state.df_maestro.columns:
        cursos += sorted(st.session_state.df_maestro['Grado'].dropna().unique().astype(str).tolist())
    curso_sel = st.selectbox("Grado:", cursos)
    
    materias_permitidas = ["TODAS"]
    if st.session_state.df_maestro is not None and 'Materia' in st.session_state.df_maestro.columns:
        materias_permitidas += sorted(st.session_state.df_maestro['Materia'].dropna().unique().astype(str).tolist())
    materia_sel = st.selectbox("Materia:", materias_permitidas)
    periodo_sel = st.selectbox("Periodo:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    
    if st.button("🔴 CERRAR SESIÓN"): 
        st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = False, "", ""
        st.rerun()

df_temp = df_m.copy() if df_m is not None else pd.DataFrame()
if curso_sel != "TODOS": df_temp = df_temp[df_temp['Grado'].astype(str) == str(curso_sel)]
if materia_sel != "TODAS" and 'Materia' in df_temp.columns: df_temp = df_temp[df_temp['Materia'].astype(str) == str(materia_sel)]
df_filtrado = df_temp.copy()

st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h1></div>", unsafe_allow_html=True)

# Enrutamiento de módulos
try:
    if menu == "🏠 Inicio": import modulos.m0_inicio as m0; m0.renderizar()
    elif menu == "👑 Centro de Mando": import modulos.m_admin as m_admin; m_admin.render_mando(df_filtrado, periodo_sel, conn_sql)
    elif menu == "🛡️ Bitácora y Backup": import modulos.m_admin as m_admin; m_admin.render_backup(conn_sql)
    elif menu == "🕒 Horarios y Asignaciones": import modulos.m1_horarios as m1; m1.renderizar(conn_sql)
    elif menu == "📊 Inteligencia Académica": import modulos.m2_inteligencia as m2; m2.renderizar(df_filtrado, periodo_sel)
    elif menu == "📈 Dashboard Estudiantil": import modulos.m3_dashboard as m3; m3.renderizar(df_filtrado, periodo_sel, conn_sql)
    elif menu == "🚦 Semáforo Académico": import modulos.m4_semaforo as m4; m4.renderizar(df_filtrado, curso_sel, periodo_sel)
    elif menu == "✍️ Digitar Notas": import modulos.m5_notas as m5; m5.renderizar(df_filtrado, periodo_sel, conn_sql)
    elif menu == "📚 Logros": import modulos.m6_logros as m6; m6.renderizar(conn_sql)
    elif menu == "📝 Asistencias y Reportes": import modulos.m7_asistencia as m7; m7.renderizar(df_filtrado, conn_sql)
    elif menu == "📜 Boletines": import modulos.m8_boletines as m8; m8.renderizar(df_filtrado, curso_sel, periodo_sel)
except Exception as e:
    st.info(f"🛠️ Sincronizando módulos... {e}")

st.markdown(f"<div class='footer-legal'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026 © {datetime.now().year}</div>", unsafe_allow_html=True)
