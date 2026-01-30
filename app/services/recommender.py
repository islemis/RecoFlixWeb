import pandas as pd
import pickle
import numpy as np
import os
import requests
from app.services.utils import get_poster
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
    """Get recommendations based on movie title"""
    if movies.empty or similarity is None:
        return pd.DataFrame(columns=['title', 'vote_average'])
    
    try:
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        return movies.iloc[movie_indices][['movie_id', 'title', 'vote_average']]
    except:
        return pd.DataFrame(columns=['title', 'vote_average'])

def personalized_home(user_favorites, top_n_reco=10, top_n_rated=10):
    # CAS 1 : utilisateur avec favoris
    if user_favorites and len(user_favorites) > 0:
        recommendations = pd.DataFrame(columns=['title', 'vote_average','movie_id'])

        for fav in user_favorites:
            recs = recommend_by_movie(fav, top_n=top_n_reco)

            # 🔐 sécurité
            if recs is not None and not recs.empty:
                recommendations = pd.concat([recommendations, recs])

        if recommendations.empty:
            return recommendations

        recommendations = (
            recommendations
            .drop_duplicates(subset='title')
            .head(top_n_reco)
        )
        recommendations["poster"] = recommendations["movie_id"].apply(get_poster)

        return recommendations.reset_index(drop=True)



def search_and_recommend(query, search_limit=10, reco_limit=5):
    query = query.lower()

    # 1️⃣ SEARCH
    search_results = movies[
        movies['title'].str.lower().str.contains(query)
    ][['movie_id', 'title', 'vote_average']].head(search_limit)

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

