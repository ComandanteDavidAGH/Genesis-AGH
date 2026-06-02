import streamlit as st
import pandas as pd

def renderizar(df, curso_sel, periodo_sel):
    st.markdown(f"<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico - Grado {curso_sel} ({periodo_sel})</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No hay datos para mostrar.")
        return
        
    col_n = periodo_sel if periodo_sel != "CONSOLIDADO FINAL" else "PROMEDIO"
    
    if col_n not in df.columns:
        st.warning(f"No se encontró la columna {col_n}.")
        return

    df_estudiantes = df.groupby(['Nombre_Completo', 'Grado'])[col_n].mean().reset_index()
    
    def color_semaforo(nota):
        if nota < 6.0: return '🔴 CRÍTICO'
        elif nota < 7.6: return '🟡 ALERTA'
        else: return '🟢 ÓPTIMO'
        
    df_estudiantes['ESTADO'] = df_estudiantes[col_n].apply(color_semaforo)
    df_estudiantes = df_estudiantes.sort_values(by=col_n, ascending=True)
    
    criticos = df_estudiantes[df_estudiantes['ESTADO'] == '🔴 CRÍTICO']
    alertas = df_estudiantes[df_estudiantes['ESTADO'] == '🟡 ALERTA']
    optimos = df_estudiantes[df_estudiantes['ESTADO'] == '🟢 ÓPTIMO']
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='tarjeta-roja'><h4 style='margin:0; color:#cc0000; font-family:Arial Black;'>🔴 Riesgo Crítico (< 6.0)</h4><h1 style='margin:0; color:#cc0000; font-family:Arial Black;'>{len(criticos)}</h1></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='tarjeta-naranja'><h4 style='margin:0; color:#cc8800; font-family:Arial Black;'>🟡 Alerta (6.0 - 7.5)</h4><h1 style='margin:0; color:#cc8800; font-family:Arial Black;'>{len(alertas)}</h1></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='tarjeta-verde'><h4 style='margin:0; color:#00994c; font-family:Arial Black;'>🟢 Óptimo (>= 7.6)</h4><h1 style='margin:0; color:#00994c; font-family:Arial Black;'>{len(optimos)}</h1></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if not criticos.empty:
        st.error("🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO")
        st.dataframe(criticos[['Nombre_Completo', 'Grado', col_n]].rename(columns={col_n: 'PROMEDIO'}).style.format({'PROMEDIO': '{:.1f}'}), use_container_width=True, hide_index=True)
