"""
Pipeline ULTRA OTIMIZADO - Processamento Paralelo com Threading
"""
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
import time
import gc
import json
import signal
import sys
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from src.api_clients.tmdb_client import TMDBClient
from src.minio_client.minio_utils import MinioClient
from src.settings.db import get_connection
from src.settings.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "tmdb_bronze_movies_v3.log")


class GracefulKiller:
    """Permite parar pipeline com Ctrl+C sem perder dados."""
    kill_now = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, *args):
        logger.warning("🛑 Sinal de parada recebido! Salvando batch atual...")
        self.kill_now = True


class TMDBMoviesExtractorV3:
    """Extrator ULTRA otimizado com threading paralelo."""
    
    def __init__(self, batch_size: int = 2000, max_workers: int = 10):
        """
        Args:
            batch_size: Filmes por arquivo Parquet (padrão: 2000)
            max_workers: Threads paralelas (padrão: 10)
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.killer = GracefulKiller()
        self.lock = Lock()  # Thread-safe operations
        
        self.minio_client = MinioClient(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY
        )
        
        self.bucket = settings.BUCKET_BRONZE_TMDB
        self.minio_client.create_bucket(self.bucket)
        
        # Checkpoint file
        self.checkpoint_file = Path("logs/tmdb_extraction_checkpoint.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True)
        
        logger.info(f"✅ Extrator V3 ULTRA inicializado")
        logger.info(f"📦 Batch size: {self.batch_size} filmes/arquivo")
        logger.info(f"🚀 Workers paralelos: {self.max_workers}")
        logger.info(f"💾 Checkpoint: {self.checkpoint_file}")
    
    def load_checkpoint(self) -> Dict:
        """Carrega checkpoint da última execução."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                logger.info(f"🔄 Checkpoint carregado: Batch {checkpoint.get('last_batch', 0)}")
                return checkpoint
        return {"last_batch": 0, "completed_batches": [], "total_success": 0, "total_errors": 0}
    
    def save_checkpoint(self, checkpoint: Dict):
        """Salva checkpoint atual (thread-safe)."""
        with self.lock:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
    
    def clear_checkpoint(self):
        """Limpa checkpoint."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.info("✅ Checkpoint limpo")
    
    def get_movielens_movies(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Busca filmes do MovieLens."""
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
            query += f" LIMIT {limit}"
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        logger.info(f"📊 {len(df):,} filmes carregados do MovieLens")
        return df
    
    def format_imdb_id(self, imdb_id: str) -> str:
        """Formata IMDb ID."""
        imdb_str = str(imdb_id).replace('tt', '').zfill(7)
        return f"tt{imdb_str}"
    
    def extract_single_movie(self, row: pd.Series, tmdb_client: TMDBClient) -> Optional[Dict]:
        """
        Extrai UM filme (thread-safe, cada thread tem seu próprio client).
        
        Args:
            row: Linha do DataFrame com dados do filme
            tmdb_client: Cliente TMDB (um por thread)
        """
        imdb_id = str(row['imdbid'])
        movie_id = int(row['movieid'])
        title = row['title']
        
        formatted_imdb_id = self.format_imdb_id(imdb_id)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = tmdb_client.get_movie_by_imdb_id(formatted_imdb_id)
                
                if not result:
                    return None
                
                tmdb_id = result.get('id')
                details = tmdb_client.get_movie_details(tmdb_id)
                
                if details:
                    details['movielens_id'] = movie_id
                    details['imdb_id'] = formatted_imdb_id
                    details['extracted_at'] = datetime.now().isoformat()
                    return details
                
                return None
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    logger.debug(f"❌ Falha em {title}: {e}")
                    return None
        
        return None
    
    def extract_batch_parallel(self, batch_movies_df: pd.DataFrame) -> tuple[List[Dict], int, int]:
        """
        Extrai batch INTEIRO em PARALELO.
        
        Args:
            batch_movies_df: DataFrame com filmes do batch
            
        Returns:
            (lista de dados, sucessos, erros)
        """
        batch_data = []
        batch_success = 0
        batch_errors = 0
        
        # Criar ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Cada thread tem seu próprio TMDBClient (thread-safe)
            futures = {}
            
            for idx, row in batch_movies_df.iterrows():
                # Criar client por thread (evita conflitos)
                tmdb_client = TMDBClient()
                future = executor.submit(self.extract_single_movie, row, tmdb_client)
                futures[future] = row
            
            # Progress bar
            with tqdm(total=len(futures), desc="Extraindo", unit="filme", leave=False) as pbar:
                for future in as_completed(futures):
                    if self.killer.kill_now:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    try:
                        movie_data = future.result(timeout=30)  # 30s timeout
                        
                        if movie_data:
                            with self.lock:  # Thread-safe append
                                batch_data.append(movie_data)
                            batch_success += 1
                        else:
                            batch_errors += 1
                        
                        pbar.update(1)
                        pbar.set_postfix({
                            'Success': batch_success,
                            'Errors': batch_errors,
                            'Taxa': f"{batch_success/(batch_success+batch_errors)*100:.1f}%"
                        })
                    
                    except Exception as e:
                        logger.error(f"❌ Erro na thread: {e}")
                        batch_errors += 1
                        pbar.update(1)
        
        return batch_data, batch_success, batch_errors
    
    def save_batch_to_minio(self, movies_data: List[Dict], batch_number: int):
        """Salva batch no MinIO."""
        if not movies_data:
            logger.warning(f"⚠️  Batch {batch_number} vazio")
            return
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df = pd.DataFrame(movies_data)
                
                # ✅ CONVERTER COLUNAS JSON PARA STRING (CORRIGIDO!)
                json_columns = ['genres', 'production_companies', 'production_countries', 'spoken_languages']
                for col in json_columns:
                    if col in df.columns:
                        # ✅ FIX: Verificar tipo correto
                        df[col] = df[col].apply(
                            lambda x: json.dumps(x) if isinstance(x, (list, dict)) else None
                        )
                
                object_name = f"movies_v3/batch_{batch_number:05d}.parquet"
                
                self.minio_client.upload_parquet(
                    bucket=self.bucket,
                    object_name=object_name,
                    data=df
                )
                
                logger.info(f"✅ Batch {batch_number} salvo: {len(movies_data)} filmes")
                return
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"⚠️  Erro ao salvar, tentativa {attempt + 1}: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ FALHA ao salvar batch {batch_number}: {e}")     
                    raise
    
    def extract_all_movies(self, limit: Optional[int] = None, resume: bool = True):
        """Extrai todos os filmes com processamento PARALELO."""
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("🎬 EXTRAÇÃO TMDB - BRONZE LAYER V3 ULTRA (PARALELO)")
        logger.info("=" * 80)
        
        # Checkpoint
        checkpoint = self.load_checkpoint() if resume else {
            "last_batch": 0, "completed_batches": [], 
            "total_success": 0, "total_errors": 0
        }
        start_batch = checkpoint["last_batch"] + 1 if resume else 1
        
        if resume and checkpoint["last_batch"] > 0:
            logger.info(f"🔄 Retomando da batch {start_batch}")
        
        # Carregar filmes
        movies_df = self.get_movielens_movies(limit=limit)
        
        if movies_df.empty:
            logger.warning("⚠️  Nenhum filme encontrado")
            return
        
        total_movies = len(movies_df)
        total_batches = (total_movies + self.batch_size - 1) // self.batch_size
        
        logger.info(f"📊 Total de filmes: {total_movies:,}")
        logger.info(f"📦 Batch size: {self.batch_size}")
        logger.info(f"📦 Total de batches: {total_batches}")
        logger.info(f"🚀 Threads paralelas: {self.max_workers}")
        logger.info("=" * 80)
        
        success_count = checkpoint["total_success"]
        error_count = checkpoint["total_errors"]
        
        # Processar batches
        for batch_num in range(start_batch, total_batches + 1):
            if self.killer.kill_now:
                logger.warning("🛑 Salvando checkpoint...")
                self.save_checkpoint(checkpoint)
                logger.info(f"✅ Progresso salvo: {success_count + error_count}/{total_movies}")
                sys.exit(0)
            
            # Calcular índices
            start_idx = (batch_num - 1) * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_movies)
            batch_movies_df = movies_df.iloc[start_idx:end_idx]
            
            batch_start_time = time.time()
            logger.info(f"📦 Batch {batch_num}/{total_batches} ({len(batch_movies_df)} filmes)...")
            
            # EXTRAÇÃO PARALELA 🚀
            batch_data, batch_success, batch_errors = self.extract_batch_parallel(batch_movies_df)
            
            batch_elapsed = time.time() - batch_start_time
            batch_rate = len(batch_movies_df) / batch_elapsed if batch_elapsed > 0 else 0
            
            success_count += batch_success
            error_count += batch_errors
            
            # Salvar batch
            if batch_data:
                try:
                    self.save_batch_to_minio(batch_data, batch_num)
                    checkpoint["completed_batches"].append(batch_num)
                    checkpoint["last_batch"] = batch_num
                    checkpoint["total_success"] = success_count
                    checkpoint["total_errors"] = error_count
                    self.save_checkpoint(checkpoint)
                    
                    logger.info(
                        f"✅ Batch {batch_num}: {batch_success} sucessos, {batch_errors} erros "
                        f"| ⚡ {batch_rate:.2f} filmes/s | ⏱️ {batch_elapsed/60:.1f}min"
                    )
                
                except Exception as e:
                    logger.error(f"❌ FALHA ao salvar batch {batch_num}: {e}")
                    sys.exit(1)
            
            # Limpar memória
            del batch_data
            gc.collect()
            
            # Progresso geral
            progress = (batch_num / total_batches) * 100
            elapsed = time.time() - start_time
            rate = (success_count + error_count) / elapsed if elapsed > 0 else 0
            remaining_movies = total_movies - (success_count + error_count)
            remaining_time = remaining_movies / rate if rate > 0 else 0
            
            logger.info(
                f"📈 Progresso: {progress:.1f}% | "
                f"✅ {success_count:,} | ❌ {error_count:,} | "
                f"⚡ {rate:.2f} filmes/s | "
                f"⏱️ Restante: {remaining_time/3600:.1f}h"
            )
            logger.info("=" * 80)
        
        # Concluído
        elapsed = time.time() - start_time
        
        logger.info("=" * 80)
        logger.info("🎉 EXTRAÇÃO CONCLUÍDA!")
        logger.info(f"📊 Total: {total_movies:,}")
        logger.info(f"✅ Sucesso: {success_count:,} ({success_count/total_movies*100:.1f}%)")
        logger.info(f"❌ Erros: {error_count:,} ({error_count/total_movies*100:.1f}%)")
        logger.info(f"📦 Batches: {total_batches}")
        logger.info(f"⏱️ Tempo: {elapsed/3600:.2f}h")
        logger.info(f"⚡ Taxa média: {(success_count + error_count)/elapsed:.2f} filmes/s")
        logger.info("=" * 80)
        
        self.clear_checkpoint()


