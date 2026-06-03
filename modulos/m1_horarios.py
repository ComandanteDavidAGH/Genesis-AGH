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
        
        df_ejemplo = pd.DataFrame(
            columns=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
            index=["07:00 AM - 08:00 AM", "08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM", "10:00 AM - 10:30 AM (RECREO)", "10:30 AM - 11:30 AM", "11:30 AM - 12:30 PM"]
        )
        st.dataframe(df_ejemplo, use_container_width=True)
        return

    st.success("📡 Conexión con el cuadrante de horarios activa.")
    
    # Buscador flexible de la columna de Grado (por si viene en mayúscula o minúscula)
    col_grado = None
    for c in df_horarios.columns:
        if str(c).upper() in ['GRADO', 'CURSO', 'NIVEL']:
            col_grado = c
            break
            
    if col_grado:
        lista_grados = sorted(df_horarios[col_grado].dropna().unique().astype(str).tolist())
        if lista_grados:
            grado_horario = st.selectbox("🔍 Seleccione el Grado para visualizar el horario:", lista_grados)
            df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == grado_horario]
            # 🔄 CORRECCIÓN DE INTERFAZ: Cambiamos index=False por hide_index=True
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_horarios, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_horarios, use_container_width=True, hide_index=True)
