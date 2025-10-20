from minio_client.minio_utils import MinioClient
from config.db import get_connection, insert_dataframe
from src.pipelines.movielens.silver.transformations import (
    transform_movies,
    transform_movie_genres,
    transform_ratings,
    transform_tags,
    transform_links
)
import pandas as pd
import os

def get_native_values(df):
    """
    Converte um DataFrame em uma lista de tuplas com valores nativos Python
    """
    df_clean = df.copy() 
    df_clean = df_clean.replace({pd.NA: None})
    values = [tuple(row) for row in df_clean.itertuples(index=False)]
    return values


def insert_genres_with_mapping(df_genres, df_movie_genres, conn):
    """
    Insere gêneros e retorna mapeamento genre_name -> genre_id
    Depois insere os relacionamentos movie-genre
    """
    # 1. Insere gêneros únicos
    print("  → Inserindo gêneros únicos...")
    if not df_genres.empty:
        values = get_native_values(df_genres)
        insert_dataframe(
            columns=['genre_name'],
            table_name='silver.genres_silver',
            conn=conn,
            values=values
        )
    
    # 2. Busca o mapeamento genre_name -> genre_id do banco
    query = "SELECT genre_id, genre_name FROM silver.genres_silver"
    genre_mapping = pd.read_sql(query, conn)
    genre_dict = dict(zip(genre_mapping['genre_name'], genre_mapping['genre_id']))
    
    # 3. Mapeia genre_name para genre_id no DataFrame
    df_movie_genres['genre_id'] = df_movie_genres['genre_name'].map(genre_dict)
    df_movie_genres = df_movie_genres[['movieid', 'genre_id']].dropna()
    df_movie_genres['genre_id'] = df_movie_genres['genre_id'].astype(int)
    
    # 4. Insere relacionamentos
    print("  → Inserindo relacionamentos filme-gênero...")
    if not df_movie_genres.empty:
        values = get_native_values(df_movie_genres)
        insert_dataframe(
            columns=['movieid', 'genre_id'],
            table_name='silver.movie_genres_silver',
            conn=conn,
            values=values
        )


def load_silver_pipeline(recreate_schema=False):
    """
    Pipeline que baixa os CSVs do MinIO, aplica transformações
    e carrega nas tabelas Silver do Postgres
    """
    print("\n=== Iniciando Pipeline Silver ===\n")
    
    # Configurações
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    BUCKET_RAW = "dataflixraw"

    # Conecta no MinIO e Postgres
    minio_client = MinioClient(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    conn = get_connection()

    # Recria schema se solicitado
    if recreate_schema:
        from src.pipelines.movielens.silver.schemas import create_silver_tables
        print("♻️  Recriando schema Silver...")
        create_silver_tables(conn)
        print()

    # Lista arquivos no bucket
    files = minio_client.list_files(BUCKET_RAW)
    print(f"Arquivos encontrados no bucket '{BUCKET_RAW}': {files}\n")

    # ========== PROCESSA MOVIES (e extrai gêneros) ==========
    if "movies.csv" in files:
        print(f"📥 Processando movies.csv...")
        try:
            df = minio_client.download_csv(BUCKET_RAW, "movies.csv")
            print(f"  - Registros lidos: {len(df)}")
            
            # Transforma movies
            df_movies = transform_movies(df)
            
            # Extrai gêneros normalizados
            df_genres, df_movie_genres = transform_movie_genres(df_movies)
            
            # Remove coluna genres de movies (não será mais usada)
            df_movies = df_movies.drop(columns=['genres'])
            
            # Insere movies
            if not df_movies.empty:
                values = get_native_values(df_movies)
                insert_dataframe(
                    columns=df_movies.columns.tolist(),
                    table_name='silver.movies_silver',
                    conn=conn,
                    values=values
                )
                print(f"  ✅ Movies carregados com sucesso!")
            
            # Insere gêneros e relacionamentos
            insert_genres_with_mapping(df_genres, df_movie_genres, conn)
            print(f"  ✅ Gêneros e relacionamentos carregados!\n")
            
        except Exception as e:
            print(f"  ❌ Erro ao processar movies.csv: {e}\n")
            conn.rollback()
            import traceback
            traceback.print_exc()

    # ========== PROCESSA OUTROS ARQUIVOS ==========
    pipeline_config = {
        "ratings.csv": {
            "table": "silver.ratings_silver",
            "transform": transform_ratings,
            "chunksize": 100_000
        },
        "tags.csv": {
            "table": "silver.tags_silver",
            "transform": transform_tags,
            "chunksize": 100_000
        },
        "links.csv": {
            "table": "silver.links_silver",
            "transform": transform_links
        }
    }

    for csv_file, config in pipeline_config.items():
        if csv_file not in files:
            print(f"⚠️  {csv_file} não encontrado no bucket\n")
            continue

        print(f"📥 Processando {csv_file}...")
        
        try:
            chunksize = config.get("chunksize", None)
            
            if chunksize:
                print(f"  ⚠️  Arquivo grande - processando em chunks...")
                chunk_iterator = minio_client.download_csv(BUCKET_RAW, csv_file, chunksize=chunksize)
                total_inserted = 0

                for chunk_num, df_chunk in enumerate(chunk_iterator, 1):
                    print(f"  - Chunk {chunk_num}: {len(df_chunk)} registros")
                    
                    df_transformed = config["transform"](df_chunk)
                    
                    if not df_transformed.empty:
                        native_values = get_native_values(df_transformed)
                        
                        try:
                            insert_dataframe(
                                columns=df_transformed.columns.tolist(),
                                table_name=config["table"],
                                conn=conn,
                                values=native_values
                            )
                            total_inserted += len(df_transformed)
                        except Exception as e:
                            print(f"    ❌ Erro ao inserir chunk {chunk_num}: {e}")
                            conn.rollback()

                print(f"  ✅ {csv_file} carregado: {total_inserted} registros totais\n")

            else:
                # Arquivos pequenos
                df = minio_client.download_csv(BUCKET_RAW, csv_file)
                print(f"  - Registros lidos: {len(df)}")
                
                df_transformed = config["transform"](df)
                
                if not df_transformed.empty:
                    native_values = get_native_values(df_transformed)
                    
                    try:
                        insert_dataframe(
                            columns=df_transformed.columns.tolist(),
                            table_name=config["table"],
                            conn=conn,
                            values=native_values
                        )
                        print(f"  ✅ {csv_file} carregado com sucesso!\n")
                    except Exception as e:
                        print(f"  ❌ Erro ao processar {csv_file}: {e}\n")
                        conn.rollback()
                else:
                    print(f"  ⚠️  DataFrame vazio após transformações\n")

        except Exception as e:
            print(f"  ❌ Erro geral ao processar {csv_file}: {e}\n")
            import traceback
            traceback.print_exc()

    conn.close()
    print("=== Pipeline Silver Concluída ===\n")