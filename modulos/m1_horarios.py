import streamlit as st
import pandas as pd
import plotly.express as px
import re

def renderizar(conn):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🕒 Matriz de Horarios Oficiales</h3>", unsafe_allow_html=True)
    
    with st.spinner("📡 Sincronizando reloj satelital con DB_HORARIOS..."):
        try:
            df_horarios = conn.read(worksheet="DB_HORARIOS", ttl=0)
            df_horarios = df_horarios.dropna(subset=['DÍA', 'BLOQUE_HORARIO'])
        except Exception as e:
            st.error("🚨 Falla Crítica: No se encontró la pestaña 'DB_HORARIOS' en la base satelital.")
            st.stop()
    
    if df_horarios.empty:
        st.warning("⚠️ La base de horarios está vacía. Ingrese los datos en Google Sheets.")
        st.stop()
        
    df_horarios = df_horarios.fillna("")
    for col in df_horarios.columns:
        df_horarios[col] = df_horarios[col].astype(str).str.strip()
        
    if st.session_state.rol == "Admin":
        st.info("👑 Modo Comandante: Tiene autorización para auditar la matriz completa.")
        tipo_vista = st.radio("Seleccione el Modo de Radar:", ["🧑‍🏫 Vista por Docente", "🎓 Vista por Grado"], horizontal=True)
        
        if tipo_vista == "🧑‍🏫 Vista por Docente":
            docentes_lista = sorted([str(d) for d in df_horarios['DOCENTE'].unique() if str(d).upper() not in ['N/A', 'NAN', '']])
            objetivo = st.selectbox("🔍 Seleccione el Docente a Inspeccionar:", docentes_lista)
            df_filtro = df_horarios[df_horarios['DOCENTE'] == objetivo].copy()
            df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#666; font-size:12px;'>(" + df_filtro['GRADO'] + ")</span>"
        else:
            grados_lista = sorted([str(g) for g in df_horarios['GRADO'].unique() if str(g).upper() not in ['N/A', 'NAN', '']])
            objetivo = st.selectbox("🔍 Seleccione el Grado a Inspeccionar:", grados_lista)
            df_filtro = df_horarios[df_horarios['GRADO'] == objetivo].copy()
            df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#0d1b2a; font-size:11px;'>[" + df_filtro['DOCENTE'] + "]</span>"
    else:
        st.info(f"👨‍🏫 Modo Docente: Mostrando carga académica oficial asignada a **{st.session_state.nombre_completo_usuario}**.")
        df_filtro = df_horarios[df_horarios['DOCENTE'].str.upper() == st.session_state.nombre_completo_usuario.upper()].copy()
        df_filtro['CELDA'] = df_filtro['MATERIA'] + "<br><span style='color:#666; font-size:12px;'>(" + df_filtro['GRADO'] + ")</span>"
        
        if df_filtro.empty:
            st.warning("Usted no tiene horas asignadas en el sistema en este momento.")
            st.stop()
            
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    df_filtro['DÍA'] = pd.Categorical(df_filtro['DÍA'].str.capitalize(), categories=dias_orden, ordered=True)
    
    matriz = df_filtro.pivot_table(
        index='BLOQUE_HORARIO', 
        columns='DÍA', 
        values='CELDA', 
        aggfunc=lambda x: '<hr style="margin:5px 0;">'.join(x.astype(str))
    ).fillna("")
    
    def extraer_hora(bloque_str):
        match = re.search(r'\((\d{2}:\d{2})', str(bloque_str))
        return match.group(1) if match else str(bloque_str)
        
    matriz['sort_key'] = matriz.index.map(extraer_hora)
    matriz = matriz.sort_values('sort_key').drop(columns=['sort_key'])
    
    html_tabla = "<table style='width:100%; border-collapse: collapse; text-align:center; border:3px solid #0d1b2a; margin-top:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);'>"
    html_tabla += "<tr style='background-color:#0d1b2a; color:#d4af37;'><th style='padding:12px; border:1px solid #d4af37; width:15%; font-family:Arial Black;'>HORARIO</th>"
    
    for d in dias_orden:
        if d in matriz.columns:
            html_tabla += f"<th style='padding:12px; border:1px solid #d4af37; font-family:Arial Black;'>{d.upper()}</th>"
    html_tabla += "</tr>"
    
    for bloque, row in matriz.iterrows():
        if "DESCANSO" in bloque.upper():
            html_tabla += f"<tr style='background-color:#f0f2f6;'><td style='padding:10px; font-weight:bold; border:1px solid #ccc; color:#0d1b2a;'>{bloque}</td>"
            for d in dias_orden:
                if d in matriz.columns:
                    html_tabla += f"<td style='padding:10px; color:#888; font-style:italic; border:1px solid #ccc; font-weight:bold;'>🥪 RECESO</td>"
            html_tabla += "</tr>"
        else:
            html_tabla += f"<tr><td style='padding:10px; font-weight:bold; background-color:#fafafa; border:1px solid #ccc; color:#0d1b2a;'>{bloque}</td>"
            for d in dias_orden:
                if d in matriz.columns:
                    val = row[d]
                    if val == "":
                        html_tabla += f"<td style='padding:10px; background-color:white; border:1px solid #ccc;'></td>"
                    else:
                        if "<hr" in val:
                            bg_color = "#ffe6e6"
                            borde_fuerte = "border:2px solid #cc0000;"
                        else:
                            bg_color = "#e6ffe6" if st.session_state.rol != "Admin" or (st.session_state.rol == "Admin" and tipo_vista == "🧑‍🏫 Vista por Docente") else "#e6f2ff"
                            borde_fuerte = "border:1px solid #ccc;"
                            
                        html_tabla += f"<td style='padding:10px; background-color:{bg_color}; {borde_fuerte} font-weight:bold; color:#000;'>{val}</td>"
            html_tabla += "</tr>"
    html_tabla += "</table>"
    
    st.markdown(html_tabla, unsafe_allow_html=True)
    
    if "<hr" in html_tabla:
        st.error("🚨 ALERTA DE COLISIÓN: Se han detectado bloques marcados en ROJO. Esto significa que hay dos asignaciones cruzadas en la misma hora. Corríjalo en Google Sheets.")
    
    if st.session_state.rol == "Admin":
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 📊 Carga Académica de la Tropa (Horas Semanales por Docente)")
        
        df_carga = df_horarios[(df_horarios['DOCENTE'] != 'N/A') & (~df_horarios['MATERIA'].str.contains('DESCANSO', case=False, na=False))]
        conteo = df_carga['DOCENTE'].value_counts().reset_index()
        conteo.columns = ['Docente', 'Horas Asignadas']
        
        fig_carga = px.bar(conteo, x='Horas Asignadas', y='Docente', orientation='h', text='Horas Asignadas', color='Horas Asignadas', color_continuous_scale='Blues')
        fig_carga.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            xaxis_title="Total Horas a la Semana", 
            yaxis_title="", 
            margin=dict(l=0, r=0, t=0, b=0), 
            height=300,
            font=dict(color="black", family="Arial Black")
        )
        fig_carga.update_traces(
            textfont=dict(color="black", size=14, family="Arial Black"), 
            textangle=0, 
            textposition="outside", 
            cliponaxis=False
        )
        fig_carga.update_yaxes(tickfont=dict(color="black", family="Arial Black"))
        fig_carga.update_xaxes(tickfont=dict(color="black", family="Arial Black"), title_font=dict(color="black", family="Arial Black"))
        
        st.plotly_chart(fig_carga, use_container_width=True)
