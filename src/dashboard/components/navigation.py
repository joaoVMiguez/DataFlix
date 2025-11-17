"""Componente de navegação superior"""

import streamlit as st

def render_navigation(current_page=""):
    """Renderiza a barra de navegação superior fixa e funcional (sobreposta)"""
    
    # --- Estilos CSS Finais ---
    st.markdown("""
    <style>
    /* Esconder header padrão */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Padding no conteúdo - Dando espaço para a barra fixa */
    .main .block-container {
        padding-top: 5rem !important;
    }
    
    /* Botões GERAIS (roxos) - Mantido */
    .stButton button {
        /* Seus estilos originais para botões roxos */
    }
    
    /* Oculta os botões roxos que aparecem na página principal */
    /* Este CSS foca em encontrar o container (div) que você está usando para os botões e OCULTÁ-LO. */
    /* st.columns gera uma div Streamlit interna. Vamos garantir que o st.container que a envolve suma */
    
    /* ATENÇÃO: Esta é a regra crítica para ocultar os botões roxos abaixo da barra */
    .nav-buttons-placeholder {
        display: none !important;
    }

    /* Container de Sobreposição (INVISÍVEL E CLICÁVEL) */
    .nav-buttons-overlay {
        position: fixed; 
        top: 0; 
        right: 2rem; /* Alinhar com o padding da barra fixa */
        z-index: 1002; /* Fica acima de tudo */
        display: flex; 
        gap: 1.5rem; /* Espaçamento dos links visuais */
        height: 4.25rem; /* Altura da barra fixa */
        align-items: center;
        width: 35%; /* Ajuste percentual para cobrir a área de links */
        justify-content: space-between;
    }
    
    /* Ajustes específicos para os botões invisíveis */
    .nav-buttons-overlay .stButton {
        height: 100%;
        display: flex;
        align-items: center;
        flex-grow: 1; /* Distribui o espaço */
    }

    .nav-buttons-overlay .stButton button {
        background: transparent !important;
        color: transparent !important; 
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0.5rem !important;
        min-width: 0 !important;
        height: 100%;
        width: 100%;
        font-weight: 500 !important;
    }
    
    .nav-buttons-overlay .stButton button:hover {
        background: rgba(102, 126, 234, 0.1) !important; /* Feedback hover */
        box-shadow: none !important;
        transform: none !important;
    }

    /* Ocultar o texto do botão de forma agressiva */
    .nav-buttons-overlay .stButton button div div {
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Barra fixa em HTML puro (Visual) ---
    st.markdown(f"""
    <div style='position: fixed; top: 0; left: 0; right: 0; background: white; 
              border-bottom: 1px solid #e5e7eb; z-index: 1000; padding: 0.75rem 2rem;'>
        <div style='max-width: 1400px; margin: 0 auto; display: flex; 
                    justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>📊</span>
                <span style='font-size: 1.2rem; font-weight: 700; color: #667eea;'>DataFlix Analytics</span>
            </div>
            <div id='visual-nav-links' style='display: flex; gap: 1.5rem; align-items: center;'>
                <span style='color: {"#667eea" if current_page == "home" else "#666"}; 
                      font-weight: {"700" if current_page == "home" else "500"}; cursor: pointer; padding: 0.5rem 0.5rem;'>
                    🏠 Home
                </span>
                <span style='color: {"#667eea" if current_page == "movielens" else "#666"}; 
                      font-weight: {"700" if current_page == "movielens" else "500"}; cursor: pointer; padding: 0.5rem 0.5rem;'>
                    🎬 MovieLens
                </span>
                <span style='color: {"#667eea" if current_page == "tmdb" else "#666"}; 
                      font-weight: {"700" if current_page == "tmdb" else "500"}; cursor: pointer; padding: 0.5rem 0.5rem;'>
                    📊 TMDB
                </span>
                <span style='color: {"#667eea" if current_page == "box_office" else "#666"}; 
                      font-weight: {"700" if current_page == "box_office" else "500"}; cursor: pointer; padding: 0.5rem 0.5rem;'>
                    💰 Box Office
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Container para ocultar os botões roxos abaixo da barra ---
    # Coloque st.columns dentro de um container com classe 'nav-buttons-placeholder'
    st.markdown('<div class="nav-buttons-placeholder">', unsafe_allow_html=True)
    
    # O Streamlit renderiza os botões, mas o CSS com 'display: none' na classe acima os oculta totalmente.
    # Usamos st.columns para criar os botões funcionais que serão ativados pela sobreposição.
    cols_hidden = st.columns([1, 1, 1, 1])

    with cols_hidden[0]:
        if st.button("Home_oculto", key="nav_home_oculto"):
            st.switch_page("pages/home.py")
    
    with cols_hidden[1]:
        if st.button("MovieLens_oculto", key="nav_movielens_oculto"):
            st.switch_page("pages/movielens.py")
    
    with cols_hidden[2]:
        if st.button("TMDB_oculto", key="nav_tmdb_oculto"):
            st.switch_page("pages/tmdb.py")
    
    with cols_hidden[3]:
        if st.button("Box_Office_oculto", key="nav_box_office_oculto"):
            st.switch_page("pages/box_office.py")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Botões funcionais (invisíveis) sobrepostos na barra fixa ---
    # Estes botões são a sua área de clique invisível. Eles precisam de uma lógica que ative os botões ocultos.
    # Infelizmente, o Streamlit não permite ativar um botão de dentro de outro de forma simples.
    
    # O método mais simples, que funcionou para outros, é manter os botões transparentes fixos, 
    # sem a necessidade de uma segunda renderização de botões ocultos.
    # Vamos usar os botões FIXOS/TRANSPARENTES como os únicos funcionais.
    
    st.markdown('<div class="nav-buttons-overlay">', unsafe_allow_html=True)
    
    # Usamos st.columns para alinhar os botões funcionais
    cols = st.columns([1, 1, 1, 1]) 

    with cols[0]:
        if st.button("Home_overlay", key="nav_home_overlay"): # Será clicável e transparente
            st.switch_page("pages/home.py")
    
    with cols[1]:
        if st.button("MovieLens_overlay", key="nav_movielens_overlay"):
            st.switch_page("pages/movielens.py")
    
    with cols[2]:
        if st.button("TMDB_overlay", key="nav_tmdb_overlay"):
            st.switch_page("pages/tmdb.py")
    
    with cols[3]:
        if st.button("Box Office_overlay", key="nav_box_office_overlay"):
            st.switch_page("pages/box_office.py")
    
    st.markdown('</div>', unsafe_allow_html=True)