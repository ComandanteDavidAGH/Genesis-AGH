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
    
    # 1. Limpieza extrema: Aniquilación del "None" y valores nulos
    if 'LOGRO' in df_render.columns and 'LOGROS' not in df_render.columns:
        df_render = df_render.rename(columns={'LOGRO': 'LOGROS'})
    if 'LOGROS' not in df_render.columns:
        df_render['LOGROS'] = ""
    
    df_render['LOGROS'] = df_render['LOGROS'].fillna("")
    df_render['LOGROS'] = df_render['LOGROS'].astype(str).replace(['nan', 'None', '<NA>', 'null', 'NONE'], '', regex=True).str.strip()
    
    if 'PROMEDIO' in df_render.columns:
        df_render['DESEMPEÑO'] = df_render['PROMEDIO'].apply(clasificar_desempeno)

    # 2. Carga Táctica del Diccionario de Logros
    diccionario_logros = {}
    if 'df_logros' in st.session_state and not st.session_state.df_logros.empty:
        df_l = st.session_state.df_logros
        for _, l_row in df_l.iterrows():
            try:
                k = (limpiar_texto(l_row.iloc[0]), limpiar_texto(l_row.iloc[1]), limpiar_texto(l_row.iloc[2]))
                diccionario_logros[k] = str(l_row.iloc[3]).strip()
            except: pass

    if 'Grado' in df_render.columns:
        df_render['Nivel_Temp'] = df_render['Grado'].apply(obtener_nivel)
    else:
        df_render['Nivel_Temp'] = "Bachillerato"

    # 3. ⚡ INYECCIÓN DE DIAGNÓSTICO: Autocompletar o avisar del fallo
    for idx, row in df_render.iterrows():
        logro_actual = str(row['LOGROS']).strip().upper()
        if logro_actual in ["", "NONE", "NAN"]:
            nivel = str(row['Nivel_Temp'])
            materia = str(row.get('Materia', ''))
            desempeno = str(row.get('DESEMPEÑO', 'BAJO'))
            
            llave = (limpiar_texto(nivel), limpiar_texto(materia), limpiar_texto(desempeno))
            
            # Si encuentra el logro lo pone. Si no, le avisa exactamente qué combinación falta en la base de datos.
            logro_sugerido = diccionario_logros.get(llave, f"⚠️ Configurar en Logros: {nivel} | {materia} | {desempeno}")
            df_render.at[idx, 'LOGROS'] = logro_sugerido

    df_render = df_render.drop(columns=['Nivel_Temp'])

    # 4. Motor de Pintura Semáforo (Rojo/Verde)
    def pintar_celdas(val):
        try:
            n = float(val)
            if n < 6.0: return 'color: #cc0000; font-weight: bold; background-color: #ffe6e6;'
            elif n >= 9.1: return 'color: #00994c; font-weight: bold; background-color: #e6ffe6;'
            elif n >= 6.0: return 'color: #0d1b2a; font-weight: bold;'
            return ''
        except: return ''

    columnas_notas = [c for c in ['P1', 'P2', 'P3', 'P4', 'PROMEDIO'] if c in df_render.columns]
    df_pintado = df_render.style.map(pintar_celdas, subset=columnas_notas).format("{:.1f}", subset=columnas_notas)

    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True, width="medium"),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True),
        'DESEMPEÑO': st.column_config.TextColumn("Desempeño", disabled=True),
        'LOGROS': st.column_config.TextColumn("Logros (Autocompletado)", disabled=False, width="large")
    }

    col_btn, _ = st.columns([2, 8])
    with col_btn:
        if st.button("💾 GUARDAR EN BD", key=f"btn_guardar_{periodo_sel}", type="primary", use_container_width=True):
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
    
    st.data_editor(df_pintado, use_container_width=True, height=450, key=key_editor, column_config=config_notas)
