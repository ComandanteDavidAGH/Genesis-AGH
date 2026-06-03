import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

zona_colombia = timezone(timedelta(hours=-5))

def registrar_bitacora(usuario, rol, accion):
    st.session_state.bitacora.append({
        "Fecha": datetime.now(zona_colombia).strftime("%Y-%m-%d"),
        "Hora": datetime.now(zona_colombia).strftime("%I:%M:%S %p"),
        "Usuario": usuario,
        "Rol": rol,
        "Acción": accion
    })

def renderizar(df, periodo_sel, conn):
    # 🚀 ENVOLTORIO EXTERNO PREMIUM PARA EL EDITOR (stDataEditor)
    st.markdown("""
    <style>
    div[data-testid="stDataEditor"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
        padding: 2px !important;
        background-color: #f0f2f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    # --- 🛡️ ESCUDO DE SEGURIDAD ULTRARRÁPIDO ---
    try:
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.read(worksheet="Configuracion", ttl=600)
            
        df_conf_shield = st.session_state.df_config_seguridad
        estado_periodo = df_conf_shield[df_conf_shield['Periodo'] == periodo_sel]['Estado'].values[0]
        
        if estado_periodo == "Cerrado":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO por la administración.")
            st.info("⚠️ No se permiten modificaciones en este periodo. Contacte a Rectoría para apertura.")
            st.stop()
    except Exception as e:
        st.warning("⚠️ Nota: No se pudo verificar el blindaje de seguridad. Proceda con precaución.")

    if df.empty:
        st.warning("No hay estudiantes asignados para este grado y materia.")
        return

    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True)
    }

    col_btn, col_espacio = st.columns([2, 8])
    with col_btn:
        if st.button("💾 GUARDAR EN EXCEL", type="primary", use_container_width=True):
            cambios = st.session_state.editor_notas.get('edited_rows', {})
            
            if cambios:
                with st.spinner("🚀 Transmitiendo datos a la Bóveda de Google Drive..."):
                    for fila_posicional, valores_nuevos in cambios.items():
                        idx_real = df.index[int(fila_posicional)]
                        for columna, valor in valores_nuevos.items():
                            st.session_state.df_maestro.at[idx_real, columna] = valor
                    
                    st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)

                    df_para_drive = st.session_state.df_maestro.copy()
                    if 'Grado' in df_para_drive.columns: 
                        df_para_drive = df_para_drive.drop(columns=['Grado'])
                    
                    df_para_drive = df_para_drive.rename(columns={
                        'Nombre_Completo': 'NOMBRE_COMPLETO',
                        'Materia': 'ASIGNATURA',
                        'LOGRO': 'LOGROS'
                    })
                    
                    try:
                        conn.update(worksheet="NOTAS_CONSOLIDADAS", data=df_para_drive)
                        st.success("✅ ¡SATÉLITE SINCRONIZADO!")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 FALLA DE CONEXIÓN: {e}")
            else:
                st.warning("⚠️ No hay cambios para guardar.")

    # ⚡ MOTOR DE PINTURA PANDAS STYLER (Pinta las celdas desde adentro)
    def pintar_celdas(val):
        try:
            n = float(val)
            if n < 6.0:
                return 'color: #cc0000; font-weight: bold; background-color: #ffe6e6;'
            elif n >= 9.0:
                return 'color: #00994c; font-weight: bold; background-color: #e6ffe6;'
            elif n >= 6.0:
                return 'color: #0d1b2a; font-weight: bold;'
            return ''
        except:
            return ''

    # Aplicamos la pintura a las columnas numéricas
    columnas_notas = [c for c in ['P1', 'P2', 'P3', 'P4', 'PROMEDIO'] if c in df.columns]
    df_pintado = df.style.map(pintar_celdas, subset=columnas_notas)

    # 👑 FALSO ENCABEZADO VIP PARA CORONAR LA TABLA
    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    
    # 🖨️ RENDERIZADO DEL EDITOR DE DATOS
    st.data_editor(df_pintado, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)
