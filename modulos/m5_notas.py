def renderizar(df, periodo_sel, conn):
    # 1. SOLUCIÓN AL ERROR DE KEY: Dinamizamos la key según el periodo
    key_editor = f"editor_notas_{periodo_sel}"

    # 🚀 MOTOR VISUAL
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
        filtro = df_conf[df_conf['periodo'].astype(str).str.upper() == str(periodo_sel).upper()]
        
        if not filtro.empty and str(filtro['estado'].values[0]).strip().upper() == "CERRADO":
            st.error(f"🚫 ACCESO DENEGADO: El {periodo_sel} ha sido CERRADO.")
            st.stop()
    except Exception:
        st.warning("⚠️ Módulo de seguridad no detectado.")

    if df.empty:
        st.warning("No hay estudiantes asignados.")
        return

    # --- 🛠️ LIMPIEZA PROFUNDA (ELIMINACIÓN DE "None") ---
    # Trabajamos sobre una copia para no alterar el original innecesariamente
    df_render = df.copy()
    
    if 'LOGROS' not in df_render.columns:
        df_render['LOGROS'] = ""
    
    # Forzamos a string, reemplazamos cualquier variante de nulo/nan/none y dejamos espacio en blanco
    df_render['LOGROS'] = df_render['LOGROS'].astype(str).replace(['nan', 'None', '<NA>', 'null'], '').fillna('')
    
    # Asegurar desempeño
    if 'DESEMPEÑO' in df_render.columns:
        df_render['DESEMPEÑO'] = df_render['PROMEDIO'].apply(clasificar_desempeno)

    # --- 🎯 CONFIGURACIÓN ---
    config_notas = { 
        'P1': st.column_config.NumberColumn("P1", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P2': st.column_config.NumberColumn("P2", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P3': st.column_config.NumberColumn("P3", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'P4': st.column_config.NumberColumn("P4", min_value=1.0, max_value=10.0, step=0.1, format="%.1f"),
        'Nombre_Completo': st.column_config.TextColumn("Estudiante", disabled=True),
        'Materia': st.column_config.TextColumn("Asignatura", disabled=True),
        'PROMEDIO': st.column_config.NumberColumn("Definitiva", disabled=True, format="%.1f"),
        'DESEMPEÑO': st.column_config.TextColumn("Desempeño", disabled=True),
        'LOGROS': st.column_config.TextColumn("Logros", disabled=False)
    }

    # --- 💾 LÓGICA DE GUARDADO ---
    if st.button("💾 GUARDAR EN BD", key=f"btn_guardar_{periodo_sel}", type="primary"):
        cambios = st.session_state.get(key_editor, {}).get('edited_rows', {})
        if cambios:
            with st.spinner("🚀 Sincronizando..."):
                for fila_pos, valores in cambios.items():
                    idx_real = df_render.index[int(fila_pos)]
                    for col, val in valores.items():
                        st.session_state.df_maestro.at[idx_real, col] = val
                
                # Recalcular
                st.session_state.df_maestro['PROMEDIO'] = st.session_state.df_maestro[['P1', 'P2', 'P3', 'P4']].mean(axis=1).round(1)
                st.session_state.df_maestro['DESEMPEÑO'] = st.session_state.df_maestro['PROMEDIO'].apply(clasificar_desempeno)
                
                try:
                    st.session_state.df_maestro.to_sql('notas_consolidadas', con=conn.engine, if_exists='replace', index=False)
                    st.success("✅ ¡Sincronizado!")
                    registrar_bitacora(st.session_state.usuario_actual, st.session_state.rol, "💾 Notas actualizadas")
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Error SQL: {e}")
        else:
            st.warning("⚠️ Sin cambios.")

    # 👑 RENDERIZADO FINAL
    st.markdown("<div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>MATRIZ OFICIAL DE CALIFICACIONES</div>", unsafe_allow_html=True)
    
    st.data_editor(df_render, use_container_width=True, height=450, key=key_editor, column_config=config_notas)
