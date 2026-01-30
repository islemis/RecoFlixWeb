from app.services.recommender import (
    personalized_home,
    search_and_recommend
)

from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search(query: str):

    result = search_and_recommend(query)

    return {
        "search_results": result["search_results"].to_dict(orient="records"),
        "recommendations": result["recommendations"].to_dict(orient="records")
    }
@router.get("/home")
def home(user_favorites: list[str] | None = None):

    recommendations = personalized_home(user_favorites)

    return {
        "recommendations": recommendations.to_dict(orient="records")
    }
