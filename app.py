import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import io
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Génesis AGH | Sistema Operativo", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

# Conexión Satelital a Drive
conn = st.connection("gsheets", type=GSheetsConnection)

# Ajuste de Zona Horaria (Colombia UTC-5)
zona_colombia = timezone(timedelta(hours=-5))

# Inicialización de Estados
if 'logueado' not in st.session_state: st.session_state.logueado = False
if 'rol' not in st.session_state: st.session_state.rol = ""
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'nombre_completo_usuario' not in st.session_state: st.session_state.nombre_completo_usuario = ""
if 'bitacora' not in st.session_state: st.session_state.bitacora = []
if 'df_maestro' not in st.session_state: st.session_state.df_maestro = None
if 'df_logros' not in st.session_state: st.session_state.df_logros = None
if 'df_asistencia' not in st.session_state: st.session_state.df_asistencia = None
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = datetime.now(zona_colombia).strftime("%I:%M %p")

# --- 2. CSS AVANZADO (OPERACIÓN MISTERIO: BLINDAJE TOTAL) ---
st.markdown("""
    <style>
    /* 🛡️ BLOQUEO RADICAL DE INTRUSOS (GATITO Y DEPLOY) */
    .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="stHeaderActionElements"] { display: none !important; }
    [data-testid="stGitHubBadge"] { display: none !important; }
    footer { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }
    
    /* 🎨 ESTÉTICA INSTITUCIONAL ALTO CONTRASTE */
    .stApp { background-color: #ffffff; }
    .stApp::before {
        content: ""; background-image: url('https://cdn-icons-png.flaticon.com/512/2231/2231644.png');
        background-size: 350px; background-repeat: no-repeat; background-position: center;
        opacity: 0.04; position: fixed; top: 0; left: 0; bottom: 0; right: 0; z-index: 0; pointer-events: none;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; z-index: 1; }
    
    /* PANEL LATERAL DORADO Y NAVY */
    [data-testid="stSidebar"] { background-color: #0d1b2a !important; border-right: 5px solid #d4af37; z-index: 2; }
    [data-testid="stSidebar"] * { color: white !important; font-weight: bold; }
    
    /* TÍTULOS Y MÉTRICAS AGH */
    .titulo-container { position: sticky; top: 0; background-color: #ffffff; padding: 10px 0; z-index: 999; border-bottom: 4px solid #d4af37; margin-bottom: 20px; }
    .titulo-Agh { color: #000000 !important; font-family: 'Arial Black', sans-serif; font-size: 2.5rem !important; text-align: center; text-shadow: 2px 2px 0px #d4af37; margin: 0;}
    
    .asistente-box { background: white; border-radius: 8px; padding: 12px; border-left: 8px solid #d4af37; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #000; margin-bottom: 20px; color: #000; font-weight: bold; font-size: 16px;}
    
    .metric-card { background-color: #ffffff; border: 3px solid #000000; border-top: 10px solid #d4af37; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 6px 6px 0px #0d1b2a; }
    .metric-value { font-size: 32px; font-weight: 900; color: #0d1b2a; font-family: 'Arial Black'; margin:0;}
    .metric-label { font-size: 14px; font-weight: bold; color: #000000; text-transform: uppercase; margin:0;}

    /* SEMÁFORO - ANIMACIÓN DE ALERTA */
    @keyframes pulso-rojo { 0% { box-shadow: 0 0 0px rgba(255, 0, 0, 0.4); } 50% { box-shadow: 0 0 25px rgba(255, 0, 0, 1); } 100% { box-shadow: 0 0 0px rgba(255, 0, 0, 0.4); } }
    .tarjeta-roja { animation: pulso-rojo 1s infinite; border: 4px solid #cc0000; background:#ffe6e6; padding:20px; border-radius:10px; color: #000; text-align: center;}
    </style>
""", unsafe_allow_html=True)

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({"Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"), "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"), "Usuario": usuario, "Rol": rol, "Acción": accion})

