import streamlit as st

def renderizar():
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        # --- BANNER PRINCIPAL ALINEADO ---
        st.markdown("""<div style="background:rgba(255,255,255,0.95); padding:20px; border-radius:10px; border-left:8px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#000; margin-bottom:20px; border:2px solid #000;">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif; text-align: center;">¡Bienvenido a la PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026!</h3>
            <p style="font-size:1.1rem; color:#000; font-family: 'Arial Black', sans-serif; font-weight:bold; text-align: center; margin-bottom:0;"><i>"Seguridad, Control y Excelencia Educativa."</i></p>
            </div>""", unsafe_allow_html=True)
        
        # --- TARJETAS DE MISIÓN Y VISIÓN (SIMETRÍA PERFECTA) ---
        col_mision, col_vision = st.columns(2)
        with col_mision:
            st.markdown("""<div style="background:white; padding:20px; border-radius:10px; border:2px solid #000; border-top:8px solid #0d1b2a; height:100%; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">🎯 Nuestra Misión</h4>
                <p style="color:#000; font-weight:bold; font-size:15px; text-align:justify;">Formar líderes con excelencia académica y valores humanos, utilizando la tecnología satelital de Génesis AGH para transformar el seguimiento educativo en un proceso de precisión y calidad.</p>
            </div>""", unsafe_allow_html=True)
        
        with col_vision:
            st.markdown("""<div style="background:white; padding:20px; border-radius:10px; border:2px solid #000; border-top:8px solid #d4af37; height:100%; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">👁️ Nuestra Visión 2028</h4>
                <p style="color:#000; font-weight:bold; font-size:15px; text-align:justify;">Seremos reconocidos como la institución líder en innovación pedagógica y transformación digital en la región, proyectando talentos hacia el éxito internacional.</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- BLINDAJE LEGAL MINISTERIO DE EDUCACIÓN (HABEAS DATA) ---
        st.markdown("""<div style="background:#f8f9fa; padding:15px; border-radius:8px; border:1px solid #ced4da; border-left:6px solid #cc0000; margin-top:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            <h5 style="color:#cc0000; font-family: 'Arial Black', sans-serif; margin-top:0; font-size:13px;">⚖️ AVISO LEGAL: POLÍTICA DE PRIVACIDAD Y TRATAMIENTO DE DATOS PERSONALES</h5>
            <p style="color:#333; font-size:12px; text-align:justify; margin-bottom:0; line-height:1.4;">
            En estricto cumplimiento de la <b>Ley 1581 de 2012</b> (Ley de Protección de Datos Personales), el Decreto 1377 de 2013 de la República de Colombia, y los lineamientos del <b>Ministerio de Educación Nacional (MEN)</b>, la Institución Educativa garantiza que la recolección, almacenamiento, uso y circulación de los datos personales y académicos de los menores de edad y sus familias se realiza de forma confidencial, segura y exclusiva para fines educativos, formativos y de certificación institucional. El acceso, navegación y uso de esta plataforma por parte de directivos y docentes constituye la aceptación expresa e irrevocable de nuestras políticas de privacidad y los acuerdos de confidencialidad.
            </p>
        </div>""", unsafe_allow_html=True)
