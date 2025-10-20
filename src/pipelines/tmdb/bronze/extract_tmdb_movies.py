import pandas as pd
from typing import Optional, Dict
from datetime import datetime
import time
from tqdm import tqdm
from src.api_clients.tmdb_client import TMDBClient
from src.minio_client.minio_utils import MinioClient
from src.settings.db import get_connection
from src.settings.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "tmdb_bronze_movies.log")


class TMDBMoviesExtractor:
    """Extrator de dados de filmes do TMDB."""
    
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
    
    def get_movielens_movies(self, limit: Optional[int] = None, offset: int = 0) -> pd.DataFrame:
        """Busca filmes do MovieLens com IMDb IDs."""
        conn = get_connection()
        
        query = """
        SELECT 
            m.movieid,
            m.title,
            m.release_year,
            l.imdbid,
            l.tmdbid
        FROM silver.movies_silver m
        LEFT JOIN silver.links_silver l ON m.movieid = l.movieid
        WHERE l.imdbid IS NOT NULL
        ORDER BY m.movieid
        """
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        logger.info(f"📊 {len(df)} filmes carregados do MovieLens")
        return df
    
    def get_existing_files(self) -> set:
        """Retorna set de IDs já extraídos."""
        try:
            objects = self.minio_client.list_objects(self.bucket, prefix="movies/")
            existing = set()
            for obj in objects:
                # Extrair ID do nome: "movies/123.parquet" -> 123
                movie_id = obj.replace("movies/", "").replace(".parquet", "")
                if movie_id.isdigit():
                    existing.add(int(movie_id))
            
            logger.info(f"📁 {len(existing)} filmes já existem no MinIO")
            return existing
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos existentes: {e}")
            return set()
    
    def format_imdb_id(self, imdb_id: str) -> str:
        """Formata IMDb ID para o padrão correto (tt + 7 dígitos)."""
        imdb_str = str(imdb_id).replace('tt', '')
        imdb_str = imdb_str.zfill(7)
        return f"tt{imdb_str}"
    
    def extract_movie_details(self, imdb_id: str, movie_id: int, title: str) -> Optional[Dict]:
        """Extrai detalhes de um filme do TMDB."""
        try:
            formatted_imdb_id = self.format_imdb_id(imdb_id)
            
            result = self.tmdb_client.get_movie_by_imdb_id(formatted_imdb_id)
            
            if not result:
                logger.warning(f"⚠️  Filme não encontrado: {title} (IMDb: {formatted_imdb_id})")
                return None
            
            tmdb_id = result.get('id')
            details = self.tmdb_client.get_movie_details(tmdb_id)
            
            if details:
                details['movielens_id'] = movie_id
                details['imdb_id'] = formatted_imdb_id
                details['extracted_at'] = datetime.now().isoformat()
                
                return details
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair {title}: {e}")
            return None
    
    def save_to_minio(self, data: Dict, movie_id: int):
        """Salva dados no MinIO em formato Parquet."""
        try:
            object_name = f"movies/{movie_id}.parquet"
            self.minio_client.upload_parquet(
                bucket=self.bucket,
                object_name=object_name,
                data=data
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar filme {movie_id}: {e}")
            raise
    
    def extract_batch(
        self, 
        batch_size: int = 100, 
        limit: Optional[int] = None,
        skip_existing: bool = True
    ):
        """Extrai filmes em lotes."""
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("🎬 INICIANDO EXTRAÇÃO TMDB - BRONZE LAYER (PARQUET)")
        logger.info("=" * 80)
        
        # Carregar filmes
        movies_df = self.get_movielens_movies(limit=limit)
        
        if movies_df.empty:
            logger.warning("⚠️  Nenhum filme encontrado")
            return
        
        # Verificar arquivos existentes
        existing_ids = set()
        if skip_existing:
            existing_ids = self.get_existing_files()
            movies_df = movies_df[~movies_df['movieid'].isin(existing_ids)]
            logger.info(f"🔄 {len(movies_df)} filmes restantes para processar")
        
        if movies_df.empty:
            logger.info("✅ Todos os filmes já foram extraídos!")
            return
        
        total = len(movies_df)
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        logger.info(f"📊 Total a processar: {total:,}")
        logger.info(f"📦 Batch size: {batch_size}")
        
        if not limit:
            estimated_hours = (total / 4 / 3600)  # 4 req/s
            logger.info(f"⏱️  Tempo estimado: {estimated_hours:.1f} horas")
        
        logger.info("=" * 80)
        
        # Barra de progresso
        with tqdm(total=total, desc="🎬 Extraindo filmes", unit="filme") as pbar:
            for idx, row in movies_df.iterrows():
                try:
                    movie_id = int(row['movieid'])
                    
                    # Extrair dados
                    movie_data = self.extract_movie_details(
                        imdb_id=str(row['imdbid']),
                        movie_id=movie_id,
                        title=row['title']
                    )
                    
                    if movie_data:
                        self.save_to_minio(movie_data, movie_id)
                        success_count += 1
                        pbar.set_postfix({
                            'Success': success_count,
                            'Errors': error_count,
                            'Taxa': f"{success_count/(success_count+error_count)*100:.1f}%"
                        })
                    else:
                        error_count += 1
                    
                    pbar.update(1)
                    
                    # Log a cada 100 filmes
                    if (success_count + error_count) % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = (success_count + error_count) / elapsed
                        remaining = (total - success_count - error_count) / rate if rate > 0 else 0
                        
                        logger.info(
                            f"📈 Progresso: {success_count + error_count:,}/{total:,} "
                            f"({(success_count + error_count)/total*100:.1f}%) | "
                            f"✅ {success_count:,} | ❌ {error_count:,} | "
                            f"⏱️  Restante: {remaining/3600:.1f}h"
                        )
                
                except Exception as e:
                    logger.error(f"❌ Erro crítico filme {row['movieid']}: {e}")
                    error_count += 1
                    pbar.update(1)
        
        elapsed = time.time() - start_time
        
        logger.info("=" * 80)
        logger.info("🎉 EXTRAÇÃO CONCLUÍDA!")
        logger.info(f"📊 Total processado: {total:,}")
        logger.info(f"✅ Sucesso: {success_count:,} ({success_count/total*100:.1f}%)")
        logger.info(f"❌ Erros: {error_count:,} ({error_count/total*100:.1f}%)")
        logger.info(f"⏱️  Tempo total: {elapsed/3600:.2f} horas")
        logger.info(f"⚡ Taxa média: {total/elapsed:.2f} filmes/segundo")
        logger.info("=" * 80)


def run_extraction(
    batch_size: int = 100, 
    limit: Optional[int] = None,
    skip_existing: bool = True
):
    """Executa extração."""
    extractor = TMDBMoviesExtractor()
    extractor.extract_batch(
        batch_size=batch_size, 
        limit=limit,
        skip_existing=skip_existing
    )


if __name__ == "__main__":
    import sys
    
    # Modo TESTE (default)
    if len(sys.argv) == 1:
        logger.info("🧪 MODO TESTE: Extraindo 10 filmes...")
        logger.info("💡 Para extrair TODOS: python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --full")
        run_extraction(batch_size=10, limit=10)
    
    # Modo PRODUCAO (--full)
    elif "--full" in sys.argv:
        logger.warning("🚀 MODO PRODUÇÃO: Extraindo TODOS os filmes (~87k)")
        logger.warning("⏱️  Isso vai levar 6-8 horas. Pressione Ctrl+C para cancelar...")
        time.sleep(3)
        run_extraction(batch_size=100, limit=None)
    
    # Modo RESUMO (--resume)
    elif "--resume" in sys.argv:
        logger.info("🔄 MODO RESUMO: Continuando extração anterior...")
        run_extraction(batch_size=100, limit=None, skip_existing=True)
    
    else:
        print("📖 Uso:")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies            # Teste (10 filmes)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --full     # Produção (todos)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --resume   # Retomar extração")