from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.favorites import add_favorite, remove_favorite , get_favorites_movies_info
from app.models.user import User
from app.core.deps import get_current_user_from_header


router = APIRouter()

@router.post("")
def add_movie_to_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_header)
):
    print("BEFORE:", current_user.favorites)

    if current_user.favorites is None:
        current_user.favorites = []

    if movie_id not in current_user.favorites:
        current_user.favorites.append(movie_id)
        db.commit()
        db.refresh(current_user)

    print("AFTER:", current_user.favorites)

    return {"favorites": current_user.favorites}

@router.delete("/{movie_id}", status_code=status.HTTP_200_OK)
def remove_movie_from_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_header)
):
    favorites = remove_favorite(db, current_user, movie_id)
    return {
        "message": "Movie removed from favorites",
        "favorites": favorites
    }
@router.get("/")
def get_full_favorites(current_user: User = Depends(get_current_user_from_header)):
    """
    Retourne les infos complètes de tous les films favoris
    """
    movies_data = get_favorites_movies_info(current_user)
    return {"favorites": movies_data}
