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

# --- 2. CSS AVANZADO (ALTO CONTRASTE Y BLINDAJE) ---
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
    
    /* Estilos de Tablas y Desplegables */
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #d4af37 !important; }
    div[data-baseweb="select"] > div * { color: #000000 !important; font-family: 'Arial Black', sans-serif !important; }
    
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 8px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 4px 4px 0px #0d1b2a; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0d1b2a; margin: 0; font-family: 'Arial Black';}
    .metric-label { font-size: 14px; font-weight: bold; color: #000000; margin: 0; text-transform: uppercase;}
    
    /* Semaforo */
    .tarjeta-roja { border: 3px solid #cc0000; border-left: 10px solid #cc0000; background:#ffe6e6; padding:15px; border-radius:8px; color: #000; }
    .tarjeta-naranja { border: 3px solid #cc8800; border-left: 10px solid #cc8800; background:#fff4e6; padding:15px; border-radius:8px; color: #000; }
    .tarjeta-verde { border: 3px solid #00994c; border-left: 10px solid #00994c; background:#e6ffe6; padding:15px; border-radius:8px; color: #000; }
    </style>
""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

# --- 3. LOGIN SEGURO ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.2, 1.5])
    with c2:
        st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=800&auto=format&fit=crop", use_container_width=True)
        u = st.text_input("👤 Usuario", placeholder="Ej: admin")
        p = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••")
        if st.button("🚀 INGRESAR", use_container_width=True):
            try:
                df_usuarios = conn.read(worksheet='DATA_USUARIOS')
                acceso = df_usuarios[(df_usuarios['USUARIO'].astype(str) == u) & (df_usuarios['PASSWORD'].astype(str) == p)]
                if not acceso.empty:
                    estado = str(acceso['ESTADO'].iloc[0]).strip().upper()
                    if estado == "ACTIVO":
                        st.session_state.logueado = True
                        st.session_state.rol = str(acceso['ROL'].iloc[0]).strip()
                        st.session_state.usuario_actual = u
                        st.session_state.nombre_completo_usuario = str(acceso['NOMBRE_COMPLETO'].iloc[0]).strip()
                        registrar_bitacora(u, st.session_state.rol, "✅ Ingreso Exitoso")
                        st.rerun()
                    else: st.error("❌ Usuario Inactivo.")
                else: st.error("❌ Credenciales incorrectas.")
            except: st.error("❌ Error de enlace. Verifique pestaña 'DATA_USUARIOS' en Drive.")
    st.stop()

# --- 4. CARGA DE DATOS ---
if st.session_state.df_maestro is None:
    try:
        df_n = conn.read(worksheet='NOTAS_CONSOLIDADAS')
        df_e = conn.read(worksheet='DATA_ESTUDIANTES')
        df_l = conn.read(worksheet='DB_LOGROS')
        df_a = conn.read(worksheet='DB_ASISTENCIA')
        df = pd.merge(df_n, df_e[['ID_Estudiante', 'Grado']], left_on='ID_Est', right_on='ID_Estudiante', how='left')
        st.session_state.df_maestro = df.fillna(0)
        st.session_state.df_logros = df_l.fillna("")
        st.session_state.df_asistencia = df_a.fillna("")
        st.rerun()
    except: st.error("❌ Fallo al sincronizar matrices."); st.stop()

# --- 5. PANEL LATERAL CON RELOJ TÁCTICO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2231/2231644.png", width=70)
    st.markdown(f"### 👤 {st.session_state.nombre_completo_usuario}")
    
    # Reloj Táctico de Misión (REINSTALADO)
    st.markdown(f"""
        <div style='background:rgba(212, 175, 55, 0.1); border:1px solid #d4af37; padding:10px; border-radius:5px; text-align:center;'>
            <p style='color:#d4af37; font-size:12px; margin:0;'>🕒 HORA DE INICIO</p>
            <p style='color:white; font-size:18px; font-weight:bold; margin:0;'>{st.session_state.hora_inicio}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    opciones = ["🏠 Inicio", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias", "📜 Boletines"]
    if st.session_state.rol == "Admin": opciones.insert(1, "🛡️ Backup")
    menu = st.radio("SECCIONES:", opciones)
    
    st.markdown("---")
    cursos = ["TODOS"] + sorted(st.session_state.df_maestro['Grado'].unique().astype(str).tolist())
    curso_sel = st.selectbox("📚 GRADO:", cursos)
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "CONSOLIDADO"])
    
    if st.button("🔴 Salir"): 
        st.session_state.logueado = False
        st.rerun()

# --- 6. CABECERA ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>ACADEMIA GLOBAL HORIZONTE</h1></div>", unsafe_allow_html=True)
st.markdown(f"<div class='asistente-box'>🔹 Módulo: {menu} | Grado: {curso_sel} | {periodo_sel}</div>", unsafe_allow_html=True)

df_m = st.session_state.df_maestro
df_filtrado = df_m[df_m['Grado'].astype(str) == curso_sel] if curso_sel != "TODOS" else df_m

# --- 7. LÓGICA DE MÓDULOS ---
if menu == "🏠 Inicio":
    st.markdown("### Bienvenido al Sistema Génesis")
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1470&auto=format&fit=crop", use_container_width=True)

elif menu == "✍️ Digitar Notas":
    st.info("Rango permitido: 1.0 a 10.0. Presione GUARDAR para sincronizar con Drive.")
    config_n = {p: st.column_config.NumberColumn(p, min_value=1.0, max_value=10.0, step=0.1) for p in ["P1","P2","P3","P4"]}
    df_editor = st.data_editor(df_filtrado, column_config=config_n, use_container_width=True, key="edit_notas")
    if st.button("💾 GUARDAR CAMBIOS"):
        with st.spinner("Subiendo datos al satélite..."):
            st.session_state.df_maestro = df_editor
            # Limpieza para subir
            df_save = df_editor.drop(columns=['Grado', 'ID_Estudiante'], errors='ignore')
            conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_save)
            st.success("✅ ¡Base de datos actualizada con éxito!")

elif menu == "🚦 Semáforo Académico":
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO" else "PROMEDIO"
    df_semaforo = df_filtrado.groupby('NOMBRE_COMPLETO')[col_n].mean().reset_index()
    
    c1, c2, c3 = st.columns(3)
    rojos = df_semaforo[df_semaforo[col_n] < 6.0]
    naranjas = df_semaforo[(df_semaforo[col_n] >= 6.0) & (df_semaforo[col_n] < 7.6)]
    verdes = df_semaforo[df_semaforo[col_n] >= 7.6]
    
    c1.markdown(f"<div class='tarjeta-roja'>🔴 CRÍTICOS: {len(rojos)}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='tarjeta-naranja'>🟡 ALERTA: {len(naranjas)}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='tarjeta-verde'>🟢 ÓPTIMOS: {len(verdes)}</div>", unsafe_allow_html=True)
    
    if not rojos.empty:
        st.error("🚨 ESTUDIANTES EN RIESGO DE REPROBACIÓN")
        st.table(rojos)

elif menu == "📜 Boletines":
    st.markdown("### Generador de Informes")
    alumno = st.selectbox("Seleccione Estudiante:", sorted(df_filtrado['NOMBRE_COMPLETO'].unique()))
    if st.button("🖨️ Generar Vista de Impresión"):
        res = df_filtrado[df_filtrado['NOMBRE_COMPLETO'] == alumno]
        html = f"""
        <div style="border:5px solid #000; padding:20px; font-family:Arial;">
            <h2 style="text-align:center;">ACADEMIA GLOBAL HORIZONTE</h2>
            <p><b>Estudiante:</b> {alumno} | <b>Grado:</b> {res['Grado'].iloc[0]}</p>
            <table border="1" style="width:100%; border-collapse:collapse;">
                <tr style="background:#eee;"><th>Asignatura</th><th>Nota</th><th>Logro</th></tr>
        """
        for _, r in res.iterrows():
            html += f"<tr><td>{r['ASIGNATURA']}</td><td>{r[periodo_sel if periodo_sel != 'CONSOLIDADO' else 'PROMEDIO']}</td><td>{r['LOGROS']}</td></tr>"
        html += "</table><br><p style='text-align:center;'>____________________<br>Firma Rectoría</p></div>"
        components.html(html, height=400, scrolling=True)

# ... Resto de módulos (Dashboard, Logros, Asistencia) siguen la misma lógica ...
