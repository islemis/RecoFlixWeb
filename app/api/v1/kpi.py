from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.core.database import get_db
from app.schemas.dashboard import (
    KPISummary,
    RatingOverTime,
    GenreStat,
    TopMovie,
    ActivityItem,
    UserGrowth
)

router = APIRouter()

@router.get("/kpi", response_model=KPISummary)
def get_kpi(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    movies = db.execute(text("SELECT COUNT(*) FROM movies")).scalar()
    ratings = db.execute(text("SELECT COUNT(*) FROM ratings")).scalar()

    return {
        "users": users,
        "movies": movies,
        "ratings": ratings
    }

@router.get("/ratings-over-time", response_model=List[RatingOverTime])
def ratings_over_time(db: Session = Depends(get_db)):
    query = """
        SELECT DATE(created_at) AS date, COUNT(*) AS count
        FROM ratings
        GROUP BY DATE(created_at)
        ORDER BY date
    """
    result = db.execute(text(query)).fetchall()
    return [{"date": str(row.date), "count": row.count} for row in result]

@router.get("/ratings-by-genre", response_model=List[GenreStat])
def ratings_by_genre(db: Session = Depends(get_db)):
    # Genres are stored as comma-separated string in movies table
    # We'll fetch relevant data and process in Python
    query = """
        SELECT m.genres, COUNT(r.id) AS count
        FROM movies m
        JOIN ratings r ON r.movie_id = m.movie_id
        WHERE m.genres IS NOT NULL
        GROUP BY m.genres
    """
    result = db.execute(text(query)).fetchall()
    
    genre_counts = {}
    for row in result:
        if not row.genres:
            continue
        genres_list = [g.strip() for g in row.genres.split(',')]
        for genre in genres_list:
            genre_counts[genre] = genre_counts.get(genre, 0) + row.count
            
    # Convert to list and sort
    stats = [{"genre": k, "count": v} for k, v in genre_counts.items()]
    stats.sort(key=lambda x: x["count"], reverse=True)
    
    return stats[:10]  # Return top 10

@router.get("/top-movies", response_model=List[TopMovie])
def top_movies(db: Session = Depends(get_db)):
    query = """
        SELECT 
            title,
            vote_average,
            release_date
        FROM movies
        WHERE vote_average IS NOT NULL
        ORDER BY vote_average DESC, release_date DESC
        LIMIT 10
    """
    
    result = db.execute(text(query)).fetchall()

    return [
        {
            "title": row.title,
            "avg_rating": float(row.vote_average),
            "release_date": row.release_date
        }
        for row in result
    ]


@router.get("/activity", response_model=List[ActivityItem])
def recent_activity(db: Session = Depends(get_db)):
    query = """
        SELECT r.id, u.username, m.title, r.rating, r.created_at
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        JOIN movies m ON r.movie_id = m.movie_id
        ORDER BY r.created_at DESC
        LIMIT 10
    """
    result = db.execute(text(query)).fetchall()
    return [
        {
            "id": row.id,
            "user_name": row.username,
            "movie_title": row.title,
            "rating": row.rating,
            "created_at": row.created_at
        }
        for row in result
    ]

@router.get("/user-growth", response_model=List[UserGrowth])
def user_growth(db: Session = Depends(get_db)):
    query = """
        SELECT DATE(created_at) AS date, COUNT(*) AS new_users
        FROM users
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """
    result = db.execute(text(query)).fetchall()
    return [{"date": str(row.date), "new_users": row.new_users} for row in result]
