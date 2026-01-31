# RecoFlix Authentication Setup Guide

## Prerequisites
- MySQL Server installed and running
- Python 3.8+
- pip package manager

## Installation Steps

### 1. Create MySQL Database
```sql
CREATE DATABASE recoflix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Setup Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=recoflix
JWT_SECRET=your-super-secret-key-change-this-in-production
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Register User
**POST** `/api/v1/auth/register`

Request Body:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true
}
```

### Login User
**POST** `/api/v1/auth/login`

Request Body:
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "johndoe",
  "email": "user@example.com"
}
```

### Get User Profile
**GET** `/api/v1/auth/me?token={access_token}`

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true
}
```

## Project Structure

```
app/
├── api/v1/
│   ├── auth.py           # Authentication endpoints
│   ├── movies.py         # Movie endpoints
│   └── router.py         # API router
├── core/
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   ├── jwt_utils.py      # JWT token utilities
│   ├── security.py       # Password hashing
│   └── recommender.py    # Recommendation logic
├── models/
│   └── user.py          # User database model
├── schemas/
│   └── user.py          # User Pydantic schemas
├── services/
│   ├── user.py          # User database operations
│   ├── recommender.py   # Recommendation service
│   └── utils.py         # Utilities
└── main.py              # FastAPI app entry point
```

## Database Schema

The `users` table is automatically created with the following fields:
- `id` - Primary key
- `email` - Unique email address
- `username` - Unique username
- `full_name` - User's full name
- `hashed_password` - Bcrypt hashed password
- `is_active` - Account status
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

## Security Features

- **Password Hashing**: Using bcrypt with 12 rounds for secure password storage
- **JWT Tokens**: Stateless authentication with 24-hour expiration
- **Email Validation**: Using pydantic email validator
- **CORS Support**: Configured for cross-origin requests

## Testing with cURL

### Register:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "Password123!"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!"
  }'
```

### Get Profile:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me?token={YOUR_ACCESS_TOKEN}"
```

## Next Steps

1. Integrate authentication with movie recommendation endpoints
2. Add refresh token functionality
3. Implement role-based access control (RBAC)
4. Add email verification on registration
5. Add password reset functionality
