"""
Transformações Bronze → Silver para TMDB
"""
import pandas as pd
import json
from datetime import datetime


def transform_movies_main(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma tabela principal de filmes."""
    df = df.copy()
    
    # Renomear colunas
    df = df.rename(columns={'id': 'tmdb_id'})
    
    # Converter tipos
    df['tmdb_id'] = pd.to_numeric(df['tmdb_id'], errors='coerce').astype('Int64')
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce').fillna(0).astype('Int64')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0).astype('Int64')
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce').astype('Int64')
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').astype('Int64')
    
    # Converter datas
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year.astype('Int64')
    df['release_month'] = df['release_date'].dt.month.astype('Int64')
    df['release_decade'] = (df['release_year'] // 10 * 10).astype('Int64')
    
    # Calcular profit e ROI
    df['profit'] = df['revenue'] - df['budget']
    df['roi'] = ((df['revenue'] - df['budget']) / df['budget'] * 100).replace([float('inf'), float('-inf')], pd.NA)
    
    # Flags booleanas
    df['has_budget'] = df['budget'] > 0
    df['has_revenue'] = df['revenue'] > 0
    df['has_overview'] = df['overview'].notna() & (df['overview'].str.len() > 0)
    df['has_poster'] = df['poster_path'].notna()
    df['has_backdrop'] = df['backdrop_path'].notna()
    
    # Categorizar budget
    df['budget_category'] = pd.cut(
        df['budget'],
        bins=[0, 1_000_000, 10_000_000, 50_000_000, float('inf')],
        labels=['Micro', 'Pequeno', 'Médio', 'Grande']
    ).astype(str)
    
    # Quality score
    df['quality_score'] = (
        (df['has_budget'].astype(int) * 20) +
        (df['has_revenue'].astype(int) * 20) +
        (df['has_overview'].astype(int) * 20) +
        (df['has_poster'].astype(int) * 20) +
        (df['has_backdrop'].astype(int) * 20)
    )
    
    # Timestamp
    df['extracted_at'] = pd.to_datetime(df['extracted_at'], errors='coerce')
    
    # Selecionar colunas
    columns = [
        'movielens_id', 'imdb_id', 'tmdb_id', 'title', 'original_title',
        'original_language', 'overview', 'tagline', 'status',
        'release_date', 'release_year', 'release_month', 'release_decade',
        'runtime', 'budget', 'revenue', 'profit', 'roi',
        'popularity', 'vote_average', 'vote_count',
        'adult', 'video', 'homepage', 'poster_path', 'backdrop_path',
        'has_budget', 'has_revenue', 'has_overview', 'has_poster', 'has_backdrop',
        'budget_category', 'quality_score', 'extracted_at'
    ]
    
    return df[columns].reset_index(drop=True)


def transform_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma e normaliza gêneros."""
    genres_list = []
    
    for _, row in df.iterrows():
        # ✅ FIX: Verificar se existe e não é None/NaN
        genres_value = row.get('genres')
        if genres_value is None or (isinstance(genres_value, float) and pd.isna(genres_value)):
            continue
            
        try:
            genres = json.loads(genres_value) if isinstance(genres_value, str) else genres_value
            if not isinstance(genres, list):
                continue
                
            for genre in genres:
                genres_list.append({
                    'movielens_id': int(row['movielens_id']),
                    'imdb_id': row['imdb_id'],
                    'tmdb_id': int(row['id']),
                    'genre_id': int(genre['id']),
                    'genre_name': genre['name']
                })
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    
    return pd.DataFrame(genres_list).reset_index(drop=True)


def transform_production_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma e normaliza empresas produtoras."""
    companies_list = []
    
    for _, row in df.iterrows():
        # ✅ FIX
        companies_value = row.get('production_companies')
        if companies_value is None or (isinstance(companies_value, float) and pd.isna(companies_value)):
            continue
            
        try:
            companies = json.loads(companies_value) if isinstance(companies_value, str) else companies_value
            if not isinstance(companies, list):
                continue
                
            for company in companies:
                companies_list.append({
                    'movielens_id': int(row['movielens_id']),
                    'imdb_id': row['imdb_id'],
                    'tmdb_id': int(row['id']),
                    'company_id': int(company['id']),
                    'company_name': company['name'],
                    'company_logo_path': company.get('logo_path'),
                    'company_country': company.get('origin_country')
                })
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    
    return pd.DataFrame(companies_list).reset_index(drop=True)


def transform_production_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma e normaliza países de produção."""
    countries_list = []
    
    for _, row in df.iterrows():
        # ✅ FIX
        countries_value = row.get('production_countries')
        if countries_value is None or (isinstance(countries_value, float) and pd.isna(countries_value)):
            continue
            
        try:
            countries = json.loads(countries_value) if isinstance(countries_value, str) else countries_value
            if not isinstance(countries, list):
                continue
                
            for country in countries:
                countries_list.append({
                    'movielens_id': int(row['movielens_id']),
                    'imdb_id': row['imdb_id'],
                    'tmdb_id': int(row['id']),
                    'country_code': country['iso_3166_1'],
                    'country_name': country['name']
                })
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    
    return pd.DataFrame(countries_list).reset_index(drop=True)


def transform_spoken_languages(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma e normaliza idiomas."""
    languages_list = []
    
    for _, row in df.iterrows():
        # ✅ FIX
        languages_value = row.get('spoken_languages')
        if languages_value is None or (isinstance(languages_value, float) and pd.isna(languages_value)):
            continue
            
        try:
            languages = json.loads(languages_value) if isinstance(languages_value, str) else languages_value
            if not isinstance(languages, list):
                continue
                
            for language in languages:
                languages_list.append({
                    'movielens_id': int(row['movielens_id']),
                    'imdb_id': row['imdb_id'],
                    'tmdb_id': int(row['id']),
                    'language_code': language['iso_639_1'],
                    'language_name': language['name'],
                    'language_english_name': language.get('english_name')
                })
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    
    return pd.DataFrame(languages_list).reset_index(drop=True)