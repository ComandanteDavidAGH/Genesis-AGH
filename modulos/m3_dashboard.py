import streamlit as st
import pandas as pd
import plotly.express as px

def renderizar(df, periodo_sel, conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📈 Radar Táctico Individual</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No hay datos para analizar en esta vista.")
        return
        
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    lista_alumnos_dash = sorted(df['Nombre_Completo'].dropna().unique()) if 'Nombre_Completo' in df.columns else []
    alumno_analisis = st.selectbox("🎯 Seleccione Estudiante a Inspeccionar:", lista_alumnos_dash)
    
    if alumno_analisis:
        df_alum = df[df['Nombre_Completo'] == alumno_analisis]
        promedio_global = df_alum[col_n].mean() if col_n in df_alum.columns else 0.0
        
        if promedio_global < 6.0: des_global = 'BAJO 🔴'
        elif promedio_global < 7.6: des_global = 'BÁSICO 🟡'
        elif promedio_global < 9.1: des_global = 'ALTO 🟢'
        else: des_global = 'SUPERIOR 🌟'
        
        novedades_count = 0
        df_hist_alum = pd.DataFrame()
        if st.session_state.df_asistencia is not None and not st.session_state.df_asistencia.empty and 'Nombre_Completo' in st.session_state.df_asistencia.columns:
            df_hist_alum = st.session_state.df_asistencia[st.session_state.df_asistencia['Nombre_Completo'] == alumno_analisis]
            novedades_count = len(df_hist_alum)
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.markdown(f"<div class='metric-card'><p class='metric-label'>Promedio ({periodo_sel})</p><p class='metric-value'>{promedio_global:.1f}</p></div>", unsafe_allow_html=True)
        with col_m2: st.markdown(f"<div class='metric-card'><p class='metric-label'>Nivel Actual</p><p class='metric-value'>{des_global}</p></div>", unsafe_allow_html=True)
        with col_m3: st.markdown(f"<div class='metric-card'><p class='metric-label'>Novedades / Faltas</p><p class='metric-value'>{novedades_count}</p></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns([1.2, 1])
        with col_r1:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>POLÍGONO DE DESEMPEÑO</p>", unsafe_allow_html=True)
            if not df_alum.empty and col_n in df_alum.columns:
                fig_radar = px.line_polar(df_alum, r=col_n, theta='Materia', line_close=True, range_r=[0,10], text=col_n)
                fig_radar.update_traces(fill='toself', fillcolor='rgba(212, 175, 55, 0.4)', line_color='#0d1b2a', line_width=3, mode='lines+markers+text', textfont=dict(color='#000000', size=13, family='Arial Black'), textposition='top center')
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color='black')), 
                        angularaxis=dict(type='category', tickfont=dict(color='black', size=13, family='Arial Black'))
                    ), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(l=60, r=60, t=30, b=30)
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={'displaylogo': False})
            else:
                st.info("📡 No hay datos suficientes para graficar el polígono.")
        with col_r2:
            st.markdown("<p style='font-weight:bold; font-family:Arial Black; text-align:center;'>HISTORIAL DISCIPLINARIO</p>", unsafe_allow_html=True)
            if novedades_count > 0: 
                st.dataframe(df_hist_alum[['FECHA', 'ESTADO', 'OBSERVACIONES']].sort_values(by='FECHA', ascending=False), use_container_width=True, hide_index=True)
            else: 
                st.info("✅ Sin reportes disciplinarios ni faltas.")
