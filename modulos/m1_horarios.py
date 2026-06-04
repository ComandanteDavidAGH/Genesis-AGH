import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# =========================================================
# ⚡ ACELERADOR DE MEMORIA (Descarga SQL de un solo viaje)
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def obtener_horarios_sql(_conn_sql):
    """
    Descarga la tabla de horarios de Supabase una sola vez y la mantiene 
    en memoria RAM durante 10 minutos (600 seg) o hasta que se fuerce el borrado.
    """
    try:
        return _conn_sql.query("SELECT * FROM db_horarios;")
    except Exception as e:
        return None

def limpiar_caracteres(txt):
    """ Filtro extractor: Elimina tildes, espacios y estandariza a mayúsculas puras """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

# =========================================================
# 👑 MOTOR PRINCIPAL DE RENDERIZADO
# =========================================================
def renderizar(conn_sql):
    # 👑 INYECTOR DE ESTILEMA 3D Y ANIMACIONES PARA TABLA Y GRÁFICOS
    st.markdown("""
        <style>
            /* Efecto 3D de los gráficos Plotly */
            div[data-testid="stPlotlyChart"] {
                background-color: #ffffff !important;
                padding: 18px !important;
                border-radius: 14px !important;
                border: 3px solid #0d1b2a !important;
                box-shadow: 7px 7px 0px #0d1b2a, 12px 12px 25px rgba(0,0,0,0.15) !important;
                margin-top: 15px !important;
                margin-bottom: 30px !important;
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            div[data-testid="stPlotlyChart"]:hover {
                transform: translateY(-5px);
                box-shadow: 9px 9px 0px #d4af37, 15px 15px 30px rgba(0,0,0,0.2) !important;
            }
            
            /* 🚀 SUPER-ESTILOS PARA LA MATRIZ DE HORARIOS */
            .tabla-horario { width:100%; border-collapse:collapse; margin-top:20px; font-family:'Arial', sans-serif; box-shadow:0px 10px 25px rgba(0,0,0,0.1); border:3px solid #0d1b2a; border-radius:10px; overflow:hidden; }
            .tabla-horario thead tr { background-color:#0d1b2a; color:white; text-align:center; border-bottom:4px solid #d4af37; }
            .tabla-horario th { padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; }
            .tabla-horario td { padding:12px; border:1px solid #e0e0e0; text-align:center; vertical-align:middle; transition: all 0.3s ease; }
            
            /* Clases interactivas para las celdas */
            .celda-clase { background-color:#ffffff; position: relative; }
            .celda-clase:hover { 
                background-color:#f8f9fa; 
                transform: scale(1.05); 
                box-shadow: 0 8px 20px rgba(212, 175, 55, 0.4); 
                border: 2px solid #d4af37; 
                z-index: 100; 
                border-radius: 6px;
            }
            .celda-vacia { background-color:#fdfdfd; color:#b0b0b0; font-weight:bold; }
            .col-bloque { font-weight:bold; color:#0d1b2a; background-color:#f0f2f6; font-size:12px; font-family:'Arial Black'; border:1px solid #0d1b2a !important; }
            
            /* Animación de pulsación para el descanso */
            .celda-descanso { background-color:#fff4e6; font-family:'Arial Black'; color:#cc8800; font-size:13px; letter-spacing:5px; text-transform:uppercase; font-weight:900; animation: pulse 2s infinite; border:1px solid #0d1b2a !important; }
            @keyframes pulse { 
                0% { opacity: 0.85; } 
                50% { opacity: 1; text-shadow: 0 0 10px rgba(204,136,0,0.7); } 
                100% { opacity: 0.85; } 
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🕒 Horarios y Asignaciones Académicas</h3>", unsafe_allow_html=True)
    
    # 🛡️ EXTRACCIÓN DESDE LA CACHÉ
    df_horarios = obtener_horarios_sql(conn_sql)
        
    if df_horarios is None or df_horarios.empty:
        st.warning("⚠️ **Base de datos de horarios no inicializada en Supabase o error de conexión.**")
        st.info("💡 *Nota de Rectoría:* Recuerde subir el archivo Excel de respaldo en la sección de 'Bitácora y Backup'.")
        return

    df_horarios.columns = df_horarios.columns.str.upper().str.strip()
    
    col_dia = df_horarios.columns[0]      # DÍA
    col_bloque = df_horarios.columns[1]   # BLOQUE_HORARIO
    col_grado = df_horarios.columns[2]    # GRADO
    col_materia = df_horarios.columns[3]  # MATERIA
    col_docente = df_horarios.columns[4]  # DOCENTE

    # 🎯 CONTROLADOR DUAL: Alternar vistas
    tipo_filtro = st.radio("🛠️ **Seleccione la Modalidad de Consulta:**", ["🔍 Ver por Curso / Grado", "👤 Ver por Docente / Profesor"], horizontal=True)
    
    col_selector, col_vacio = st.columns([4, 6])
    with col_selector:
        if tipo_filtro == "🔍 Ver por Curso / Grado":
            lista_opciones = sorted(df_horarios[col_grado].dropna().unique().astype(str).tolist())
            seleccion = st.selectbox("🎯 Seleccione el Grado:", lista_opciones)
            df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == seleccion].copy()
            modo_docente = False
        else:
            lista_opciones = sorted(df_horarios[col_docente].dropna().unique().astype(str).tolist())
            seleccion = st.selectbox("🎯 Seleccione el Docente:", lista_opciones)
            df_filtrado = df_horarios[df_horarios[col_docente].astype(str) == seleccion].copy()
            modo_docente = True

    if df_filtrado.empty:
        st.info("No se encontraron registros de horarios para la selección actual.")
        return

    df_filtrado['DIA_CLEAN'] = df_filtrado[col_dia].apply(limpiar_caracteres)
    df_filtrado['BLOQUE_CLEAN'] = df_filtrado[col_bloque].astype(str).str.strip()

    dias_secuencia = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"]
    bloques_ordenados = [str(b).strip() for b in list(df_horarios[col_bloque].dropna().unique())]

    # 🚀 MAPEO EN O(1)
    mapa_horario = {}
    for _, fila in df_filtrado.iterrows():
        llave = (fila['BLOQUE_CLEAN'], fila['DIA_CLEAN'])
        mapa_horario[llave] = fila

    # 👑 CONSTRUCCIÓN DE LA TABLA BELLA INTEGRADA CON CLASES CSS
    html_lineas = [
        '<table class="tabla-horario">'
        '<thead>'
        '<tr>'
        '<th style="width:18%;">HORARIO / JORNADA</th>'
        '<th style="width:16.4%;">LUNES</th>'
        '<th style="width:16.4%;">MARTES</th>'
        '<th style="width:16.4%;">MIÉRCOLES</th>'
        '<th style="width:16.4%;">JUEVES</th>'
        '<th style="width:16.4%;">VIERNES</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
    ]

    for bloque in bloques_ordenados:
        es_recreo = "DESCANSO" in bloque.upper() or "RECREO" in bloque.upper()
        
        if es_recreo:
            html_lineas.append(
                f'<tr style="background-color:#fff4e6; text-align:center;">'
                f'<td class="col-bloque">{bloque}</td>'
                f'<td colspan="5" class="celda-descanso">☕ ✨ D E S C A N S O ✨ ☕</td>'
                f'</tr>'
            )
        else:
            html_lineas.append('<tr style="text-align:center; background-color:#ffffff;">')
            html_lineas.append(f'<td class="col-bloque">{bloque}</td>')
            
            for dia in dias_secuencia:
                celda = mapa_horario.get((bloque, dia))
                
                if celda is not None:
                    materia = str(celda[col_materia]).strip()
                    docente = str(celda[col_docente]).strip()
                    grado = str(celda[col_grado]).strip()
                    
                    sub_texto = f"🏫 Grado: {grado}" if modo_docente else f"👤 {docente}"
                    
                    # Se inyecta la clase interactiva "celda-clase"
                    html_lineas.append(
                        f'<td class="celda-clase">'
                        f'<div style="color:#000000; font-weight:900; font-size:13px; font-family:\'Arial\', sans-serif; line-height:1.2;">{materia}</div>'
                        f'<div style="color:#cc8800; font-size:11px; font-weight:bold; margin-top:5px; font-family:\'Arial\';">{sub_texto}</div>'
                        f'</td>'
                    )
                else:
                    html_lineas.append('<td class="celda-vacia">-</td>')
            html_lineas.append('</tr>')

    html_lineas.append('</tbody></table><br>')
    
    st.markdown("".join(html_lineas), unsafe_allow_html=True)

    # 📊 ANALÍTICA DE CARGA ACADÉMICA
    st.markdown("---")
    st.markdown("<h4 style='color:#0d1b2a; font-family:Arial Black;'>📊 Análisis Estadístico de Carga Laboral Docente</h4>", unsafe_allow_html=True)
    
    df_carga = df_horarios[
        (~df_horarios[col_materia].astype(str).str.upper().str.strip().isin(['DESCANSO', 'RECREO', '-', ''])) & 
        (~df_horarios[col_bloque].astype(str).str.upper().str.strip().str.contains('DESCANSO|RECREO'))
    ].copy()
    
    if not df_carga.empty:
        carga_docentes = df_carga[col_docente].value_counts().reset_index()
        carga_docentes.columns = ['Docente', 'Bloques Asignados']
        carga_docentes = carga_docentes.sort_values(by='Bloques Asignados', ascending=False)
        
        altura_dinamica = max(350, len(carga_docentes) * 35)
        
        # ⚡ GRÁFICO MEJORADO: Mapa de Color según Carga Laboral
        fig = px.bar(
            carga_docentes, 
            x='Bloques Asignados', 
            y='Docente', 
            orientation='h',
            color='Bloques Asignados', # Activamos el gradiente
            color_continuous_scale=['#d4af37', '#0d1b2a'], # Dorado a Azul Noche
            title='Distribución de Intensidad Horaria Semanal por Profesor',
            labels={'Bloques Asignados': 'Horas / Bloques Semanales', 'Docente': 'Profesor'},
            text='Bloques Asignados'
        )
        
        fig.update_layout(
            font_family="Arial",
            title_font_family="Arial Black",
            title_font_color="#0d1b2a",
            xaxis=dict(tickmode='linear', dtick=2, gridcolor='#e0e0e0'),
            yaxis=dict(gridcolor='rgba(0,0,0,0)', autorange="reversed"), 
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=150, r=50, t=50, b=50),
            height=altura_dinamica,
            coloraxis_showscale=False # Oculta la barra lateral de color para mantenerlo limpio
        )
        
        fig.update_traces(
            marker_line_color='#000000',
            marker_line_width=1.5,
            opacity=0.95,
            textposition='outside',
            textfont=dict(family="Arial Black", size=12, color="#0d1b2a"),
            hovertemplate="<b>%{y}</b><br>Asignaciones: %{x}<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos de asignaciones para estructurar el gráfico de análisis.")
