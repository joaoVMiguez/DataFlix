# dashboard/components/navigation.py

import streamlit as st

def render_navigation(current_page=""):
    """
    Renderiza a barra de navegação usando widgets Streamlit, com CSS para fixação e estilo.
    """
    
    # Mapeamento para garantir que o st.switch_page funcione
    page_map = {
        "home": "pages/home.py",
        "movielens": "pages/movielens.py",
        "tmdb": "pages/tmdb.py",
        "box_office": "pages/box_office.py",
    }
    
    # ==================== CSS para Fixar a Barra e Estilizar ====================
    st.markdown("""
    <style>
    /* 1. Ocultar Cabeçalho/Rodapé padrão do Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* 2. Padding para o corpo da página (dando espaço para a barra fixa) */
    /* Este seletor atinge o container principal do conteúdo */
    .main .block-container {
        padding-top: 5rem !important; /* Altura da barra fixa + espaço */
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px; 
    }

    /* 3. Container da Barra de Navegação Streamlit (st.columns) - FIXAÇÃO */
    /* ATENÇÃO: Seletor AGRESSIVO para fixar o primeiro elemento da página */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: white; 
        border-bottom: 1px solid #e5e7eb;
        padding: 0.75rem 2rem; 
    }
    
    /* 4. Ocultar rótulos (Labels) que st.columns adiciona (para evitar quebras de layout) */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) label {
        display: none;
    }

    /* 5. Estilo dos botões de navegação (para parecerem links) */
    .nav-button button {
        background: transparent !important;
        color: #666 !important; /* Cor padrão do link */
        border: none !important;
        box-shadow: none !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.5rem !important;
        transition: all 0.2s !important;
        min-height: 0 !important; /* Ajuste fino */
        height: 100%;
    }

    /* 6. Estilo do botão ativo */
    .nav-button.active button {
        color: #667eea !important; /* Cor do link ativo */
        font-weight: 700 !important;
        border-bottom: 2px solid #667eea !important;
        border-radius: 0 !important;
    }
    
    /* 7. Hover effect */
    .nav-button button:hover {
        color: #667eea !important;
        background: rgba(102, 126, 234, 0.1) !important;
    }

    /* 8. Botão roxo primário padrão (Mantido para os cards de exploração) */
    .stButton button {
        background: #667eea !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ==================== BARRA DE NAVEGAÇÃO STREAMLIT (Widgets Funcionais) ====================
    
    # 1. Colunas para Logo e Links
    # Ajustamos o espaçamento para centralizar os links na direita
    col_logo, col_spacer, col_nav = st.columns([2, 5, 5])

    # 2. Logo em HTML puro (para evitar quebras no CSS)
    with col_logo:
        st.markdown(
            """
            <div style='display: flex; align-items: center; height: 100%;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>📊</span>
                <span style='font-size: 1.2rem; font-weight: 700; color: #667eea;'>DataFlix Analytics</span>
            </div>
            """, unsafe_allow_html=True
        )

    # 3. Links de Navegação (st.button)
    with col_nav:
        # Colunas menores para os 4 botões de navegação
        nav_cols = st.columns(4)
        
        links = [
            ("Home", "home", "🏠"),
            ("MovieLens", "movielens", "🎬"),
            ("TMDB", "tmdb", "📊"),
            ("Box Office", "box_office", "💰"),
        ]

        for idx, (label, key_name, emoji) in enumerate(links):
            with nav_cols[idx]:
                # Adiciona uma div com a classe CSS para estilizar o botão Streamlit
                css_class = "nav-button active" if key_name == current_page else "nav-button"
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                
                # O botão Streamlit real
                if st.button(f"{emoji} {label}", key=f"nav_btn_{key_name}", use_container_width=True):
                    # Se o botão for clicado, navega
                    if key_name in page_map:
                        st.switch_page(page_map[key_name])
                
                st.markdown('</div>', unsafe_allow_html=True)