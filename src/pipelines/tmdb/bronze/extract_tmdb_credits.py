import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
import time
from tqdm import tqdm
from src.api_clients.tmdb_client import TMDBClient
from src.minio_client.minio_utils import MinioClient
from src.settings.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "tmdb_bronze_credits.log")


class TMDBCreditsExtractor:
    """Extrator de créditos (elenco e equipe) do TMDB."""
    
    def __init__(self):
        self.tmdb_client = TMDBClient()
        
        self.minio_client = MinioClient(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY
        )
        
        self.bucket = settings.BUCKET_BRONZE_TMDB
        self.minio_client.create_bucket(self.bucket)
        logger.info(f"✅ Bucket {self.bucket} pronto")
    
    def get_extracted_movies(self) -> List[int]:
        """Retorna lista de IDs de filmes já extraídos."""
        try:
            objects = self.minio_client.list_objects(self.bucket, prefix="movies/")
            movie_ids = []
            
            for obj in objects:
                movie_id = obj.replace("movies/", "").replace(".parquet", "")
                if movie_id.isdigit():
                    movie_ids.append(int(movie_id))
            
            logger.info(f"📁 {len(movie_ids)} filmes encontrados no MinIO")
            return sorted(movie_ids)
        
        except Exception as e:
            logger.error(f"❌ Erro ao listar filmes: {e}")
            return []
    
    def get_existing_credits(self) -> set:
        """Retorna set de IDs de créditos já extraídos."""
        try:
            objects = self.minio_client.list_objects(self.bucket, prefix="credits/")
            existing = set()
            
            for obj in objects:
                movie_id = obj.replace("credits/", "").replace(".parquet", "")
                if movie_id.isdigit():
                    existing.add(int(movie_id))
            
            logger.info(f"📁 {len(existing)} créditos já existem no MinIO")
            return existing
        
        except Exception as e:
            logger.error(f"❌ Erro ao listar créditos existentes: {e}")
            return set()
    
    def extract_credits(self, movie_id: int, tmdb_id: int) -> Optional[Dict]:
        """Extrai créditos de um filme."""
        try:
            credits = self.tmdb_client.get_credits(tmdb_id)
            
            if credits:
                credits['movielens_id'] = movie_id
                credits['tmdb_id'] = tmdb_id
                credits['extracted_at'] = datetime.now().isoformat()
                
                return credits
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair créditos do filme {movie_id}: {e}")
            return None
    
    def save_to_minio(self, data: Dict, movie_id: int):
        """Salva créditos no MinIO."""
        try:
            object_name = f"credits/{movie_id}.parquet"
            self.minio_client.upload_parquet(
                bucket=self.bucket,
                object_name=object_name,
                data=data
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar créditos do filme {movie_id}: {e}")
            raise
    
    def extract_all_credits(self, limit: Optional[int] = None, skip_existing: bool = True):
        """Extrai créditos de todos os filmes."""
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("🎭 INICIANDO EXTRAÇÃO DE CRÉDITOS TMDB")
        logger.info("=" * 80)
        
        # Obter filmes já extraídos
        movie_ids = self.get_extracted_movies()
        
        if not movie_ids:
            logger.warning("⚠️  Nenhum filme encontrado. Execute extract_tmdb_movies primeiro!")
            return
        
        # Filtrar já existentes
        if skip_existing:
            existing = self.get_existing_credits()
            movie_ids = [mid for mid in movie_ids if mid not in existing]
            logger.info(f"🔄 {len(movie_ids)} créditos restantes para processar")
        
        if limit:
            movie_ids = movie_ids[:limit]
        
        total = len(movie_ids)
        success_count = 0
        error_count = 0
        
        logger.info(f"📊 Total a processar: {total:,}")
        logger.info("=" * 80)
        
        # Barra de progresso
        with tqdm(total=total, desc="🎭 Extraindo créditos", unit="filme") as pbar:
            for movie_id in movie_ids:
                try:
                    # Ler arquivo do filme para pegar tmdb_id
                    movie_data = self.minio_client.download_parquet(
                        self.bucket,
                        f"movies/{movie_id}.parquet"
                    )
                    
                    if movie_data.empty or 'id' not in movie_data.columns:
                        logger.warning(f"⚠️  TMDB ID não encontrado para filme {movie_id}")
                        error_count += 1
                        pbar.update(1)
                        continue
                    
                    tmdb_id = int(movie_data['id'].iloc[0])
                    
                    # Extrair créditos
                    credits_data = self.extract_credits(movie_id, tmdb_id)
                    
                    if credits_data:
                        self.save_to_minio(credits_data, movie_id)
                        success_count += 1
                        pbar.set_postfix({
                            'Success': success_count,
                            'Errors': error_count
                        })
                    else:
                        error_count += 1
                    
                    pbar.update(1)
                
                except Exception as e:
                    logger.error(f"❌ Erro crítico filme {movie_id}: {e}")
                    error_count += 1
                    pbar.update(1)
        
        elapsed = time.time() - start_time
        
        logger.info("=" * 80)
        logger.info("🎉 EXTRAÇÃO DE CRÉDITOS CONCLUÍDA!")
        logger.info(f"📊 Total processado: {total:,}")
        logger.info(f"✅ Sucesso: {success_count:,} ({success_count/total*100:.1f}%)")
        logger.info(f"❌ Erros: {error_count:,} ({error_count/total*100:.1f}%)")
        logger.info(f"⏱️  Tempo total: {elapsed/60:.2f} minutos")
        logger.info("=" * 80)


def run_credits_extraction(limit: Optional[int] = None, skip_existing: bool = True):
    """Executa extração de créditos."""
    extractor = TMDBCreditsExtractor()
    extractor.extract_all_credits(limit=limit, skip_existing=skip_existing)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        logger.info("🧪 MODO TESTE: Extraindo créditos de 10 filmes...")
        run_credits_extraction(limit=10)
    elif "--full" in sys.argv:
        logger.info("🚀 MODO PRODUÇÃO: Extraindo créditos de TODOS os filmes...")
        run_credits_extraction(limit=None)
    else:
        print("📖 Uso:")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_credits         # Teste (10)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_credits --full  # Produção (todos)")