from sqlalchemy.orm import Session
from app.models.user import User
from app.services.recommender import get_movie_by_id

def add_favorite(db: Session, user: User, movie_id: int):
    if user.favorites is None:
        user.favorites = []

    if movie_id not in user.favorites:
        user.favorites.append(movie_id)
        db.commit()
        db.refresh(user)

    return user.favorites


def remove_favorite(db: Session, user: User, movie_id: int):
    if user.favorites and movie_id in user.favorites:
        user.favorites.remove(movie_id)
        db.commit()
        db.refresh(user)

    return user.favorites

def get_favorites_movies_info(user: User):
    """
    Retourne les infos complètes de tous les films favoris de l'utilisateur
    en utilisant get_movie_by_id
    """
    favorite_ids = user.favorites or []

    movies_info = []
    for movie_id in favorite_ids:
        movie_data = get_movie_by_id(movie_id)
        if movie_data:  # vérifier que le film existe
            movies_info.append(movie_data)

    return movies_info
