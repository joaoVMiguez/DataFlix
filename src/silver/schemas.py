CREATE_SILVER_SCHEMA = """
-- Remover schema antigo se existir
DROP SCHEMA IF EXISTS silver CASCADE;

-- Criar schema
CREATE SCHEMA silver;

-- Tabelas aqui (use o SQL que criei no artifact)
"""

def create_silver_tables(conn):
    """Cria as tabelas Silver no Postgres"""
    with conn.cursor() as cur:
        cur.execute(CREATE_SILVER_SCHEMA)
        conn.commit()
    print("✓ Schema Silver criado com sucesso!")