"""Componentes de sidebar"""

import streamlit as st
from datetime import datetime

def render_sidebar_header():
    """Header da sidebar com logo e info"""
    st.sidebar.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='margin: 0; color: #FF6B6B;'>🎬</h1>
            <h3 style='margin: 0.5rem 0 0 0;'>DataFlix</h3>
            <p style='margin: 0; font-size: 0.8rem; color: #888;'>Analytics Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

def render_movielens_filters():
    """Filtros do MovieLens - SEM busca de texto"""
    from dashboard.data import movielens
    
    st.sidebar.subheader("🔍 Filtros")
    
    # Obter range de anos
    min_year, max_year = movielens.get_year_range()
    
    # Inicializar session_state
    if 'ml_year_range' not in st.session_state:
        st.session_state.ml_year_range = (min_year, max_year)
    if 'ml_genre' not in st.session_state:
        st.session_state.ml_genre = "Todos"
    if 'ml_rating' not in st.session_state:
        st.session_state.ml_rating = 0.0
    
    # Gênero
    st.sidebar.caption("🎭 GÊNERO")
    genres = ["Todos"] + movielens.get_genres()
    
    try:
        genre_index = genres.index(st.session_state.ml_genre)
    except ValueError:
        genre_index = 0
    
    genre = st.sidebar.selectbox(
        "Gênero",
        genres,
        index=genre_index,
        label_visibility="collapsed",
        key="genre_select"
    )
    st.session_state.ml_genre = genre
    genre_filter = "" if genre == "Todos" else genre
    
    # Período
    st.sidebar.caption("📅 PERÍODO")
    year_range = st.sidebar.slider(
        "Período",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.ml_year_range,
        label_visibility="collapsed",
        key="year_slider"
    )
    st.session_state.ml_year_range = year_range
    
    # Avaliação
    st.sidebar.caption("⭐ AVALIAÇÃO MÍNIMA")
    rating = st.sidebar.slider(
        "Avaliação",
        min_value=0.0,
        max_value=5.0,
        value=st.session_state.ml_rating,
        step=0.5,
        format="%.1f ⭐",
        label_visibility="collapsed",
        key="rating_slider"
    )
    st.session_state.ml_rating = rating
    
    # Limpar filtros
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
        st.session_state.ml_year_range = (min_year, max_year)
        st.session_state.ml_genre = "Todos"
        st.session_state.ml_rating = 0.0
        st.rerun()
    
    # Mostrar filtros ativos
    active_count = 0
    if genre_filter:
        active_count += 1
    if rating > 0:
        active_count += 1
    if year_range != (min_year, max_year):
        active_count += 1
    
    if active_count > 0:
        st.sidebar.success(f"✅ {active_count} filtro(s) ativo(s)")
    
    return genre_filter, rating, year_range

def render_tmdb_filters():
    """Filtros do TMDB"""
    from dashboard.data import tmdb
    
    st.sidebar.subheader("🔍 Filtros TMDB")
    
    min_year, max_year = tmdb.get_year_range()
    
    if 'tmdb_year_range' not in st.session_state:
        st.session_state.tmdb_year_range = (min_year, max_year)
    if 'tmdb_top_n' not in st.session_state:
        st.session_state.tmdb_top_n = 10
    
    st.sidebar.caption("📅 PERÍODO")
    year_range = st.sidebar.slider(
        "Período TMDB",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.tmdb_year_range,
        label_visibility="collapsed",
        key="tmdb_year_slider"
    )
    st.session_state.tmdb_year_range = year_range
    
    st.sidebar.caption("🏆 TOP N FILMES")
    top_n = st.sidebar.slider(
        "Top N",
        min_value=5,
        max_value=50,
        value=st.session_state.tmdb_top_n,
        step=5,
        label_visibility="collapsed",
        key="tmdb_top_slider"
    )
    st.session_state.tmdb_top_n = top_n
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True, key="clear_tmdb"):
        st.session_state.tmdb_year_range = (min_year, max_year)
        st.session_state.tmdb_top_n = 10
        st.rerun()
    
    return year_range, top_n

def render_box_office_filters():
    """Filtros do Box Office"""
    from dashboard.data import box_office
    
    st.sidebar.subheader("🔍 Filtros Box Office")
    
    min_year, max_year = box_office.get_year_range()
    
    if 'box_year_range' not in st.session_state:
        st.session_state.box_year_range = (min_year, max_year)
    if 'box_min_revenue' not in st.session_state:
        st.session_state.box_min_revenue = "Todas"
    
    st.sidebar.caption("📅 PERÍODO")
    year_range = st.sidebar.slider(
        "Período Box Office",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.box_year_range,
        label_visibility="collapsed",
        key="box_year_slider"
    )
    st.session_state.box_year_range = year_range
    
    st.sidebar.caption("💰 RECEITA MÍNIMA")
    min_revenue_options = {
        "Todas": 0,
        "$1M+": 1_000_000,
        "$10M+": 10_000_000,
        "$50M+": 50_000_000,
        "$100M+": 100_000_000
    }
    
    options_list = list(min_revenue_options.keys())
    try:
        revenue_index = options_list.index(st.session_state.box_min_revenue)
    except ValueError:
        revenue_index = 0
    
    min_revenue_label = st.sidebar.select_slider(
        "Receita",
        options=options_list,
        value=options_list[revenue_index],
        label_visibility="collapsed",
        key="box_revenue_slider"
    )
    st.session_state.box_min_revenue = min_revenue_label
    min_revenue = min_revenue_options[min_revenue_label]
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True, key="clear_box"):
        st.session_state.box_year_range = (min_year, max_year)
        st.session_state.box_min_revenue = "Todas"
        st.rerun()
    
    return year_range, min_revenue

def render_sidebar_footer():
    """Footer da sidebar com informações"""
    st.sidebar.markdown("---")
    
    st.sidebar.markdown(
        f"""
        <div style='text-align: center; font-size: 0.75rem; color: #888;'>
            <p style='margin: 0;'>🎬 DataFlix Analytics</p>
            <p style='margin: 0.25rem 0;'>v1.0.0</p>
            <p style='margin: 0.25rem 0;'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )