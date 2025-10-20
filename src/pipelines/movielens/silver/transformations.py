import pandas as pd
import re

def transform_movies(df):
    """
    Transforma dados de filmes:
    - Remove duplicados
    - Extrai ano do título
    - Remove ano do título
    - Trata valores nulos
    - Padroniza textos
    """
    print(f"  Transformando movies: {len(df)} registros originais")
    
    # Remove duplicados
    df = df.drop_duplicates(subset=['movieId'], keep='first')
    
    # Renomeia colunas para lowercase
    df.columns = df.columns.str.lower()
    
    # Extrai ano do título (formato: "Movie Name (2020)")
    df['release_year'] = df['title'].str.extract(r'\((\d{4})\)$')[0]
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df['release_year'] = df['release_year'].fillna(0).astype(int)  # ← Volta ao original
    
    # Remove o ano do título (mantém só o nome)
    df['title'] = df['title'].str.replace(r'\s*\(\d{4}\)\s*$', '', regex=True)
    
    # Trata valores nulos
    df['title'] = df['title'].fillna('Unknown').str.strip()
    df['genres'] = df['genres'].fillna('(no genres listed)').str.strip()
    
    # Garante tipos corretos
    df['movieid'] = df['movieid'].astype(int)
    
    print(f"  ✓ Movies transformados: {len(df)} registros finais")
    return df

def transform_movie_genres(df_movies):
    """
    Cria DataFrame de gêneros normalizados a partir dos filmes
    Retorna dois DataFrames: genres e movie_genres
    """
    print(f"  Extraindo gêneros dos filmes...")
    
    # Cria lista de gêneros por filme
    df = df_movies[['movieid', 'genres']].copy()
    df['genres_list'] = df['genres'].str.split('|')
    
    # Explode para criar uma linha por gênero
    df_exploded = df.explode('genres_list')
    df_exploded['genres_list'] = df_exploded['genres_list'].str.strip()
    
    # Remove gêneros inválidos
    df_exploded = df_exploded[
        (df_exploded['genres_list'].notna()) & 
        (df_exploded['genres_list'] != '') &
        (df_exploded['genres_list'] != '(no genres listed)')
    ]
    
    # Cria DataFrame de gêneros únicos
    genres_unique = df_exploded['genres_list'].unique()
    df_genres = pd.DataFrame({
        'genre_name': sorted(genres_unique)
    })
    
    # Cria DataFrame de relacionamento movie-genre
    df_movie_genres = df_exploded[['movieid', 'genres_list']].copy()
    df_movie_genres.columns = ['movieid', 'genre_name']
    df_movie_genres = df_movie_genres.drop_duplicates()
    
    print(f"  ✓ {len(df_genres)} gêneros únicos encontrados")
    print(f"  ✓ {len(df_movie_genres)} relações filme-gênero criadas")
    
    return df_genres, df_movie_genres


def transform_ratings(df):
    """
    Transforma dados de ratings:
    - Remove duplicados
    - Valida range de ratings (0.5 a 5.0)
    - Remove registros inválidos
    """
    print(f"  Transformando ratings: {len(df)} registros originais")
    
    # Renomeia colunas para lowercase
    df.columns = df.columns.str.lower()
    
    # Remove duplicados
    df = df.drop_duplicates(subset=['userid', 'movieid', 'timestamp'], keep='first')
    
    # Converte para tipos nativos do Python
    df['userid'] = pd.to_numeric(df['userid'], errors='coerce').astype('Int64')
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce').astype('Int64')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype(float)
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').astype('Int64')
    
    # Remove registros com valores nulos
    df = df.dropna()
    
    # Valida range de ratings
    df = df[(df['rating'] >= 0.5) & (df['rating'] <= 5.0)]
    
    # Converte para tipos Python puros
    df['userid'] = df['userid'].astype(int)
    df['movieid'] = df['movieid'].astype(int)
    df['timestamp'] = df['timestamp'].astype(int)
    df['rating'] = df['rating'].astype(float)
    
    print(f"  ✓ Ratings transformados: {len(df)} registros finais")
    return df


def transform_tags(df):
    """
    Transforma dados de tags:
    - Remove duplicados
    - Limpa tags (lowercase, remove espaços extras)
    - Remove tags vazias
    """
    print(f"  Transformando tags: {len(df)} registros originais")
    
    # Renomeia colunas para lowercase
    df.columns = df.columns.str.lower()
    
    # Remove duplicados
    df = df.drop_duplicates(subset=['userid', 'movieid', 'timestamp'], keep='first')
    
    # Limpa tags
    df['tag'] = df['tag'].str.strip().str.lower()
    
    # Remove tags vazias ou nulas
    df = df[df['tag'].notna() & (df['tag'] != '')]
    
    # Garante tipos corretos
    df['userid'] = pd.to_numeric(df['userid'], errors='coerce').astype('Int64')
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce').astype('Int64')
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').astype('Int64')
    
    # Remove registros com valores nulos
    df = df.dropna()
    
    df['userid'] = df['userid'].astype(int)
    df['movieid'] = df['movieid'].astype(int)
    df['timestamp'] = df['timestamp'].astype(int)
    
    print(f"  ✓ Tags transformados: {len(df)} registros finais")
    return df


def transform_links(df):
    """
    Transforma dados de links:
    - Remove duplicados
    - Padroniza IDs externos
    """
    print(f"  Transformando links: {len(df)} registros originais")
    
    # Renomeia colunas para lowercase
    df.columns = df.columns.str.lower()
    
    # Remove duplicados
    df = df.drop_duplicates(subset=['movieid'], keep='first')
    
    # Garante tipos corretos
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce')
    
    # Remove registros sem movieid
    df = df.dropna(subset=['movieid'])
    df['movieid'] = df['movieid'].astype(int)
    
    # Converte IDs externos para string
    df['imdbid'] = df['imdbid'].astype(str).replace('nan', None)
    df['tmdbid'] = df['tmdbid'].astype(str).replace('nan', None)
    
    print(f"  ✓ Links transformados: {len(df)} registros finais")
    return df