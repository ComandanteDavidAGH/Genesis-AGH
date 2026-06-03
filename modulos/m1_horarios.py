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
        st.info("💡 *Nota de Rectoría:* Recuerde subir el archivo Excel de respaldo en la sección de 'Bitácora y Backup' para activar este módulo.")
        return

    st.success("📡 Conexión con el cuadrante de horarios activa.")
    
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
        grado_horario = st.selectbox("🔍 Seleccione el Grado para visualizar el horario:", lista_grados)
        df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == grado_horario].copy()
    else:
        df_filtrado = df_horarios.copy()

    if df_filtrado.empty:
        st.info("No se encontraron registros de horarios para la selección actual.")
        return

    # 🔄 LA MAGIA MATRICIAL: Convertir lista plana a Cuadrícula de Horario (Como antes)
    try:
        columnas_clave = ['DÍA', 'BLOQUE_HORARIO', 'MATERIA', 'DOCENTE']
        if all(c in df_filtrado.columns for c in columnas_clave):
            
            # Formateamos el texto interno de cada celda: "Materia \n(Docente)"
            df_filtrado['CELDA_INFO'] = df_filtrado['MATERIA'].astype(str) + " \n(" + df_filtrado['DOCENTE'].astype(str) + ")"
            
            # Removemos duplicados accidentales de tiempo/día antes de pivotar
            df_clean = df_filtrado.drop_duplicates(subset=['BLOQUE_HORARIO', 'DÍA'])
            
            # Pivotamos la estructura: Filas = Horas, Columnas = Días, Valores = Contenido combinando Materia y Docente
            df_matriz = df_clean.pivot(index='BLOQUE_HORARIO', columns='DÍA', values='CELDA_INFO')
            
            # Ordenamos las columnas de forma lógica siguiendo los días de la semana
            orden_dias_maestro = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", 
                                  "LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
            columnas_ordenadas = [d for d in orden_dias_maestro if d in df_matriz.columns]
            for col in df_matriz.columns:
                if col not in columnas_ordenadas:
                    columnas_ordenadas.append(col)
            df_matriz = df_matriz.reindex(columns=columnas_ordenadas)
            
            # Mantenemos el orden de las horas tal y como vienen organizadas cronológicamente en el Excel
            orden_horas = [h for h in df_filtrado['BLOQUE_HORARIO'].unique() if h in df_matriz.index]
            df_matriz = df_matriz.reindex(index=orden_horas)
            
            # Convertimos las filas de horas en una columna limpia visible y rellenamos espacios vacíos
            df_matriz = df_matriz.reset_index()
            df_matriz = df_matriz.rename(columns={'BLOQUE_HORARIO': 'BLOQUE HORARIO / JORNADA'})
            df_matriz = df_matriz.fillna("-")
            
            # Renderizado final del Cuadrante Estructural
            st.markdown("#### 📅 Distribución Horaria Semanal")
            st.dataframe(df_matriz, use_container_width=True, hide_index=True)
            
            # Pestaña de respaldo por si el usuario desea auditar el listado plano original
            with st.expander("📋 Ver registros en formato de lista plana (Auditoría)"):
                st.dataframe(df_filtrado[['DÍA', 'BLOQUE_HORARIO', 'MATERIA', 'DOCENTE']], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    except Exception as e_pivot:
        st.info(f"💡 Mostrando formato de lista optimizado: {e_pivot}")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
