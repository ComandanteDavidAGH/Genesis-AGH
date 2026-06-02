import streamlit as st

def renderizar():
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📖 Manual de Operaciones</h3>", unsafe_allow_html=True)
    
    with st.expander("🔐 1. ACCESO Y SEGURIDAD", expanded=True):
        st.write("""
        * **Ingreso:** Utilice sus credenciales asignadas. El sistema registra cada ingreso en la bitácora de seguridad.
        * **Habeas Data:** Al ingresar, usted acepta el tratamiento de datos personales bajo la Ley 1581 de 2012. 
        * **Cierre de Sesión:** Siempre use el botón 'Salir' para proteger la información de los menores.
        """)

    with st.expander("✍️ 2. GESTIÓN ACADÉMICA (NOTAS)"):
        st.write("""
        * **Rango:** El sistema solo permite notas entre 1.0 y 10.0.
        * **Guardado:** Es obligatorio presionar el botón azul **'GUARDAR'** después de digitar. Si no lo hace, el satélite no recibirá los datos.
        * **Escala MEN:** El sistema traduce automáticamente su nota numérica a la escala nacional (Bajo, Básico, Alto, Superior).
        """)

    with st.expander("📝 3. CONVIVENCIA Y ASISTENCIA"):
        st.write("""
        * **Registro:** En la pestaña 'Registrar Novedad' puede anotar fallas, retardos o felicitaciones.
        * **Observador Oficial:** En la pestaña 'Generar Observador', seleccione al alumno y presione 'Preparar Observador' para obtener el documento legal listo para firmas.
        * **Corrección:** Si comete un error, use el botón **'↩️ DESHACER'** inmediatamente.
        """)

    with st.expander("📊 4. INTELIGENCIA Y REPORTES (EXCLUSIVO RECTORÍA)"):
        st.write("""
        * **Dashboard:** Visualice el 'Radar Táctico' para ver las fortalezas y debilidades de cada estudiante.
        * **SIMAT:** En el módulo de Backup, puede descargar el reporte listo para el Ministerio de Educación.
        * **Eficiencia:** Monitoree el medidor de eficiencia interna; si baja del 80%, el sistema emitirá una alerta de riesgo de reprobación masiva.
        """)
