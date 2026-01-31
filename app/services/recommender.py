import pandas as pd
import pickle
import numpy as np
import os
import requests
from app.services.utils import get_poster
from app.models.rating import Rating
# Load preprocessed data
data_dir = os.path.join(os.path.dirname(__file__), '../../data')
try:
    movies = pickle.load(open(os.path.join(data_dir, 'movies.pkl'), 'rb'))
    similarity = np.load(os.path.join(data_dir, 'similarity.npy'))
except Exception as e:
    print(f"Warning: Could not load data - {e}")
    movies = pd.DataFrame(columns=['title', 'vote_average'])
    similarity = None


def recommend_by_movie(title, top_n=5):
    """Get recommendations based on movie title (case-insensitive)"""
    if movies.empty or similarity is None:
        return pd.DataFrame(columns=['title', 'vote_average', 'movie_id'])
    
    try:
        # Transformation en minuscules
        title_lower = title.lower()
        titles_lower = movies['title'].str.lower()

        idx = titles_lower[titles_lower == title_lower].index[0]

        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        return movies.iloc[movie_indices][['movie_id', 'title', 'vote_average']]
    except:
        return pd.DataFrame(columns=['title', 'vote_average', 'movie_id'])



def search_and_recommend(query, search_limit=10, reco_limit=5):
    query = query.lower()

    # 1️⃣ SEARCH
    search_results = movies[
        movies['title'].str.lower().str.contains(query)
    ][['movie_id', 'title', 'vote_average','release_date']].head(search_limit)

    if search_results.empty:
        return {
            "search_results": [],
            "recommendations": []
        }

    # add posters to search
    search_results = search_results.copy()
    search_results["poster"] = search_results["movie_id"].apply(get_poster)

    # 2️⃣ RECOMMEND
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

def recommend_by_movie_id(movie_id, top_n=5):
    """Retourne les films similaires pour un movie_id donné"""
    if movies.empty or similarity is None:
        return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])
    
    try:
        if movie_id not in movies['movie_id'].values:
            return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])
        
        idx = movies[movies['movie_id'] == movie_id].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        
        recs = movies.iloc[movie_indices][['movie_id', 'title', 'vote_average']].copy()
        recs['poster'] = recs['movie_id'].apply(get_poster)
        return recs.reset_index(drop=True)
    except Exception as e:
        print(f"Error in recommend_by_movie_id: {e}")
        return pd.DataFrame(columns=['movie_id', 'title', 'vote_average'])


from datetime import datetime

from datetime import datetime
import pandas as pd


from datetime import datetime
import pandas as pd

def personalized_home(current_user=None, top_n_per_fav=5, top_n_rated=10):
    """
    Recommandations :
    - utilisateur connecté → basées sur favoris
    - utilisateur non connecté → films récents bien notés
    - fallback → top-rated globaux
    """

    recommendations = pd.DataFrame(
        columns=['movie_id', 'title', 'vote_average', 'poster', 'release_date']
    )

    # 1️⃣ Favoris utilisateur
    user_favorites_ids = (
        current_user.favorites
        if current_user and current_user.favorites
        else []
    )

    # ===============================
    # CAS 1 : utilisateur avec favoris
    # ===============================
    if user_favorites_ids:
        for fav_id in user_favorites_ids:
            recs = recommend_by_movie_id(fav_id, top_n=top_n_per_fav)

            fav_movie = movies[
                movies['movie_id'] == fav_id
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

    # ======================================
    # CAS 2 : utilisateur non connecté
    # → films récents bien notés
    # ======================================
    movies_copy = movies.copy()
    movies_copy['release_date'] = pd.to_datetime(
        movies_copy['release_date'],
        errors='coerce'
    )

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

    # ===============================
    # CAS 3 : FALLBACK FINAL
    # ===============================
    top_rated = (
        movies_copy
        .sort_values(by='vote_average', ascending=False)
        .head(top_n_rated)
        .copy()
    )

    top_rated['poster'] = top_rated['movie_id'].apply(get_poster)
    return top_rated.reset_index(drop=True)



# Préparer un dictionnaire pour un accès rapide aux détails des films

movies_dict = movies.set_index('movie_id').to_dict(orient='index')


def get_movie_by_id(movie_id: int, current_user=None, db=None):
    """
    Return movie details by movie_id
    + infos user (favorite / rated) si utilisateur connecté
    """

    if movie_id not in movies_dict:
        return None

    movie = movies_dict[movie_id]
    poster = get_poster(movie_id)

    # ✅ Par défaut (user non connecté)
    is_favorite = False
    has_rated = False

    # ✅ Si user connecté
    if current_user:
        # Vérifier favoris
        if current_user.favorites:
            is_favorite = movie_id in current_user.favorites

        # Vérifier rating
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
        "title": movie.get("title"),
        "overview": movie.get("overview"),
        "genres": movie.get("genres"),
        "keywords": movie.get("keywords"),
        "cast": movie.get("cast"),
        "crew": movie.get("crew"),
        "poster": poster,
        "vote_average": movie.get("vote_average"),
        "release_date": movie.get("release_date"),

        # 🔥 INFOS USER
        "is_favorite": is_favorite,
        "has_rated": has_rated
    }

