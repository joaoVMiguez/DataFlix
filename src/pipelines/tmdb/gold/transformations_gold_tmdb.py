import sys
sys.path.insert(0, '/app')
from settings.db import get_connection
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def aggregate_movies_tmdb() -> pd.DataFrame:
    """
    Agrega dimensão principal de filmes TMDB com dados agregados.
    """
    print("  📊 Agregando dimensão de filmes TMDB...")
    
    conn = get_connection()
    
    query = """
    WITH genres_agg AS (
        SELECT 
            movielens_id,
            COUNT(DISTINCT genre_id) as total_genres,
            STRING_AGG(DISTINCT genre_name, ', ' ORDER BY genre_name) as genres_list
        FROM silver_tmdb.genres_tmdb
        GROUP BY movielens_id
    ),
    companies_agg AS (
        SELECT 
            movielens_id,
            COUNT(DISTINCT company_id) as total_companies,
            MAX(company_name) as main_company
        FROM silver_tmdb.production_companies_tmdb
        GROUP BY movielens_id
    ),
    countries_agg AS (
        SELECT 
            movielens_id,
            COUNT(DISTINCT country_code) as total_countries,
            MAX(country_name) as main_country
        FROM silver_tmdb.production_countries_tmdb
        GROUP BY movielens_id
    ),
    languages_agg AS (
        SELECT 
            movielens_id,
            COUNT(DISTINCT language_code) as total_languages
        FROM silver_tmdb.spoken_languages_tmdb
        GROUP BY movielens_id
    )
    SELECT 
        m.movielens_id,
        m.tmdb_id,
        m.imdb_id,
        m.title,
        m.original_title,
        m.release_year,
        m.release_decade,
        m.runtime,
        m.budget,
        m.revenue,
        m.profit,
        m.roi,
        m.popularity,
        m.vote_average,
        m.vote_count,
        
        COALESCE(g.total_genres, 0) as total_genres,
        COALESCE(g.genres_list, '') as genres_list,
        COALESCE(c.total_companies, 0) as total_production_companies,
        c.main_company as main_production_company,
        COALESCE(co.total_countries, 0) as total_countries,
        co.main_country,
        COALESCE(l.total_languages, 0) as total_languages,
        
        m.quality_score,
        m.has_budget,
        m.has_revenue,
        m.has_overview
    FROM silver_tmdb.movies_tmdb m
    LEFT JOIN genres_agg g ON m.movielens_id = g.movielens_id
    LEFT JOIN companies_agg c ON m.movielens_id = c.movielens_id
    LEFT JOIN countries_agg co ON m.movielens_id = co.movielens_id
    LEFT JOIN languages_agg l ON m.movielens_id = l.movielens_id
    ORDER BY m.movielens_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} filmes agregados")
    return df


def aggregate_box_office() -> pd.DataFrame:
    """
    Agrega métricas de bilheteria e performance financeira.
    """
    print("  📊 Agregando desempenho de bilheteria...")
    
    conn = get_connection()
    
    query = """
    SELECT 
        movielens_id,
        title,
        release_year,
        budget,
        revenue,
        profit,
        roi,
        CASE 
            WHEN budget > 0 THEN ROUND((revenue::NUMERIC / budget), 2)
            ELSE NULL 
        END as payback_ratio,
        
        -- Categorias de budget
        CASE 
            WHEN budget = 0 THEN 'Unknown'
            WHEN budget < 1000000 THEN 'Micro'
            WHEN budget < 10000000 THEN 'Small'
            WHEN budget < 50000000 THEN 'Medium'
            WHEN budget < 100000000 THEN 'Large'
            ELSE 'Blockbuster'
        END as budget_category,
        
        -- Categorias de revenue
        CASE 
            WHEN revenue = 0 THEN 'Unknown'
            WHEN revenue < 1000000 THEN 'Flop'
            WHEN revenue < 50000000 THEN 'Modest'
            WHEN revenue < 200000000 THEN 'Success'
            WHEN revenue < 500000000 THEN 'Hit'
            ELSE 'Mega Hit'
        END as revenue_category,
        
        -- Categorias de ROI
        CASE 
            WHEN roi IS NULL OR budget = 0 THEN 'Unknown'
            WHEN roi < 0 THEN 'Loss'
            WHEN roi < 50 THEN 'Low'
            WHEN roi < 200 THEN 'Medium'
            WHEN roi < 500 THEN 'High'
            ELSE 'Exceptional'
        END as roi_category,
        
        -- Flags
        CASE WHEN profit > 0 THEN TRUE ELSE FALSE END as is_profitable,
        CASE WHEN revenue >= 200000000 THEN TRUE ELSE FALSE END as is_blockbuster
        
    FROM silver_tmdb.movies_tmdb
    WHERE budget > 0 AND revenue > 0
    ORDER BY revenue DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} filmes com dados financeiros")
    return df


