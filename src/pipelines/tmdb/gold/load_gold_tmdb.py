import sys
import os
sys.path.insert(0, '/app')

import pandas as pd
import time
from sqlalchemy import create_engine
from settings.db import get_connection
from settings.settings import settings
from utils.logger import setup_logger
from pipelines.tmdb.gold.schemas_gold_tmdb import ALL_GOLD_TMDB_SCHEMAS
from pipelines.tmdb.gold.transformations_gold_tmdb import (
    aggregate_movies_tmdb,
    aggregate_box_office,
    aggregate_studio_performance,
    aggregate_country_performance
)

logger = setup_logger(__name__, "tmdb_gold_pipeline.log")


def create_schemas():
    """Cria schemas e tabelas Gold TMDB no PostgreSQL."""
    logger.info("🏗️  Criando schemas e tabelas Gold TMDB...")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        for schema_sql in ALL_GOLD_TMDB_SCHEMAS:
            cur.execute(schema_sql)
        
        conn.commit()
        logger.info("✅ Schemas e tabelas Gold TMDB criadas com sucesso")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao criar schemas: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def get_sqlalchemy_engine():
    """Cria SQLAlchemy engine para PostgreSQL."""
    connection_string = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    return create_engine(connection_string)


def clean_numeric_overflows(df: pd.DataFrame):
    """Limpa valores absurdos que causam overflow no banco."""
    for col in ['roi', 'avg_roi']:
        if col in df.columns:
            df.loc[df[col].abs() > 1e8, col] = None
    return df


def save_to_postgres(df: pd.DataFrame, table_name: str, schema: str = 'gold_tmdb'):
    """Salva DataFrame no PostgreSQL."""
    logger.info(f"💾 Salvando {table_name} no PostgreSQL...")
    
    if df.empty:
        logger.warning(f"⚠️  DataFrame {table_name} vazio, pulando...")
        return
    
    # ✅ Limpar valores absurdos
    df = clean_numeric_overflows(df)
    
    engine = get_sqlalchemy_engine()
    conn = get_connection()
    
    try:
        # Truncar tabela
        cur = conn.cursor()
        cur.execute(f"TRUNCATE TABLE {schema}.{table_name} RESTART IDENTITY CASCADE")
        conn.commit()
        cur.close()
        logger.info(f"  🗑️  Tabela {schema}.{table_name} truncada")
        
        # Inserir em batches
        batch_size = 100
        total_batches = (len(df) - 1) // batch_size + 1
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            
            with engine.begin() as connection:
                batch.to_sql(
                    name=table_name,
                    con=connection,
                    schema=schema,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
            
            batch_num = i // batch_size + 1
            if batch_num % 10 == 0 or batch_num == total_batches:
                logger.info(f"  ✓ Batch {batch_num}/{total_batches} inserido")
        
        logger.info(f"✅ {schema}.{table_name}: {len(df):,} registros salvos")
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar {table_name}: {e}")
        raise
    finally:
        conn.close()
        engine.dispose()


def run_gold_tmdb_pipeline():
    """Executa pipeline completo Silver → Gold TMDB."""
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("🏆 PIPELINE GOLD LAYER - TMDB")
    logger.info("=" * 80)
    
    try:
        # 1. Criar schemas
        create_schemas()
        
        # 2. Agregar dimensão de filmes
        logger.info("\n📦 [1/4] Processando dimensão de filmes TMDB...")
        df_movies = aggregate_movies_tmdb()
        save_to_postgres(df_movies, 'dim_movies_tmdb', 'gold_tmdb')
        
        # 3. Agregar bilheteria
        logger.info("\n📦 [2/4] Processando desempenho de bilheteria...")
        df_box_office = aggregate_box_office()
        save_to_postgres(df_box_office, 'fact_box_office', 'gold_tmdb')
        
        # 4. Agregar estúdios
        logger.info("\n📦 [3/4] Processando performance de estúdios...")
        df_studios = aggregate_studio_performance()
        save_to_postgres(df_studios, 'fact_studio_performance', 'gold_tmdb')
        
        # 5. Agregar países
        logger.info("\n📦 [4/4] Processando performance por país...")
        df_countries = aggregate_country_performance()
        save_to_postgres(df_countries, 'fact_country_performance', 'gold_tmdb')
        
        # Resumo
        elapsed = time.time() - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 PIPELINE GOLD TMDB CONCLUÍDO!")
        logger.info(f"🎬 dim_movies_tmdb: {len(df_movies):,}")
        logger.info(f"💰 fact_box_office: {len(df_box_office):,}")
        logger.info(f"🏢 fact_studio_performance: {len(df_studios):,}")
        logger.info(f"🌍 fact_country_performance: {len(df_countries):,}")
        logger.info(f"⏱️  Tempo total: {elapsed:.2f}s ({elapsed/60:.2f}min)")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erro no pipeline Gold TMDB: {e}")
        raise


if __name__ == "__main__":
    run_gold_tmdb_pipeline()