from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.user import UserResponse
from app.services.user import get_user_by_id, get_user_by_username, get_user_by_email, update_user, delete_user
from app.models.user import User
from app.core.deps import admin_required

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), _=Depends(admin_required)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, payload: dict, db: Session = Depends(get_db), _=Depends(admin_required)):
    allowed = {"email", "username", "full_name"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")
    user = update_user(db, user_id, **updates)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None

@router.post("/users/{user_id}/promote", response_model=UserResponse)
def promote_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="This endpoint has been removed")

@router.post("/users/{user_id}/demote", response_model=UserResponse)
def demote_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):    raise HTTPException(status_code=status.HTTP_410_GONE, detail="This endpoint has been removed")
