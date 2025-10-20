import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_connection, insert_dataframe
from gold.transformations_gold import (
    aggregate_movie_ratings,
    aggregate_ratings_by_year,
    enrich_movies_dimension,
    aggregate_genres,
    get_movie_genres_relationships
)
import pandas as pd

def get_native_values(df):
    """Converte DataFrame em lista de tuplas com valores nativos Python"""
    df_clean = df.copy() 
    df_clean = df_clean.replace({pd.NA: None})
    values = [tuple(row) for row in df_clean.itertuples(index=False)]
    return values


def insert_gold_data(df, table_name, conn):
    """Insere dados na camada Gold"""
    if df.empty:
        print(f"  ⚠️  DataFrame vazio para {table_name}")
        return
    
    values = get_native_values(df)
    columns = df.columns.tolist()
    
    try:
        insert_dataframe(
            columns=columns,
            table_name=table_name,
            conn=conn,
            values=values
        )
        print(f"  ✅ {len(df):,} registros inseridos em {table_name}\n")
    except Exception as e:
        print(f"  ❌ Erro ao inserir em {table_name}: {e}\n")
        conn.rollback()
        raise


def load_gold_pipeline(recreate_schema=False):
    """
    Pipeline que transforma dados Silver em Gold (agregados e modelados)
    """
    print("\n" + "="*60)
    print("🏆 INICIANDO PIPELINE GOLD")
    print("="*60 + "\n")
    
    conn = get_connection()
    
    try:
        # 1. Carregar dimensão de gêneros
        print("📦 [1/5] Processando dimensão de gêneros...")
        df_genres = aggregate_genres()
        insert_gold_data(df_genres, 'gold.dim_genres', conn)
        
        # 2. Carregar dimensão de filmes (enriquecida)
        print("📦 [2/5] Processando dimensão de filmes...")
        df_movies = enrich_movies_dimension()
        insert_gold_data(df_movies, 'gold.dim_movies', conn)
        
        # 3. Carregar fato de ratings por filme
        print("📦 [3/5] Processando fato de ratings...")
        df_ratings = aggregate_movie_ratings()
        insert_gold_data(df_ratings, 'gold.fact_movie_ratings', conn)
        
        # 4. Carregar fato de ratings por ano
        print("📦 [4/5] Processando fato temporal...")
        df_by_year = aggregate_ratings_by_year()
        insert_gold_data(df_by_year, 'gold.fact_ratings_by_year', conn)
        
        # 5. Carregar relacionamentos filme-gênero
        print("📦 [5/5] Processando relacionamentos filme-gênero...")
        df_movie_genres = get_movie_genres_relationships()
        insert_gold_data(df_movie_genres, 'gold.fact_movie_genres', conn)
        
        print("="*60)
        print("✅ PIPELINE GOLD CONCLUÍDO COM SUCESSO!")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ ERRO NO PIPELINE GOLD: {e}")
        print("="*60 + "\n")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    load_gold_pipeline()