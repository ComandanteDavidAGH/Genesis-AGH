import streamlit as st

def renderizar():
    # 🚀 ESTILOS AVANZADOS: Animaciones y Efectos Interactivos (Hover)
    st.markdown("""
    <style>
    /* Animación de caída para el Banner */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Animación de subida para las Tarjetas y el Logo */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Clases CSS personalizadas */
    .banner-intro {
        animation: fadeInDown 0.6s ease-out forwards;
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,242,246,0.95) 100%);
        padding: 20px; border-radius: 10px; border-left: 8px solid #0d1b2a; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); color: #000; margin-bottom: 20px; border: 2px solid #000;
    }
    .card-mision-vision {
        background: white; padding: 25px; border-radius: 10px; border: 2px solid #000; 
        height: 100%; box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInUp 0.8s ease-out forwards;
    }
    /* El Efecto de Levitación */
    .card-mision-vision:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(212, 175, 55, 0.25);
        border-color: #d4af37;
    }
    .border-mision { border-top: 8px solid #0d1b2a; }
    .border-vision { border-top: 8px solid #d4af37; }
    
    /* Separador sutil para los textos */
    .divisor-fino { border-top: 2px solid #eeeeee; margin: 10px 0 15px 0; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 8, 1])
    
    with c2:
        # --- CONSTANTES DE ESTILO Y TEXTOS ---
        BANNER_HTML = """
        <div class="banner-intro">
            <h3 style="margin-top:0; color:#000000; font-family: 'Arial Black', sans-serif; text-align: center; text-transform: uppercase; letter-spacing: 1px;">¡Bienvenido a la PLATAFORMA ESTUDIANTIL GÉNESIS OMEGA 2026!</h3>
            <p style="font-size:1.1rem; color:#0d1b2a; font-family: 'Arial Black', sans-serif; font-weight:bold; text-align: center; margin-bottom:0;"><i>"Seguridad, Control y Excelencia Educativa."</i></p>
        </div>
        """
        
        MISION_HTML = """
        <div class="card-mision-vision border-mision">
            <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">🎯 Nuestra Misión</h4>
            <hr class="divisor-fino">
            <p style="color:#222; font-weight:bold; font-size:14.5px; text-align:justify; line-height: 1.5;">Ser la herramienta tecnológica que aporta valor estratégico a la institución en el acompañamiento académico y disciplinario, brindando a docentes y directivos un sistema centralizado, rápido y blindado que optimiza el tiempo y garantiza la precisión de la información.</p>
        </div>
        """
        
        VISION_HTML = """
        <div class="card-mision-vision border-vision">
            <h4 style="color:#000000; font-family: 'Arial Black', sans-serif; margin-top:0; text-align:center;">👁️ Nuestra Visión 2028</h4>
            <hr class="divisor-fino">
            <p style="color:#222; font-weight:bold; font-size:14.5px; text-align:justify; line-height: 1.5;">Consolidar a Génesis Omega como la plataforma estudiantil de referencia en la transformación digital educativa, integrando inteligencia de datos para elevar la calidad institucional y asegurar el cumplimiento de las normativas del Ministerio de Educación.</p>
        </div>
        """

        # --- RENDERIZADO DE LA INTERFAZ ---
        st.markdown(BANNER_HTML, unsafe_allow_html=True)
        
        col_mision, col_vision = st.columns(2)
        with col_mision:
            st.markdown(MISION_HTML, unsafe_allow_html=True)
        
        with col_vision:
            st.markdown(VISION_HTML, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # --- ESCUDO CENTRAL Y LOGO ULTRA-RÁPIDO ---
        col_img1, col_img2, col_img3 = st.columns([3, 4, 3])
        with col_img2:
            # 🎯 EL SALVAVIDAS SATELITAL: Usamos la URL directa para no congelar el servidor
            URL_LOGO_OFICIAL = "https://raw.githubusercontent.com/ComandanteDavidAGH/Genesis-AGH/main/logo.png"
            
            # HTML para centrar, escalar y animar la imagen en milisegundos
            LOGO_HTML = f"""
            <div style="animation: fadeInUp 1s ease-out forwards; text-align:center;">
                <img src="{URL_LOGO_OFICIAL}" style="max-width: 100%; height: auto; object-fit: contain;">
            </div>
            """
            st.markdown(LOGO_HTML, unsafe_allow_html=True)
