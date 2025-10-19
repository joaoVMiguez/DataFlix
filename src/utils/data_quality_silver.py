import sys
import os
# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_connection
import pandas as pd

def validate_silver_data():
    """
    Valida qualidade dos dados na camada Silver
    Retorna True se tudo estiver OK, False se houver problemas
    """
    print("\n🔍 Validando qualidade dos dados Silver...\n")
    
    conn = get_connection()
    issues = []
    
    # 1. Verifica se tabelas têm dados
    tables_check = pd.read_sql("""
        SELECT 'movies_silver' as tabela, COUNT(*) as total FROM silver.movies_silver
        UNION ALL
        SELECT 'genres_silver', COUNT(*) FROM silver.genres_silver
        UNION ALL
        SELECT 'ratings_silver', COUNT(*) FROM silver.ratings_silver
        UNION ALL
        SELECT 'tags_silver', COUNT(*) FROM silver.tags_silver
        UNION ALL
        SELECT 'links_silver', COUNT(*) FROM silver.links_silver
    """, conn)
    
    print("📊 Contagem de registros:")
    for _, row in tables_check.iterrows():
        print(f"  {row['tabela']}: {row['total']:,}")
        if row['total'] == 0:
            issues.append(f"❌ Tabela {row['tabela']} está vazia!")
    print()
    
    # 2. Verifica integridade referencial
    orphans = pd.read_sql("""
        SELECT COUNT(*) as total
        FROM silver.ratings_silver r
        LEFT JOIN silver.movies_silver m ON r.movieid = m.movieid
        WHERE m.movieid IS NULL
    """, conn)
    
    orphan_count = orphans['total'].values[0]
    if orphan_count > 0:
        issues.append(f"❌ {orphan_count} ratings sem filme correspondente!")
        print(f"⚠️  Ratings órfãos: {orphan_count}")
    else:
        print("✅ Integridade referencial: OK")
    
    # 3. Verifica range de ratings
    rating_check = pd.read_sql("""
        SELECT MIN(rating) as min, MAX(rating) as max
        FROM silver.ratings_silver
    """, conn)
    
    min_rating = rating_check['min'].values[0]
    max_rating = rating_check['max'].values[0]
    
    if min_rating < 0.5 or max_rating > 5.0:
        issues.append(f"❌ Ratings fora do range: {min_rating} - {max_rating}")
        print(f"⚠️  Range de ratings: {min_rating} - {max_rating}")
    else:
        print(f"✅ Range de ratings: {min_rating} - {max_rating}")
    
    # 4. Verifica porcentagem de filmes sem gênero
    no_genre = pd.read_sql("""
        SELECT COUNT(*) as total
        FROM silver.movies_silver m
        LEFT JOIN silver.movie_genres_silver mg ON m.movieid = mg.movieid
        WHERE mg.movieid IS NULL
    """, conn)
    
    total_movies = tables_check[tables_check['tabela'] == 'movies_silver']['total'].values[0]
    no_genre_count = no_genre['total'].values[0]
    no_genre_pct = (no_genre_count / total_movies) * 100
    
    print(f"⚠️  Filmes sem gênero: {no_genre_count:,} ({no_genre_pct:.1f}%)")
    if no_genre_pct > 10:
        issues.append(f"⚠️  {no_genre_pct:.1f}% dos filmes sem gênero")
    
    conn.close()
    
    # Resumo
    print("\n" + "="*50)
    if issues:
        print("❌ VALIDAÇÃO FALHOU - Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ VALIDAÇÃO OK - Todos os dados estão corretos!")
    print("="*50 + "\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    validate_silver_data()