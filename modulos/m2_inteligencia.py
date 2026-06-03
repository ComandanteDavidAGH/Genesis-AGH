import streamlit as st
import pandas as pd
import plotly.express as px

def renderizar(df, periodo_sel):
    # 🚀 INYECCIÓN DEL MOTOR DE ANIMACIÓN Y ESTILOS 3D
    st.markdown("""
    <style>
    /* Efecto 3D de los gráficos Plotly */
    [data-testid="stPlotlyChart"] {
        background-color: #ffffff !important;
        padding: 18px !important;
        border-radius: 14px !important;
        border: 3px solid #0d1b2a !important;
        box-shadow: 7px 7px 0px #0d1b2a, 12px 12px 25px rgba(0,0,0,0.15) !important;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        will-change: transform !important;
        z-index: 1;
    }
    
    /* Efecto de Levitación Magnética al Hover */
    [data-testid="stPlotlyChart"]:hover {
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 9px 9px 0px #d4af37, 15px 15px 30px rgba(0,0,0,0.2) !important;
        border-color: #d4af37 !important;
        z-index: 999 !important;
    }
    
    /* Tarjetas de KPI Tácticos */
    .kpi-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a365d 100%);
        border-left: 5px solid #d4af37;
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .kpi-title { font-size: 12px; font-weight: bold; color: #d4af37; text-transform: uppercase; letter-spacing: 1px; margin:0; }
    .kpi-value { font-size: 24px; font-family: 'Arial Black', sans-serif; margin: 5px 0 0 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📊 Inteligencia Académica</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No hay datos para analizar.")
        return

    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if col_n not in df.columns:
        st.error(f"La columna '{col_n}' no existe en la base de datos actual.")
        return

    # 🛑 CONTROL ULTRA-ESTRICTO DE ERRORES DE USUARIO (Mantenido por su excelente lógica)
    notas_convertidas = pd.to_numeric(df[col_n], errors='coerce')
    filas_con_error = df[notas_convertidas.isna() & df[col_n].notna() & (df[col_n].astype(str).str.strip() != "")]

    if not filas_con_error.empty:
        st.error(f"🚨 **¡Falla de Integridad en Datos!** Se detectaron caracteres no numéricos (letras o símbolos) en la columna de calificaciones de **{periodo_sel}**.")
        with st.expander("🔍 Ver registros corrompidos para corrección inmediata:", expanded=True):
            columnas_clave = [c for c in ['Nombre_Completo', 'Grado', 'Materia', col_n] if c in df.columns]
            st.dataframe(filas_con_error[columnas_clave])
        st.info("💡 *Por favor, diríjase al módulo 'Digitar Notas' o a su archivo de respaldo y corrija las celdas afectadas.*")
        return  

    # Limpiamos los nulos legítimos
    df_seguro = df.dropna(subset=[col_n]).copy()
    df_seguro[col_n] = df_seguro[col_n].astype(float)

    if df_seguro.empty:
        st.info("No hay calificaciones registradas para generar los gráficos en este periodo.")
        return

    # 🚀 NUEVO: TARJETAS DE MANDO (KPIs)
    df_promedios = df_seguro.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
    
    total_evaluados = df_seguro['Nombre_Completo'].nunique() if 'Nombre_Completo' in df_seguro.columns else len(df_seguro)
    promedio_global = df_seguro[col_n].mean()
    mejor_materia = str(df_promedios.iloc[-1]['Materia']) if not df_promedios.empty else "N/A"

    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Alumnos Evaluados</p><p class='kpi-value'>{total_evaluados}</p></div>", unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Promedio Global</p><p class='kpi-value'>{promedio_global:.1f}</p></div>", unsafe_allow_html=True)
    with col_k3:
        st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Materia Destacada</p><p class='kpi-value' style='font-size:16px; margin-top:12px;'>🏆 {mejor_materia}</p></div>", unsafe_allow_html=True)

    # --- CONFIGURACIÓN Y RENDERIZADO DE GRÁFICOS ---
    config_espanol = {'locale': 'es', 'displaylogo': False}
    c1, c2 = st.columns(2)
    
    with c1: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Rendimiento por Materia ({periodo_sel})</div>", unsafe_allow_html=True)
        
        # ⚡ Gráfico de Barras con "Mapa de Calor" según el Promedio
        fig1 = px.bar(
            df_promedios, x=col_n, y='Materia', text_auto='.1f', 
            color=col_n, 
            color_continuous_scale=['#cc0000', '#d4af37', '#0d1b2a'], # Semáforo de Riesgo a Éxito
            orientation='h'
        )
        
        fig1.update_traces(
            marker=dict(line=dict(color='#000000', width=1.5)), 
            opacity=0.95,
            hovertemplate="<b>%{y}</b><br>Promedio: %{x:.1f}<extra></extra>" # Tooltip Limpio
        )
        fig1.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10), 
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            showlegend=False, coloraxis_showscale=False # Oculta la barra lateral para verse más limpio
        )
        fig1.update_yaxes(title_text="", visible=True, tickmode='linear', dtick=1, tickfont=dict(size=12, color='#000000', family="Arial Black"), automargin=True) 
        fig1.update_xaxes(title_text="Promedio Ponderado", title_font=dict(color="#000", family="Arial Black"), tickfont=dict(color="#000", family="Arial Black"))
        
        st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
    
    with c2: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
        
        limites = [-1, 6.0, 7.6, 9.1, 100.0]
        etiquetas = ['BAJO', 'BÁSICO', 'ALTO', 'SUPERIOR']
        
        df_pie = df_seguro.copy()
        df_pie['DESEMPEÑO_FILTRO'] = pd.cut(df_pie[col_n], bins=limites, labels=etiquetas, right=False)
        colores_vivos = {'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'}
        
        fig2 = px.pie(df_pie, names='DESEMPEÑO_FILTRO', hole=0.45, color='DESEMPEÑO_FILTRO', color_discrete_map=colores_vivos)
        
        fig2.update_traces(
            textposition='inside', textinfo='percent+label', 
            textfont=dict(color="#000000", family="Arial Black", size=13), 
            pull=[0.03]*4, 
            marker=dict(line=dict(color='#000000', width=1.5)), 
            opacity=0.95,
            hovertemplate="<b>Nivel %{label}</b><br>Alumnos: %{value}<br>Proporción: %{percent}<extra></extra>" # Tooltip Detallado
        )
        fig2.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        
        st.plotly_chart(fig2, use_container_width=True, config=config_espanol)
