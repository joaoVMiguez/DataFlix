"""
Orquestrador da Camada Bronze TMDB.
Executa todas as extrações em sequência.
"""

import time
from src.utils.logger import setup_logger
from src.pipelines.tmdb.bronze.extract_tmdb_movies import run_extraction as run_movies
from src.pipelines.tmdb.bronze.extract_tmdb_credits import run_credits_extraction

logger = setup_logger(__name__, "tmdb_bronze_pipeline.log")


def run_bronze_pipeline(mode: str = "test"):
    """
    Executa pipeline completo da camada Bronze.
    
    Args:
        mode: 'test' (10 filmes) ou 'full' (todos)
    """
    start_time = time.time()
    
    logger.info("=" * 90)
    logger.info("🎬 INICIANDO PIPELINE BRONZE TMDB COMPLETO")
    logger.info("=" * 90)
    
    limit = 10 if mode == "test" else None
    
    try:
        # PASSO 1: Extrair filmes
        logger.info("\n" + "=" * 90)
        logger.info("📝 PASSO 1/2: Extraindo dados dos filmes...")
        logger.info("=" * 90)
        run_movies(batch_size=100, limit=limit, skip_existing=True)
        
        # PASSO 2: Extrair créditos
        logger.info("\n" + "=" * 90)
        logger.info("🎭 PASSO 2/2: Extraindo créditos (elenco e equipe)...")
        logger.info("=" * 90)
        run_credits_extraction(limit=limit, skip_existing=True)
        
        elapsed = time.time() - start_time
        
        logger.info("\n" + "=" * 90)
        logger.info("🎉 PIPELINE BRONZE CONCLUÍDO COM SUCESSO!")
        logger.info(f"⏱️  Tempo total: {elapsed/3600:.2f} horas")
        logger.info("=" * 90)
        
    except Exception as e:
        logger.error(f"❌ Erro no pipeline: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if "--full" in sys.argv:
        logger.warning("🚀 MODO PRODUÇÃO: Pipeline completo (6-8 horas)")
        logger.warning("⏱️  Pressione Ctrl+C nos próximos 5 segundos para cancelar...")
        time.sleep(5)
        run_bronze_pipeline(mode="full")
    else:
        logger.info("🧪 MODO TESTE: Pipeline com 10 filmes")
        run_bronze_pipeline(mode="test")