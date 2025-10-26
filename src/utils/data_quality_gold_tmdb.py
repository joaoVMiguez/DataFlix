import sys
import os
sys.path.insert(0, '/app')

from settings.db import get_connection
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def validate_gold_tmdb():
    """
    Valida qualidade dos dados na camada Gold TMDB
    """
    print("\n🔍 Validando qualidade dos dados Gold TMDB...\n")
    
    conn = get_connection()
    issues = []
    
    # 1. Verifica contagem de registros
    tables_check = pd.read_sql("""
        SELECT 'dim_movies_tmdb' as tabela, COUNT(*) as total FROM gold_tmdb.dim_movies_tmdb
        UNION ALL
        SELECT 'fact_box_office', COUNT(*) FROM gold_tmdb.fact_box_office
        UNION ALL
        SELECT 'fact_studio_performance', COUNT(*) FROM gold_tmdb.fact_studio_performance
        UNION ALL
        SELECT 'fact_country_performance', COUNT(*) FROM gold_tmdb.fact_country_performance
    """, conn)
    
    print("📊 Contagem de registros:")
    for _, row in tables_check.iterrows():
        print(f"  {row['tabela']}: {row['total']:,}")
        if row['total'] == 0:
            issues.append(f"❌ Tabela {row['tabela']} está vazia!")
    print()
    
    # 2. Verifica cobertura de dados financeiros
    financial_coverage = pd.read_sql("""
        SELECT 
            COUNT(*) as total_movies,
            COUNT(*) FILTER (WHERE budget > 0) as with_budget,
            COUNT(*) FILTER (WHERE revenue > 0) as with_revenue,
            COUNT(*) FILTER (WHERE budget > 0 AND revenue > 0) as with_both,
            ROUND(COUNT(*) FILTER (WHERE budget > 0)::NUMERIC / COUNT(*) * 100, 1) as pct_budget,
            ROUND(COUNT(*) FILTER (WHERE revenue > 0)::NUMERIC / COUNT(*) * 100, 1) as pct_revenue
        FROM gold_tmdb.dim_movies_tmdb
    """, conn)
    
    print("💰 Cobertura de dados financeiros:")
    print(f"  Total de filmes: {financial_coverage['total_movies'].values[0]:,}")
    print(f"  Com budget: {financial_coverage['with_budget'].values[0]:,} ({financial_coverage['pct_budget'].values[0]}%)")
    print(f"  Com revenue: {financial_coverage['with_revenue'].values[0]:,} ({financial_coverage['pct_revenue'].values[0]}%)")
    print(f"  Com ambos: {financial_coverage['with_both'].values[0]:,}")
    print()
    
    # 3. Verifica quality score
    quality = pd.read_sql("""
        SELECT 
            ROUND(AVG(quality_score)) as avg_quality,
            MIN(quality_score) as min_quality,
            MAX(quality_score) as max_quality
        FROM gold_tmdb.dim_movies_tmdb
    """, conn)
    
    print("📈 Quality Score:")
    print(f"  Média: {quality['avg_quality'].values[0]}/100")
    print(f"  Mínimo: {quality['min_quality'].values[0]}/100")
    print(f"  Máximo: {quality['max_quality'].values[0]}/100")
    print()
    
    # 4. Top 5 filmes por ROI
    top_roi = pd.read_sql("""
        SELECT 
            title,
            budget,
            revenue,
            roi
        FROM gold_tmdb.fact_box_office
        WHERE roi IS NOT NULL
        ORDER BY roi DESC
        LIMIT 5
    """, conn)
    
    print("🏆 Top 5 filmes por ROI:")
    for _, row in top_roi.iterrows():
        print(f"  • {row['title']}: {row['roi']:.1f}% ROI (Budget: ${row['budget']:,}, Revenue: ${row['revenue']:,})")
    print()
    
    # 5. Top 5 estúdios por ROI médio
    top_studios = pd.read_sql("""
        SELECT 
            company_name,
            total_movies,
            avg_roi,
            success_rate
        FROM gold_tmdb.fact_studio_performance
        ORDER BY avg_roi DESC
        LIMIT 5
    """, conn)
    
    print("🏢 Top 5 estúdios por ROI médio:")
    for _, row in top_studios.iterrows():
        print(f"  • {row['company_name']}: {row['avg_roi']:.1f}% ROI médio ({row['total_movies']} filmes, {row['success_rate']:.1f}% sucesso)")
    print()
    
    # 6. Top 5 países produtores
    top_countries = pd.read_sql("""
        SELECT 
            country_name,
            total_movies,
            avg_roi,
            top_genre
        FROM gold_tmdb.fact_country_performance
        ORDER BY total_movies DESC
        LIMIT 5
    """, conn)
    
    print("🌍 Top 5 países produtores:")
    for _, row in top_countries.iterrows():
        print(f"  • {row['country_name']}: {row['total_movies']} filmes (ROI: {row['avg_roi']:.1f}%, Gênero top: {row['top_genre']})")
    print()
    
    # 7. Distribuição de filmes por categoria de budget
    budget_dist = pd.read_sql("""
        SELECT 
            budget_category,
            COUNT(*) as total,
            ROUND(AVG(roi), 1) as avg_roi
        FROM gold_tmdb.fact_box_office
        GROUP BY budget_category
        ORDER BY 
            CASE budget_category
                WHEN 'Blockbuster' THEN 1
                WHEN 'Large' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Small' THEN 4
                WHEN 'Micro' THEN 5
                ELSE 6
            END
    """, conn)
    
    print("💵 Distribuição por categoria de budget:")
    for _, row in budget_dist.iterrows():
        print(f"  • {row['budget_category']}: {row['total']:,} filmes (ROI médio: {row['avg_roi']}%)")
    print()
    
    conn.close()
    
    # Resumo
    print("=" * 50)
    if issues:
        print("❌ VALIDAÇÃO FALHOU - Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ VALIDAÇÃO OK - Camada Gold TMDB está correta!")
    print("=" * 50 + "\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    validate_gold_tmdb()