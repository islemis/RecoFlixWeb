from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user_from_header
from app.models.user import User
from app.services.rating import add_rating, get_ratings_by_movie
from fastapi import Request
from app.models.rating import Rating
router = APIRouter()




@router.post("")
async def create_rating(request: Request,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_header)):
    data = await request.json()
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    comment = data.get("comment")

    # validation simple
    if movie_id is None or rating is None:
        raise HTTPException(status_code=400, detail="movie_id and rating are required")
    if rating < 0 or rating > 10:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 10")

    # Vérifier si l'utilisateur a déjà noté ce film
    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == movie_id
    ).first()

    if existing:
        # Retourner un message clair
        raise HTTPException(
            status_code=400,
            detail="Vous avez déjà noté ce film. Vous ne pouvez pas ajouter un autre commentaire."
        )

    # Utiliser add_rating pour gérer la logique de mise à jour
    new_rating = add_rating(db, current_user.id, movie_id, rating, comment)

    return {
        "id": new_rating.id,
        "user_id": new_rating.user_id,
        "movie_id": new_rating.movie_id,
        "rating": new_rating.rating,
        "comment": new_rating.comment,
        "created_at": new_rating.created_at
    }


@router.get("/movie/{movie_id}")
def movie_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = get_ratings_by_movie(db, movie_id)
    return [
        {
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at
        } for r in ratings
    ]
