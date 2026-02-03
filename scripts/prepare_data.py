import pandas as pd
import ast
import pickle
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.movie import Movie

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Preparing data from database...")

def convert_str_to_list(obj):
    if pd.isna(obj) or obj is None or obj == '':
        return []
    return obj.split(',')

def get_movies_from_db():
    db: Session = SessionLocal()
    movies = db.query(Movie).all()
    db.close()
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'movie_id': m.id,
            'title': m.title,
            'overview': m.overview,
            'genres': m.genres,
            'keywords': m.keywords,
            'vote_average': m.vote_average,
            'release_date': m.release_date,
            'cast': m.cast,
            'crew': m.crew
        }
        for m in movies
    ])
    return df

movies = get_movies_from_db()

movies['genres'] = movies['genres'].apply(convert_str_to_list)
movies['keywords'] = movies['keywords'].apply(convert_str_to_list)
movies['cast'] = movies['cast'].apply(convert_str_to_list)
movies['crew'] = movies['crew'].apply(convert_str_to_list)

movies['tags'] = (
    movies['genres'] +
    movies['keywords'] +
    movies['cast']
)

movies['tags'] = movies['tags'].apply(lambda x: " ".join(x))
features = movies[['tags', 'vote_average']]

preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(max_features=5000, stop_words='english'), 'tags'),
        ('rating', MinMaxScaler(), ['vote_average'])
    ]
)

X = preprocessor.fit_transform(features)
similarity = cosine_similarity(X)
pickle.dump(movies, open("data/movies.pkl", "wb"))
pickle.dump(preprocessor, open("data/preprocessor.pkl", "wb"))
np.save("data/similarity.npy", similarity)

print("✅ Data prepared successfully from database")
