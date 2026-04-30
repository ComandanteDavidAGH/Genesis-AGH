import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH", layout="wide", page_icon="🎓")

# Conexión Satelital
conn = st.connection("gsheets", type=GSheetsConnection)

# Inicialización de Estados
if 'logueado' not in st.session_state: st.session_state.logueado = False
if 'rol' not in st.session_state: st.session_state.rol = ""
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'nombre_completo_usuario' not in st.session_state: st.session_state.nombre_completo_usuario = ""
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now().strftime("%H:%M:%S")

# --- 2. CSS DE ALTO IMPACTO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; }
    [data-testid="stSidebar"] * { color: white !important; }
    .titulo-Agh { color: #000; font-family: 'Arial Black'; text-align: center; border-bottom: 3px solid #d4af37; }
    .asistente-box { background: #f0f2f6; border-left: 6px solid #d4af37; padding: 10px; font-weight: bold; color: #000; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if not st.session_state.logueado:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h2 style='text-align:center;'>🔐 ACCESO</h2>", unsafe_allow_html=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            df_u = conn.read(worksheet='DATA_USUARIOS')
            acc = df_u[(df_u['USUARIO'].astype(str) == u) & (df_u['PASSWORD'].astype(str) == p)]
            if not acc.empty:
                st.session_state.logueado = True
                st.session_state.rol = str(acc['ROL'].iloc[0])
                st.session_state.nombre_completo_usuario = str(acc['NOMBRE_COMPLETO'].iloc[0])
                st.session_state.usuario_actual = u
                st.rerun()
            else: st.error("Error de credenciales")
    st.stop()

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=600)
def cargar_todo():
    df_n = conn.read(worksheet='NOTAS_CONSOLIDADAS')
    df_e = conn.read(worksheet='DATA_ESTUDIANTES')
    df_l = conn.read(worksheet='DB_LOGROS')
    df_a = conn.read(worksheet='DB_ASISTENCIA')
    df_m = pd.merge(df_n, df_e[['ID_Estudiante', 'Grado']], left_on='ID_Est', right_on='ID_Estudiante', how='left')
    return df_m.fillna(0), df_l.fillna(""), df_a.fillna("")

df_maestro, df_logros, df_asistencia = cargar_todo()

# --- 5. PANEL LATERAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.nombre_completo_usuario}")
    st.markdown(f"""<div style='border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center;'>
            <p style='color:#d4af37; font-size:12px; margin:0;'>🕒 INICIO DE SESIÓN</p>
            <p style='font-size:18px; font-weight:bold;'>{st.session_state.hora_inicio}</p>
        </div>""", unsafe_allow_html=True)
    menu = st.radio("MENÚ:", ["🏠 Inicio", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias", "🚦 Semáforo", "📜 Boletines"])
    curso_sel = st.selectbox("Grado:", ["TODOS"] + sorted(df_maestro['Grado'].unique().tolist()))
    periodo_sel = st.selectbox("Periodo:", ["P1", "P2", "P3", "P4"])
    if st.button("Cerrar Sesión"):
        st.session_state.logueado = False
        st.rerun()

st.markdown(f"<h1 class='titulo-Agh'>ACADEMIA GLOBAL HORIZONTE</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='asistente-box'>Módulo: {menu} | {curso_sel}</div>", unsafe_allow_html=True)

df_f = df_maestro[df_maestro['Grado'] == curso_sel] if curso_sel != "TODOS" else df_maestro

# --- 6. MÓDULOS ---
if menu == "🏠 Inicio":
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1000", use_container_width=True)

elif menu == "✍️ Digitar Notas":
    df_ed = st.data_editor(df_f, use_container_width=True)
    if st.button("💾 GUARDAR EN DRIVE"):
        conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_ed.drop(columns=['Grado', 'ID_Estudiante']))
        st.success("¡Notas actualizadas!")

elif menu == "📚 Logros":
    st.dataframe(df_logros, use_container_width=True)

elif menu == "📝 Asistencias":
    st.dataframe(df_asistencia, use_container_width=True)

elif menu == "🚦 Semáforo":
    nota_min = 6.0
    riesgo = df_f[df_f[periodo_sel] < nota_min]
    st.warning(f"Estudiantes en riesgo en {periodo_sel}")
    st.table(riesgo[['NOMBRE_COMPLETO', 'ASIGNATURA', periodo_sel]])

elif menu == "📜 Boletines":
    est = st.selectbox("Seleccione Alumno:", df_f['NOMBRE_COMPLETO'].unique())
    if st.button("Generar"):
        datos = df_f[df_f['NOMBRE_COMPLETO'] == est]
        html = f"<div style='border:2px solid #000; padding:20px;'><h2>Boletín: {est}</h2><table border=1 width='100%'>"
        for _, r in datos.iterrows():
            html += f"<tr><td>{r['ASIGNATURA']}</td><td>{r[periodo_sel]}</td></tr>"
        html += "</table></div>"
        components.html(html, height=400)
