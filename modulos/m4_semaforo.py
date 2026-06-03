import streamlit as st
import pandas as pd

def renderizar(conn_sql):
    # 👑 INYECTOR DE ANIMACIÓN TITILANTE Y PANELS 3D EXECUTIVE
    st.markdown("""
        <style>
            /* 🚨 ANIMACIÓN MAESTRA DE PARPADEO (EFECTO TITILANTE) */
            @keyframes titilar_critico {
                0% { opacity: 1; transform: scale(1); text-shadow: 0 0 15px rgba(204, 0, 0, 0.6); }
                50% { opacity: 0.2; transform: scale(1.05); text-shadow: 0 0 0px rgba(204, 0, 0, 0); }
                100% { opacity: 1; transform: scale(1); text-shadow: 0 0 15px rgba(204, 0, 0, 0.6); }
            }
            
            /* Clases de control estético */
            .titular-semaforo {
                font-family: 'Arial Black', sans-serif;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .numero-critico-3d {
                font-size: 85px;
                font-family: 'Arial Black', sans-serif;
                font-weight: 900;
                color: #cc0000;
                display: inline-block;
                /* Activar el efecto titilante original */
                animation: titilar_critico 1.3s infinite ease-in-out;
            }
            
            .numero-alerta-3d {
                font-size: 85px;
                font-family: 'Arial Black', sans-serif;
                font-weight: 900;
                color: #cc8800;
                display: inline-block;
            }
            
            .numero-optimo-3d {
                font-size: 85px;
                font-family: 'Arial Black', sans-serif;
                font-weight: 900;
                color: #00994c;
                display: inline-block;
            }
            
            /* Tarjetas de contenedor con relieve rígido 3D */
            .card-semaforo-3d {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 12px;
                border: 3px solid #0d1b2a;
                box-shadow: 6px 6px 0px #0d1b2a;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico</h3>", unsafe_allow_html=True)
    
    # 🛡️ LECTURA EXTRACTORA DESDE EL BÚNKER DE SUPABASE
    try:
        df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
    except Exception as e:
        st.error(f"❌ Error al conectar con la bitácora de notas: {e}")
        return

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ Base de datos de notas vacía o no inicializada.")
        return

    # Normalizar columnas
    df_notas.columns = [str(c).upper().strip() for c in df_notas.columns]
    
    # Identificar columna promedio de forma flexible
    col_promedio = next((c for c in df_notas.columns if c in ['PROMEDIO', 'PROMEDIO_FINAL', 'DEF']), None)
    col_nombre = next((c for c in df_notas.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), None)
    col_grado = next((c for c in df_notas.columns if c in ['GRADO', 'CURSO']), None)

    if not all([col_promedio, col_nombre, col_grado]):
        st.error("🚨 Las columnas de la tabla SQL no coinciden con el mapeo del Semáforo.")
        return

    # Conversión forzada de datos métricos
    df_notas[col_promedio] = pd.to_numeric(df_notas[col_promedio], errors='coerce').fillna(0.0)
    
    # Filtros estructurales de barra lateral o cabecera
    grados_validos = sorted(df_notas[col_grado].dropna().unique().astype(str).tolist())
    grado_sel = st.selectbox("🔍 Seleccione el Grado para evaluar el Perímetro:", ["TODOS"] + grados_validos)
    
    df_trabajo = df_notas.copy()
    if grado_sel != "TODOS":
        df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # Clasificación matemática de los Batallones Académicos
    criticos = df_trabajo[df_trabajo[col_promedio] < 6.0]
    alertas = df_trabajo[(df_trabajo[col_promedio] >= 6.0) & (df_trabajo[col_promedio] <= 7.5)]
    optimos = df_trabajo[df_trabajo[col_promedio] > 7.5]

    count_criticos = len(criticos[col_nombre].unique())
    count_alertas = len(alertas[col_nombre].unique())
    count_optimos = len(optimos[col_nombre].unique())

    # 📅 MAQUETACIÓN EN COLUMNAS CON RELIEVE 3D ISOMÉTRICO
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
            <div class='card-semaforo-3d' style='border-top: 6px solid #cc0000;'>
                <div class='titular-semaforo' style='color:#cc0000;'>🔴 Riesgo Crítico (< 6.0)</div>
                <div class='numero-critico-3d'>{count_criticos}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
            <div class='card-semaforo-3d' style='border-top: 6px solid #cc8800;'>
                <div class='titular-semaforo' style='color:#cc8800;'>🟡 Alerta (6.0 - 7.5)</div>
                <div class='numero-alerta-3d'>{count_alertas}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
            <div class='card-semaforo-3d' style='border-top: 6px solid #00994c;'>
                <div class='titular-semaforo' style='color:#00994c;'>🟢 Óptimo (>= 7.6)</div>
                <div class='numero-optimo-3d'>{count_optimos}</div>
            </div>
        """, unsafe_allow_html=True)

    # 🚨 TABLA DE AUDITORÍA DE ESTUDIANTES EN RIESGO CRÍTICO
    st.markdown("<br><div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:10px; border-radius:8px; text-align:center; font-family:Arial Black; color:#cc0000; font-size:14px; letter-spacing:1px;'>🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO</div><br>", unsafe_allow_html=True)
    
    if not criticos.empty:
        df_mostrar = criticos[[col_nombre, col_grado, col_promedio]].drop_duplicates().sort_values(by=col_promedio)
        df_mostrar.columns = ['Nombre Completo', 'Grado', 'Promedio']
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Excelente estabilidad operativa: Cero estudiantes detectados en Riesgo Crítico.")
