import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
def renderizar(df, periodo_sel, conn):
    # 🚀 MOTOR VISUAL RESTAURADO: Recuadro y Cabecera VIP
    st.markdown("""
    <style>
    /* Borde y sombra para el editor */
    div[data-testid="stDataEditor"] {
        border: 3px solid #0d1b2a !important;
        border-radius: 0 0 8px 8px !important;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#000000; border-bottom:3px solid #d4af37; padding-bottom:5px; font-family:Arial Black;'>✍️ Registro de Calificaciones</h3>", unsafe_allow_html=True)

    # ... (Tu lógica de seguridad y botones se mantiene igual aquí) ...

    # 👑 FALSO ENCABEZADO VIP PARA CORONAR LA TABLA
    st.markdown("""
    <div style='background-color:#0d1b2a; color:#d4af37; font-family:Arial Black; font-size:13px; text-align:center; padding:10px; border:3px solid #0d1b2a; border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px; letter-spacing:1px;'>
    MATRIZ OFICIAL DE CALIFICACIONES
    </div>
    """, unsafe_allow_html=True)
    
    # 🖨️ RENDERIZADO DEL EDITOR ENCAPSULADO
    st.data_editor(df, use_container_width=True, height=450, key="editor_notas", column_config=config_notas)
