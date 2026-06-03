import streamlit as st
import pandas as pd

def renderizar(df_notas, periodo_sel, conn_sql=None):
    # 👑 MOTOR VISUAL TÁCTICO: Animaciones, Levitación y Marcos VIP
    st.markdown("""
    <style>
    /* Animaciones de Pulso para los Números */
    @keyframes pulso_critico { 0%, 100% { opacity: 1; text-shadow: 0 0 0px #cc0000; } 50% { opacity: 0.8; text-shadow: 0 0 15px rgba(204,0,0,0.6); } }
    @keyframes pulso_alerta { 0%, 100% { opacity: 1; text-shadow: 0 0 0px #cc8800; } 50% { opacity: 0.8; text-shadow: 0 0 15px rgba(204,136,0,0.6); } }
    @keyframes pulso_optimo { 0%, 100% { opacity: 1; text-shadow: 0 0 0px #00994c; } 50% { opacity: 0.8; text-shadow: 0 0 15px rgba(0,153,76,0.6); } }
    
    /* Tarjetas Blindadas con Hover */
    .card-semaforo {
        padding: 15px; 
        border-radius: 14px; 
        text-align: center;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card-semaforo:hover {
        transform: translateY(-5px);
        box-shadow: 6px 12px 20px rgba(0,0,0,0.15);
    }
    
    /* Colores Específicos */
    .c-critica { background-color: #ffebeb; border: 3px solid #cc0000; }
    .c-alerta { background-color: #fffef0; border: 3px solid #cc8800; }
    .c-optima { background-color: #e6f9f0; border: 3px solid #00994c; }
    
    /* Tipografía Numérica */
    .num-critico { font-size: 45px; font-family: 'Arial Black'; color: #cc0000; animation: pulso_critico 1.5s infinite; margin: 0; line-height: 1; }
    .num-alerta { font-size: 45px; font-family: 'Arial Black'; color: #cc8800; animation: pulso_alerta 1.5s infinite; margin: 0; line-height: 1; }
    .num-optimo { font-size: 45px; font-family: 'Arial Black'; color: #00994c; animation: pulso_optimo 1.5s infinite; margin: 0; line-height: 1; }
    
    /* Etiqueta Superior */
    .txt-titular { font-family: 'Arial Black', sans-serif; font-size: 14px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; color: #0d1b2a; }
    
    /* Blindaje para las Tablas Internas */
    div[data-testid="stDataFrame"] {
        border: 2px solid #0d1b2a !important;
        border-radius: 8px !important;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico</h3>", unsafe_allow_html=True)

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ No hay datos disponibles para el Semáforo.")
        return

    # Estandarización de columnas
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]
    
    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    
    col_nota = periodo_sel.upper().strip() if periodo_sel and periodo_sel.upper().strip() in df_trabajo.columns else \
               next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'PROMEDIO_FINAL', 'DEF', 'NOTA']), None)

    if not col_nota:
        st.error(f"🚨 No se encontró la columna de notas válida para el periodo: {periodo_sel}.")
        return

    df_trabajo[col_nota] = pd.to_numeric(df_trabajo[col_nota], errors='coerce')
    
    # 🎯 SELECTOR COMPACTO Y ELEGANTE
    col_selector, _ = st.columns([4, 6])
    grado_sel = "TODOS"
    
    with col_selector:
        if col_grado:
            grados_validos = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
            grado_sel = st.selectbox("🔍 Filtrar Escuadrón / Grado:", ["TODOS"] + grados_validos)
            
    if grado_sel != "TODOS":
        df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # Agrupación Táctica por Estudiante
    df_resumen = df_trabajo.groupby(col_nombre).agg({col_nota: 'mean', col_grado: 'first'}).reset_index()
    df_resumen = df_resumen.dropna(subset=[col_nota])
    df_resumen = df_resumen.rename(columns={col_nota: "Promedio"})

    # Clasificación Estratégica
    criticos = df_resumen[df_resumen["Promedio"] < 6.0].sort_values(by="Promedio", ascending=True)
    alertas = df_resumen[(df_resumen["Promedio"] >= 6.0) & (df_resumen["Promedio"] < 7.6)].sort_values(by="Promedio", ascending=True)
    optimos = df_resumen[df_resumen["Promedio"] >= 7.6].sort_values(by="Promedio", ascending=False)

    # 📊 PANELES SUPERIORES (KPIs)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='card-semaforo c-critica'><div class='txt-titular'>Riesgo Crítico</div><p class='num-critico'>{len(criticos)}</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card-semaforo c-alerta'><div class='txt-titular'>En Alerta</div><p class='num-alerta'>{len(alertas)}</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card-semaforo c-optima'><div class='txt-titular'>Óptimo</div><p class='num-optimo'>{len(optimos)}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ⚙️ CONFIGURACIÓN DE COLUMNAS (Barra de Progreso Integrada)
    config_tablas = {
        col_nombre: st.column_config.TextColumn("Estudiante", width="large"),
        col_grado: st.column_config.TextColumn("Grado", width="medium"),
        "Promedio": st.column_config.ProgressColumn("Nivel Ponderado", help="Promedio acumulado", format="%.1f", min_value=0, max_value=10)
    }

    # 🛡️ PESTAÑAS DE INSPECCIÓN 360°
    tab1, tab2, tab3 = st.tabs(["🔴 RIESGO CRÍTICO (< 6.0)", "🟡 EN ALERTA (6.0 - 7.5)", "🟢 RENDIMIENTO ÓPTIMO (> 7.5)"])
    
    with tab1:
        if not criticos.empty:
            st.dataframe(criticos, use_container_width=True, hide_index=True, column_config=config_tablas)
        else:
            st.success("✅ Excelente: No hay estudiantes en riesgo crítico en este corte.")
            
    with tab2:
        if not alertas.empty:
            st.dataframe(alertas, use_container_width=True, hide_index=True, column_config=config_tablas)
        else:
            st.info("ℹ️ No hay estudiantes en zona de alerta (Básico).")
            
    with tab3:
        if not optimos.empty:
            st.dataframe(optimos, use_container_width=True, hide_index=True, column_config=config_tablas)
        else:
            st.warning("⚠️ No se registran estudiantes con rendimiento alto o superior.")
