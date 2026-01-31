from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, username: str, full_name: str, password: str):
    """Create a new user"""
    hashed_password = hash_password(password)
    db_user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, **updates):
    """Update user fields (username, full_name, email)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for key, value in updates.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    """Delete a user by ID"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def set_user_admin(db: Session, user_id: int, is_admin: bool = True):
    """Set or unset admin flag for a user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.is_admin = is_admin
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
