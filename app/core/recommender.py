import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

print("🚀 Loading recommendation models...")

# Load precomputed data
movies = pickle.load(open("data/movies.pkl", "rb"))
preprocessor = pickle.load(open("data/preprocessor.pkl", "rb"))
similarity = np.load("data/similarity.npy")

print("✅ Recommendation system readyyy")
print(movies.columns)
print(movies.head())
