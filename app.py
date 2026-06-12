import streamlit as st
import pandas as pd
import streamlit.components.v1 as components  
import base64
import os
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

# 🔒 CREDENCIALES MAESTRAS DE RESCATE (Bypass total de Base de Datos)
USUARIOS_RESCATE = {
    "Admin": {"PASSWORD": "Genesis2026_Admin*", "ROL": "Admin", "Nombre_Completo": "Administrador de Emergencia"},
    "comandante": {"PASSWORD": "Agh2026_Master*", "ROL": "Admin", "Nombre_Completo": "Comandante David AGH"}
}

# ---------------------------------------------------------
# ⚙️ 2. CONFIGURACIÓN DEL NÚCLEO Y CSS LIMPIO
# ---------------------------------------------------------
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* Limpieza de marcas de Streamlit */
[data-testid="stToolbarActions"] { display: none !important; }
.viewerBadge_container { display: none !important; visibility: hidden !important; opacity: 0 !important; }
footer { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: visible; }

/* Fondo de la App */
.stApp { background-color: #ffffff; }
.stApp::before {
    content: ""; background-image: url('https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png');
    background-size: 350px; background-repeat: no-repeat; background-position: center;
    opacity: 0.15; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
}
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }

/* Panel Lateral */
[data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; font-weight: bold; }
[data-testid="stSidebar"] .stButton > button { background-color: #990000 !important; border: 2px solid #ff4d4d !important; border-radius: 8px !important; padding: 10px !important; transition: all 0.3s ease !important; }
[data-testid="stSidebar"] .stButton > button * { color: #ffffff !important; font-weight: 900 !important; }
[data-testid="stSidebar"] .stButton > button:hover { background-color: #ff3333 !important; border-color: #ffffff !important; transform: scale(1.02); }

/* Estilos de Elementos Internos */
div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
div[data-baseweb="select"] > div * { color: #000000 !important; }
.metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
.metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
.metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
.titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
.titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🏛️ ARQUITECTURA DE CONTENEDORES (LA MAGIA VISUAL)
# =====================================================================
main_container = st.container()
footer_container = st.container()

with footer_container:
    st.markdown(f"""
        <div style="background-color:#0d1b2a; padding:15px; border-radius:10px; border:2px solid #d4af37; border-bottom:6px solid #d4af37; text-align:center; margin-top: 40px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); position: relative; z-index: 2;">
            <h4 style="color:#d4af37; margin:0; font-family:'Arial Black', sans-serif; font-size:13px;">PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026 © {datetime.now().year}</h4>
            <p style="color:#ffffff; margin:3px 0 0 0; font-size:11px; font-weight:bold;">SISTEMA OPERATIVO PROTEGIDO | Modo de Contingencia Activo</p>
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# 🚀 TODA LA LÓGICA DE LA APP OCURRE DENTRO DEL CONTENEDOR PRINCIPAL
# =====================================================================
with main_container:

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

    @st.cache_resource
    def get_db_connection():
        try:
            return st.connection("postgresql", type="sql")
        except Exception:
            return None

    conn_sql = get_db_connection()

    @st.cache_data(ttl=600, show_spinner=False)
    def get_maestro_data():
        try:
            if conn_sql is None: raise Exception("No hay conexión activa")
            df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
            df_notas = df_notas.rename(columns={'NOMBRE_COMPLETO': 'Nombre_Completo', 'ASIGNATURA': 'Materia', 'LOGROS': 'LOGRO'})
            df_estud = conn_sql.query("SELECT * FROM data_estudiantes;")
            df_grados = df_estud[['Nombre_Completo', 'Grado']].drop_duplicates() if not df_estud.empty else pd.DataFrame(columns=['Nombre_Completo', 'Grado'])
            df_m = pd.merge(df_notas, df_grados, on='Nombre_Completo', how='left')
            df_m['Grado'] = df_m['Grado'].fillna("Sin Grado") 
            for col_nota in ['P1', 'P2', 'P3', 'P4']:
                if col_nota in df_m.columns:
                    df_m[col_nota] = pd.to_numeric(df_m[col_nota], errors='coerce').fillna(0.0).round(1)
            if all(c in df_m.columns for c in ['P1', 'P2', 'P3', 'P4']):
                df_m['PROMEDIO'] = df_m[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
            return df_m
        except Exception:
            # 🚨 ESCUELA DE CONTINGENCIA: Retorna estructura limpia con filas piloto para evitar caídas
            return pd.DataFrame([
                {"Nombre_Completo": "Carlos Alberto Mendoza", "Materia": "Matemáticas", "P1": 4.5, "P2": 4.0, "P3": 0.0, "P4": 0.0, "LOGRO": "Excelente desempeño", "Grado": "11°", "PROMEDIO": 2.1},
                {"Nombre_Completo": "María Camila Restrepo", "Materia": "Lenguaje", "P1": 3.8, "P2": 4.2, "P3": 0.0, "P4": 0.0, "LOGRO": "Buen manejo temático", "Grado": "10°", "PROMEDIO": 2.0}
            ])

    @st.cache_data(ttl=600, show_spinner=False)
    def get_aux_data(table_name):
        try: 
            if conn_sql is None: raise Exception("No hay conexión activa")
            return conn_sql.query(f"SELECT * FROM {table_name};")
        except Exception: 
            return pd.DataFrame()

    # ---------------------------------------------------------
    # 🔐 4. SISTEMA DE ACCESO ULTRA-BLINDADO (CON CONTINGENCIA LOCAL)
    # ---------------------------------------------------------
    if not st.session_state.logueado:
        st.markdown("<br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
        with c2:
            try: st.image("logo.png", width=250)
            except: pass 
            st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #990000; border: 2px solid #000; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 10px; margin-top: -10px;"><h3 style="color:#990000; font-family:'Arial Black'; margin-top:0; font-size:18px;">MODO RESCATE ACTIVO</h3></div>""", unsafe_allow_html=True)
            
            u = st.text_input("👤 Usuario", placeholder="Ej: admin", label_visibility="collapsed")
            p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 INGRESAR", use_container_width=True):
                # 🛠️ CAPA ALFA: Verificación inmediata por diccionario local estático
                if u in USUARIOS_RESCATE and p == USUARIOS_RESCATE[u]["PASSWORD"]:
                    st.session_state.logueado = True
                    st.session_state.rol = USUARIOS_RESCATE[u]["ROL"]
                    st.session_state.usuario_actual = u
                    st.session_state.nombre_completo_usuario = USUARIOS_RESCATE[u]["Nombre_Completo"]
                    registrar_bitacora(u, USUARIOS_RESCATE[u]["ROL"], "⚠️ Ingreso de Rescate Exitoso")
                    st.rerun()
                else:
                    # Si no es credencial de rescate, intenta buscar en la base de datos caída
                    with st.spinner("Validando en Bóveda SQL..."):
                        try:
                            df_usuarios = get_aux_data("data_usuarios")
                            if df_usuarios.empty:
                                st.error("🚨 Servidor desconectado. Use las credenciales maestras de rescate.")
                            else:
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
                        except Exception:
                            st.error("🚨 Error de infraestructura SQL. Use las claves maestras cableadas.")
        st.info("💡 Tip de emergencia: Ingrese con usuario 'comandante' y la clave de rescate designada.")
        st.stop() 

    # Carga a Memoria Local Protegida
    if 'df_maestro' not in st.session_state or st.session_state.df_maestro is None:
        with st.spinner("⚡ Activando Acelerador SQL en Contingencia..."):
            st.session_state.df_maestro = get_maestro_data().copy()
            st.session_state.df_logros = get_aux_data("db_logros").copy()
            st.session_state.df_asistencia = get_aux_data("db_asistencia").copy()

    df_m = st.session_state.df_maestro

    # ---------------------------------------------------------
    # 🧭 5. PANEL LATERAL
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
        if st.session_state.rol == "Docente":
            if "📜 Boletines" in opciones_menu: opciones_menu.remove("📜 Boletines")
            
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
        col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
        
        if st.button("🔴 CERRAR SESIÓN"): 
            st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = False, "", ""
            st.cache_data.clear()
            st.rerun()

    # Filtro Dinámico Rápido
    df_filtrado = df_m
    if df_filtrado is not None and not df_filtrado.empty:
        if str(curso_sel) != "TODOS":
            df_filtrado = df_filtrado[df_filtrado['Grado'].astype(str) == str(curso_sel)]
        if str(materia_sel) != "TODAS" and 'Materia' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Materia'].astype(str) == str(materia_sel)]
    else:
        df_filtrado = pd.DataFrame()

    st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026</h1></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔀 6. ENRUTAMIENTO CONTROLADO
    # ---------------------------------------------------------
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
        elif menu == "📜 Boletines": import modulos.m8_boletines as m8; m8.renderizar(df_m, curso_sel, periodo_sel)
        elif menu == "📖 Manual de Usuario": import modulos.m9_manual as m9; m9.renderizar()
        elif menu == "📸 Eventos Institucionales": import modulos.m10_eventos as m10; m10.renderizar()

    except Exception as e:
        st.error(f"🛠️ Sincronizando módulos... Detalle técnico: {e}")
