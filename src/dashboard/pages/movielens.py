"""Página MovieLens - Estilo Protótipo Moderno"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import movielens
from dashboard.components import charts
from dashboard.components import navigation
import math

# ==================== NAVEGAÇÃO ====================
navigation.render_navigation("movielens")

# ==================== MODAL ====================
@st.dialog("🎬 Detalhes do Filme", width="large")
def show_movie_details(movie_id):
    movie = movielens.get_movie_by_id(movie_id)
    
    if movie is not None:
        st.markdown(f"## {movie['title']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            year_val = movie['release_year']
            st.metric("📅 Ano", int(year_val) if year_val else "N/A")
        
        with col2:
            rating_val = float(movie['avg_rating'])
            st.metric("⭐ Avaliação", f"{rating_val:.2f}/5.00" if rating_val > 0 else "N/A")
        
        with col3:
            num_ratings = int(movie['num_ratings'])
            st.metric("👥 Avaliações", f"{num_ratings:,}")
        
        with col4:
            if num_ratings > 5000:
                pop = "🔥 Blockbuster"
            elif num_ratings > 1000:
                pop = "⭐ Popular"
            else:
                pop = "👍 Conhecido"
            st.metric("Status", pop)
        
        if movie['genres']:
            st.markdown("### 🎭 Gêneros")
            st.info(movie['genres'])
        
        if rating_val > 0:
            st.markdown("### 📊 Análise")
            st.progress(rating_val / 5.0)
            if rating_val >= 4.5:
                st.success("🌟 OBRA-PRIMA")
            elif rating_val >= 4.0:
                st.info("⭐ EXCELENTE")
            elif rating_val >= 3.5:
                st.info("👍 MUITO BOM")

# ==================== ESTADOS ====================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 20
if 'search_text' not in st.session_state:
    st.session_state.search_text = ""
if 'ml_genre' not in st.session_state:
    st.session_state.ml_genre = "All"

# ==================== HEADER ====================
st.markdown("""
<div style='margin-bottom: 1rem;'>
    <h1 style='font-size: 2.5rem; font-weight: 800; margin: 0;'>MovieLens Analytics</h1>
    <p style='color: #666; margin: 0.5rem 0 0 0;'>Análise completa de avaliações e preferências de usuários</p>
</div>
""", unsafe_allow_html=True)

# ==================== STATS CARDS ====================
stats = movielens.get_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Total de Filmes</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>{stats['total_movies']:,}</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>🎬</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Total de Avaliações</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>{int(stats['total_ratings']/1000000)}M+</h2>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>⭐</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #a8caba 0%, #5d4e6d 100%);
                border-radius: 12px; padding: 1.5rem; color: white;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.85rem;'>Avaliação Média</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700;'>{stats['avg_rating']}</h2>
                <p style='margin: 0.25rem 0 0 0; font-size: 0.75rem; opacity: 0.8;'>de 5.00</p>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>📊</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    num_users = 138493  # valor aproximado do MovieLens
    st.markdown(f"""
    <div style='background: white; border: 2px solid #e5e7eb;
                border-radius: 12px; padding: 1.5rem;'>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div>
                <p style='margin: 0; color: #666; font-size: 0.85rem;'>Usuários Ativos</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: 700; color: #111;'>{num_users:,}</h2>
            </div>
            <div style='background: #f3f4f6; padding: 0.5rem; border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>👥</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== BUSCA ====================
