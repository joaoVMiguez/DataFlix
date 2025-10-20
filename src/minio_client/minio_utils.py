import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import Union, Dict, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MinioClient:
    """Cliente para operações no MinIO."""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        """
        Inicializa cliente MinIO.
        
        Args:
            endpoint: Endereço do MinIO (ex: 'localhost:9000')
            access_key: Access key do MinIO
            secret_key: Secret key do MinIO
            secure: Se True, usa HTTPS
        """
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        logger.info(f"MinioClient conectado em {endpoint}")
    
    def create_bucket(self, bucket_name: str):
        """Cria bucket se não existir."""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Bucket criado: {bucket_name}")
            else:
                logger.debug(f"Bucket ja existe: {bucket_name}")
        except S3Error as e:
            logger.error(f"Erro ao criar bucket {bucket_name}: {e}")
            raise
    
    def upload_json(self, bucket: str, object_name: str, data: Union[Dict, List]):
        """
        Faz upload de dados JSON para o MinIO.
        
        Args:
            bucket: Nome do bucket
            object_name: Caminho do objeto (ex: 'movies/1.json')
            data: Dados em formato Dict ou List
        """
        try:
            json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
            
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=BytesIO(json_bytes),
                length=len(json_bytes),
                content_type="application/json"
            )
            
            logger.debug(f"Upload JSON concluido: {bucket}/{object_name}")
        
        except S3Error as e:
            logger.error(f"Erro no upload JSON para {bucket}/{object_name}: {e}")
            raise
    
    def upload_parquet(self, bucket: str, object_name: str, data: Union[Dict, List, pd.DataFrame]):
        """
        Faz upload de dados em formato Parquet (comprimido com Snappy).
        
        Args:
            bucket: Nome do bucket
            object_name: Caminho do objeto (ex: 'movies/1.parquet')
            data: Dict, List ou DataFrame
        """
        try:
            # Converter para DataFrame se necessário
            if isinstance(data, dict):
                # Transformar dict aninhado em DataFrame flat
                df = pd.json_normalize(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError(f"Tipo não suportado: {type(data)}")
            
            # Converter para Parquet em memória
            buffer = BytesIO()
            df.to_parquet(
                buffer,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            
            # Voltar para o início do buffer
            buffer.seek(0)
            parquet_size = buffer.getbuffer().nbytes
            
            # Upload para MinIO
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=buffer,
                length=parquet_size,
                content_type="application/octet-stream"
            )
            
            logger.debug(f"Upload Parquet concluido: {bucket}/{object_name} ({parquet_size} bytes)")
        
        except Exception as e:
            logger.error(f"Erro no upload Parquet para {bucket}/{object_name}: {e}")
            raise
    
    def download_json(self, bucket: str, object_name: str) -> Union[Dict, List]:
        """
        Faz download de JSON do MinIO.
        
        Args:
            bucket: Nome do bucket
            object_name: Caminho do objeto
            
        Returns:
            Dados em formato Dict ou List
        """
        try:
            response = self.client.get_object(bucket, object_name)
            data = json.loads(response.read().decode('utf-8'))
            logger.debug(f"Download JSON concluido: {bucket}/{object_name}")
            return data
        
        except S3Error as e:
            logger.error(f"Erro no download JSON de {bucket}/{object_name}: {e}")
            return {}
        
        finally:
            response.close()
            response.release_conn()
    
    def download_parquet(self, bucket: str, object_name: str) -> pd.DataFrame:
        """
        Faz download de Parquet do MinIO.
        
        Args:
            bucket: Nome do bucket
            object_name: Caminho do objeto
            
        Returns:
            DataFrame com os dados
        """
        try:
            response = self.client.get_object(bucket, object_name)
            df = pd.read_parquet(BytesIO(response.read()))
            logger.debug(f"Download Parquet concluido: {bucket}/{object_name}")
            return df
        
        except S3Error as e:
            logger.error(f"Erro no download Parquet de {bucket}/{object_name}: {e}")
            return pd.DataFrame()
        
        finally:
            response.close()
            response.release_conn()
    
    def list_objects(self, bucket: str, prefix: str = "", recursive: bool = True) -> List[str]:
        """
        Lista objetos em um bucket.
        
        Args:
            bucket: Nome do bucket
            prefix: Prefixo para filtrar objetos
            recursive: Se True, lista recursivamente
            
        Returns:
            Lista de nomes de objetos
        """
        try:
            objects = self.client.list_objects(
                bucket_name=bucket,
                prefix=prefix,
                recursive=recursive
            )
            return [obj.object_name for obj in objects]
        
        except S3Error as e:
            logger.error(f"Erro ao listar objetos em {bucket}: {e}")
            return []
    
    def delete_object(self, bucket: str, object_name: str):
        """
        Remove um objeto do MinIO.
        
        Args:
            bucket: Nome do bucket
            object_name: Caminho do objeto
        """
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Objeto removido: {bucket}/{object_name}")
        
        except S3Error as e:
            logger.error(f"Erro ao remover {bucket}/{object_name}: {e}")
            raise
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Verifica se um bucket existe.
        
        Args:
            bucket_name: Nome do bucket
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            logger.error(f"Erro ao verificar bucket {bucket_name}: {e}")
            return False