import streamlit as st
import pandas as pd
import unicodedata
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def limpiar_texto(txt):
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

    # 🚀 MOTOR VISUAL (BORDES FORZADOS)
    st.markdown("""
    <style>
    /* Forzar contorno sólido en la tabla de Streamlit */
    [data-testid="stDataEditor"], [data-testid="stDataFrame"] {
        border-left: 3px solid #0d1b2a !important;
        border-right: 3px solid #0d1b2a !important;
        border-bottom: 3px solid #0d1b2a !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        margin-top: -10px !important; /* Ajuste suave para fusionar con el título */
        box-shadow: 0px 5px 15px rgba(0,0,0,0.15) !important;
        overflow: hidden !important;
    }
    
    /* Eliminar doble borde interno */
    [data-testid="stDataFrameResizable"] {
        border: none !important;
    }
    
    /* Mini-KPIs del Docente */
    .hud-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #d4af37;
        padding: 10px 15px;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #dee2e6;
    }
    .hud-item { text-align: center; }
    .hud-title { font-size: 11px; color: #6c757d; font-family: 'Arial Black', sans-serif; text-transform: uppercase; margin: 0; }
    .hud-value { font-size: 18px; color: #0d1b2a; font-weight: 900; margin: 0; font-family: Arial, sans-serif; }
    .hud-value-gold { color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    try:
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.query("SELECT * FROM configuracion;", ttl=600)
            
        df_conf = st.session_state.df_config_seguridad
        col_periodo = 'periodo' if 'periodo' in df_conf.columns else 'Periodo'
        col_estado = 'estado' if 'estado' in df_conf.columns else 'Estado'
        
        filtro = df_conf[df_conf[col_periodo].astype(str).str.upper() == str(periodo_sel).upper()]
        if not filtro.empty and str(filtro[col_estado].values[0]).strip().upper() == "CERRADO":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO por Rectoría.")
            st.stop()
    except Exception:
        st.warning("⚠️ Módulo de seguridad no detectado.")

    if df.empty:
        st.warning("No hay estudiantes asignados a esta vista.")
        return

    df_render = df.copy()
    
    if 'LOGRO' in df_render.columns and 'LOGROS' not in df_render.columns:
        df_render = df_render.rename(columns={'LOGRO': 'LOGROS'})
    if 'LOGROS' not in df_render.columns:
        df_render['LOGROS'] = ""
    
    df_render['LOGROS'] = df_render['LOGROS'].fillna("")
    df_render['LOGROS'] = df_render['LOGROS'].astype(str).replace(['nan', 'None', '<NA>', 'null', 'NONE'], '', regex=True).str.strip()
    
    if 'PROMEDIO' in df_render.columns:
        df_render['PROMEDIO'] = pd.to_numeric(df_render['PROMEDIO'], errors='coerce').fillna(0.0)
        df_render['DESEMPEÑO'] = df_render['PROMEDIO'].apply(clasificar_desempeno)

    if 'PROMEDIO' in df_render.columns and 'Nombre_Completo' in df_render.columns:
        df_agrupado = df_render.groupby('Nombre_Completo')['PROMEDIO'].mean()
        
        total_est = df_render['Nombre_Completo'].nunique()
        promedio_grupo = df_agrupado.mean() if not df_agrupado.empty else 0.0
        aprobados = len(df_agrupado[df_agrupado >= 6.0])
        
        tasa_aprobacion = (aprobados / total_est) * 100 if total_est > 0 else 0
        color_tasa = "green" if tasa_aprobacion >= 70 else ("orange" if tasa_aprobacion >= 50 else "red")
        
        st.markdown(f"""
        <div class="hud-box">
            <div class="hud-item">
                <p class="hud-title">Estudiantes</p>
                <p class="hud-value">{total_est}</p>
            </div>
            <div class="hud-item">
                <p class="hud-title">Promedio Grupo</p>
                <p class="hud-value hud-value-gold">{promedio_grupo:.1f}</p>
            </div>
            <div class="hud-item">
                <p class="hud-title">Aprobación</p>
                <p class="hud-value" style="color: {color_tasa};">{tasa_aprobacion:.1f}%</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

    for idx, row in df_render.iterrows():
        logro_actual = str(row['LOGROS']).strip().upper()
        if logro_actual in ["", "NONE", "NAN"]:
            nivel = str(row['Nivel_Temp'])
            materia = str(row.get('Materia', ''))
            desempeno = str(row.get('DESEMPEÑO', 'BAJO'))
            
            llave = (limpiar_texto(nivel), limpiar_texto(materia), limpiar_texto(desempeno))
            logro_sugerido = diccionario_logros.get(llave, f"⚠️ Configurar en Logros: {nivel} | {materia} | {desempeno}")
            df_render.at[idx, 'LOGROS'] = logro_sugerido

    df_render = df_render.drop(columns=['Nivel_Temp'])

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

    col_vacia, col_btn = st.columns([7, 3])
    with col_btn:
        if st.button("💾 GUARDAR EN BASE DE DATOS", key=f"btn_guardar_{periodo_sel}", type="primary", use_container_width=True):
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
                        st.toast("✅ ¡Notas sincronizadas exitosamente en el búnker SQL!", icon="🚀")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                        st.cache_data.clear()
                        import time
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 Error SQL: {e}")
            else:
                st.toast("⚠️ No detecté cambios en la matriz para guardar.", icon="👀")

    # Título enmarcado
    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-radius:8px 8px 0 0; position:relative; z-index:11; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    
    st.data_editor(df_pintado, use_container_width=True, height=450, key=key_editor, column_config=config_notas)
