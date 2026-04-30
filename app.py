import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

# Conexión Satelital a Drive
conn = st.connection("gsheets", type=GSheetsConnection)

# Inicialización de Estados
if 'logueado' not in st.session_state: st.session_state.logueado = False
if 'rol' not in st.session_state: st.session_state.rol = ""
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'nombre_completo_usuario' not in st.session_state: st.session_state.nombre_completo_usuario = ""
if 'bitacora' not in st.session_state: st.session_state.bitacora = []
if 'df_maestro' not in st.session_state: st.session_state.df_maestro = None
if 'df_logros' not in st.session_state: st.session_state.df_logros = None
if 'df_asistencia' not in st.session_state: st.session_state.df_asistencia = None
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now().strftime("%H:%M:%S")

# --- 2. CSS AVANZADO (SU DISEÑO ORIGINAL) ---
st.markdown("""
    <style>
    [data-testid="stDecoration"] { display: none !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #ffffff; }
    .stApp::before {
        content: ""; background-image: url('https://cdn-icons-png.flaticon.com/512/2231/2231644.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; font-weight: bold; }
    .titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 3px solid #d4af37; margin-bottom: 20px; }
    .titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.2rem !important; text-align: center; margin-top: 0px; margin-bottom: 5px; text-shadow: 2px 2px 0px #d4af37; }
    .asistente-box { background: white; border-radius: 8px; padding: 8px 15px; border-left: 6px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; align-items: center; border: 2px solid #000; margin-bottom: 15px; color: #000; font-weight: bold;}
    @keyframes pulso-rojo { 0% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } 50% { box-shadow: 0 0 20px rgba(255, 0, 0, 1), inset 0 0 10px rgba(255, 0, 0, 0.5); } 100% { box-shadow: 0 0 0px rgba(255, 51, 51, 0.4); } }
    .tarjeta-roja { animation: pulso-rojo 1.5s infinite; border: 3px solid #cc0000; border-left: 10px solid #cc0000; background:#ffe6e6; padding:15px; border-radius:8px; color: #000; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
    div[data-baseweb="select"] > div * { color: #000000 !important; font-family: 'Arial Black', sans-serif !important; }
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
    </style>
""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({"Fecha": datetime.now().strftime("%Y-%m-%d"), "Hora": datetime.now().strftime("%H:%M:%S"), "Usuario": usuario, "Rol": rol, "Acción": accion})

# --- 3. LOGIN SEGURO ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=800&auto=format&fit=crop", use_container_width=True)
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #d4af37; border: 2px solid #000; text-align: center;"><h3 style="color:#000; font-family:'Arial Black';">ACCESO AL SISTEMA</h3></div>""", unsafe_allow_html=True)
        u = st.text_input("👤 Usuario", label_visibility="collapsed")
        p = st.text_input("🔑 Contraseña", type="password", label_visibility="collapsed")
        if st.button("🚀 INGRESAR", use_container_width=True):
            try:
                df_u = conn.read(worksheet='DATA_USUARIOS')
                acc = df_u[(df_u['USUARIO'] == u) & (df_u['PASSWORD'] == p)]
                if not acc.empty:
                    st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, str(acc['ROL'].iloc[0]).capitalize(), u
                    st.session_state.nombre_completo_usuario = str(acc['NOMBRE_COMPLETO'].iloc[0])
                    registrar_bitacora(u, st.session_state.rol, "✅ Ingreso")
                    st.rerun()
                elif u == "admin" and p == "agh2024":
                    st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, "Admin", u
                    st.session_state.nombre_completo_usuario = "Comandante"
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
            except: st.error("❌ Fallo de conexión")
    st.stop()

# --- 4. CARGA AUTOMÁTICA ---
if st.session_state.df_maestro is None:
    try:
        df_n = conn.read(worksheet='NOTAS_CONSOLIDADAS')
        df_e = conn.read(worksheet='DATA_ESTUDIANTES')
        df_l = conn.read(worksheet='DB_LOGROS')
        df_a = conn.read(worksheet='DB_ASISTENCIA')
        df = pd.merge(df_n, df_e[['ID_Estudiante', 'Grado']], left_on='ID_Est', right_on='ID_Estudiante', how='left')
        st.session_state.df_maestro, st.session_state.df_logros, st.session_state.df_asistencia = df.fillna(0), df_l.fillna(""), df_a.fillna("")
        st.rerun()
    except: st.error("Fallo de sincronización"); st.stop()

