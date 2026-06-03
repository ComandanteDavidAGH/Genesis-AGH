import streamlit as st
import pandas as pd
import plotly.express as px

def renderizar(df, periodo_sel):
    # 🚀 INYECCIÓN DEL MOTOR DE ANIMACIÓN (GRÁFICOS VIVOS)
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
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📊 Inteligencia Académica</h3>", unsafe_allow_html=True)
    if df.empty:
        st.warning("No hay datos para analizar.")
        return

    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    config_espanol = {'locale': 'es', 'displaylogo': False}
    c1, c2 = st.columns(2)
    
    with c1: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Rendimiento por Materia ({periodo_sel})</div>", unsafe_allow_html=True)
        if col_n in df.columns:
            df_promedios = df.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
            fig1 = px.bar(df_promedios, x=col_n, y='Materia', text_auto='.1f', color='Materia', orientation='h')
            
            # Ajuste interno de contraste
            fig1.update_traces(marker=dict(line=dict(color='#000000', width=1.5)), opacity=0.9)
            fig1.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            fig1.update_yaxes(title_text="", visible=True, tickmode='linear', dtick=1, tickfont=dict(size=13, color='#000000', family="Arial Black"), automargin=True) 
            fig1.update_xaxes(title_text="Promedio", title_font=dict(color="#000", family="Arial Black"), tickfont=dict(color="#000", family="Arial Black"))
            
            st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
    
    with c2: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
        if col_n in df.columns:
            def evaluar_filtro(nota):
                if nota < 6.0: return 'BAJO'
                elif nota < 7.6: return 'BÁSICO'
                elif nota < 9.1: return 'ALTO'
                else: return 'SUPERIOR'
            df_pie = df.copy()
            df_pie['DESEMPEÑO_FILTRO'] = df_pie[col_n].apply(evaluar_filtro)
            colores_vivos = {'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'}
            
            fig2 = px.pie(df_pie, names='DESEMPEÑO_FILTRO', hole=0.45, color='DESEMPEÑO_FILTRO', color_discrete_map=colores_vivos)
            
            # Ajuste interno de contraste para la dona
            fig2.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color="#000000", family="Arial Black", size=13), pull=[0.02]*4, marker=dict(line=dict(color='#000000', width=1.5)), opacity=0.95)
            fig2.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            
            st.plotly_chart(fig2, use_container_width=True, config=config_espanol)
