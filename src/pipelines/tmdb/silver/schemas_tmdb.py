"""
Schemas SQL para tabelas Silver TMDB
"""

CREATE_SCHEMA_SILVER_TMDB = """
CREATE SCHEMA IF NOT EXISTS silver_tmdb;
"""

CREATE_SCHEMA_GOLD_TMDB = """
CREATE SCHEMA IF NOT EXISTS gold_tmdb;
"""

# ✅ DROPAR TABELAS ANTIGAS
DROP_ALL_TABLES = """
DROP TABLE IF EXISTS silver_tmdb.spoken_languages_tmdb CASCADE;
DROP TABLE IF EXISTS silver_tmdb.production_countries_tmdb CASCADE;
DROP TABLE IF EXISTS silver_tmdb.production_companies_tmdb CASCADE;
DROP TABLE IF EXISTS silver_tmdb.genres_tmdb CASCADE;
DROP TABLE IF EXISTS silver_tmdb.movies_tmdb CASCADE;
"""

# Tabela principal de filmes (✅ ROI COM PRECISÃO MAIOR)
CREATE_MOVIES_TMDB = """
CREATE TABLE silver_tmdb.movies_tmdb (
    movielens_id INTEGER PRIMARY KEY,
    imdb_id VARCHAR(20) NOT NULL,
    tmdb_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    original_language VARCHAR(10),
    overview TEXT,
    tagline TEXT,
    status VARCHAR(50),
    release_date DATE,
    release_year INTEGER,
    release_month INTEGER,
    release_decade INTEGER,
    runtime INTEGER,
    budget BIGINT,
    revenue BIGINT,
    profit BIGINT,
    roi NUMERIC(18, 2),
    popularity NUMERIC(15, 3),
    vote_average NUMERIC(4, 2),
    vote_count INTEGER,
    adult BOOLEAN,
    video BOOLEAN,
    homepage TEXT,
    poster_path VARCHAR(200),
    backdrop_path VARCHAR(200),
    has_budget BOOLEAN,
    has_revenue BOOLEAN,
    has_overview BOOLEAN,
    has_poster BOOLEAN,
    has_backdrop BOOLEAN,
    budget_category VARCHAR(20),
    quality_score INTEGER,
    extracted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movies_tmdb_tmdb_id ON silver_tmdb.movies_tmdb(tmdb_id);
CREATE INDEX idx_movies_tmdb_imdb_id ON silver_tmdb.movies_tmdb(imdb_id);
CREATE INDEX idx_movies_tmdb_release_year ON silver_tmdb.movies_tmdb(release_year);
CREATE INDEX idx_movies_tmdb_budget ON silver_tmdb.movies_tmdb(budget);
CREATE INDEX idx_movies_tmdb_revenue ON silver_tmdb.movies_tmdb(revenue);

COMMENT ON TABLE silver_tmdb.movies_tmdb IS 'Tabela principal de filmes TMDB (Silver Layer)';
"""

# Tabela de gêneros
CREATE_GENRES_TMDB = """
CREATE TABLE silver_tmdb.genres_tmdb (
    id SERIAL PRIMARY KEY,
    movielens_id INTEGER NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    tmdb_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    genre_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movielens_id) REFERENCES silver_tmdb.movies_tmdb(movielens_id) ON DELETE CASCADE
);

CREATE INDEX idx_genres_tmdb_movielens_id ON silver_tmdb.genres_tmdb(movielens_id);
CREATE INDEX idx_genres_tmdb_genre_id ON silver_tmdb.genres_tmdb(genre_id);
CREATE INDEX idx_genres_tmdb_genre_name ON silver_tmdb.genres_tmdb(genre_name);

COMMENT ON TABLE silver_tmdb.genres_tmdb IS 'Gêneros dos filmes (normalizado)';
"""

# Tabela de empresas produtoras
CREATE_PRODUCTION_COMPANIES_TMDB = """
CREATE TABLE silver_tmdb.production_companies_tmdb (
    id SERIAL PRIMARY KEY,
    movielens_id INTEGER NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    tmdb_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    company_logo_path VARCHAR(200),
    company_country VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movielens_id) REFERENCES silver_tmdb.movies_tmdb(movielens_id) ON DELETE CASCADE
);

CREATE INDEX idx_companies_tmdb_movielens_id ON silver_tmdb.production_companies_tmdb(movielens_id);
CREATE INDEX idx_companies_tmdb_company_id ON silver_tmdb.production_companies_tmdb(company_id);
CREATE INDEX idx_companies_tmdb_company_name ON silver_tmdb.production_companies_tmdb(company_name);

COMMENT ON TABLE silver_tmdb.production_companies_tmdb IS 'Empresas produtoras dos filmes';
"""

# Tabela de países de produção
CREATE_PRODUCTION_COUNTRIES_TMDB = """
CREATE TABLE silver_tmdb.production_countries_tmdb (
    id SERIAL PRIMARY KEY,
    movielens_id INTEGER NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    tmdb_id INTEGER NOT NULL,
    country_code VARCHAR(10) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movielens_id) REFERENCES silver_tmdb.movies_tmdb(movielens_id) ON DELETE CASCADE
);

CREATE INDEX idx_countries_tmdb_movielens_id ON silver_tmdb.production_countries_tmdb(movielens_id);
CREATE INDEX idx_countries_tmdb_country_code ON silver_tmdb.production_countries_tmdb(country_code);

COMMENT ON TABLE silver_tmdb.production_countries_tmdb IS 'Países de produção dos filmes';
"""

# Tabela de idiomas
CREATE_SPOKEN_LANGUAGES_TMDB = """
CREATE TABLE silver_tmdb.spoken_languages_tmdb (
    id SERIAL PRIMARY KEY,
    movielens_id INTEGER NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    tmdb_id INTEGER NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    language_name VARCHAR(100) NOT NULL,
    language_english_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movielens_id) REFERENCES silver_tmdb.movies_tmdb(movielens_id) ON DELETE CASCADE
);

CREATE INDEX idx_languages_tmdb_movielens_id ON silver_tmdb.spoken_languages_tmdb(movielens_id);
CREATE INDEX idx_languages_tmdb_language_code ON silver_tmdb.spoken_languages_tmdb(language_code);

COMMENT ON TABLE silver_tmdb.spoken_languages_tmdb IS 'Idiomas falados nos filmes';
"""

# ✅ LISTA ATUALIZADA: DROPAR ANTES DE CRIAR
ALL_SCHEMAS = [
    CREATE_SCHEMA_SILVER_TMDB,
    CREATE_SCHEMA_GOLD_TMDB,
    DROP_ALL_TABLES,  # ✅ ADICIONADO
    CREATE_MOVIES_TMDB,
    CREATE_GENRES_TMDB,
    CREATE_PRODUCTION_COMPANIES_TMDB,
    CREATE_PRODUCTION_COUNTRIES_TMDB,
    CREATE_SPOKEN_LANGUAGES_TMDB
]