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
    
    if col_n not in df.columns:
        st.error(f"La columna '{col_n}' no existe en la base de datos actual.")
        return

    # 🛑 CONTROL ULTRA-ESTRICTO DE ERRORES DE USUARIO
    # Intentamos convertir a número, si hay letras 'coerce' las volverá NaN temporalmente
    notas_convertidas = pd.to_numeric(df[col_n], errors='coerce')
    
    # Buscamos si el DataFrame original tenía datos que NO eran números ni estaban vacíos originalmente
    # Esto detecta letras, guiones, espacios raros, etc.
    filas_con_error = df[notas_convertidas.isna() & df[col_n].notna() & (df[col_n].astype(str).str.strip() != "")]

    if not filas_con_error.empty:
        st.error(f"🚨 **¡Error crítico en la base de datos!** Se detectaron caracteres no numéricos (letras o símbolos) en la columna de calificaciones de **{periodo_sel}**.")
        
        # Le mostramos al usuario exactamente dónde está el error para que lo solucione
        with st.expander("🔍 Ver registros afectados que debes corregir:", expanded=True):
            # Mostramos las columnas clave para que el usuario localice la falla rápido
            columnas_clave = [c for c in ['Estudiante', 'Grado', 'Materia', col_n] if c in df.columns]
            st.dataframe(filas_con_error[columnas_clave])
        
        st.info("💡 *Por favor, corrige el archivo de origen (elimina las letras o espacios en blanco de las notas) y vuelve a cargarlo.*")
        return  # ✋ Detiene por completo la ejecución de los gráficos

    # Si pasa la validación estricta, limpiamos los nulos legítimos (alumnos sin nota aún)
    df_seguro = df.dropna(subset=[col_n]).copy()
    df_seguro[col_n] = df_seguro[col_n].astype(float)

    if df_seguro.empty:
        st.info("No hay calificaciones registradas para generar los gráficos en este periodo.")
        return

    # --- CONFIGURACIÓN Y RENDERIZADO DE GRÁFICOS (Se ejecuta solo si todo está limpio) ---
    config_espanol = {'locale': 'es', 'displaylogo': False}
    c1, c2 = st.columns(2)
    
    with c1: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Rendimiento por Materia ({periodo_sel})</div>", unsafe_allow_html=True)
        
        df_promedios = df_seguro.groupby('Materia')[col_n].mean().reset_index().sort_values(by=col_n, ascending=True) 
        fig1 = px.bar(df_promedios, x=col_n, y='Materia', text_auto='.1f', color='Materia', orientation='h')
        
        fig1.update_traces(marker=dict(line=dict(color='#000000', width=1.5)), opacity=0.9)
        fig1.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        fig1.update_yaxes(title_text="", visible=True, tickmode='linear', dtick=1, tickfont=dict(size=13, color='#000000', family="Arial Black"), automargin=True) 
        fig1.update_xaxes(title_text="Promedio", title_font=dict(color="#000", family="Arial Black"), tickfont=dict(color="#000", family="Arial Black"))
        
        st.plotly_chart(fig1, use_container_width=True, config=config_espanol)
    
    with c2: 
        st.markdown(f"<div style='background:#000000; color:white; padding:10px; border-radius:5px; text-align:center; font-family:Arial Black; font-weight:bold; margin-bottom:15px; border:2px solid #d4af37;'>Distribución de Niveles ({periodo_sel})</div>", unsafe_allow_html=True)
        
        limites = [-1, 6.0, 7.6, 9.1, 100.0]
        etiquetas = ['BAJO', 'BÁSICO', 'ALTO', 'SUPERIOR']
        
        df_pie = df_seguro.copy()
        df_pie['DESEMPEÑO_FILTRO'] = pd.cut(df_pie[col_n], bins=limites, labels=etiquetas, right=False)
        colores_vivos = {'BAJO': '#e63946', 'BÁSICO': '#f4a261', 'ALTO': '#2a9d8f', 'SUPERIOR': '#1d3557'}
        
        fig2 = px.pie(df_pie, names='DESEMPEÑO_FILTRO', hole=0.45, color='DESEMPEÑO_FILTRO', color_discrete_map=colores_vivos)
        
        fig2.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color="#000000", family="Arial Black", size=13), pull=[0.02]*4, marker=dict(line=dict(color='#000000', width=1.5)), opacity=0.95)
        fig2.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        
        st.plotly_chart(fig2, use_container_width=True, config=config_espanol)
