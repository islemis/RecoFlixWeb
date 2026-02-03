from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base

class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False,)
    overview = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)  # comma-separated
    keywords = Column(Text, nullable=True)  # comma-separated
    cast = Column(Text, nullable=True)  # comma-separated
    crew = Column(Text, nullable=True)  # comma-separated
    poster = Column(String(255), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    release_date = Column(DateTime, nullable=True)
