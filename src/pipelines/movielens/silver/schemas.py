CREATE_SILVER_SCHEMA = """
-- Remover schema antigo se existir
DROP SCHEMA IF EXISTS silver CASCADE;

-- Criar schema
CREATE SCHEMA silver;

-- Tabela de filmes (sem gêneros, agora normalizado)
CREATE TABLE silver.movies_silver (
    movieid INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    release_year SMALLINT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de gêneros (normalizada)
CREATE TABLE silver.genres_silver (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relacionamento filme-gênero (DE-PARA)
CREATE TABLE silver.movie_genres_silver (
    movieid INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (movieid, genre_id),
    FOREIGN KEY (movieid) REFERENCES silver.movies_silver(movieid) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES silver.genres_silver(genre_id) ON DELETE CASCADE
);

-- Tabela de ratings
CREATE TABLE silver.ratings_silver (
    userid INTEGER NOT NULL,
    movieid INTEGER NOT NULL,
    rating NUMERIC(2,1) NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    timestamp BIGINT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (userid, movieid, timestamp)
);

-- Tabela de tags
CREATE TABLE silver.tags_silver (
    userid INTEGER NOT NULL,
    movieid INTEGER NOT NULL,
    tag VARCHAR(255),
    timestamp BIGINT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (userid, movieid, timestamp)
);

-- Tabela de links
CREATE TABLE silver.links_silver (
    movieid INTEGER PRIMARY KEY,
    imdbid VARCHAR(20),
    tmdbid VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance
CREATE INDEX idx_movie_genres_movieid ON silver.movie_genres_silver(movieid);
CREATE INDEX idx_movie_genres_genreid ON silver.movie_genres_silver(genre_id);
CREATE INDEX idx_ratings_movieid ON silver.ratings_silver(movieid);
CREATE INDEX idx_ratings_userid ON silver.ratings_silver(userid);
CREATE INDEX idx_tags_movieid ON silver.tags_silver(movieid);
CREATE INDEX idx_movies_title ON silver.movies_silver(title);
CREATE INDEX idx_movies_year ON silver.movies_silver(release_year);

-- View útil para consultar filmes com gêneros
CREATE OR REPLACE VIEW silver.vw_movies_with_genres AS
SELECT 
    m.movieid,
    m.title,
    m.release_year,
    STRING_AGG(g.genre_name, ' | ' ORDER BY g.genre_name) as genres
FROM silver.movies_silver m
LEFT JOIN silver.movie_genres_silver mg ON m.movieid = mg.movieid
LEFT JOIN silver.genres_silver g ON mg.genre_id = g.genre_id
GROUP BY m.movieid, m.title, m.release_year;

-- Comentários nas tabelas
COMMENT ON TABLE silver.movies_silver IS 'Dados de filmes na camada Silver (sem gêneros inline)';
COMMENT ON TABLE silver.genres_silver IS 'Gêneros únicos normalizados';
COMMENT ON TABLE silver.movie_genres_silver IS 'Relacionamento N:N entre filmes e gêneros';
COMMENT ON TABLE silver.ratings_silver IS 'Avaliações de usuários na camada Silver';
COMMENT ON TABLE silver.tags_silver IS 'Tags atribuídas por usuários na camada Silver';
COMMENT ON TABLE silver.links_silver IS 'Links externos (IMDB, TMDB) na camada Silver';
"""

def create_silver_tables(conn):
    """Cria as tabelas Silver no Postgres"""
    with conn.cursor() as cur:
        cur.execute(CREATE_SILVER_SCHEMA)
        conn.commit()
    print("✓ Schema Silver criado com sucesso!")