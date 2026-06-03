import streamlit as st
import pandas as pd
import plotly.express as px

def renderizar(df, periodo_sel, conn):
    # 🚀 INYECCIÓN DEL MOTOR DE ANIMACIÓN 3D Y ESTILOS DE TARJETAS (KPIs)
    st.markdown("""
    <style>
    /* Efecto base de las gráficas */
    [data-testid="stPlotlyChart"] {
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        border: 2px solid #0d1b2a !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.08) !important;
        will-change: transform !important;
        z-index: 1;
        padding: 10px !important;
    }
    
    /* Efecto de Agrandamiento y Levitación al pasar el mouse */
    [data-testid="stPlotlyChart"]:hover {
        transform: translateY(-8px) scale(1.035) !important;
        box-shadow: 0 22px 45px rgba(212, 175, 55, 0.45) !important;
        border-color: #d4af37 !important;
        z-index: 999 !important;
    }

    /* 🎨 ESTILOS RESTAURADOS PARA LAS TARJETAS SUPERIORES (KPIs) */
    .metric-card {
        background: #ffffff;
        border: 2px solid #0d1b2a;
        border-top: 5px solid #d4af37;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.05);
        height: 100%;
    }
    .metric-label {
        font-size: 12px;
        color: #555555;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 24px;
        color: #0d1b2a;
        font-weight: bold;
        margin: 0;
        font-family: Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📈 Radar Táctico Individual</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No hay datos para analizar en esta vista.")
        return
        
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    # Restringir ancho del selector para mejor estética (como vimos antes)
    col_sel, _ = st.columns([5, 5])
    with col_sel:
        lista_alumnos_dash = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
        alumno_analisis = st.selectbox("🎯 Seleccione Estudiante a Inspeccionar:", lista_alumnos_dash)
    
    if alumno_analisis:
        # Aislamos el dataframe del alumno y aseguramos tipo de dato numérico
        df_alum = df[df['Nombre_Completo'] == alumno_analisis].copy()
        df_alum[col_n] = pd.to_numeric(df_alum[col_n], errors='coerce')
        
        # Promedio global con seguridad contra nulos (NaN)
        promedio_global = df_alum[col_n].mean()
        if pd.isna(promedio_global): promedio_global = 0.0
        
        if promedio_global < 6.0: des_global = 'BAJO 🔴'
        elif promedio_global < 7.6: des_global = 'BÁSICO 🟡'
        elif promedio_global < 9.1: des_global = 'ALTO 🟢'
        else: des_global = 'SUPERIOR 🌟'
        
        # 🛡️ BLINDAJE DE SESSION STATE (Evitar KeyError)
        novedades_count = 0
        df_hist_alum = pd.DataFrame()
        
        if 'df_asistencia' in st.session_state and st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty:
            if 'Nombre_Completo' in st.session_state.df_asistencia.columns:
                df_hist_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_analisis]
                novedades_count = len(df_hist_alum)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # TARJETAS MÉTRICAS (Ahora sí con su CSS activo)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio ({periodo_sel})</p><p class='metric-value'>{promedio_global:.1f}</p></div>", unsafe_allow_html=True)
        with col_m2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Nivel Actual</p><p class='metric-value'>{des_global}</p></div>", unsafe_allow_html=True)
        with col_m3: st.markdown(f"<div class='metric-card'><p class='metric-label'>Novedades / Faltas</p><p class='metric-value'>{novedades_count}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns([1.2, 1])
        with col_r1:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>POLÍGONO DE DESEMPEÑO</p>", unsafe_allow_html=True)
            
            # Limpiamos notas nulas antes de graficar para no deformar el polígono
            df_radar = df_alum.dropna(subset=[col_n]).copy()
            
            if not df_radar.empty:
                # Formateamos el texto para que solo muestre 1 decimal limpio en el gráfico
                df_radar['Etiqueta_Nota'] = df_radar[col_n].apply(lambda x: f"{x:.1f}")
                
                fig_radar = px.line_polar(df_radar, r=col_n, theta='Materia', line_close=True, range_r=[0,10], text='Etiqueta_Nota')
                fig_radar.update_traces(fill='toself', fillcolor='rgba(212, 175, 55, 0.4)', line_color='#0d1b2a', line_width=3, mode='lines+markers+text', textfont=dict(color='#000000', size=13, family='Arial Black'), textposition='top center')
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color='black')), 
                        angularaxis=dict(type='category', tickfont=dict(color='black', size=11, family='Arial Black'))
                    ), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(l=60, r=60, t=30, b=30)
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={'displaylogo': False})
            else:
                st.info("📡 No hay datos numéricos suficientes para graficar el polígono.")
                
        with col_r2:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>HISTORIAL DISCIPLINARIO</p>", unsafe_allow_html=True)
            if novedades_count > 0: 
                # Validamos que las columnas existan antes de seleccionarlas
                cols_mostrar = [c for c in ['FECHA', 'ESTADO', 'OBSERVACIONES'] if c in df_hist_alum.columns]
                st.dataframe(df_hist_alum[cols_mostrar].sort_values(by=cols_mostrar[0] if cols_mostrar else df_hist_alum.columns[0], ascending=False), use_container_width=True, hide_index=True)
            else: 
                st.success("✅ Sin reportes disciplinarios ni faltas. ¡Excelente comportamiento!")
