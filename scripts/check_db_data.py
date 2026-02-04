from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.core.database import DATABASE_URL

def check_data():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("--- Database Stats ---")
        
        # Check Movie count
        count_movies = db.execute(text("SELECT COUNT(*) FROM movies")).scalar()
        print(f"Total Movies: {count_movies}")
        
        # Check Rating count
        count_ratings = db.execute(text("SELECT COUNT(*) FROM ratings")).scalar()
        print(f"Total Ratings: {count_ratings}")
        
        # Check Max ratings for a single movie
        max_ratings = db.execute(text("SELECT MAX(cnt) FROM (SELECT COUNT(*) as cnt FROM ratings GROUP BY movie_id) as t")).scalar()
        print(f"Max ratings for a single movie: {max_ratings}")
        
        # Check movie with most ratings
        query = """
        SELECT m.title, COUNT(r.id) as cnt 
        FROM movies m 
        JOIN ratings r ON r.movie_id = m.movie_id 
        GROUP BY m.movie_id, m.title 
        ORDER BY cnt DESC 
        LIMIT 10
        """
        top_rated = db.execute(text(query)).fetchall()
        print("\nTop 10 Most Rated Movies:")
        for row in top_rated:
            print(f"- {row.title}: {row.cnt} ratings")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