def aggregate_studio_performance() -> pd.DataFrame:
    """
    Agrega performance de estúdios/produtoras.
    """
    print("  📊 Agregando performance de estúdios...")
    
    conn = get_connection()
    
    query = """
    WITH studio_movies AS (
        SELECT 
            pc.company_id,
            pc.company_name,
            m.movielens_id,
            m.title,
            m.budget,
            m.revenue,
            m.profit,
            m.roi
        FROM silver_tmdb.production_companies_tmdb pc
        JOIN silver_tmdb.movies_tmdb m ON pc.movielens_id = m.movielens_id
        WHERE m.budget > 0 AND m.revenue > 0
    ),
    studio_stats AS (
        SELECT 
            company_id,
            company_name,
            COUNT(*) as total_movies,
            SUM(budget) as total_budget,
            SUM(revenue) as total_revenue,
            SUM(profit) as total_profit,
            ROUND(AVG(roi)::NUMERIC, 2) as avg_roi,
            COUNT(*) FILTER (WHERE profit > 0) as profitable_movies
        FROM studio_movies
        GROUP BY company_id, company_name
        HAVING COUNT(*) >= 3
    ),
    top_movies AS (
        SELECT DISTINCT ON (company_id)
            company_id,
            title as top_movie_title,
            revenue as top_movie_revenue
        FROM studio_movies
        ORDER BY company_id, revenue DESC
    )
    SELECT 
        s.company_id,
        s.company_name,
        s.total_movies,
        s.total_budget,
        s.total_revenue,
        s.total_profit,
        s.avg_roi,
        s.profitable_movies,
        ROUND((s.profitable_movies::NUMERIC / s.total_movies * 100), 2) as success_rate,
        t.top_movie_title,
        t.top_movie_revenue
    FROM studio_stats s
    LEFT JOIN top_movies t ON s.company_id = t.company_id
    ORDER BY s.avg_roi DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} estúdios processados")
    return df


def aggregate_country_performance() -> pd.DataFrame:
    """
    Agrega performance por país produtor.
    """
    print("  📊 Agregando performance por país...")
    
    conn = get_connection()
    
    query = """
    WITH country_movies AS (
        SELECT 
            pc.country_code,
            pc.country_name,
            m.movielens_id,
            m.budget,
            m.revenue,
            m.profit,
            m.roi
        FROM silver_tmdb.production_countries_tmdb pc
        JOIN silver_tmdb.movies_tmdb m ON pc.movielens_id = m.movielens_id
        WHERE m.budget > 0 AND m.revenue > 0
    ),
    country_genres AS (
        SELECT DISTINCT ON (pc.country_code)
            pc.country_code,
            g.genre_name,
            COUNT(*) as genre_count
        FROM silver_tmdb.production_countries_tmdb pc
        JOIN silver_tmdb.genres_tmdb g ON pc.movielens_id = g.movielens_id
        GROUP BY pc.country_code, g.genre_name
        ORDER BY pc.country_code, genre_count DESC
    ),
    country_studios AS (
        SELECT DISTINCT ON (pc.country_code)
            pc.country_code,
            pco.company_name,
            COUNT(*) as company_count
        FROM silver_tmdb.production_countries_tmdb pc
        JOIN silver_tmdb.production_companies_tmdb pco ON pc.movielens_id = pco.movielens_id
        GROUP BY pc.country_code, pco.company_name
        ORDER BY pc.country_code, company_count DESC
    )
    SELECT 
        cm.country_code,
        cm.country_name,
        COUNT(*) as total_movies,
        ROUND(AVG(cm.budget)) as avg_budget,
        ROUND(AVG(cm.revenue)) as avg_revenue,
        ROUND(AVG(cm.roi)::NUMERIC, 2) as avg_roi,
        SUM(cm.profit) as total_profit,
        cg.genre_name as top_genre,
        cs.company_name as most_prolific_studio
    FROM country_movies cm
    LEFT JOIN country_genres cg ON cm.country_code = cg.country_code
    LEFT JOIN country_studios cs ON cm.country_code = cs.country_code
    GROUP BY cm.country_code, cm.country_name, cg.genre_name, cs.company_name
    HAVING COUNT(*) >= 5
    ORDER BY total_movies DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"  ✓ {len(df):,} países processados")
    return df