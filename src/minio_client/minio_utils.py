from minio import Minio
import pandas as pd
from io import BytesIO

class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def list_files(self, bucket_name):
        """Lista arquivos no bucket"""
        objects = self.client.list_objects(bucket_name)
        return [obj.object_name for obj in objects]

    def download_csv(self, bucket_name, object_name, chunksize=None):
        """
        Baixa CSV do MinIO e retorna um DataFrame
        Se chunksize for especificado, retorna um iterador
        """
        response = self.client.get_object(bucket_name, object_name)
        
        if chunksize:
            # Retorna iterador para processar em chunks
            df_iterator = pd.read_csv(BytesIO(response.read()), chunksize=chunksize)
            response.close()
            response.release_conn()
            return df_iterator
        else:
            # Retorna DataFrame completo
            df = pd.read_csv(BytesIO(response.read()))
            response.close()
            response.release_conn()
            return df