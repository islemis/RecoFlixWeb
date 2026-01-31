from app.services.recommender import (
    personalized_home,
    search_and_recommend,
    get_movie_by_id
)

from fastapi import APIRouter , Body , Depends, HTTPException, status
from typing import List, Optional , Dict
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.deps import get_current_user_from_header , get_current_user_optional
router = APIRouter()


@router.get("/search")
def search(query: str):

    result = search_and_recommend(query)

    return {
        "search_results": result["search_results"].to_dict(orient="records"),
        "recommendations": result["recommendations"].to_dict(orient="records")
    }

@router.get("/home")
def get_home_recommendations(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)

):
    """
    Retourne les recommandations personnalisées pour l'utilisateur connecté.
    Si l'utilisateur n'est pas connecté → top films récents cette année.
    """
    try:
        recommendations = personalized_home(current_user=current_user, top_n_per_fav=5, top_n_rated=10)
        return {
            "count": len(recommendations),
            "recommendations": recommendations.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération des recommandations: {e}"
        )

@router.get("/{movie_id}")
def movie_detail(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    movie = get_movie_by_id(
        movie_id=movie_id,
        current_user=current_user,
        db=db
    )

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie

