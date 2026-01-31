from fastapi import APIRouter
from app.api.v1.movies import router as movies_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.ratings import router as ratings_router
api_router = APIRouter()

api_router.include_router(
    auth_router,
    tags=["Authentication"]
)

api_router.include_router(
    movies_router,
    prefix="/movies",
    tags=["Movies"]
)

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)
api_router.include_router(
   favorites_router,
    prefix="/favorites",
    tags=["Favorites"]
)
api_router.include_router(
    ratings_router,
    prefix="/ratings",  
    tags=["Ratings"]
)