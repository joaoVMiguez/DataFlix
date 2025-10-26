import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_connection
import pandas as pd

def validate_silver_tmdb():
    """Valida camada Silver TMDB."""
    print("\n🔍 Validando Silver TMDB...\n")
    
    conn = get_connection()
    
    # Contagem
    tables = pd.read_sql("""
        SELECT 'movies_tmdb' as tabela, COUNT(*) as total FROM silver_tmdb.movies_tmdb
        UNION ALL
        SELECT 'genres_tmdb', COUNT(*) FROM silver_tmdb.genres_tmdb
        UNION ALL
        SELECT 'production_companies_tmdb', COUNT(*) FROM silver_tmdb.production_companies_tmdb
    """, conn)
    
    print("📊 Contagem:")
    for _, row in tables.iterrows():
        print(f"  {row['tabela']}: {row['total']:,}")
    
    # Qualidade
    quality = pd.read_sql("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE budget > 0) as with_budget,
            COUNT(*) FILTER (WHERE revenue > 0) as with_revenue,
            ROUND(AVG(quality_score)) as avg_quality
        FROM silver_tmdb.movies_tmdb
    """, conn)
    
    print("\n📈 Qualidade:")
    print(f"  Filmes com budget: {quality['with_budget'].values[0]:,}")
    print(f"  Filmes com revenue: {quality['with_revenue'].values[0]:,}")
    print(f"  Quality score médio: {quality['avg_quality'].values[0]}/100")
    
    conn.close()
    print("\n✅ Validação concluída!\n")

if __name__ == "__main__":
    validate_silver_tmdb()