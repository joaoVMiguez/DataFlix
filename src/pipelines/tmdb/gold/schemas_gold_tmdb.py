"""
Schemas Gold TMDB - Dados agregados do TMDB
"""

DROP_GOLD_TMDB_TABLES = """
DROP TABLE IF EXISTS gold_tmdb.fact_country_performance CASCADE;
DROP TABLE IF EXISTS gold_tmdb.fact_studio_performance CASCADE;
DROP TABLE IF EXISTS gold_tmdb.fact_box_office CASCADE;
DROP TABLE IF EXISTS gold_tmdb.dim_movies_tmdb CASCADE;
"""

# Dimensão principal de filmes TMDB (agregada)
CREATE_DIM_MOVIES_TMDB = """
CREATE TABLE gold_tmdb.dim_movies_tmdb (
    movielens_id INTEGER PRIMARY KEY,
    tmdb_id INTEGER NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    release_year SMALLINT,
    release_decade INTEGER,
    runtime INTEGER,
    
    -- Financial Metrics
    budget BIGINT,
    revenue BIGINT,
    profit BIGINT,
    roi NUMERIC(18,2),
    
    -- Popularity & Ratings
    popularity NUMERIC(10,3),
    vote_average NUMERIC(4,2),
    vote_count INTEGER,
    
    -- Aggregated Data
    total_genres INTEGER,
    genres_list TEXT,
    total_production_companies INTEGER,
    main_production_company VARCHAR(200),
    total_countries INTEGER,
    main_country VARCHAR(100),
    total_languages INTEGER,
    
    -- Quality Flags
    quality_score INTEGER,
    has_budget BOOLEAN,
    has_revenue BOOLEAN,
    has_overview BOOLEAN,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_movies_tmdb_year ON gold_tmdb.dim_movies_tmdb(release_year);
CREATE INDEX idx_dim_movies_tmdb_budget ON gold_tmdb.dim_movies_tmdb(budget);
CREATE INDEX idx_dim_movies_tmdb_revenue ON gold_tmdb.dim_movies_tmdb(revenue);
CREATE INDEX idx_dim_movies_tmdb_roi ON gold_tmdb.dim_movies_tmdb(roi DESC);
CREATE INDEX idx_dim_movies_tmdb_quality ON gold_tmdb.dim_movies_tmdb(quality_score DESC);

COMMENT ON TABLE gold_tmdb.dim_movies_tmdb IS 'Dimensão de filmes TMDB agregada (Gold)';
"""

# Fato de desempenho de bilheteria
CREATE_FACT_BOX_OFFICE = """
CREATE TABLE gold_tmdb.fact_box_office (
    movielens_id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    release_year SMALLINT,
    
    budget BIGINT NOT NULL,
    revenue BIGINT NOT NULL,
    profit BIGINT,
    roi NUMERIC(18,2),
    payback_ratio NUMERIC(10,2),
    
    -- Categories
    budget_category VARCHAR(20),
    revenue_category VARCHAR(20),
    roi_category VARCHAR(20),
    
    -- Flags
    is_profitable BOOLEAN,
    is_blockbuster BOOLEAN,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movielens_id) REFERENCES gold_tmdb.dim_movies_tmdb(movielens_id)
);

CREATE INDEX idx_box_office_profit ON gold_tmdb.fact_box_office(profit DESC);
CREATE INDEX idx_box_office_roi ON gold_tmdb.fact_box_office(roi DESC);
CREATE INDEX idx_box_office_category ON gold_tmdb.fact_box_office(budget_category);

COMMENT ON TABLE gold_tmdb.fact_box_office IS 'Análise de desempenho financeiro';
"""

# Fato de performance de estúdios/produtoras
CREATE_FACT_STUDIO_PERFORMANCE = """
CREATE TABLE gold_tmdb.fact_studio_performance (
    company_id INTEGER PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    
    total_movies INTEGER NOT NULL,
    total_budget BIGINT,
    total_revenue BIGINT,
    total_profit BIGINT,
    avg_roi NUMERIC(18,2),
    
    profitable_movies INTEGER,
    success_rate NUMERIC(5,2),
    
    top_movie_title VARCHAR(500),
    top_movie_revenue BIGINT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_studio_roi ON gold_tmdb.fact_studio_performance(avg_roi DESC);
CREATE INDEX idx_studio_revenue ON gold_tmdb.fact_studio_performance(total_revenue DESC);
CREATE INDEX idx_studio_success ON gold_tmdb.fact_studio_performance(success_rate DESC);

COMMENT ON TABLE gold_tmdb.fact_studio_performance IS 'Performance agregada de produtoras';
"""

# Fato de performance por país
CREATE_FACT_COUNTRY_PERFORMANCE = """
CREATE TABLE gold_tmdb.fact_country_performance (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    
    total_movies INTEGER NOT NULL,
    avg_budget BIGINT,
    avg_revenue BIGINT,
    avg_roi NUMERIC(18,2),
    total_profit BIGINT,
    
    top_genre VARCHAR(100),
    most_prolific_studio VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_country_movies ON gold_tmdb.fact_country_performance(total_movies DESC);
CREATE INDEX idx_country_roi ON gold_tmdb.fact_country_performance(avg_roi DESC);

COMMENT ON TABLE gold_tmdb.fact_country_performance IS 'Performance por país produtor';
"""

# Lista de todos os schemas
ALL_GOLD_TMDB_SCHEMAS = [
    DROP_GOLD_TMDB_TABLES,
    CREATE_DIM_MOVIES_TMDB,
    CREATE_FACT_BOX_OFFICE,
    CREATE_FACT_STUDIO_PERFORMANCE,
    CREATE_FACT_COUNTRY_PERFORMANCE
]