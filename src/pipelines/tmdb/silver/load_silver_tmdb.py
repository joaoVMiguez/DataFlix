"""
Pipeline Silver Layer TMDB - Carrega Bronze e transforma para Silver
Segue o mesmo padrão do MovieLens
"""
import pandas as pd
import time
from sqlalchemy import create_engine
from src.minio_client.minio_utils import MinioClient
from src.settings.settings import settings
from src.settings.db import get_connection
from src.utils.logger import setup_logger
from src.pipelines.tmdb.silver.schemas_tmdb import ALL_SCHEMAS
from src.pipelines.tmdb.silver.transformations_silver_tmdb import (
    transform_movies_main,
    transform_genres,
    transform_production_companies,
    transform_production_countries,
    transform_spoken_languages
)

logger = setup_logger(__name__, "tmdb_silver_pipeline.log")


def create_schemas():
    """Cria schemas e tabelas no PostgreSQL."""
    logger.info("🏗️  Criando schemas e tabelas...")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        for schema_sql in ALL_SCHEMAS:
            cur.execute(schema_sql)
        
        conn.commit()
        logger.info("✅ Schemas e tabelas criadas com sucesso")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao criar schemas: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def load_bronze_data() -> pd.DataFrame:
    """Carrega todos os batches Bronze do MinIO."""
    logger.info("📥 Carregando dados Bronze do MinIO...")
    
    minio_client = MinioClient(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY
    )
    
    # Listar arquivos
    objects = minio_client.list_objects(
        bucket=settings.BUCKET_BRONZE_TMDB,
        prefix='movies_v3/',
        recursive=True
    )
    
    batch_files = [obj for obj in objects if obj.endswith('.parquet')]
    logger.info(f"📦 Encontrados {len(batch_files)} batches")
    
    # Carregar todos
    dfs = []
    for i, batch_file in enumerate(batch_files, 1):
        df = minio_client.download_parquet(settings.BUCKET_BRONZE_TMDB, batch_file)
        dfs.append(df)
        if i % 10 == 0:
            logger.info(f"  {i}/{len(batch_files)} batches carregados...")
    
    df_all = pd.concat(dfs, ignore_index=True)
    logger.info(f"✅ {len(df_all):,} filmes carregados do Bronze")
    
    return df_all


def get_sqlalchemy_engine():
    """Cria SQLAlchemy engine para PostgreSQL."""
    connection_string = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    return create_engine(connection_string)


def save_to_postgres(df: pd.DataFrame, table_name: str, schema: str = 'silver_tmdb'):
    """Salva DataFrame no PostgreSQL usando TRUNCATE + APPEND em batches."""
    logger.info(f"💾 Salvando {table_name} no PostgreSQL...")
    
    engine = get_sqlalchemy_engine()
    conn = get_connection()
    
    try:
        # 1. Truncar tabela
        cur = conn.cursor()
        cur.execute(f"TRUNCATE TABLE {schema}.{table_name} RESTART IDENTITY CASCADE")
        conn.commit()
        cur.close()
        logger.info(f"  🗑️  Tabela {schema}.{table_name} truncada")
        
        # 2. Inserir em batches PEQUENOS com COMMIT forçado
        batch_size = 50  # ✅ REDUZIDO PARA 50
        total_batches = (len(df) - 1) // batch_size + 1
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            
            # ✅ USAR CONEXÃO DIRETA (não SQLAlchemy) para controlar COMMIT
            with engine.begin() as connection:
                batch.to_sql(
                    name=table_name,
                    con=connection,
                    schema=schema,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
            # ✅ COMMIT AUTOMÁTICO ao sair do 'with'
            
            batch_num = i // batch_size + 1
            if batch_num % 20 == 0 or batch_num == total_batches:
                logger.info(f"  ✓ Batch {batch_num}/{total_batches} inserido ({len(batch)} registros)")
        
        logger.info(f"✅ {schema}.{table_name}: {len(df):,} registros salvos")
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar {table_name}: {e}")
        raise
    finally:
        conn.close()
        engine.dispose()


def run_silver_pipeline_tmdb():
    """Executa pipeline completo Bronze → Silver TMDB."""
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("🥈 PIPELINE SILVER LAYER - TMDB MOVIES")
    logger.info("=" * 80)
    
    # 1. Criar schemas
    create_schemas()
    
    # 2. Carregar Bronze
    df_bronze = load_bronze_data()
    
    logger.info(f"📋 Colunas disponíveis: {df_bronze.columns.tolist()}")
    logger.info(f"📊 Primeiras 3 linhas:\n{df_bronze.head(3).to_string()}")
    
    # 3. Transformar movies_tmdb
    df_movies = transform_movies_main(df_bronze)
    save_to_postgres(df_movies, 'movies_tmdb', 'silver_tmdb')
    
    # 4. Transformar genres_tmdb
    df_genres = transform_genres(df_bronze)
    save_to_postgres(df_genres, 'genres_tmdb', 'silver_tmdb')
    
    # 5. Transformar production_companies_tmdb
    df_companies = transform_production_companies(df_bronze)
    save_to_postgres(df_companies, 'production_companies_tmdb', 'silver_tmdb')
    
    # 6. Transformar production_countries_tmdb
    df_countries = transform_production_countries(df_bronze)
    save_to_postgres(df_countries, 'production_countries_tmdb', 'silver_tmdb')
    
    # 7. Transformar spoken_languages_tmdb
    df_languages = transform_spoken_languages(df_bronze)
    save_to_postgres(df_languages, 'spoken_languages_tmdb', 'silver_tmdb')
    
    # Resumo
    elapsed = time.time() - start_time
    
    logger.info("=" * 80)
    logger.info("🎉 PIPELINE SILVER CONCLUÍDO!")
    logger.info(f"🎬 movies_tmdb: {len(df_movies):,}")
    logger.info(f"🎭 genres_tmdb: {len(df_genres):,}")
    logger.info(f"🏢 production_companies_tmdb: {len(df_companies):,}")
    logger.info(f"🌍 production_countries_tmdb: {len(df_countries):,}")
    logger.info(f"🗣️  spoken_languages_tmdb: {len(df_languages):,}")
    logger.info(f"⏱️  Tempo total: {elapsed:.2f}s ({elapsed/60:.2f}min)")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_silver_pipeline_tmdb()