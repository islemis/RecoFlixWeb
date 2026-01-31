from sqlalchemy.orm import Session
from app.models.rating import Rating

def add_rating(db: Session, user_id: int, movie_id: int, rating_value: float, comment: str = None):
    new_rating = Rating(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating_value,
        comment=comment
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

def get_ratings_by_movie(db: Session, movie_id: int):
    return db.query(Rating).filter(Rating.movie_id == movie_id).all()

def get_ratings_by_user(db: Session, user_id: int):
    return db.query(Rating).filter(Rating.user_id == user_id).all()