st.markdown("""
<div style='background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e5e7eb; margin-bottom: 1.5rem;'>
    <h3 style='margin: 0 0 1rem 0; font-size: 1.2rem; font-weight: 700;'>Buscar Filmes</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 2, 1])

with col1:
    search_text = st.text_input(
        "Nome",
        placeholder="Digite o nome do filme...",
        value=st.session_state.search_text,
        key="search_input",
        label_visibility="collapsed"
    )
    if search_text != st.session_state.search_text:
        st.session_state.search_text = search_text
        st.session_state.current_page = 1

with col2:
    genres = ["All"] + movielens.get_genres()
    genre = st.selectbox(
        "Gênero",
        genres,
        index=genres.index(st.session_state.ml_genre) if st.session_state.ml_genre in genres else 0,
        key="genre_select",
        label_visibility="collapsed"
    )
    st.session_state.ml_genre = genre

with col3:
    if st.button("Limpar Filtros", use_container_width=True):
        st.session_state.search_text = ""
        st.session_state.ml_genre = "All"
        st.session_state.current_page = 1
        st.rerun()

# ==================== RESULTADOS ====================
genre_filter = "" if genre == "All" else genre
min_year, max_year = movielens.get_year_range()

total_results = movielens.count_search_results(
    search_term=search_text,
    genre=genre_filter,
    year_min=min_year,
    year_max=max_year,
    rating_min=0
)

st.markdown(f"""
<div style='margin: 1.5rem 0 1rem 0;'>
    <h3 style='margin: 0; font-size: 1.3rem; font-weight: 700;'>Resultados ({total_results})</h3>
</div>
""", unsafe_allow_html=True)

if total_results > 0:
    items_per_page = st.session_state.items_per_page
    total_pages = math.ceil(total_results / items_per_page)
    current_page = min(st.session_state.current_page, total_pages)
    offset = (current_page - 1) * items_per_page
    
    results = movielens.search_movies(
        search_term=search_text,
        genre=genre_filter,
        year_min=min_year,
        year_max=max_year,
        rating_min=0,
        limit=items_per_page,
        offset=offset
    )
    
    if len(results) > 0:
        # Tabela estilo protótipo
        st.markdown("""
        <style>
        .dataframe-container {
            background: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            results,
            column_config={
                "movieid": None,
                "title": st.column_config.TextColumn("Título", width="large"),
                "release_year": st.column_config.NumberColumn("Ano", width="small"),
                "genres": st.column_config.TextColumn("Gênero", width="medium"),
                "avg_rating": st.column_config.NumberColumn("Avaliação", format="⭐ %.1f", width="small"),
                "num_ratings": st.column_config.NumberColumn("Reviews", width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=500,
            on_select="rerun",
            selection_mode="single-row",
            key=f"table_{current_page}"
        )
        
        # Modal
        table_key = f"table_{current_page}"
        if table_key in st.session_state and "selection" in st.session_state[table_key]:
            selected_rows = st.session_state[table_key]["selection"].get("rows", [])
            if len(selected_rows) > 0 and selected_rows[0] < len(results):
                show_movie_details(int(results.iloc[selected_rows[0]]["movieid"]))
        
        # Paginação
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            cols = st.columns(7)
            with cols[0]:
                if st.button("⏮", disabled=(current_page == 1), use_container_width=True):
                    st.session_state.current_page = 1
                    st.rerun()
            with cols[1]:
                if st.button("◀", disabled=(current_page == 1), use_container_width=True):
                    st.session_state.current_page = current_page - 1
                    st.rerun()
            with cols[2]:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Página</div>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem; font-weight: 700;'>{current_page}</div>", unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>de {total_pages}</div>", unsafe_allow_html=True)
            with cols[5]:
                if st.button("▶", disabled=(current_page == total_pages), use_container_width=True):
                    st.session_state.current_page = current_page + 1
                    st.rerun()
            with cols[6]:
                if st.button("⏭", disabled=(current_page == total_pages), use_container_width=True):
                    st.session_state.current_page = total_pages
                    st.rerun()

# ==================== GRÁFICOS ====================
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top 10 Filmes")
    top_movies = movielens.get_top_movies(10, min_year, max_year)
    if len(top_movies) > 0:
        st.plotly_chart(charts.create_top_movies_chart(top_movies), use_container_width=True)

with col2:
    st.markdown("### 🎭 Top Gêneros")
    genre_data = movielens.get_genre_stats(min_year, max_year)
    if len(genre_data) > 0:
        st.plotly_chart(charts.create_top_genres(genre_data, 10), use_container_width=True)

st.markdown("### 📅 Análise por Década")
decade_data = movielens.get_movies_by_decade(min_year, max_year)
if len(decade_data) > 0:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.create_movies_by_decade(decade_data), use_container_width=True)
    with col2:
        st.plotly_chart(charts.create_ratings_by_decade(decade_data), use_container_width=True)