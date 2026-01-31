import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "recoflix"),
    "port": int(os.getenv("DB_PORT", 3306))
}

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# App settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
