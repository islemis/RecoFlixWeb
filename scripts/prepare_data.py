import pandas as pd
import ast
import pickle
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Preparing data...")

try:
    movies = pd.read_csv("data/movies.csv")
    credits = pd.read_csv("data/credits.csv")
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("Make sure data/movies.csv and data/credits.csv exist")
    exit(1)
# Rename movies.id → movie_id
movies.rename(columns={"id": "movie_id"}, inplace=True)

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L
def get_director_producer_names(crew_str):
    """Return a list containing director(s) and producer(s) names"""
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

    
movies = movies[['movie_id','title','overview','genres','keywords','vote_average','release_date']]
movies = movies.merge(credits, on='movie_id')
movies['crew'] = movies['crew'].apply(get_director_producer_names)  # only directors and producers
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(
    lambda x: [i['name'] for i in ast.literal_eval(x)[:3]]
)

movies['tags'] = (
    movies['genres'] +
    movies['keywords'] +
    movies['cast'] 
)


movies['tags'] = movies['tags'].apply(lambda x: " ".join(x))
features = movies[['tags', 'vote_average']]
movies.rename(columns={'title_x': 'title'}, inplace=True)

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

print("✅ Data prepared successfully")
