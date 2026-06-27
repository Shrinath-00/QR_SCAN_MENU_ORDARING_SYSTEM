from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserRegister, UserLogin, Token, UserResponse
from backend.security import hash_password, verify_password, create_access_token, verify_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Insufficient permissions."
            )
        return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed,
        role=user_data.role or "waiter"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

from backend.schemas.user import CredentialsUpdate

@router.post("/update-credentials")
def update_credentials(
    payload: CredentialsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin"]))
):
    user = db.query(User).filter(User.role == payload.role).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with role '{payload.role}' not found")
    
    if payload.new_username:
        existing = db.query(User).filter(
            User.username == payload.new_username,
            User.role != payload.role
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username is already taken by another user")
        user.username = payload.new_username
        
    if payload.new_password:
        user.password_hash = hash_password(payload.new_password)
        
    db.commit()
    db.refresh(user)
    return {"success": True, "message": f"Successfully updated credentials for role '{payload.role}'"}
