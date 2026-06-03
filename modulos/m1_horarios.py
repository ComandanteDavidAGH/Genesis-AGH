import streamlit as st
import pandas as pd

def renderizar(conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🕒 Horarios y Asignaciones Académicas</h3>", unsafe_allow_html=True)
    
    # 🛡️ ESCUDO PROTECTOR SQL
    try:
        df_horarios = conn_sql.query("SELECT * FROM db_horarios;")
    except Exception:
        df_horarios = pd.DataFrame()
        
    if df_horarios is None or df_horarios.empty:
        st.warning("⚠️ **Base de datos de horarios no inicializada en Supabase.**")
        st.info("💡 *Nota de Rectoría:* Recuerde subir el archivo Excel de respaldo en la sección de 'Bitácora y Backup' para activar este módulo por primera vez.")
        return

    # Normalizamos los nombres de las columnas a mayúsculas para trabajar seguros
    df_horarios.columns = [str(c).upper().strip() for c in df_horarios.columns]
    
    # Identificar la columna de Grado de forma flexible
    col_grado = 'GRADO' if 'GRADO' in df_horarios.columns else None
    if not col_grado:
        for c in df_horarios.columns:
            if c in ['CURSO', 'NIVEL']:
                col_grado = c
                break
                
    if col_grado:
        lista_grados = sorted(df_horarios[col_grado].dropna().unique().astype(str).tolist())
        # 🎯 CONTROL CENTRALIZADO: Selector integrado en el flujo visual
        grado_horario = st.selectbox("🔍 Filtrar Cuadrante por Grado / Curso:", lista_grados)
        df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == grado_horario].copy()
    else:
        df_filtrado = df_horarios.copy()

    if df_filtrado.empty:
        st.info("No se encontraron registros de horarios para la selección actual.")
        return

    # 🔄 RECONSTRUCCIÓN DE LA MATRIZ TIPO CALENDARIO ESCOLAR
    try:
        columnas_clave = ['DÍA', 'BLOQUE_HORARIO', 'MATERIA', 'DOCENTE']
        if all(c in df_filtrado.columns for c in columnas_clave):
            
            # Formateamos el texto interno de cada bloque: "Materia - Profesor"
            df_filtrado['CELDA_INFO'] = df_filtrado['MATERIA'].astype(str) + " (" + df_filtrado['DOCENTE'].astype(str) + ")"
            
            # Limpieza de duplicados estructurales
            df_clean = df_filtrado.drop_duplicates(subset=['BLOQUE_HORARIO', 'DÍA'])
            
            # Pivotaje dinámico
            df_matriz = df_clean.pivot(index='BLOQUE_HORARIO', columns='DÍA', values='CELDA_INFO')
            
            # Ordenamiento estricto de Lunes a Viernes
            orden_dias_maestro = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", 
                                  "LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]
            columnas_ordenadas = [d for d in orden_dias_maestro if d in df_matriz.columns]
            for col in df_matriz.columns:
                if col not in columnas_ordenadas:
                    columnas_ordenadas.append(col)
            df_matriz = df_matriz.reindex(columns=columnas_ordenadas)
            
            # Mantener la secuencia de las horas del archivo original
            orden_horas = [h for h in df_filtrado['BLOQUE_HORARIO'].unique() if h in df_matriz.index]
            df_matriz = df_matriz.reindex(index=orden_horas)
            
            # Ajuste de cabeceras para presentación ejecutiva
            df_matriz = df_matriz.reset_index()
            df_matriz = df_matriz.rename(columns={'BLOQUE_HORARIO': 'HORARIO / JORNADA'})
            df_matriz = df_matriz.fillna("-")
            
            # 👑 RENDERIZADO PREMIUM CON ST.TABLE (Activa el CSS corporativo)
            st.markdown("<br><p style='font-weight:bold; color:#0d1b2a;'>📅 DISTRIBUCIÓN HORARIA SEMANAL INSTITUTIONAL</p>", unsafe_allow_html=True)
            st.table(df_matriz)
            
        else:
            st.table(df_filtrado)
    except Exception as e_pivot:
        st.table(df_filtrado)
