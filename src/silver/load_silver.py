# load_silver.py
from minio_client.minio_utils import MinioClient
from config.db import get_connection, insert_dataframe
from silver.transformations import (
    transform_movies,
    transform_ratings,
    transform_tags,
    transform_links
)
import pandas as pd
import os

# Função para converter DataFrames para uma lista de tuplas com tipos nativos Python
def get_native_values(df):
    """
    Converte um DataFrame em uma lista de tuplas com valores que 
    o psycopg2 consegue serializar (tipos nativos Python: int, float, str, None).
    Valores nulos de tipos estendidos (como pd.NA/Int64) são substituídos por None.
    """
    # 1. Cria uma cópia para evitar warnings e garante que colunas sejam tratadas como tipos objeto/puros
    # O uso de itertuples() ou tolist() em colunas limpas geralmente resolve o problema do 'np'.
    
    # É mais seguro substituir nulos explicitamente se houver tipos Int64 (inteiros nulos)
    df_clean = df.copy() 
    df_clean = df_clean.replace({pd.NA: None})
    
    # Retorna uma lista de tuplas, onde cada item da tupla é um tipo nativo Python
    # O .itertuples(index=False) é eficiente para gerar esses valores.
    values = [tuple(row) for row in df_clean.itertuples(index=False)]
    return values


def load_silver_pipeline():
    """
    Pipeline que baixa os CSVs do MinIO, aplica transformações
    e carrega nas tabelas Silver do Postgres.
    """
    print("\n=== Iniciando Pipeline Silver ===\n")
    
    # Configurações
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    BUCKET_RAW = "dataflixraw"

    # Conecta no MinIO e Postgres
    minio_client = MinioClient(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    # Abre a conexão uma vez
    conn = get_connection() 

    # Lista arquivos no bucket
    files = minio_client.list_files(BUCKET_RAW)
    print(f"Arquivos encontrados no bucket '{BUCKET_RAW}': {files}\n")

    # Mapeamento de arquivos, tabelas e funções de transformação
    pipeline_config = {
        "movies.csv": {
            "table": "silver.movies_silver",
            "transform": transform_movies
        },
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

    # Processa cada arquivo
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
                        # GERA OS VALORES NATIVOS AQUI!
                        native_values = get_native_values(df_transformed)
                        
                        try:
                            # Passa a lista de valores nativos para a função de inserção
                            insert_dataframe(df_transformed.columns.tolist(), config["table"], conn, values=native_values)
                            total_inserted += len(df_transformed)
                        except Exception as e:
                            print(f"    ❌ Erro ao inserir chunk {chunk_num}: {e}")
                            # ESSENCIAL: Faz o rollback para limpar o estado de transação abortada
                            conn.rollback() 
                            # Opcional: Para em caso de erro crítico
                            # break

                print(f"  ✅ {csv_file} carregado: {total_inserted} registros totais\n")

            else:
                # Arquivos pequenos (movies.csv e links.csv)
                df = minio_client.download_csv(BUCKET_RAW, csv_file)
                print(f"  - Registros lidos: {len(df)}")
                print(f"  - Colunas: {list(df.columns)}")

                df_transformed = config["transform"](df)
                
                if not df_transformed.empty:
                    # GERA OS VALORES NATIVOS AQUI!
                    native_values = get_native_values(df_transformed)
                    
                    try:
                        # Passa a lista de valores nativos
                        insert_dataframe(df_transformed.columns.tolist(), config["table"], conn, values=native_values)
                        print(f"  ✅ {csv_file} carregado com sucesso!\n")
                    except Exception as e:
                        print(f"  ❌ Erro ao processar {csv_file}: {e}\n")
                        # ESSENCIAL: Faz o rollback para limpar o estado de transação abortada
                        conn.rollback()
                        
                else:
                    print(f"  ⚠️  DataFrame vazio após transformações\n")

        except Exception as e:
            print(f"  ❌ Erro geral ao processar {csv_file}: {e}\n")
            import traceback
            traceback.print_exc()

    # Fecha a conexão após o loop
    conn.close() 
    print("=== Pipeline Silver Concluída ===\n")