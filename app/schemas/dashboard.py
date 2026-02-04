from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class KPISummary(BaseModel):
    users: int
    movies: int
    ratings: int

class RatingOverTime(BaseModel):
    date: str
    count: int

class GenreStat(BaseModel):
    genre: str
    count: int

class TopMovie(BaseModel):
    title: str
    avg_rating: float
    release_date: datetime | None


class ActivityItem(BaseModel):
    id: int
    user_name: str
    movie_title: str
    rating: float
    created_at: datetime

class UserGrowth(BaseModel):
    date: str
    new_users: int
