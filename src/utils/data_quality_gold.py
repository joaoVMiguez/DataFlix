import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_connection
import pandas as pd

def validate_gold_data():
    """
    Valida qualidade dos dados na camada Gold
    """
    print("\n🔍 Validando qualidade dos dados Gold...\n")
    
    conn = get_connection()
    issues = []
    
    # 1. Verifica contagem de registros
    tables_check = pd.read_sql("""
        SELECT 'dim_genres' as tabela, COUNT(*) as total FROM gold.dim_genres
        UNION ALL
        SELECT 'dim_movies', COUNT(*) FROM gold.dim_movies
        UNION ALL
        SELECT 'fact_movie_ratings', COUNT(*) FROM gold.fact_movie_ratings
        UNION ALL
        SELECT 'fact_ratings_by_year', COUNT(*) FROM gold.fact_ratings_by_year
    """, conn)
    
    print("📊 Contagem de registros:")
    for _, row in tables_check.iterrows():
        print(f"  {row['tabela']}: {row['total']:,}")
        if row['total'] == 0:
            issues.append(f"❌ Tabela {row['tabela']} está vazia!")
    print()
    
    # 2. Verifica se há ratings fora do range
    rating_check = pd.read_sql("""
        SELECT 
            MIN(avg_rating) as min_rating,
            MAX(avg_rating) as max_rating
        FROM gold.dim_movies
        WHERE avg_rating IS NOT NULL
    """, conn)
    
    min_r = rating_check['min_rating'].values[0]
    max_r = rating_check['max_rating'].values[0]
    
    if min_r < 0.5 or max_r > 5.0:
        issues.append(f"❌ Ratings fora do range: {min_r} - {max_r}")
        print(f"⚠️  Range de ratings: {min_r} - {max_r}")
    else:
        print(f"✅ Range de ratings: {min_r} - {max_r}")
    
    # 3. Verifica filmes sem ratings
    no_ratings = pd.read_sql("""
        SELECT COUNT(*) as total
        FROM gold.dim_movies
        WHERE total_ratings = 0
    """, conn)
    
    no_ratings_count = no_ratings['total'].values[0]
    total_movies = tables_check[tables_check['tabela'] == 'dim_movies']['total'].values[0]
    no_ratings_pct = (no_ratings_count / total_movies) * 100
    
    print(f"⚠️  Filmes sem ratings: {no_ratings_count:,} ({no_ratings_pct:.1f}%)")
    
    # 4. Verifica top 5 filmes
    top_movies = pd.read_sql("""
        SELECT title, total_ratings, avg_rating
        FROM gold.dim_movies
        ORDER BY total_ratings DESC
        LIMIT 5
    """, conn)
    
    print("\n🏆 Top 5 filmes mais avaliados:")
    for _, row in top_movies.iterrows():
        print(f"  • {row['title']}: {row['total_ratings']:,} avaliações ({row['avg_rating']} ⭐)")
    
    conn.close()
    
    # Resumo
    print("\n" + "="*50)
    if issues:
        print("❌ VALIDAÇÃO FALHOU - Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ VALIDAÇÃO OK - Camada Gold está correta!")
    print("="*50 + "\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    validate_gold_data()