import streamlit as st
import pandas as pd
import unicodedata

def limpiar_caracteres(txt):
    """ Filtro extractor: Elimina tildes, espacios y estandariza a mayúsculas puras """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def renderizar(conn_sql):
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🕒 Horarios y Asignaciones Académicas</h3>", unsafe_allow_html=True)
    
    # 🛡️ ESCUDO PROTECTOR SQL
    try:
        df_horarios = conn_sql.query("SELECT * FROM db_horarios;")
    except Exception as e:
        st.error(f"❌ Error crítico de enlace SQL: {e}")
        return
        
    if df_horarios is None or df_horarios.empty:
        st.warning("⚠️ **Base de datos de horarios no inicializada en Supabase.**")
        st.info("💡 *Nota de Rectoría:* Recuerde subir el archivo Excel de respaldo en la sección de 'Bitácora y Backup'.")
        return

    # Estandarizamos los nombres de las columnas a mayúsculas limpias
    df_horarios.columns = [str(c).upper().strip() for c in df_horarios.columns]
    
    # Mapeo automatizado de columnas por posición absoluta (Inmune a cualquier cambio)
    col_dia = df_horarios.columns[0]      # Columna 1: DÍA
    col_bloque = df_horarios.columns[1]   # Columna 2: BLOQUE_HORARIO
    col_grado = df_horarios.columns[2]    # Columna 3: GRADO
    col_materia = df_horarios.columns[3]  # Columna 4: MATERIA
    col_docente = df_horarios.columns[4]  # Columna 5: DOCENTE

    # Selector de grado institucional
    lista_grados = sorted(df_horarios[col_grado].dropna().unique().astype(str).tolist())
    grado_horario = st.selectbox("🔍 Seleccione el Grado para desplegar el Horario Oficial:", lista_grados)
    
    df_filtrado = df_horarios[df_horarios[col_grado].astype(str) == grado_horario].copy()
    
    if df_filtrado.empty:
        st.info("No se encontraron registros de horarios para el grado seleccionado.")
        return

    # Aplicamos el filtro extractor para una coincidencia limpia del 100%
    df_filtrado['DIA_CLEAN'] = df_filtrado[col_dia].apply(limpiar_caracteres)
    df_filtrado['BLOQUE_CLEAN'] = df_filtrado[col_bloque].astype(str).str.strip()

    # Secuencia de días escolares
    dias_secuencia = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"]
    
    # Conservamos la lista de bloques en orden cronológico real
    bloques_ordenados = []
    for b in df_filtrado[col_bloque].dropna().tolist():
        b_str = str(b).strip()
        if b_str not in bloques_ordenados:
            bloques_ordenados.append(b_str)

    # 👑 CONSTRUCCIÓN DEL HORARIO SIN SANGRIAS REBELDES
    html_table = (
        '<table style="width:100%; border-collapse:collapse; margin-top:20px; font-family:\'Arial\', sans-serif; '
        'box-shadow:4px 4px 15px rgba(0,0,0,0.1); border:3px solid #0d1b2a; border-radius:8px; overflow:hidden;">'
        '<thead>'
        '<tr style="background-color:#0d1b2a; color:white; text-align:center; border-bottom:4px solid #d4af37;">'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:18%;">HORARIO / JORNADA</th>'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:16.4%;">LUNES</th>'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:16.4%;">MARTES</th>'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:16.4%;">MIÉRCOLES</th>'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:16.4%;">JUEVES</th>'
        '<th style="padding:14px; border:1px solid #d4af37; font-family:\'Arial Black\'; font-size:13px; color:#ffffff; width:16.4%;">VIERNES</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
    )

    for bloque in bloques_ordenados:
        df_bloque_actual = df_filtrado[df_filtrado['BLOQUE_CLEAN'] == bloque]
        es_recreo = "DESCANSO" in bloque.upper() or "RECREO" in bloque.upper()
        
        if es_recreo:
            html_table += (
                f'<tr style="background-color:#fff4e6; text-align:center;">'
                f'<td style="padding:12px; font-weight:bold; color:#0d1b2a; border:1px solid #0d1b2a; background-color:#f0f2f6; font-size:12px; font-family:\'Arial Black\';">{bloque}</td>'
                f'<td colspan="5" style="padding:12px; font-family:\'Arial Black\'; color:#cc8800; font-size:13px; letter-spacing:5px; text-transform:uppercase; border:1px solid #0d1b2a; font-weight:900;">☕ ✨ D E S C A N S O ✨ ☕</td>'
                f'</tr>'
            )
        else:
            html_table += (
                f'<tr style="text-align:center; background-color:#ffffff;">'
                f'<td style="padding:12px; font-weight:bold; color:#0d1b2a; border:1px solid #0d1b2a; background-color:#f8f9fa; font-size:12px; font-family:\'Arial Black\';">{bloque}</td>'
            )
            for dia in dias_secuencia:
                celda = df_bloque_actual[df_bloque_actual['DIA_CLEAN'] == dia]
                
                if not celda.empty:
                    materia = str(celda[col_materia].iloc[0]).strip()
                    docente = str(celda[col_docente].iloc[0]).strip()
                    
                    html_table += (
                        f'<td style="padding:12px; border:1px solid #e0e0e0; background-color:#ffffff; vertical-align:middle;">'
                        f'<div style="color:#000000; font-weight:900; font-size:13px; font-family:\'Arial\', sans-serif; line-height:1.2;">{materia}</div>'
                        f'<div style="color:#cc8800; font-size:11px; font-weight:bold; margin-top:5px; font-family:\'Arial\';">👤 {docente}</div>'
                        f'</td>'
                    )
                else:
                    html_table += '<td style="padding:12px; border:1px solid #e0e0e0; background-color:#ffffff; color:#b0b0b0; font-weight:bold;">-</td>'
            html_table += '</tr>'

    html_table += '</tbody></table><br>'
    
    # ⚡ EXTRACCIÓN DIRECTA NATIVA: Salta las restricciones de Markdown ⚡
    st.html(html_table)
