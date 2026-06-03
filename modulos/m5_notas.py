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

    # --- 🛡️ ESCUDO DE SEGURIDAD (TRADUCIDO A SQL SUPABASE) ---
    try:
        # Consultamos a Supabase la tabla de configuración
        if 'df_config_seguridad' not in st.session_state:
            st.session_state.df_config_seguridad = conn.query("SELECT * FROM configuracion;", ttl=600)
            
        df_conf_shield = st.session_state.df_config_seguridad
        
        # En SQL las columnas a veces bajan en minúsculas, aseguramos el cruce:
        col_periodo = 'periodo' if 'periodo' in df_conf_shield.columns else 'Periodo'
        col_estado = 'estado' if 'estado' in df_conf_shield.columns else 'Estado'
        
        # Buscamos el estado del periodo actual
        filtro_estado = df_conf_shield[df_conf_shield[col_periodo].astype(str).str.upper() == str(periodo_sel).upper()]
        
        if not filtro_estado.empty:
            estado_periodo = str(filtro_estado[col_estado].values[0]).strip().upper()
            if estado_periodo == "CERRADO":
                st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO por la administración.")
                st.info("⚠️ No se permiten modificaciones en este periodo. Contacte a Rectoría para apertura.")
                st.stop()
    except Exception as e:
        st.warning("⚠️ Nota: Módulo de seguridad desconectado o tabla 'configuracion' no hallada en Supabase.")

    if df.empty:
        st.warning("No hay estudiantes asignados para este grado y materia.")
        return

    # 🎯 CORTE DE DECIMALES: format="%.1f" restringe la vista a 1 solo número
    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True, format="%.1f")
    }

    col_btn, col_espacio = st.columns([2, 8])
    with col_btn:
        if st.button("💾 GUARDAR EN BD", type="primary", use_container_width=True):
            cambios = st.session_state.editor_notas.get('edited_rows', {})
            
            if cambios:
                with st.spinner("🚀 Transmitiendo datos a la Bóveda SQL..."):
                    # Aplicamos cambios locales
                    for fila_posicional, valores_nuevos in cambios.items():
                        idx_real = df.index[int(fila_posicional)]
                        for columna, valor in valores_nuevos.items():
                            st.session_state.df_maestro.at[idx_real, columna] = valor
                    
                    st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)

                    # Preparamos el empaquetado final
                    df_para_sql = st.session_state.df_maestro.copy()
                    if 'Grado' in df_para_sql.columns: 
                        df_para_sql = df_para_sql.drop(columns=['Grado'])
                    
                    df_para_sql = df_para_sql.rename(columns={
                        'Nombre_Completo': 'NOMBRE_COMPLETO',
                        'Materia': 'ASIGNATURA',
                        'LOGRO': 'LOGROS'
                    })
                    
                    try:
                        # ⚡ ESCRITURA DIRECTA A SUPABASE USANDO EL MOTOR SQL
                        df_para_sql.to_sql('notas_consolidadas', con=conn.engine, if_exists='replace', index=False)
                        
                        st.success("✅ ¡SATÉLITE SQL SINCRONIZADO!")
                        registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                        st.balloons()
                        
                        # Vaciamos la memoria caché para que los boletines reflejen los cambios al instante
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 FALLA DE ESCRITURA SQL: {e}")
            else:
                st.warning("⚠️ No hay cambios para guardar.")

    # ⚡ MOTOR DE PINTURA PANDAS STYLER
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

    columnas_notas = [c for c in ['P1', 'P2', 'P3', 'P4', 'PROMEDIO'] if c in df.columns]
    df_pintado = df.style.map(pintar_celdas, subset=columnas_notas).format("{:.1f}", subset=columnas_notas)

    # 👑 FALSO ENCABEZADO VIP
    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    
    # 🖨️ RENDERIZADO DEL EDITOR
    st.data_editor(df_pintado, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)
