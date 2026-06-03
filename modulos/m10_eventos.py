import streamlit as st

def renderizar():
    # --- 1. TÍTULO CON ESTILO ---
    TITULO_HTML = """
    <h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>
        📸 Memorias Institucionales
    </h3>
    """
    st.markdown(TITULO_HTML, unsafe_allow_html=True)
    
    # --- 2. BASE DE DATOS DE LA GALERÍA ---
    # Si a futuro quieres cambiar las fotos por locales, solo pones "foto1.jpg", "foto2.jpg"
    galeria = [
        {"url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", "caption": "🔬 Feria Científica"},
        {"url": "https://images.unsplash.com/photo-1523580494112-071d1694335c?q=80&w=800", "caption": "🎓 Ceremonia de Grados"},
        {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?q=80&w=800", "caption": "🤝 Comunidad Estudiantil"}
        # Puedes agregar más diccionarios aquí y el código las acomodará automáticamente
    ]
    
    # --- 3. MOTOR DE RENDERIZADO (Distribución automática en 3 columnas) ---
    columnas = st.columns(3)
    
    for i, item in enumerate(galeria):
        # El operador % (módulo) asigna la foto a c1, c2 o c3 repetitivamente, creando nuevas filas
        col_actual = columnas[i % 3] 
        
        with col_actual:
            try:
                # use_container_width=True es la forma moderna para que las fotos se adapten 
                # perfecto al tamaño del celular o monitor sin deformarse.
                st.image(item["url"], caption=item["caption"], use_container_width=True)
            except Exception:
                # Si no hay internet o el enlace falla, mostramos una caja gris amigable en su lugar
                st.info(f"🖼️ Imagen no disponible: {item['caption']}")

    st.markdown("<br>", unsafe_allow_html=True) # Espaciado final
