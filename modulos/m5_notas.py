import streamlit as st
import pandas as pd
import unicodedata
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def limpiar_texto(txt):
    """ Estandariza cadenas para cruces perfectos en bases de datos """
    if pd.isna(txt): return ""
    txt_str = str(txt).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt_str) if unicodedata.category(c) != 'Mn')

def registrar_bitacora(usuario, rol, accion):
    if 'bitacora' not in st.session_state:
        st.session_state.bitacora = []
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

def clasificar_desempeno(nota):
    try:
        n = float(nota)
        if n < 6.0: return 'BAJO'
        elif n < 7.6: return 'BÁSICO'
        elif n < 9.1: return 'ALTO'
        else: return 'SUPERIOR'
    except:
        return 'BAJO'

def obtener_nivel(grado):
    g_str = str(grado).upper()
    if any(k in g_str for k in ["1", "2", "3", "4", "5", "PRIMER", "SEGUND", "TERCER", "CUART", "QUINT"]) and not any(k in g_str for k in ["10", "11", "DECIMO", "ONCE"]):
        return "Primaria"
    return "Bachillerato"

def renderizar(df, periodo_sel, conn):
    key_editor = f"editor_notas_{periodo_sel}"

    st.markdown("""
    <style>
    div[data-testid="stDataEditor"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    # --- 🛡️ ESCUDO DE SEGURIDAD ---
    try:
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.query("SELECT * FROM configuracion;", ttl=600)
            
        df_conf = st.session_state.df_config_seguridad
        col_periodo = 'periodo' if 'periodo' in df_conf.columns else 'Periodo'
        col_estado = 'estado' if 'estado' in df_conf.columns else 'Estado'
        
        filtro = df_conf[df_conf[col_periodo].astype(str).str.upper() == str(periodo_sel).upper()]
        if not filtro.empty and str(filtro[col_estado].values[0]).strip().upper() == "CERRADO":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO.")
            st.stop()
    except Exception:
        st.warning("⚠️ Módulo de seguridad no detectado.")

    if df.empty:
        st.warning("No hay estudiantes asignados.")
        return

    df_render = df.copy()
    
    if 'LOGRO' in df_render.columns and 'LOGROS' not in df_render.columns:
        df_render = df_render.rename(columns={'LOGRO': 'LOGROS'})
    if 'LOGROS' not in df_render.columns:
        df_render['LOGROS'] = ""
    
    df_render['LOGROS'] = df_render['LOGROS'].astype(str).replace(['nan', 'None', '<NA>', 'null'], '').fillna('')
    
    if 'PROMEDIO' in df_render.columns:
        df_render['DESEMPEÑO'] = df_render['PROMEDIO'].apply(clasificar_desempeno)

    # ⚡ INYECCIÓN DE IA: AUTOCOMPLETADO DE LOGROS DESDE EL DICCIONARIO
    diccionario_logros = {}
    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
        for _, l_row in st.session_state.df_logros.iterrows():
            try:
                k = (limpiar_texto(l_row.iloc[0]), limpiar_texto(l_row.iloc[1]), limpiar_texto(l_row.iloc[2]))
                diccionario_logros[k] = str(l_row.iloc[3])
            except: pass

    # Creamos columna temporal de nivel para el cruce
    if 'Grado' in df_render.columns:
        df_render['Nivel_Temp'] = df_render['Grado'].apply(obtener_nivel)
    else:
        df_render['Nivel_Temp'] = "Bachillerato"

    # Evaluamos fila por fila si necesita autocompletado
    for idx, row in df_render.iterrows():
        logro_actual = str(row['LOGROS']).strip()
        if not logro_actual:
            llave = (limpiar_texto(row['Nivel_Temp']), limpiar_texto(row.get('Materia', '')), limpiar_texto(row.get('DESEMPEÑO', 'BAJO')))
            logro_sugerido = diccionario_logros.get(llave, "")
            df_render.at[idx, 'LOGROS'] = logro_sugerido

    # Limpiamos la arquitectura (eliminamos columna temporal)
    df_render = df_render.drop(columns=['Nivel_Temp'])

    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True, width="medium"),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True, format="%.1f"),
        'DESEMPEÑO': st.column_config.TextColumn("Desempeño", disabled=True),
        'LOGROS': st.column_config.TextColumn("Logros (Autocompletado)", disabled=False, width="large")
    }

    if st.button("💾 GUARDAR EN BD", key=f"btn_guardar_{periodo_sel}", type="primary"):
        cambios = st.session_state.get(key_editor, {}).get('edited_rows', {})
        if cambios:
            with st.spinner("🚀 Sincronizando al Satélite SQL..."):
                for fila_pos, valores in cambios.items():
                    idx_real = df_render.index[int(fila_pos)]
                    for col, val in valores.items():
                        st.session_state.df_maestro.at[idx_real, col] = val
                
                st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                
                try:
                    df_para_sql = st.session_state.df_maestro.copy()
                    if 'Grado' in df_para_sql.columns: 
                        df_para_sql = df_para_sql.drop(columns=['Grado'])
                    
                    df_para_sql = df_para_sql.rename(columns={
                        'Nombre_Completo': 'NOMBRE_COMPLETO',
                        'Materia': 'ASIGNATURA',
                        'LOGRO': 'LOGROS'
                    })

                    df_para_sql.to_sql('notas_consolidadas', con=conn.engine, if_exists='replace', index=False)
                    st.success("✅ ¡Sincronizado exitosamente!")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Error SQL: {e}")
        else:
            st.warning("⚠️ Sin cambios registrados para guardar.")

    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    
    st.data_editor(df_render, use_container_width=True, height=450, key=key_editor, column_config=config_notas)
