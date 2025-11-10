"""Página MovieLens - Interface Moderna"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from dashboard.data import movielens
from dashboard.components import charts, sidebar
import math

# ==================== SIDEBAR ====================
sidebar.render_sidebar_header()
genre_filter, rating, year_range = sidebar.render_movielens_filters()
sidebar.render_sidebar_footer()

# ==================== ESTILOS CSS ====================
st.markdown(
    """
    <style>
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .modern-search {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
    }
    
    .charts-container {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================== HEADER ====================
st.title("🎬 MovieLens Analytics")
st.markdown("### Explore o maior catálogo de avaliações de filmes")

# ==================== INICIALIZAR ESTADOS ====================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 10
if 'search_text' not in st.session_state:
    st.session_state.search_text = ""

# ==================== BUSCA AVANÇADA COM PAGINAÇÃO ====================
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("## 🔍 Busca Avançada")

# Obter range de anos
min_year, max_year = movielens.get_year_range()

# Input de busca e seletor ALINHADOS na mesma linha
col1, col2 = st.columns([4, 1])

with col1:
    search_text = st.text_input(
        "🔎 Digite o nome do filme",
        placeholder="Ex: Matrix, Inception, Avatar...",
        key="search_input",
        value=st.session_state.search_text
    )
    # Atualizar o estado e resetar página
    if search_text != st.session_state.search_text:
        st.session_state.search_text = search_text
        st.session_state.current_page = 1

with col2:
    items_per_page = st.selectbox(
        "Por página",
        [10, 20, 50, 100],
        index=[10, 20, 50, 100].index(st.session_state.items_per_page),
        key="items_select"
    )
    if items_per_page != st.session_state.items_per_page:
        st.session_state.items_per_page = items_per_page
        st.session_state.current_page = 1

# Filtros rápidos
st.markdown("### ⚡ Filtros Rápidos")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📅 Últimos 5 Anos", use_container_width=True, key="btn_5years"):
        st.session_state.ml_year_range = (max_year - 5, max_year)
        st.session_state.current_page = 1
        st.rerun()

with col2:
    if st.button("📆 Última Década", use_container_width=True, key="btn_decade"):
        st.session_state.ml_year_range = (max_year - 10, max_year)
        st.session_state.current_page = 1
        st.rerun()

with col3:
    if st.button("🔥 Populares", use_container_width=True, key="btn_popular"):
        st.session_state.ml_rating = 4.0
        st.session_state.current_page = 1
        st.rerun()

with col4:
    if st.button("🎭 Clássicos", use_container_width=True, key="btn_classics"):
        st.session_state.ml_year_range = (min_year, 2000)
        st.session_state.ml_rating = 4.0
        st.session_state.current_page = 1
        st.rerun()

with col5:
    if st.button("🔄 Limpar Tudo", use_container_width=True, type="secondary", key="btn_clear"):
        # Limpar filtros da sidebar
        st.session_state.ml_year_range = (min_year, max_year)
        st.session_state.ml_genre = "Todos"
        st.session_state.ml_rating = 0.0
        st.session_state.current_page = 1
        
        # Limpar busca - REINICIALIZAR ao invés de deletar
        st.session_state.search_text = ""
        
        st.rerun()

# Mostrar filtros ativos
active_filters = []
if st.session_state.search_text:
    active_filters.append(f"🔎 '{st.session_state.search_text}'")
if genre_filter:
    active_filters.append(f"🎭 {genre_filter}")
if rating > 0:
    active_filters.append(f"⭐ ≥{rating}")
if year_range != (min_year, max_year):
    active_filters.append(f"📅 {year_range[0]}-{year_range[1]}")

if active_filters:
    st.info("**Filtros ativos:** " + " • ".join(active_filters))

# Buscar total de resultados
total_results = movielens.count_search_results(
    search_term=st.session_state.search_text,
    genre=genre_filter,
    year_min=year_range[0],
    year_max=year_range[1],
    rating_min=rating
)

if total_results > 0:
    # Calcular paginação
    total_pages = math.ceil(total_results / st.session_state.items_per_page)
    current_page = st.session_state.current_page
    
    # Validar página atual
    if current_page > total_pages:
        current_page = 1
        st.session_state.current_page = 1
    
    offset = (current_page - 1) * st.session_state.items_per_page
    
    # Buscar dados
    results = movielens.search_movies(
        search_term=st.session_state.search_text,
        genre=genre_filter,
        year_min=year_range[0],
        year_max=year_range[1],
        rating_min=rating,
        limit=st.session_state.items_per_page,
        offset=offset
    )
    
    if len(results) > 0:
        # Métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📊 Total", f"{total_results:,}")
        with col2:
            st.metric("📄 Página", f"{current_page}/{total_pages}")
        with col3:
            st.metric("⭐ Média", f"{results['avg_rating'].mean():.2f}")
        with col4:
            st.metric("🏆 Melhor", f"{results['avg_rating'].max():.2f}")
        with col5:
            st.metric("📈 Avaliações", f"{results['num_ratings'].sum():,}")
        
        # Tabela
        st.dataframe(
            results,
            column_config={
                "movieid": st.column_config.NumberColumn("ID", width="small"),
                "title": st.column_config.TextColumn("🎬 Título", width="large"),
                "release_year": st.column_config.NumberColumn("📅 Ano", width="small"),
                "genres": st.column_config.TextColumn("🎭 Gêneros", width="medium"),
                "avg_rating": st.column_config.NumberColumn("⭐", format="%.2f", width="small"),
                "num_ratings": st.column_config.NumberColumn("👥", width="small")
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        # Paginação
        st.markdown("### 📄 Navegação")
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ Primeira", disabled=(current_page == 1), use_container_width=True, key="btn_first"):
                st.session_state.current_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Anterior", disabled=(current_page == 1), use_container_width=True, key="btn_prev"):
                st.session_state.current_page = current_page - 1
                st.rerun()
        
        with col3:
            page_options = list(range(1, min(total_pages + 1, 101)))
            selected_page = st.selectbox(
                "Ir para página:",
                page_options,
                index=min(current_page - 1, len(page_options) - 1),
                key="page_selector",
                label_visibility="collapsed"
            )
            if selected_page != current_page:
                st.session_state.current_page = selected_page
                st.rerun()
        
        with col4:
            if st.button("▶️ Próxima", disabled=(current_page == total_pages), use_container_width=True, key="btn_next"):
                st.session_state.current_page = current_page + 1
                st.rerun()
        
        with col5:
            if st.button("⏭️ Última", disabled=(current_page == total_pages), use_container_width=True, key="btn_last"):
                st.session_state.current_page = total_pages
                st.rerun()
        
        st.caption(f"Mostrando {offset + 1}-{min(offset + st.session_state.items_per_page, total_results)} de {total_results:,} resultados")
    else:
        st.warning("❌ Nenhum filme encontrado")
else:
    st.info("💡 Use os filtros acima ou a barra lateral para explorar o catálogo")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== BUSCA INDIVIDUAL ====================
st.markdown('<div class="modern-search">', unsafe_allow_html=True)
st.markdown("## 🎯 Consultar Filme Específico")

if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None
if 'movie_search_term' not in st.session_state:
    st.session_state.movie_search_term = ""

col1, col2 = st.columns([5, 1])
with col1:
    movie_search = st.text_input(
        "Digite o nome do filme:",
        placeholder="Ex: The Shawshank Redemption, Avatar...",
        key="movie_detail_search",
        value=st.session_state.movie_search_term,
        label_visibility="collapsed"
    )
with col2:
    search_movie_btn = st.button("🔍 Buscar", use_container_width=True, type="primary", key="btn_search_movie")

if search_movie_btn and movie_search:
    st.session_state.movie_search_term = movie_search
    st.session_state.selected_movie_id = None
    movie_results = movielens.get_movie_details(movie_search)
    
    if len(movie_results) > 0:
        st.session_state.movie_results = movie_results
    else:
        st.session_state.movie_results = None

if 'movie_results' in st.session_state and st.session_state.movie_results is not None:
    movie_results = st.session_state.movie_results
    
    if len(movie_results) > 1:
        st.success(f"✅ {len(movie_results)} filmes encontrados")
        
        options_dict = {}
        for idx, row in movie_results.iterrows():
            year = int(row['release_year']) if row['release_year'] else "N/A"
            rating_val = float(row['avg_rating'])
            rating_str = f"{rating_val:.2f}" if rating_val > 0 else "N/A"
            label = f"{row['title']} ({year}) - ⭐{rating_str}"
            options_dict[label] = row['movieid']
        
        selected_label = st.selectbox(
            "Selecione o filme:",
            list(options_dict.keys()),
            key="movie_selector",
            label_visibility="collapsed"
        )
        
        if selected_label:
            st.session_state.selected_movie_id = options_dict[selected_label]
    
    elif len(movie_results) == 1:
        st.session_state.selected_movie_id = movie_results.iloc[0]['movieid']

if st.session_state.selected_movie_id:
    selected_movie = movielens.get_movie_by_id(st.session_state.selected_movie_id)
    
    if selected_movie is not None:
        st.markdown(f"### 🎬 {selected_movie['title']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            year_val = selected_movie['release_year']
            st.metric("📅 Ano", int(year_val) if year_val else "N/A")
        
        with col2:
            rating_val = float(selected_movie['avg_rating'])
            st.metric("⭐ Nota", f"{rating_val:.2f}" if rating_val > 0 else "N/A")
        
        with col3:
            num_ratings = int(selected_movie['num_ratings'])
            st.metric("👥 Avaliações", f"{num_ratings:,}")
        
        with col4:
            if num_ratings > 5000:
                pop = "🔥 Blockbuster"
            elif num_ratings > 1000:
                pop = "⭐ Popular"
            elif num_ratings > 500:
                pop = "👍 Conhecido"
            else:
                pop = "🆕 Nicho"
            st.metric("📊 Status", pop)
        
        if selected_movie['genres']:
            st.info(f"🎭 **Gêneros:** {selected_movie['genres']}")
        
        if rating_val > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.progress(rating_val / 5.0)
                st.caption(f"{rating_val:.2f} / 5.00")
            
            with col2:
                if rating_val >= 4.5:
                    st.success("🌟 Obra-Prima")
                elif rating_val >= 4.0:
                    st.info("⭐ Excelente")
                elif rating_val >= 3.5:
                    st.info("👍 Muito Bom")
                else:
                    st.warning("😐 Regular")
        
        if st.button("🔄 Nova Consulta", key="btn_new_search"):
            st.session_state.selected_movie_id = None
            st.session_state.movie_results = None
            st.session_state.movie_search_term = ""
            st.rerun()

elif st.session_state.movie_search_term and 'movie_results' in st.session_state and st.session_state.movie_results is None:
    st.error(f"❌ Nenhum resultado para: '{st.session_state.movie_search_term}'")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== ESTATÍSTICAS ====================
st.markdown('<div class="stats-container">', unsafe_allow_html=True)
st.markdown("## 📊 Estatísticas Gerais")

stats = movielens.get_stats()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎬 Filmes", f"{stats['total_movies']:,}")
with col2:
    st.metric("⭐ Avaliações", f"{stats['total_ratings']:,}")
with col3:
    st.metric("📊 Média", f"{stats['avg_rating']} ⭐")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== GRÁFICOS ====================
st.markdown('<div class="charts-container">', unsafe_allow_html=True)
st.markdown("## 📈 Análises Visuais")

st.subheader("🏆 Top 10 Filmes")
top_movies = movielens.get_top_movies(10, year_range[0], year_range[1])
if len(top_movies) > 0:
    st.plotly_chart(charts.create_top_movies_chart(top_movies), use_container_width=True)

st.subheader("📅 Por Década")
decade_data = movielens.get_movies_by_decade(year_range[0], year_range[1])
if len(decade_data) > 0:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.create_movies_by_decade(decade_data), use_container_width=True)
    with col2:
        st.plotly_chart(charts.create_ratings_by_decade(decade_data), use_container_width=True)

st.subheader("🎭 Top Gêneros")
genre_data = movielens.get_genre_stats(year_range[0], year_range[1])
if len(genre_data) > 0:
    st.plotly_chart(charts.create_top_genres(genre_data, 10), use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

st.caption("💡 Use os filtros rápidos ou a barra lateral para análises específicas")