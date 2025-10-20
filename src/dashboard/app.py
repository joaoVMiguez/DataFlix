import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.db import get_connection

# Configuração da página
st.set_page_config(
    page_title="DataFlix Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache da conexão
@st.cache_resource
def get_db_connection():
    return get_connection()

@st.cache_data(ttl=600) 
def load_overview_stats():
    conn = get_db_connection()
    
    query = """
    SELECT 
        COUNT(*) as total_movies,
        COALESCE(SUM(total_ratings), 0) as total_ratings,
        COALESCE(
            ROUND(
                CASE
                    WHEN SUM(total_ratings) > 0
                    THEN (SUM(avg_rating * total_ratings) / SUM(total_ratings))::numeric
                    ELSE 0
                END,
                2
            ),
            0
        ) as overall_avg_rating,
        COUNT(DISTINCT CASE WHEN total_ratings > 0 THEN movieid END) as rated_movies
    FROM gold.dim_movies
    WHERE avg_rating IS NOT NULL AND total_ratings > 0
    """
    
    df = pd.read_sql(query, conn)
    
    # Converter para tipos Python nativos
    result = df.iloc[0].to_dict()
    return {
        'total_movies': int(result['total_movies']),
        'total_ratings': int(result['total_ratings']),
        'overall_avg_rating': float(result['overall_avg_rating']),
        'rated_movies': int(result['rated_movies'])
    }

@st.cache_data(ttl=600)
def load_top_movies(limit=10):
    conn = get_db_connection()
    query = f"""
    SELECT 
        movieid,
        title,
        release_year,
        avg_rating,
        total_ratings,
        genres
    FROM gold.vw_top_movies
    LIMIT {limit}
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def load_movies_by_decade():
    conn = get_db_connection()
    query = """
    SELECT * FROM gold.vw_movies_by_decade
    ORDER BY decade
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def load_genre_stats():
    conn = get_db_connection()
    query = """
    SELECT * FROM gold.vw_genre_performance
    ORDER BY total_movies DESC
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def load_all_genres():
    """Carrega lista de gêneros para o filtro"""
    conn = get_db_connection()
    query = "SELECT DISTINCT genre_name FROM gold.dim_genres ORDER BY genre_name"
    return pd.read_sql(query, conn)['genre_name'].tolist()

@st.cache_data(ttl=600)
def search_movies(search_term, genre_filter=None, year_min=None, year_max=None, rating_min=None):
    """Busca filmes com filtros"""
    conn = get_db_connection()
    
    # Base query
    query = """
    SELECT 
        m.movieid,
        m.title,
        m.release_year,
        m.avg_rating,
        m.total_ratings,
        STRING_AGG(g.genre_name, ', ' ORDER BY g.genre_name) as genres
    FROM gold.dim_movies m
    LEFT JOIN gold.fact_movie_genres fmg ON m.movieid = fmg.movieid
    LEFT JOIN gold.dim_genres g ON fmg.genre_id = g.genre_id
    WHERE 1=1
    """
    
    params = []
    
    # Filtro de busca por título
    if search_term:
        query += " AND LOWER(m.title) LIKE LOWER(%s)"
        params.append(f"%{search_term}%")
    
    # Filtro de ano
    if year_min:
        query += " AND m.release_year >= %s"
        params.append(year_min)
    
    if year_max:
        query += " AND m.release_year <= %s"
        params.append(year_max)
    
    # Filtro de rating
    if rating_min:
        query += " AND m.avg_rating >= %s"
        params.append(rating_min)
    
    query += """
    GROUP BY m.movieid, m.title, m.release_year, m.avg_rating, m.total_ratings
    """
    
    # Filtro de gênero (após o GROUP BY)
    if genre_filter:
        query += " HAVING STRING_AGG(g.genre_name, ', ' ORDER BY g.genre_name) LIKE %s"
        params.append(f"%{genre_filter}%")
    
    query += " ORDER BY m.total_ratings DESC LIMIT 100"
    
    df = pd.read_sql(query, conn, params=params)
    return df

# ========== HEADER ==========
st.title("🎬 DataFlix Analytics Dashboard")
st.markdown("---")

# ========== SIDEBAR COM FILTROS ==========
with st.sidebar:
    st.header("📊 Filtros e Busca")
    
    # Busca por título
    search_term = st.text_input(
        "🔍 Buscar filme por título",
        placeholder="Digite o nome do filme..."
    )
    
    st.markdown("---")
    
    # Filtros adicionais
    with st.expander("🎛️ Filtros Avançados", expanded=False):
        # Filtro de gênero
        genres = ["Todos"] + load_all_genres()
        genre_filter = st.selectbox("🎭 Gênero", genres)
        if genre_filter == "Todos":
            genre_filter = None
        
        # Filtro de ano
        col1, col2 = st.columns(2)
        with col1:
            year_min = st.number_input("📅 Ano mínimo", min_value=1900, max_value=2024, value=1900, step=1)
        with col2:
            year_max = st.number_input("📅 Ano máximo", min_value=1900, max_value=2024, value=2024, step=1)
        
        # Filtro de rating
        rating_min = st.slider("⭐ Rating mínimo", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    
    st.markdown("---")
    st.info("💡 Use os filtros para explorar o catálogo de filmes!")

# ========== BUSCA DE FILMES ==========
if search_term or genre_filter or rating_min > 0:
    st.header("🔎 Resultados da Busca")
    
    results = search_movies(
        search_term=search_term,
        genre_filter=genre_filter,
        year_min=year_min,
        year_max=year_max,
        rating_min=rating_min
    )
    
    if not results.empty:
        st.success(f"✅ {len(results)} filme(s) encontrado(s)")
        
        # Tabela de resultados
        st.dataframe(
            results,
            column_config={
                "movieid": "ID",
                "title": "Título",
                "release_year": "Ano",
                "avg_rating": st.column_config.NumberColumn("Rating ⭐", format="%.2f"),
                "total_ratings": st.column_config.NumberColumn("Avaliações", format="%d"),
                "genres": "Gêneros"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Detalhes ao clicar (opcional)
        with st.expander("📋 Ver detalhes de um filme"):
            selected_movie = st.selectbox(
                "Selecione um filme:",
                options=results['title'].tolist(),
                index=0
            )
            
            movie_data = results[results['title'] == selected_movie].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎬 Título", movie_data['title'])
            with col2:
                st.metric("📅 Ano", movie_data['release_year'])
            with col3:
                st.metric("⭐ Rating", f"{movie_data['avg_rating']:.2f}")
            
            st.markdown(f"**🎭 Gêneros:** {movie_data['genres']}")
            st.markdown(f"**👥 Total de avaliações:** {movie_data['total_ratings']:,}")
    else:
        st.warning("❌ Nenhum filme encontrado com esses critérios")
    
    st.markdown("---")

# ========== OVERVIEW METRICS ==========
st.header("📈 Visão Geral")

stats = load_overview_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎬 Total de Filmes",
        value=f"{int(stats['total_movies']):,}"
    )

with col2:
    st.metric(
        label="⭐ Avaliações Totais",
        value=f"{int(stats['total_ratings']):,}"
    )

with col3:
    st.metric(
        label="📊 Rating Médio Geral",
        value=f"{stats['overall_avg_rating']:.2f} ⭐"
    )

with col4:
    st.metric(
        label="✅ Filmes Avaliados",
        value=f"{int(stats['rated_movies']):,}"
    )

st.markdown("---")

# ========== TOP MOVIES ==========
st.header("🏆 Top 10 Filmes Mais Bem Avaliados")

top_movies = load_top_movies(10)

fig = px.bar(
    top_movies,
    x='avg_rating',
    y='title',
    orientation='h',
    title='Rating Médio',
    labels={'avg_rating': 'Rating', 'title': 'Filme'},
    color='avg_rating',
    color_continuous_scale='Viridis',
    text='avg_rating'
)
fig.update_layout(height=500, showlegend=False)
fig.update_traces(texttemplate='%{text:.2f}⭐', textposition='outside')

st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 Ver detalhes dos filmes"):
    st.dataframe(
        top_movies,
        hide_index=True,
        use_container_width=True
    )

st.markdown("---")

# ========== MOVIES BY DECADE ==========
st.header("📅 Filmes por Década")

decade_data = load_movies_by_decade()

col1, col2 = st.columns(2)

with col1:
    fig_line = px.line(
        decade_data,
        x='decade',
        y='total_movies',
        title='Quantidade de Filmes por Década',
        markers=True,
        labels={'decade': 'Década', 'total_movies': 'Total de Filmes'}
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    fig_bar = px.bar(
        decade_data,
        x='decade',
        y='total_ratings',
        title='Total de Avaliações por Década',
        labels={'decade': 'Década', 'total_ratings': 'Total de Avaliações'},
        color='avg_rating',
        color_continuous_scale='RdYlGn'
    )
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ========== GENRE STATISTICS ==========
st.header("🎭 Estatísticas por Gênero")

genre_data = load_genre_stats()

col1, col2 = st.columns(2)

with col1:
    fig_genres = px.bar(
        genre_data.head(10),
        x='genre_name',
        y='total_movies',
        title='Top 10 Gêneros - Quantidade de Filmes',
        labels={'genre_name': 'Gênero', 'total_movies': 'Total de Filmes'},
        color='total_movies',
        color_continuous_scale='Blues'
    )
    fig_genres.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_genres, use_container_width=True)

with col2:
    fig_rating = px.scatter(
        genre_data,
        x='total_movies',
        y='avg_rating',
        size='total_ratings',
        hover_data=['genre_name'],
        title='Rating Médio vs Quantidade (tamanho = total avaliações)',
        labels={
            'total_movies': 'Total de Filmes',
            'avg_rating': 'Rating Médio',
            'genre_name': 'Gênero'
        },
        color='avg_rating',
        color_continuous_scale='RdYlGn'
    )
    fig_rating.update_layout(height=400)
    st.plotly_chart(fig_rating, use_container_width=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    "**DataFlix Analytics** | Dados atualizados em tempo real da camada Gold 🏆"
)