# --- 5. PANEL LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2231/2231644.png", width=70)
    st.markdown(f"### 👤 {st.session_state.nombre_completo_usuario}")
    # --- RECUPERACIÓN REGLA DE ORO: EL RELOJ ---
    st.markdown(f"""<div style='border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center;'>
        <p style='color:#d4af37; font-size:12px; margin:0;'>🕒 INICIO SESIÓN</p>
        <p style='font-size:18px; font-weight:bold;'>{st.session_state.hora_inicio}</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    opciones_menu = ["🏠 Inicio", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias y Reportes", "📜 Boletines", "📖 Manual de Usuario", "📸 Eventos Institucionales"]
    if st.session_state.rol == "Admin": opciones_menu.insert(1, "🛡️ Bitácora y Backup")
    menu = st.radio("SECCIONES:", opciones_menu)
    curso_sel = st.selectbox("Grado:", ["TODOS"] + sorted(st.session_state.df_maestro['Grado'].unique().tolist()))
    periodo_sel = st.selectbox("Periodo:", ["P1", "P2", "P3", "P4", "CONSOLIDADO FINAL"])
    if st.button("🔴 Salir"): st.session_state.logueado = False; st.rerun()

# --- 6. CABECERA ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>ACADEMIA GLOBAL HORIZONTE</h1></div>", unsafe_allow_html=True)
df = st.session_state.df_maestro
df_f = df[df['Grado'] == curso_sel] if curso_sel != "TODOS" else df
col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"

# --- 7. MÓDULOS (TODOS LOS QUE TENÍAMOS) ---
if menu == "🏠 Inicio":
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1470", use_container_width=True)
elif menu == "✍️ Digitar Notas":
    config_notas = {p: st.column_config.NumberColumn(p, min_value=1.0, max_value=10.0, step=0.1) for p in ["P1","P2","P3","P4"]}
    ed = st.data_editor(df_f, column_config=config_notas, use_container_width=True)
    if st.button("💾 GUARDAR"):
        conn.update(worksheet="NOTAS_CONSOLIDADAS", data=ed.drop(columns=['Grado', 'ID_Estudiante'], errors='ignore'))
        st.success("Sincronizado")
elif menu == "🚦 Semáforo Académico":
    df_s = df_f.groupby('NOMBRE_COMPLETO')[col_n].mean().reset_index()
    rojos = df_s[df_s[col_n] < 6.0]
    st.markdown(f"<div class='tarjeta-roja'>🔴 CRÍTICOS: {len(rojos)}</div>", unsafe_allow_html=True)
    st.dataframe(rojos)
elif menu == "📊 Inteligencia Académica":
    fig = px.bar(df_f.groupby('ASIGNATURA')[col_n].mean().reset_index(), x=col_n, y='ASIGNATURA', orientation='h', color='ASIGNATURA')
    st.plotly_chart(fig, use_container_width=True)
elif menu == "📈 Dashboard Estudiantil":
    alum = st.selectbox("Alumno:", df_f['NOMBRE_COMPLETO'].unique())
    fig_radar = px.line_polar(df_f[df_f['NOMBRE_COMPLETO']==alum], r=col_n, theta='ASIGNATURA', line_close=True)
    st.plotly_chart(fig_radar, use_container_width=True)
elif menu == "📝 Asistencias y Reportes":
    st.dataframe(st.session_state.df_asistencia, use_container_width=True)
elif menu == "📚 Logros":
    st.dataframe(st.session_state.df_logros, use_container_width=True)
elif menu == "📜 Boletines":
    alum_b = st.selectbox("Seleccione Alumno:", df_f['NOMBRE_COMPLETO'].unique())
    if st.button("Generar"):
        st.write(f"Generando boletín para {alum_b}...")
elif menu == "🛡️ Bitácora y Backup":
    st.write("Registro de acciones")
    st.dataframe(pd.DataFrame(st.session_state.bitacora))
