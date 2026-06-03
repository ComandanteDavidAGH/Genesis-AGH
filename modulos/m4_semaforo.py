# ... código anterior ...

    # 🛡️ BLINDAJE: Convertir a numérico PERO manteniendo NaNs para alumnos sin calificación
    df_trabajo[col_nota] = pd.to_numeric(df_trabajo[col_nota], errors='coerce')
    
    # 🎯 AJUSTE DE UI: Selector compacto para el Grado
    # Creamos columnas: [3, 7] significa 30% de ancho para el selector, 70% vacío
    col_selector, _ = st.columns([3, 7])
    
    grado_sel = "TODOS" # Valor por defecto
    
    with col_selector:
        if col_grado:
            grados_validos = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
            grado_sel = st.selectbox("🔍 Filtrar por Grado:", ["TODOS"] + grados_validos)
            
    # Filtro aplicado
    if grado_sel != "TODOS":
        df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # ... resto del código ...
