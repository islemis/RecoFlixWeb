from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.movie import Movie
import numpy as np
import pandas as pd
from app.services.utils import get_poster
from app.models.rating import Rating
import os

# Load preprocessed similarity and preprocessor
SIMILARITY_PATH = os.path.join(os.path.dirname(__file__), '../../data/similarity.npy')
similarity = np.load(SIMILARITY_PATH) if os.path.exists(SIMILARITY_PATH) else None

# Helper to get all movies as DataFrame (for similarity index)
def get_movies_df():
    db: Session = SessionLocal()
    movies = db.query(Movie).all()
    db.close()
    df = pd.DataFrame([
        {
            'movie_id': m.movie_id,
            'title': m.title,
            'vote_average': m.vote_average,
            'release_date': m.release_date,
            'poster': m.poster,
            'genres': m.genres,
            'keywords': m.keywords,
            'cast': m.cast,
            'crew': m.crew
        }
        for m in movies
    ])
    return df

movies_df = get_movies_df()

# --- Recommendation functions ---
def recommend_by_movie(title, top_n=5):
    if movies_df.empty or similarity is None:
        return pd.DataFrame(columns=['title', 'vote_average', 'movie_id'])
    try:
        title_lower = title.lower()
        titles_lower = movies_df['title'].str.lower()
        idx = titles_lower[titles_lower == title_lower].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        return movies_df.iloc[movie_indices][['movie_id', 'title', 'vote_average']]
    except:
        return pd.DataFrame(columns=['title', 'vote_average', 'movie_id'])

def search_and_recommend(query, search_limit=10, reco_limit=10):
    query = query.lower()
    search_results = movies_df[
        movies_df['title'].str.lower().str.contains(query)
    ][['movie_id', 'title', 'vote_average','release_date']].head(search_limit)
    if search_results.empty:
        return {
            "search_results": [],
            "recommendations": []
        }
    search_results = search_results.copy()
    search_results["poster"] = search_results["movie_id"].apply(get_poster)
    recommendations = pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])
    for title in search_results['title'][:3]:
        recs = recommend_by_movie(title, reco_limit)
        if recs is not None and not recs.empty:
            recommendations = pd.concat([recommendations, recs])
    if not recommendations.empty:
        recommendations = (
            recommendations
            .drop_duplicates(subset='title')
            .head(reco_limit)
            .copy()
        )
        recommendations["poster"] = recommendations["movie_id"].apply(get_poster)
    return {
        "search_results": search_results.reset_index(drop=True),
        "recommendations": recommendations.reset_index(drop=True)
    }

def recommend_by_movie_id(movie_id, top_n=10):
    if movies_df.empty or similarity is None:
        return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])
    try:
        if movie_id not in movies_df['movie_id'].values:
            return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])
        idx = movies_df[movies_df['movie_id'] == movie_id].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        recs = movies_df.iloc[movie_indices][['movie_id', 'title', 'vote_average']].copy()
        recs['poster'] = recs['movie_id'].apply(get_poster)
        return recs.reset_index(drop=True)
    except Exception as e:
        print(f"Error in recommend_by_movie_id: {e}")
        return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])

def personalized_home(current_user=None, top_n_per_fav=5, top_n_rated=10):
    recommendations = pd.DataFrame(
        columns=['movie_id', 'title', 'vote_average', 'poster', 'release_date']
    )
    user_favorites_ids = (
        current_user.favorites
        if current_user and current_user.favorites
        else []
    )
    if user_favorites_ids:
        for fav_id in user_favorites_ids:
            recs = recommend_by_movie_id(fav_id, top_n=top_n_per_fav)
            fav_movie = movies_df[
                movies_df['movie_id'] == fav_id
            ][['movie_id', 'title', 'vote_average', 'release_date']].copy()
            if not fav_movie.empty:
                fav_movie['poster'] = fav_movie['movie_id'].apply(get_poster)
                recs = pd.concat([fav_movie, recs])
            if recs is not None and not recs.empty:
                recommendations = pd.concat([recommendations, recs])
        if not recommendations.empty:
            return (
                recommendations
                .drop_duplicates(subset='movie_id')
                .reset_index(drop=True)
            )
    movies_copy = movies_df.copy()
    movies_copy['release_date'] = pd.to_datetime(
        movies_copy['release_date'],
        errors='coerce'
    )
    from datetime import datetime
    current_year = datetime.now().year
    recent_movies = movies_copy[
        movies_copy['release_date'].dt.year >= current_year - 1
    ]
    if not recent_movies.empty:
        recent_movies = (
            recent_movies
            .sort_values(by='vote_average', ascending=False)
            .head(top_n_rated)
            .copy()
        )
        recent_movies['poster'] = recent_movies['movie_id'].apply(get_poster)
        return recent_movies.reset_index(drop=True)
    top_rated = (
        movies_copy
        .sort_values(by='vote_average', ascending=False)
        .head(top_n_rated)
        .copy()
    )
    top_rated['poster'] = top_rated['movie_id'].apply(get_poster)
    return top_rated.reset_index(drop=True)

def get_movie_by_id(movie_id: int, current_user=None, db=None):
    db_session = db or SessionLocal()
    movie = db_session.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        return None
    poster = movie.poster or get_poster(movie_id)
    is_favorite = False
    has_rated = False
    if current_user:
        if current_user.favorites:
            is_favorite = movie_id in current_user.favorites
        if db:
            rating = (
                db.query(Rating)
                .filter(
                    Rating.user_id == current_user.id,
                    Rating.movie_id == movie_id
                )
                .first()
            )
            has_rated = rating is not None
    return {
        "movie_id": movie_id,
        "title": movie.title,
        "overview": movie.overview,
        "genres": movie.genres,
        "keywords": movie.keywords,
        "cast": movie.cast,
        "crew": movie.crew,
        "poster": poster,
        "vote_average": movie.vote_average,
        "release_date": movie.release_date,
        "is_favorite": is_favorite,
        "has_rated": has_rated
    }

