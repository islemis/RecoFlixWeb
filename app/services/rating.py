from sqlalchemy.orm import Session
from app.models.rating import Rating
from app.models.movie import Movie
from sqlalchemy import func

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

    # Update movie's average rating and vote_count
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if movie:
        # Increase vote_count by 1
        movie.vote_count = (movie.vote_count or 0) + 1
        # Calculate new average
        total = (movie.vote_average or 0) * (movie.vote_count - 1) + rating_value
        movie.vote_average = total / movie.vote_count
        db.commit()
        db.refresh(movie)

    return new_rating

def get_ratings_by_movie(db: Session, movie_id: int):
    return db.query(Rating).filter(Rating.movie_id == movie_id).all()

def get_ratings_by_user(db: Session, user_id: int):
    return db.query(Rating).filter(Rating.user_id == user_id).all()
