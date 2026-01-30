import requests
import os

TMDB_API_KEY = "d9527eb03d66a68663e398d238b24bb5"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

def get_poster(movie_id: int) -> str | None:
    """Return full poster URL for a given TMDB movie ID."""
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=3
        )
        r.raise_for_status()
        poster_path = r.json().get("poster_path")
        if poster_path:
            return TMDB_IMG + poster_path
        return None
    except Exception as e:
        print(f"⚠️ Error fetching poster for {movie_id}: {e}")
        return None