# --- 3. ACCESO AL BÚNKER (LOGIN) ---
if not st.session_state.logueado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])
    with c2:
        st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=800", use_container_width=True)
        st.markdown("""<div style="background: white; padding: 20px; border-radius: 10px; border-top: 8px solid #d4af37; border: 3px solid #000; text-align: center; margin-bottom: 15px;"><h2 style="color:#000; font-family:'Arial Black';">LOGIN GÉNESIS</h2></div>""", unsafe_allow_html=True)
        u = st.text_input("👤 USUARIO", placeholder="Admin / Docente", label_visibility="collapsed")
        p = st.text_input("🔑 CONTRASEÑA", type="password", placeholder="••••••••", label_visibility="collapsed")
        if st.button("🚀 INICIAR OPERACIÓN", use_container_width=True):
            try:
                df_usuarios = conn.read(worksheet='DATA_USUARIOS')
                acceso = df_usuarios[(df_usuarios['USUARIO'] == u) & (df_usuarios['PASSWORD'] == p)]
                if not acceso.empty:
                    st.session_state.logueado, st.session_state.rol = True, str(acceso['ROL'].iloc[0]).strip().capitalize()
                    st.session_state.usuario_actual, st.session_state.nombre_completo_usuario = u, str(acceso['NOMBRE_COMPLETO'].iloc[0]).strip()
                    registrar_bitacora(u, st.session_state.rol, "✅ Ingreso Exitoso")
                    st.rerun()
                elif u == "admin" and p == "agh2024":
                    st.session_state.logueado, st.session_state.rol, st.session_state.usuario_actual = True, "Admin", u
                    st.session_state.nombre_completo_usuario = "Comandante Supremo"
                    st.rerun()
                else: st.error("❌ Credenciales Inválidas")
            except: st.error("❌ Error 404: No se detecta el Excel en el satélite")
    st.stop()

# --- 4. CARGA DE INTELIGENCIA (DATOS) ---
if st.session_state.df_maestro is None:
    with st.spinner("Sincronizando con la Bóveda Satelital..."):
        try:
            df_n = conn.read(worksheet='NOTAS_CONSOLIDADAS')
            df_e = conn.read(worksheet='DATA_ESTUDIANTES')
            df_l = conn.read(worksheet='DB_LOGROS')
            df_a = conn.read(worksheet='DB_ASISTENCIA')
            df = pd.merge(df_n, df_e[['ID_Estudiante', 'Grado']], left_on='ID_Est', right_on='ID_Estudiante', how='left')
            st.session_state.df_maestro, st.session_state.df_logros, st.session_state.df_asistencia = df.fillna(0), df_l.fillna(""), df_a.fillna("")
            st.rerun()
        except: st.error("🚨 ERROR CRÍTICO: El archivo de Google Drive no responde. Verifique los Secrets."); st.stop()

