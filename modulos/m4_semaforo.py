import streamlit as st
import pandas as pd
import unicodedata

def limpiar_caracteres(txt):
    """ Filtro extractor: Elimina tildes, espacios y estandariza a mayúsculas puras """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 👑 INYECTOR DE ANIMACIÓN TITILANTE Y PANELES 3D EXECUTIVE
    st.markdown("""
        <style>
            /* 🚨 ANIMACIÓN MAESTRA DE PARPADEO (EFECTO TITILANTE) */
            @keyframes titilar_critico {
                0% { opacity: 1; transform: scale(1); text-shadow: 0 0 15px rgba(204, 0, 0, 0.7); }
                50% { opacity: 0.15; transform: scale(1.03); text-shadow: 0 0 0px rgba(204, 0, 0, 0); }
                100% { opacity: 1; transform: scale(1); text-shadow: 0 0 15px rgba(204, 0, 0, 0.7); }
            }
            
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
                animation: titilar_critico 1.2s infinite ease-in-out;
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
                padding: 20px;
                border-radius: 14px;
                border: 3px solid #0d1b2a;
                box-shadow: 7px 7px 0px #0d1b2a, 10px 10px 20px rgba(0,0,0,0.1) !important;
                text-align: center;
                margin-bottom: 20px;
                transition: transform 0.2s ease;
            }
            .card-semaforo-3d:hover {
                transform: translate(-2px, -2px);
                box-shadow: 9px 9px 0px #d4af37, 12px 12px 25px rgba(0,0,0,0.15) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico</h3>", unsafe_allow_html=True)
    
    # Desempaquetado inteligente de argumentos enviados desde app.py
    df_notas = None
    periodo_sel = None
    conn_sql = None

    if len(args) >= 1:
        df_notas = args[0] if isinstance(args[0], pd.DataFrame) else None
    if len(args) >= 2:
        periodo_sel = args[1] if isinstance(args[1], str) else None
    if len(args) >= 3:
        conn_sql = args[2]

    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try:
            df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception:
            pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible para el Semáforo.**")
        return

    # Clonamos la información para procesar de forma segura
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]
    
    # Mapeo de columnas críticas
    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    
    # Determinar qué columna de notas evaluar
    col_nota = None
    if periodo_sel:
        p_norm = str(periodo_sel).upper().strip()
        col_nota = next((c for c in df_trabajo.columns if c == p_norm), None)
        
    if not col_nota:
        col_nota = next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'PROMEDIO_FINAL', 'DEF', 'NOTA']), None)

    if not col_nota:
        for c in df_trabajo.columns:
            if c not in [col_nombre, col_grado, 'ID', 'USUARIO']:
                col_nota = c
                break

    if not col_nota:
        st.error("🚨 No se encontró una columna de notas procesable para el Semáforo.")
        return

    # Forzar formato numérico
    df_trabajo[col_nota] = pd.to_numeric(df_trabajo[col_nota], errors='coerce').fillna(0.0)

    # Filtro de Grados
    if col_grado:
        grados_validos = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
        grado_sel = st.selectbox("🔍 Seleccione el Grado para evaluar el Perímetro:", ["TODOS"] + grados_validos)
        if grado_sel != "TODOS":
            df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # ⚡ EL MOTOR CONSOLIDADOR CORRECCIONAL (Agrupar por alumno antes de medir los rangos) ⚡
    df_resumen_alumno = df_trabajo.groupby(col_nombre).agg({
        col_nota: 'mean',                      # Saca el promedio real definitivo del estudiante
        col_grado: 'first'                     # Mantiene el registro de su grado correspondiente
    }).reset_index()

    # Clasificación exacta basada en 1 Fila por Alumno (Suma total = 750)
    criticos = df_resumen_alumno[df_resumen_alumno[col_nota] < 6.0]
    alertas = df_resumen_alumno[(df_resumen_alumno[col_nota] >= 6.0) & (df_resumen_alumno[col_nota] <= 7.5)]
    optimos = df_resumen_alumno[df_resumen_alumno[col_nota] > 7.5]

    count_criticos = len(criticos)
    count_alertas = len(alertas)
    count_optimos = len(optimos)

    # 📅 DESPLIEGUE EN COLUMNAS CON EL VERDADERO EFECTO 3D ISOMÉTRICO
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

    # 🚨 LISTADO DIRECTIVO DE ALUMNOS EN RIESGO CRÍTICO REAL
    st.markdown("<br><div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:12px; border-radius:8px; text-align:center; font-family:Arial Black; color:#cc0000; font-size:14px; letter-spacing:1px;'>🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO (PROMEDIO GENERAL)</div><br>", unsafe_allow_html=True)
    
    if not criticos.empty:
        df_mostrar = criticos[[col_nombre, col_grado, col_nota]].sort_values(by=col_nota)
        df_mostrar[col_nota] = df_mostrar[col_nota].round(2)
        df_mostrar.columns = ['Nombre Completo', 'Grado', 'Promedio General']
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Perímetro estable: Cero estudiantes detectados en Riesgo Crítico.")
