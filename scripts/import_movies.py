import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import ast
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.core.database import SessionLocal
from app.services.utils import get_poster
import numpy as np

def convert(obj):
    if pd.isna(obj):
        return []
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def get_director_producer_names(crew_str):
    if pd.isna(crew_str):
        return []
    names = []
    try:
        crew = ast.literal_eval(crew_str)
        for member in crew:
            job = member.get("job", "").lower()
            if job == "director" or job == "producer":
                names.append(member.get("name"))
    except Exception:
        pass
    return names

def safe_str(val):
    if pd.isna(val) or val is None:
        return ""
    return str(val)

def import_movies():
    movies = pd.read_csv("data/movies.csv")
    credits = pd.read_csv("data/credits.csv")
    movies.rename(columns={"id": "movie_id"}, inplace=True)
    movies = movies[['movie_id','title','overview','genres','keywords','vote_average','release_date','vote_count']]
    movies = movies.merge(credits, on='movie_id')
    movies['crew'] = movies['crew'].apply(get_director_producer_names)
    movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)[:3]] if not pd.isna(x) else [])
    movies.rename(columns={'title_x': 'title'}, inplace=True)
    db: Session = SessionLocal()
    for _, row in movies.iterrows():
        movie_id = int(row["movie_id"])
        movie = Movie(
            movie_id=movie_id,
            title=safe_str(row.get("title")),
            overview=safe_str(row.get("overview")),
            genres=",".join(row["genres"]) if isinstance(row["genres"], list) else "",
            keywords=",".join(row["keywords"]) if isinstance(row["keywords"], list) else "",
            cast=",".join(row["cast"]) if isinstance(row["cast"], list) else "",
            crew=",".join(row["crew"]) if isinstance(row["crew"], list) else "",
            vote_average=float(row.get("vote_average", 0)) if not pd.isna(row.get("vote_average")) else 0,
            vote_count=int(row.get("vote_count", 0)) if not pd.isna(row.get("vote_count", 0)) else 0,
            release_date=row["release_date"] if not pd.isna(row["release_date"]) else None
        )
        db.merge(movie)
    db.commit()
    db.close()

if __name__ == "__main__":
    import_movies()
