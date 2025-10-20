import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_connection():
    """Retorna uma conexão psycopg2 (para inserts)."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "moviesdb"),
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "admin"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        conn.autocommit = False 
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        raise

def get_sqlalchemy_engine():
    """Retorna engine SQLAlchemy (para queries do pandas)."""
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "admin")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "moviesdb")
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string)


def insert_dataframe(columns, table_name, conn, batch_size=50000, values=None):
    """
    Insere dados usando execute_values do psycopg2.
    """
    if not values:
        print("A lista de valores está vazia. Nada para inserir.")
        return

    column_names = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({column_names}) VALUES %s"
    
    cur = None
    try:
        cur = conn.cursor()
        execute_values(cur, query, values, page_size=batch_size)
        conn.commit() 
        
    except Exception as e:
        conn.rollback() 
        raise e
        
    finally:
        if cur:
            cur.close()