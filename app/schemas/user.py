from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }

class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: str
    is_admin: bool = False
    
    class Config:
        from_attributes = True
