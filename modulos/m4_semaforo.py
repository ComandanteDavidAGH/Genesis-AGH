import streamlit as st
import pandas as pd
import unicodedata

def limpiar_caracteres(txt):
    """ Filtro extractor: Elimina tildes, espacios y estandariza a mayúsculas puras """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(*args, **kwargs):
    # 👑 MOTOR VISUAL EMULADOR: Réplica exacta de colores suaves y titileo total
    st.markdown("""
        <style>
            /* 🚨 ANIMACIONES DE PULSACIÓN DE LUMINISCENCIA (EFECTO TITILANTE) */
            @keyframes pulso_critico {
                0% { text-shadow: 0 0 5px rgba(204, 0, 0, 0.5); opacity: 1; transform: scale(1); }
                50% { text-shadow: 0 0 25px rgba(204, 0, 0, 0.95); opacity: 0.8; transform: scale(1.02); }
                100% { text-shadow: 0 0 5px rgba(204, 0, 0, 0.5); opacity: 1; transform: scale(1); }
            }
            @keyframes pulso_alerta {
                0% { text-shadow: 0 0 5px rgba(204, 136, 0, 0.5); opacity: 1; transform: scale(1); }
                50% { text-shadow: 0 0 25px rgba(204, 136, 0, 0.95); opacity: 0.8; transform: scale(1.02); }
                100% { text-shadow: 0 0 5px rgba(204, 136, 0, 0.5); opacity: 1; transform: scale(1); }
            }
            @keyframes pulso_optimo {
                0% { text-shadow: 0 0 5px rgba(0, 153, 76, 0.5); opacity: 1; transform: scale(1); }
                50% { text-shadow: 0 0 25px rgba(0, 153, 76, 0.95); opacity: 0.8; transform: scale(1.02); }
                100% { text-shadow: 0 0 5px rgba(0, 153, 76, 0.5); opacity: 1; transform: scale(1); }
            }
            
            /* ESTILOS DE LAS TARJETAS CON FONDO COMPLETO SUAVE Y BORDES GRUESOS */
            .card-critica-bella {
                background-color: #ffebeb !important;
                border: 4px solid #cc0000 !important;
                padding: 20px; border-radius: 14px; text-align: center; margin-bottom: 20px;
                box-shadow: 4px 4px 15px rgba(0,0,0,0.12), 5px 5px 0px #cc0000;
            }
            .card-alerta-bella {
                background-color: #fffef0 !important;
                border: 4px solid #cc8800 !important;
                padding: 20px; border-radius: 14px; text-align: center; margin-bottom: 20px;
                box-shadow: 4px 4px 15px rgba(0,0,0,0.12), 5px 5px 0px #cc8800;
            }
            .card-optima-bella {
                background-color: #e6f9f0 !important;
                border: 4px solid #00994c !important;
                padding: 20px; border-radius: 14px; text-align: center; margin-bottom: 20px;
                box-shadow: 4px 4px 15px rgba(0,0,0,0.12), 5px 5px 0px #00994c;
            }
            
            /* CONTROL INDIVIDUAL DEL TITILEO EN LOS NÚMEROS GIGANTES */
            .num-critico-titila {
                font-size: 80px; font-family: 'Arial Black', sans-serif; font-weight: 900; color: #cc0000;
                display: inline-block; animation: pulso_critico 1.3s infinite ease-in-out;
            }
            .num-alerta-titila {
                font-size: 80px; font-family: 'Arial Black', sans-serif; font-weight: 900; color: #cc8800;
                display: inline-block; animation: pulso_alerta 1.3s infinite ease-in-out;
            }
            .num-optimo-titila {
                font-size: 80px; font-family: 'Arial Black', sans-serif; font-weight: 900; color: #00994c;
                display: inline-block; animation: pulso_optimo 1.3s infinite ease-in-out;
            }
            
            .txt-titular { font-family: 'Arial Black', sans-serif; font-size: 16px; font-weight: bold; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico</h3>", unsafe_allow_html=True)
    
    # Desempaquetado inteligente de argumentos enviados desde app.py
    df_notas = None
    periodo_sel = None
    conn_sql = None

    if len(args) >= 1: df_notas = args[0] if isinstance(args[0], pd.DataFrame) else None
    if len(args) >= 2: periodo_sel = args[1] if isinstance(args[1], str) else None
    if len(args) >= 3: conn_sql = args[2]

    if (df_notas is None or df_notas.empty) and conn_sql is not None:
        try: df_notas = conn_sql.query("SELECT * FROM notas_consolidadas;")
        except Exception: pass

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ **Base de datos de calificaciones no disponible para el Semáforo.**")
        return

    # Clonación y estandarización de seguridad
    df_trabajo = df_notas.copy()
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]
    
    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    
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
        st.error("🚨 No se encontró una columna de notas procesable.")
        return

    df_trabajo[col_nota] = pd.to_numeric(df_trabajo[col_nota], errors='coerce').fillna(0.0)

    if col_grado:
        grados_validos = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
        grado_sel = st.selectbox("🔍 Seleccione el Grado para evaluar el Perímetro:", ["TODOS"] + grados_validos)
        if grado_sel != "TODOS":
            df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # ⚡ ESCUDO MATEMÁTICO ANTI-DUPLICADOS: Consolidamos el promedio único por alumno
    df_resumen_alumno = df_trabajo.groupby(col_nombre).agg({
        col_nota: 'mean',
        col_grado: 'first'
    }).reset_index()

    # Clasificación real (La suma de los tres dará exactamente el número de alumnos reales)
    criticos = df_resumen_alumno[df_resumen_alumno[col_nota] < 6.0]
    alertas = df_resumen_alumno[(df_resumen_alumno[col_nota] >= 6.0) & (df_resumen_alumno[col_nota] <= 7.5)]
    optimos = df_resumen_alumno[df_resumen_alumno[col_nota] > 7.5]

    count_criticos = len(criticos)
    count_alertas = len(alertas)
    count_optimos = len(optimos)

    # 📅 CONSTRUCCIÓN DE LOS CONTENEDORES CON RENDER NATIVO HTML
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.html(f"""
            <div class='card-critica-bella'>
                <div class='txt-titular' style='color:#cc0000;'>🔴 Riesgo Crítico (&lt; 6.0)</div>
                <div class='num-critico-titila'>{count_criticos}</div>
            </div>
        """)
        
    with c2:
        st.html(f"""
            <div class='card-alerta-bella'>
                <div class='txt-titular' style='color:#cc8800;'>🟡 Alerta (6.0 - 7.5)</div>
                <div class='num-alerta-titila'>{count_alertas}</div>
            </div>
        """)
        
    with c3:
        st.html(f"""
            <div class='card-optima-bella'>
                <div class='txt-titular' style='color:#00994c;'>🟢 Óptimo (&gt;= 7.6)</div>
                <div class='num-optimo-titila'>{count_optimos}</div>
            </div>
        """)

    st.markdown("<br><div style='background-color:#ffe6e6; border:3px solid #cc0000; padding:12px; border-radius:8px; text-align:center; font-family:Arial Black; color:#cc0000; font-size:14px; letter-spacing:1px;'>🚨 LISTADO DE ESTUDIANTES EN RIESGO CRÍTICO (PROMEDIO GENERAL REAL)</div><br>", unsafe_allow_html=True)
    
    if not criticos.empty:
        df_mostrar = criticos[[col_nombre, col_grado, col_nota]].sort_values(by=col_nota)
        df_mostrar[col_nota] = df_mostrar[col_nota].round(2)
        df_mostrar.columns = ['Nombre Completo', 'Grado', 'Promedio General']
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Perímetro estable: Cero estudiantes detectados en Riesgo Crítico.")
