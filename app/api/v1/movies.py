from app.services.recommender import (
    personalized_home,
    search_and_recommend,
    get_movie_by_id
)

from fastapi import APIRouter , Body
from typing import List, Optional , Dict

router = APIRouter()


@router.get("/search")
def search(query: str):

    result = search_and_recommend(query)

    return {
        "search_results": result["search_results"].to_dict(orient="records"),
        "recommendations": result["recommendations"].to_dict(orient="records")
    }

@router.post("/home")
def home(payload: Dict[str, Optional[List[int]]] = Body(...)):
    user_favorites = payload.get("user_favorites")
    print("User favorites:", user_favorites)
    recommendations = personalized_home(user_favorites)

    return {
        "recommendations": recommendations.to_dict(orient="records") if not recommendations.empty else []
    }

@router.get("/{movie_id}")
def movie(movie_id: int):
    movie_data = get_movie_by_id(movie_id)
    if not movie_data:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie_data
