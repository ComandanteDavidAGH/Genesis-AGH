import streamlit as st

def renderizar():
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.markdown("""<div style="background:rgba(255,255,255,0.95); padding:15px; border-radius:10px; border-left:6px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#000; margin-bottom:15px; border:2px solid #000;">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif;">¡Bienvenido a la PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026!</h3>
            <p style="font-size:1rem; color:#000; font-family: 'Arial Black', sans-serif; font-weight:bold;"><i>"Seguridad, Control y Excelencia Educativa."</i></p>
            </div>""", unsafe_allow_html=True)
            
        col_mision, col_vision = st.columns(2)
        with col_mision:
            st.markdown("""<div style="background:white; padding:15px; border-radius:10px; border:2px solid #000; border-top:6px solid #0d1b2a; height:100%;">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0;">🎯 Nuestra Misión</h4>
                <p style="color:#000; font-weight:bold; font-size:15px;">Formar líderes con excelencia académica y valores humanos, utilizando la tecnología satelital de Génesis AGH para transformar el seguimiento educativo en un proceso de precisión y calidad.</p>
            </div>""", unsafe_allow_html=True)
            
        with col_vision:
            st.markdown("""<div style="background:white; padding:15px; border-radius:10px; border:2px solid #000; border-top:6px solid #d4af37; height:100%;">
                <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0;">👁️ Nuestra Visión 2028</h4>
                <p style="color:#000; font-weight:bold; font-size:15px;">Seremos reconocidos como la institución líder en innovación pedagógica y transformación digital en la región, proyectando talentos hacia el éxito internacional.</p>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", width=400)
        except:
            pass