def run_extraction_v3(
    batch_size: int = 2000,
    max_workers: int = 10,
    limit: Optional[int] = None,
    resume: bool = True
):
    """Executa extração V3 ULTRA com paralelismo."""
    extractor = TMDBMoviesExtractorV3(batch_size=batch_size, max_workers=max_workers)
    extractor.extract_all_movies(limit=limit, resume=resume)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        logger.info("🧪 MODO TESTE: 1 batch (2000 filmes) com 10 threads")
        run_extraction_v3(batch_size=2000, max_workers=10, limit=2000, resume=False)
    
    elif "--full" in sys.argv:
        logger.warning("🚀 MODO PRODUÇÃO: TODOS os filmes (PARALELO)")
        logger.warning("⏱️ Pressione Ctrl+C para pausar (não perde dados)")
        time.sleep(3)
        run_extraction_v3(batch_size=2000, max_workers=10, limit=None, resume=True)
    
    elif "--resume" in sys.argv:
        logger.info("🔄 MODO RESUMO: Continuando...")
        run_extraction_v3(batch_size=2000, max_workers=10, limit=None, resume=True)
    
    elif "--reset" in sys.argv:
        logger.warning("🔄 MODO RESET: Começando do zero")
        time.sleep(2)
        run_extraction_v3(batch_size=2000, max_workers=10, limit=None, resume=False)
    
    elif "--turbo" in sys.argv:
        logger.warning("🚀🔥 MODO TURBO: 20 threads paralelas!")
        time.sleep(2)
        run_extraction_v3(batch_size=2000, max_workers=20, limit=None, resume=True)
    
    else:
        print("📖 Uso:")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies              # Teste (10 threads)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --full       # Produção (10 threads)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --turbo      # TURBO (20 threads)")
        print("  python -m src.pipelines.tmdb.bronze.extract_tmdb_movies --resume     # Retomar")