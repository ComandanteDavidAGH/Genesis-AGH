import streamlit as st
import pandas as pd

def renderizar(df_notas, periodo_sel, conn_sql=None):
    # 👑 MOTOR VISUAL EMULADOR: Réplica exacta con diseño responsivo
    st.markdown("""
    <style>
    @keyframes pulso_critico { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.02); } }
    @keyframes pulso_alerta { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.02); } }
    @keyframes pulso_optimo { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.02); } }
    
    .card-critica-bella { background-color: #ffebeb; border: 4px solid #cc0000; padding: 15px; border-radius: 14px; text-align: center; }
    .card-alerta-bella { background-color: #fffef0; border: 4px solid #cc8800; padding: 15px; border-radius: 14px; text-align: center; }
    .card-optima-bella { background-color: #e6f9f0; border: 4px solid #00994c; padding: 15px; border-radius: 14px; text-align: center; }
    
    .num-critico-titila { font-size: 50px; font-weight: 900; color: #cc0000; animation: pulso_critico 1.3s infinite; }
    .num-alerta-titila { font-size: 50px; font-weight: 900; color: #cc8800; animation: pulso_alerta 1.3s infinite; }
    .num-optimo-titila { font-size: 50px; font-weight: 900; color: #00994c; animation: pulso_optimo 1.3s infinite; }
    .txt-titular { font-family: 'Arial Black', sans-serif; font-size: 13px; margin-bottom: 5px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>🚦 Semáforo de Riesgo Académico</h3>", unsafe_allow_html=True)

    if df_notas is None or df_notas.empty:
        st.warning("⚠️ No hay datos disponibles para el Semáforo.")
        return

    df_trabajo = df_notas.copy()
    # Estandarizar columnas a mayúsculas para evitar errores de tipeo
    df_trabajo.columns = [str(c).upper().strip() for c in df_trabajo.columns]
    
    # Detección inteligente de columnas
    col_nombre = next((c for c in df_trabajo.columns if c in ['NOMBRE_COMPLETO', 'ESTUDIANTE', 'NOMBRE']), df_trabajo.columns[0])
    col_grado = next((c for c in df_trabajo.columns if c in ['GRADO', 'CURSO']), None)
    
    # Lógica de columna de nota
    col_nota = periodo_sel.upper().strip() if periodo_sel and periodo_sel.upper().strip() in df_trabajo.columns else \
               next((c for c in df_trabajo.columns if c in ['PROMEDIO', 'PROMEDIO_FINAL', 'DEF', 'NOTA']), None)

    if not col_nota:
        st.error("🚨 No se encontró una columna de notas válida.")
        return

    # 🛡️ BLINDAJE: Convertir a numérico PERO manteniendo NaNs para alumnos sin calificación
    df_trabajo[col_nota] = pd.to_numeric(df_trabajo[col_nota], errors='coerce')
    
    # Filtro de Grado
    if col_grado:
        grados_validos = sorted(df_trabajo[col_grado].dropna().unique().astype(str).tolist())
        grado_sel = st.selectbox("🔍 Filtrar por Grado:", ["TODOS"] + grados_validos)
        if grado_sel != "TODOS":
            df_trabajo = df_trabajo[df_trabajo[col_grado].astype(str) == grado_sel]

    # Consolidado Real (Ignorando NaNs para que no salgan como riesgo 0.0)
    df_resumen = df_trabajo.groupby(col_nombre).agg({col_nota: 'mean', col_grado: 'first'}).reset_index()
    df_resumen = df_resumen.dropna(subset=[col_nota]) # Solo alumnos con nota real

    criticos = df_resumen[df_resumen[col_nota] < 6.0]
    alertas = df_resumen[(df_resumen[col_nota] >= 6.0) & (df_resumen[col_nota] <= 7.5)]
    optimos = df_resumen[df_resumen[col_nota] > 7.5]

    c1, c2, c3 = st.columns(3)
    c1.html(f"<div class='card-critica-bella'><div class='txt-titular'>Riesgo Crítico</div><div class='num-critico-titila'>{len(criticos)}</div></div>")
    c2.html(f"<div class='card-alerta-bella'><div class='txt-titular'>Alerta</div><div class='num-alerta-titila'>{len(alertas)}</div></div>")
    c3.html(f"<div class='card-optima-bella'><div class='txt-titular'>Óptimo</div><div class='num-optimo-titila'>{len(optimos)}</div></div>")

    # Tabla de riesgo con estilo
    if not criticos.empty:
        st.markdown("---")
        st.subheader("🚨 Estudiantes en Riesgo Crítico")
        st.dataframe(criticos[[col_nombre, col_grado, col_nota]].rename(columns={col_nota: "Promedio"}), use_container_width=True, hide_index=True)
    else:
        st.success("✅ ¡Todo el perímetro está estable!")
