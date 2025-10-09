import pandas as pd
import re

def transform_movies(df):
    """
    Transforma dados de filmes:
    - Remove duplicados
    - Extrai ano do título
    - Trata valores nulos
    - Padroniza textos
    """
    print(f"  Transformando movies: {len(df)} registros originais")
    
    df = df.drop_duplicates(subset=['movieId'], keep='first')
    df.columns = df.columns.str.lower()
    
    df['release_year'] = df['title'].str.extract(r'\((\d{4})\)$')[0]
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df['release_year'] = df['release_year'].fillna(0).astype(int)
    
    df['title'] = df['title'].fillna('Unknown').str.strip()
    df['genres'] = df['genres'].fillna('(no genres listed)').str.strip()
    df['movieid'] = df['movieid'].astype(int)
    
    print(f"  ✓ Movies transformados: {len(df)} registros finais")
    return df


def transform_ratings(df):
    """
    Transforma dados de ratings:
    - Remove duplicados
    - Valida range de ratings (0.5 a 5.0)
    - Remove registros inválidos
    """
    print(f"  Transformando ratings: {len(df)} registros originais")
    
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates(subset=['userid', 'movieid', 'timestamp'], keep='first')
    
    # Converte para tipos nativos do Python
    df['userid'] = pd.to_numeric(df['userid'], errors='coerce').astype('Int64')
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce').astype('Int64')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype(float)
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').astype('Int64')
    
    df = df.dropna()
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
    
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates(subset=['userid', 'movieid', 'timestamp'], keep='first')
    
    # Usa .loc para evitar SettingWithCopyWarning
    df.loc[:, 'tag'] = df['tag'].str.strip().str.lower()
    df = df[df['tag'].notna() & (df['tag'] != '')]
    
    df['userid'] = pd.to_numeric(df['userid'], errors='coerce').astype('Int64')
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce').astype('Int64')
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').astype('Int64')
    
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
    
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates(subset=['movieid'], keep='first')
    
    df['movieid'] = pd.to_numeric(df['movieid'], errors='coerce').astype('Int64')
    df = df.dropna(subset=['movieid'])
    df['movieid'] = df['movieid'].astype(int)
    
    df['imdbid'] = df['imdbid'].astype(str).replace('nan', None)
    df['tmdbid'] = df['tmdbid'].astype(str).replace('nan', None)
    
    print(f"  ✓ Links transformados: {len(df)} registros finais")
    return df
