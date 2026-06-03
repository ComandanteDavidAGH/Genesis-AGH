import streamlit as st

def renderizar():
    c1, c2, c3 = st.columns([1, 8, 1])
    
    with c2:
        # --- CONSTANTES DE ESTILO Y TEXTOS (Más fácil de editar a futuro) ---
        BANNER_HTML = """
        <div style="background:rgba(255,255,255,0.95); padding:20px; border-radius:10px; border-left:8px solid #0d1b2a; box-shadow:0 4px 10px rgba(0,0,0,0.05); color:#000; margin-bottom:20px; border:2px solid #000;">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif; text-align: center;">¡Bienvenido a la PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026!</h3>
            <p style="font-size:1.1rem; color:#000; font-family: 'Arial Black', sans-serif; font-weight:bold; text-align: center; margin-bottom:0;"><i>"Seguridad, Control y Excelencia Educativa."</i></p>
        </div>
        """
        
        MISION_HTML = """
        <div style="background:white; padding:20px; border-radius:10px; border:2px solid #000; border-top:8px solid #0d1b2a; height:100%; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
            <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">🎯 Nuestra Misión</h4>
            <p style="color:#000; font-weight:bold; font-size:14.5px; text-align:justify;">Ser la herramienta tecnológica que aporta valor estratégico a la institución en el acompañamiento académico y disciplinario, brindando a docentes y directivos un sistema centralizado, rápido y blindado que optimiza el tiempo y garantiza la precisión de la información.</p>
        </div>
        """
        
        VISION_HTML = """
        <div style="background:white; padding:20px; border-radius:10px; border:2px solid #000; border-top:8px solid #d4af37; height:100%; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
            <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">👁️ Nuestra Visión 2028</h4>
            <p style="color:#000; font-weight:bold; font-size:14.5px; text-align:justify;">Consolidar a Génesis Omega como la plataforma estudiantil de referencia en la transformación digital educativa, integrando inteligencia de datos para elevar la calidad institucional y asegurar el cumplimiento de las normativas del Ministerio de Educación.</p>
        </div>
        """

        # --- RENDERIZADO DE LA INTERFAZ ---
        st.markdown(BANNER_HTML, unsafe_allow_html=True)
        
        col_mision, col_vision = st.columns(2)
        with col_mision:
            st.markdown(MISION_HTML, unsafe_allow_html=True)
        
        with col_vision:
            st.markdown(VISION_HTML, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- ESCUDO CENTRAL CON MANEJO DE ERRORES SEGURO ---
        col_img1, col_img2, col_img3 = st.columns([2.5, 5, 2.5])
        with col_img2:
            try:
                st.image("logo.png", use_container_width=True)
            except FileNotFoundError:
                # 🛡️ Manejo de error específico: te avisa si borraron la imagen por accidente
                st.info("📌 Logo institucional no encontrado. Verifica que 'logo.png' se encuentre en el directorio raíz.")
            except Exception as e:
                # 🛡️ Captura cualquier otro error extraño para que no se caiga la app
                st.error(f"⚠️ Error al cargar el logo: {e}")
