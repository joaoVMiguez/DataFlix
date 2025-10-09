# config/db.py
import psycopg2
from psycopg2.extras import execute_values
import os 
# from ... (Seus outros imports)

# Defina as credenciais do seu banco de dados
# DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, etc.

def get_connection():
    """Retorna uma conexão aberta com o PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "movies"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        # Seta o modo de autocommit como False para gerenciar transações
        conn.autocommit = False 
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


def insert_dataframe(columns, table_name, conn, batch_size=50000, values=None):
    """
    Insere dados usando execute_values do psycopg2.
    Requer que 'values' seja uma lista de tuplas com tipos nativos Python (int, float, str, None).
    """
    if not values:
        print("A lista de valores está vazia. Nada para inserir.")
        return

    column_names = ", ".join(columns)
    # Query que usa o placeholder %s, necessário para execute_values
    query = f"INSERT INTO {table_name} ({column_names}) VALUES %s"
    
    cur = None
    try:
        cur = conn.cursor()
        
        # execute_values é a forma eficiente de inserção em lote
        # Ele formata os valores corretamente, desde que sejam tipos Python puros.
        execute_values(cur, query, values, page_size=batch_size)
        
        # Commit da transação após a inserção bem-sucedida
        conn.commit() 
        
    except Exception as e:
        # Se houver erro, a transação deve ser revertida (rollback)
        # Isso é crucial para liberar a transação e permitir novos comandos SQL
        conn.rollback() 
        # Levanta a exceção para que o load_silver.py a capture e imprima o erro
        raise e
        
    finally:
        if cur:
            cur.close()