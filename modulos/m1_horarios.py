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
        st.info("💡 *Nota de Rectoría:* Recuerde subir el archivo Excel de respaldo en la sección de 'Bitácora y Backup'.")
        return

    # Normalizar nombres de columnas a mayúsculas para evitar conflictos de lectura
    df_horarios.columns = [str(c).upper().strip() for c in df_horarios.columns]
    
    # Mapeo inteligente de columnas
    col_grado = next((c for c in df_horarios.columns if c in ['GRADO', 'CURSO', 'NIVEL']), None)
    col_dia = next((c for c in df_horarios.columns if c in ['DÍA', 'DIA']), None)
    col_bloque = next((c for c in df_horarios.columns if c in ['BLOQUE_HORARIO', 'BLOQUE', 'HORA', 'HORARIO', 'BLOQUE HORARIO / JORNADA']), None)
    col_materia = next((c for c in df_horarios.columns if c in ['MATERIA', 'ASIGNATURA']), None)
    col_docente = next((c for c in df_horarios.columns if c in ['DOCENTE', 'PROFESOR']), None)

    if not all([col_grado, col_dia, col_bloque, col_materia, col_docente]):
        st.error("🚨 **Error de Estructura:** Las columnas de la tabla en Supabase no coinciden con el formato requerido.")
        return

    # Selector institucional de Curso
    lista_grados = sorted(df_horarios[col_grado].dropna().unique().astype(str).tolist())
    grado_horario = st.selectbox("🔍 Seleccione el Grado para desplegar el Horario Oficial:", lista_grados)
    
    df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == grado_horario].copy()
    
    if df_filtrado.empty:
        st.info("No se encontraron registros de horarios para el grado seleccionado.")
        return

    # Días estándar de la semana escolar
    dias_ordenados = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]
    
    # Respetar el orden cronológico exacto de las horas del Excel original
    bloques_ordenados = list(df_filtrado[col_bloque].dropna().unique())

    # 👑 RÉPLICA EXACTA DE LA MAQUETACIÓN DE SU TABLA BELLA
    html_table = """
    <table style="width:100%; border-collapse:collapse; margin-top:20px; font-family:'Arial', sans-serif; box-shadow:4px 4px 15px rgba(0,0,0,0.1); border:3px solid #0d1b2a; border-radius:8px; overflow:hidden;">
        <thead>
            <tr style="background-color:#0d1b2a; color:white; text-align:center; border-bottom:4px solid #d4af37;">
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:18%;">HORARIO / JORNADA</th>
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:16.4%;">LUNES</th>
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:16.4%;">MARTES</th>
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:16.4%;">MIÉRCOLES</th>
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:16.4%;">JUEVES</th>
                <th style="padding:14px; border:1px solid #d4af37; font-family:'Arial Black'; font-size:13px; color:#ffffff; width:16.4%;">VIERNES</th>
            </tr>
        </thead>
        <tbody>
    """

    for bloque in bloques_ordenados:
        df_bloque_actual = df_filtrado[df_filtrado[col_bloque] == bloque]
        
        # Detectar de forma inteligente si la fila corresponde al descanso
        es_recreo = "DESCANSO" in str(bloque).upper() or "RECREO" in str(bloque).upper() or any(str(m).upper().strip() in ['DESCANSO', 'RECREO', 'N/A'] for m in df_bloque_actual[col_materia].tolist())
        
        if es_recreo:
            # ☕ RÉPLICA EXACTA DE SU FILA DE DESCANSO UNIFICADA
            html_table += f"""
            <tr style="background-color:#fff4e6; text-align:center;">
                <td style="padding:12px; font-weight:bold; color:#0d1b2a; border:1px solid #0d1b2a; background-color:#f0f2f6; font-size:12px; font-family:'Arial Black';">{bloque}</td>
                <td colspan="5" style="padding:12px; font-family:'Arial Black'; color:#cc8800; font-size:13px; letter-spacing:5px; text-transform:uppercase; border:1px solid #0d1b2a; font-weight:900;">☕ ✨ D E S C A N S O ✨ ☕</td>
            </tr>
            """
        else:
            # 📅 FILA DE CLASES CON EL DISEÑO DE CELDAS ORIGINAL
            html_table += f"""
            <tr style="text-align:center; background-color:#ffffff;">
                <td style="padding:12px; font-weight:bold; color:#0d1b2a; border:1px solid #0d1b2a; background-color:#f8f9fa; font-size:12px; font-family:'Arial Black';">{bloque}</td>
            """
            for dia in dias_ordenados:
                # Filtrar celda correspondiente a la intersección exacta de Hora y Día
                celda = df_filtrado[(df_filtrado[col_bloque] == bloque) & (df_filtrado[col_dia].astype(str).str.upper().str.strip() == dia)]
                
                if not celda.empty:
                    materia = str(celda[col_materia].iloc[0]).strip()
                    docente = str(celda[col_docente].iloc[0]).strip()
                    
                    if materia.upper() in ['DESCANSO', 'RECREO', 'N/A']:
                        html_table += '<td style="padding:12px; border:1px solid #e0e0e0; background-color:#fff4e6; color:#cc8800; font-weight:bold; font-size:12px;">DESCANSO</td>'
                    else:
                        # 📝 COMPORTAMIENTO IDÉNTICO A SU CÓDIGO FUENTE
                        html_table += f"""
                        <td style="padding:12px; border:1px solid #e0e0e0; background-color:#ffffff; vertical-align:middle;">
                            <div style="color:#000000; font-weight:900; font-size:13px; font-family:'Arial', sans-serif; line-height:1.2;">{materia}</div>
                            <div style="color:#cc8800; font-size:11px; font-weight:bold; margin-top:5px; font-family:'Arial';">👤 {docente}</div>
                        </td>
                        """
                else:
                    # Celda de rejilla vacía para mantener la simetría de la tabla
                    html_table += '<td style="padding:12px; border:1px solid #e0e0e0; background-color:#ffffff; color:#b0b0b0; font-weight:bold;">-</td>'
            html_table += "</tr>"

    html_table += "</tbody></table><br>"
    
    # Inyección directa del HTML purificado en Streamlit
    st.markdown(html_table, unsafe_allow_html=True)
