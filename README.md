# 🎬 DataFlix - Movie Data Pipeline

Complete data pipeline using Medallion Architecture (Bronze → Silver → Gold) to process and analyze MovieLens movie data.

## 📊 Architecture

Pipeline based on **Medallion Architecture** with 3 layers:

### 🥉 Bronze (Raw Data)
- **Storage**: MinIO (Object Storage)
- **Format**: Raw CSVs
- **Data**: movies.csv, ratings.csv, tags.csv, links.csv

### 🥈 Silver (Cleaned & Normalized) ✅ IMPLEMENTED
- **Storage**: PostgreSQL
- **Status**: ✅ Operational
- **Tables**:
  - `movies_silver` - 87,585 movies
  - `genres_silver` - 19 unique genres
  - `movie_genres_silver` - 147,090 movie-genre relationships
  - `ratings_silver` - 32,000,204 ratings
  - `tags_silver` - 1,105,512 tags
  - `links_silver` - 87,585 links (IMDB/TMDB)

### 🥇 Gold (Analytics Ready) 🚧 IN DEVELOPMENT
- **Storage**: PostgreSQL
- **Status**: 🚧 Next phase
- **Goal**: Aggregated and modeled data for dashboards

---

## 🛠️ Tech Stack

| Technology | Usage | Port |
|------------|-------|------|
| **PostgreSQL 15** | Relational database | 5432 |
| **MinIO** | Object storage (S3-compatible) | 9000/9001 |
| **pgAdmin** | Web interface for PostgreSQL | 5050 |
| **Python 3.13** | Pipeline language | - |
| **Docker Compose** | Container orchestration | - |
| **Pandas** | Data manipulation | - |
| **psycopg2** | PostgreSQL connector | - |


## 📁 Project Structure

The project follows a modular structure:

- **`src/silver/`** - Clean and normalized data layer
- **`src/gold/`** - Aggregated data for analytics (in development)
- **`src/config/`** - Database and configuration files
- **`src/minio_client/`** - MinIO object storage client
- **`src/utils/`** - Data validation and logging utilities
- **`main.py`** - Main pipeline execution script
- **`docker-compose.yml`** - Infrastructure orchestration
- **`requirements.txt`** - Python dependencies

## 🚀 How to Run

### 1. Start infrastructure
```bash
docker-compose up -d

This will start:

PostgreSQL (port 5432)
pgAdmin (http://localhost:5050)
MinIO (http://localhost:9001)

2. Access services
pgAdmin:

URL: http://localhost:5050
Email: admin@admin.com
Password: admin

MinIO Console:

URL: http://localhost:9001
User: minioadmin
Password: minioadmin

3. Run Silver pipeline
docker-compose run --rm dataflix-pipeline

4. Validate loaded data
docker-compose run --rm dataflix-pipeline python utils/data_quality.py

📊 Data
Silver Layer
Main tables:

silver.movies_silver - 87,585 movies
silver.genres_silver - 19 unique genres
silver.movie_genres_silver - 147,090 movie-genre relationships
silver.ratings_silver - 32 million ratings
silver.tags_silver - 1.1 million tags
silver.links_silver - Links to IMDB and TMDB

Useful views:

silver.vw_movies_complete - Movies with all data
silver.vw_top_rated_movies - Top ranked movies
silver.vw_movies_by_genre - Statistics by genre
silver.vw_ratings_by_year - Temporal evolution
silver.vw_popular_tags - Most used tags

📈 Next Steps
In Development

 Gold Layer - Create aggregations and dimensional modeling
 REST API - Expose data via FastAPI
 Dashboard - Visualizations with Streamlit