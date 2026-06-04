import streamlit as st

# =========================================================
# ⚡ ACELERADOR DE MEMORIA (Caché de Galería)
# =========================================================
@st.cache_data
def obtener_galeria():
    """Guarda la base de datos de imágenes en la memoria ultrarrápida"""
    return [
        {"url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", "caption": "🔬 Feria Científica"},
        {"url": "https://images.unsplash.com/photo-1523580494112-071d1694335c?q=80&w=800", "caption": "🎓 Ceremonia de Grados"},
        {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?q=80&w=800", "caption": "🤝 Comunidad Estudiantil"},
        {"url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800", "caption": "📚 Maratón de Lectura"},
        {"url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?q=80&w=800", "caption": "🏆 Olimpiadas Deportivas"},
        {"url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=800", "caption": "🎭 Festival de Arte"}
    ]

# =========================================================
# 👑 MOTOR VISUAL Y RENDERIZADO
# =========================================================
def renderizar():
    # --- 1. MOTOR CSS VIP (Animaciones, Levitación y Marcos) ---
    st.markdown("""
    <style>
    /* Animación de entrada suave desde abajo */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* El cofre blindado de cada fotografía */
    .gallery-card {
        background-color: #ffffff;
        border: 2px solid #0d1b2a;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
        opacity: 0; /* Inicia invisible para la animación */
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    /* Efecto Hover (Levitación e Iluminación Dorada) */
    .gallery-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 25px rgba(212, 175, 55, 0.3);
        border-color: #d4af37;
        z-index: 10;
    }
    
    /* Auto-ajuste de la imagen para que no se deforme */
    .gallery-img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        display: block;
        border-bottom: 2px solid #d4af37;
    }
    
    /* Placa de texto VIP */
    .gallery-caption {
        background-color: #0d1b2a;
        color: #d4af37;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        padding: 10px;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. TÍTULO CON ESTILO ---
    TITULO_HTML = """
    <h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>
        📸 Memorias Institucionales
    </h3>
    """
    st.markdown(TITULO_HTML, unsafe_allow_html=True)
    
    # --- 3. EXTRACCIÓN DE LA CACHÉ ---
    galeria = obtener_galeria()
    
    # --- 4. MOTOR DE RENDERIZADO (Distribución Automática e Inteligente) ---
    columnas = st.columns(3)
    
    for i, item in enumerate(galeria):
        col_actual = columnas[i % 3] 
        
        with col_actual:
            # Multiplicamos el índice por 0.15s para crear el efecto "Cascada" al cargar
            retraso_animacion = i * 0.15 
            
            TARJETA_HTML = f"""
            <div class="gallery-card" style="animation-delay: {retraso_animacion}s;">
                <img class="gallery-img" src="{item['url']}" alt="{item['caption']}">
                <div class="gallery-caption">{item['caption']}</div>
            </div>
            """
            st.markdown(TARJETA_HTML, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
