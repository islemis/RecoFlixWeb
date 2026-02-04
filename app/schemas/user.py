from pydantic import BaseModel, EmailStr, Field 
from typing import List, Optional

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

class UserUpdate(BaseModel):
    """Schema for user update"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "username": "newusername",
                "full_name": "New Name"
            }
        }

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: str
    is_admin: bool = False
    favorites: List[int] = []  

    class Config:
        from_attributes = True
