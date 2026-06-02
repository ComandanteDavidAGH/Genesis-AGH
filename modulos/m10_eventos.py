import streamlit as st

def renderizar():
    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>📸 Memorias Institucionales</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.image("https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=800", caption="Feria Científica")
    c2.image("https://images.unsplash.com/photo-1523580494112-071d1694335c?q=80&w=800", caption="Ceremonia de Grados")
    c3.image("https://images.unsplash.com/photo-1511632765486-a01980e01a18?q=80&w=800", caption="Comunidad Estudiantil")
