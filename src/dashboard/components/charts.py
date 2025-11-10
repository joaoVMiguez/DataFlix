"""Gráficos do dashboard"""

import plotly.express as px
import plotly.graph_objects as go

def create_top_movies_chart(df):
    """Gráfico de top filmes"""
    fig = px.bar(
        df,
        x='avg_rating',
        y='title',
        orientation='h',
        title='🏆 Top Filmes por Avaliação',
        labels={'avg_rating': 'Avaliação Média', 'title': 'Filme'},
        color='avg_rating',
        color_continuous_scale='Viridis',
        text='avg_rating'
    )
    fig.update_traces(texttemplate='%{text:.2f}⭐', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        height=500,
        showlegend=False,
        xaxis_title="Avaliação Média",
        yaxis_title=""
    )
    return fig

def create_movies_by_decade(df):
    """Gráfico de filmes por década"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['decade'],
        y=df['total_movies'],
        name='Filmes',
        marker_color='lightblue',
        text=df['total_movies'],
        texttemplate='%{text:,.0f}',
        textposition='outside'
    ))
    
    fig.update_layout(
        title='📅 Filmes por Década',
        xaxis_title='Década',
        yaxis_title='Quantidade de Filmes',
        height=400,
        showlegend=False
    )
    
    return fig

def create_ratings_by_decade(df):
    """Gráfico de avaliações por década"""
    fig = px.line(
        df,
        x='decade',
        y='avg_rating',
        markers=True,
        title='⭐ Avaliação Média por Década',
        labels={'decade': 'Década', 'avg_rating': 'Avaliação Média'}
    )
    
    fig.update_traces(
        line_color='#FF6B6B',
        line_width=3,
        marker=dict(size=10)
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_top_genres(df, limit=10):
    """Gráfico de top gêneros"""
    top_df = df.nlargest(limit, 'total_movies')
    
    fig = px.bar(
        top_df,
        x='total_movies',
        y='genre',
        orientation='h',
        title=f'🎭 Top {limit} Gêneros Mais Populares',
        labels={'total_movies': 'Quantidade de Filmes', 'genre': 'Gênero'},
        color='avg_rating',
        color_continuous_scale='RdYlGn',
        text='total_movies'
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=500,
        xaxis_title="Quantidade de Filmes",
        yaxis_title=""
    )
    
    return fig

# ==================== TMDB ====================

def create_top_revenue_movies_chart(df):
    """Top filmes por receita"""
    df['revenue_millions'] = df['revenue'] / 1_000_000
    
    fig = px.bar(
        df,
        x='revenue_millions',
        y='title',
        orientation='h',
        title='💰 Top Filmes por Receita',
        labels={'revenue_millions': 'Receita (Milhões USD)', 'title': 'Filme'},
        color='revenue_millions',
        color_continuous_scale='Greens',
        text='revenue_millions'
    )
    
    fig.update_traces(texttemplate='$%{text:.1f}M', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=500,
        showlegend=False,
        xaxis_title="Receita (Milhões USD)",
        yaxis_title=""
    )
    
    return fig

def create_revenue_by_year_chart(df):
    """Receita por ano"""
    df['revenue_billions'] = df['total_revenue'] / 1_000_000_000
    
    fig = px.area(
        df,
        x='year',
        y='revenue_billions',
        title='📊 Evolução da Receita Total por Ano',
        labels={'year': 'Ano', 'revenue_billions': 'Receita (Bilhões USD)'}
    )
    
    fig.update_traces(line_color='#2E86AB', fill='tozeroy')
    fig.update_layout(height=400)
    
    return fig

# ==================== BOX OFFICE ====================

def create_top_profitable_movies_chart(df):
    """Filmes mais lucrativos"""
    df['profit_millions'] = df['profit'] / 1_000_000
    
    fig = px.bar(
        df,
        x='profit_millions',
        y='title',
        orientation='h',
        title='💎 Filmes Mais Lucrativos',
        labels={'profit_millions': 'Lucro (Milhões USD)', 'title': 'Filme'},
        color='roi',
        color_continuous_scale='RdYlGn',
        text='profit_millions'
    )
    
    fig.update_traces(texttemplate='$%{text:.1f}M', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=500,
        xaxis_title="Lucro (Milhões USD)",
        yaxis_title=""
    )
    
    return fig

def create_success_rate_chart(df):
    """Taxa de sucesso por ano"""
    fig = px.line(
        df,
        x='year',
        y='success_rate',
        markers=True,
        title='📈 Taxa de Sucesso (% Filmes Lucrativos) por Ano',
        labels={'year': 'Ano', 'success_rate': '% Lucrativos'}
    )
    
    fig.update_traces(
        line_color='#06D6A0',
        line_width=3,
        marker=dict(size=8)
    )
    
    fig.update_layout(
        height=400,
        yaxis=dict(ticksuffix='%', range=[0, 100])
    )
    
    return fig