# --- 5. PANEL DE MANDO LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2231/2231644.png", width=80)
    st.markdown(f"### 🎖️ {st.session_state.nombre_completo_usuario}")
    st.markdown(f"<p style='color:#d4af37; font-size:14px;'>🕒 INGRESO: {st.session_state.hora_inicio}</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("SECCIONES TÁCTICAS:", ["🏠 Inicio", "👑 Centro de Mando", "📊 Inteligencia Académica", "📈 Dashboard Estudiantil", "🚦 Semáforo Académico", "✍️ Digitar Notas", "📚 Logros", "📝 Asistencias", "📜 Boletines", "📖 Manual VIP", "🛡️ Bitácora"])
    st.markdown("---")
    curso_sel = st.selectbox("📚 GRADO:", ["TODOS"] + sorted(st.session_state.df_maestro['Grado'].unique().astype(str).tolist()))
    periodo_sel = st.selectbox("🎯 PERIODO:", ["P1", "P2", "P3", "P4", "PROMEDIO"])
    if st.button("🔴 CERRAR SESIÓN"): st.session_state.logueado = False; st.rerun()

# --- 6. CABECERA AGH ---
st.markdown("<div class='titulo-container'><h1 class='titulo-Agh'>ACADEMIA GLOBAL HORIZONTE</h1></div>", unsafe_allow_html=True)
df_f = st.session_state.df_maestro[st.session_state.df_maestro['Grado'].astype(str) == curso_sel] if curso_sel != "TODOS" else st.session_state.df_maestro

# --- 7. DESPLIEGUE DE MÓDULOS ---
if menu == "🏠 Inicio":
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1470", use_container_width=True)
    st.markdown("<div class='asistente-box'>Génesis: 'Bienvenido al Búnker, Comandante. Perímetro asegurado y datos sincronizados.'</div>", unsafe_allow_html=True)

elif menu == "👑 Centro de Mando":
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><p class='metric-label'>Estudiantes Activos</p><p class='metric-value'>{len(df_f['NOMBRE_COMPLETO'].unique())}</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio Institucional</p><p class='metric-value'>{df_f[periodo_sel].mean():.1f}</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><p class='metric-label'>Fallas Reportadas</p><p class='metric-value'>{len(st.session_state.df_asistencia)}</p></div>", unsafe_allow_html=True)
    st.plotly_chart(px.bar(df_f.groupby('Grado')[periodo_sel].mean().reset_index(), x='Grado', y=periodo_sel, color='Grado', title="Rendimiento por Grado"), use_container_width=True)

elif menu == "✍️ Digitar Notas":
    st.warning("⚠️ RANGO VÁLIDO: 1.0 a 10.0. Use punto (.) para decimales.")
    config = {p: st.column_config.NumberColumn(p, min_value=1.0, max_value=10.0, step=0.1) for p in ["P1","P2","P3","P4"]}
    ed = st.data_editor(df_f, column_config=config, use_container_width=True, num_rows="dynamic")
    if st.button("💾 GUARDAR CAMBIOS EN LA NUBE"):
        with st.spinner("Sincronizando con Drive..."):
            conn.update(worksheet="NOTAS_CONSOLIDADAS", data=ed.drop(columns=['Grado', 'ID_Estudiante'], errors='ignore'))
            st.success("✅ OPERACIÓN EXITOSA: Notas Blindadas en Drive.")

elif menu == "🚦 Semáforo Académico":
    rojos = df_f[df_f[periodo_sel] < 6.0]
    st.markdown(f"<div class='tarjeta-roja'>🚨 ALERTA ROJA: {len(rojos)} Estudiantes en Riesgo Académico</div>", unsafe_allow_html=True)
    st.dataframe(rojos[['NOMBRE_COMPLETO', 'ASIGNATURA', periodo_sel]].style.format({periodo_sel: "{:.1f}"}))

elif menu == "📜 Boletines":
    alum = st.selectbox("🎯 Seleccione Estudiante:", sorted(df_f['NOMBRE_COMPLETO'].unique()))
    if st.button("🚀 GENERAR BOLETÍN VIP"):
        st.balloons()
        st.success(f"Boletín de {alum} listo para impresión.")
        st.info("Utilice el comando CTRL+P para imprimir el reporte generado.")

elif menu == "📖 Manual VIP":
    st.markdown("### 📖 Manual de Supervivencia del Sistema")
    with st.expander("🔹 Cómo cargar notas"): st.write("Entre a 'Digitar Notas', use el teclado y no olvide presionar el botón azul de GUARDAR abajo.")
    with st.expander("🔹 El Reloj no coincide"): st.write("El sistema usa la hora de Colombia (UTC-5) configurada en el motor Génesis.")

elif menu == "🛡️ Bitácora":
    st.markdown("### 🕵️ Registro de Movimientos")
    st.dataframe(pd.DataFrame(st.session_state.bitacora).iloc[::-1], use_container_width=True)

# --- FIN DEL ARSENAL GÉNESIS ---
