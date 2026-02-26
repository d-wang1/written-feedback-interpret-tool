from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"  # Change this in production!
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: Optional[bool] = False

class UserSignup(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

# Mock user database (replace with real database later)
users_db = {}

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup):
    # Check if user already exists
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    # Store user
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.now()
    }
    
    # Create token
    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={"sub": user_id, "email": user_data.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=user_id)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    # Check if user exists
    user = users_db.get(user_data.email)
    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=user["id"])

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/me")
async def get_current_user(token: str = security):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"user_id": user_id, "email": email}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )