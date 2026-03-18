from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Database connection
async def get_database():
    # Import database from the main app module
    from app.mongodb import database
    return database

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: Optional[bool] = False

class UserSignup(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    submission_id: Optional[str] = None
    remember_me: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup):
    db = await get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    # Store user
    user_doc = {
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "submission_id": user_data.submission_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Create token
    access_token_expires = timedelta(days=7 if user_data.remember_me else 1)
    access_token = create_access_token(
        data={"sub": user_id, "email": user_data.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=user_id)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = await get_database()
    
    # Check if user exists
    user = await db.users.find_one({"email": user_data.email})
    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    access_token_expires = timedelta(days=7 if user_data.remember_me else 1)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=str(user["_id"]))

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/users")
async def get_all_users():
    db = await get_database()
    users = []
    async for user in db.users.find({}, {"password": 0}):  # Exclude password field
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        users.append(user)
    return users

@router.post("/users/delete/{user_id}")
async def delete_user_post(user_id: str):
    db = await get_database()
    
    try:
        # Convert string ID to ObjectId
        from bson import ObjectId
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    result = await db.users.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} deleted successfully"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    db = await get_database()
    
    try:
        # Convert string ID to ObjectId
        from bson import ObjectId
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    result = await db.users.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} deleted successfully"}

@router.get("/me")
async def get_current_user(token: str = Depends(security)):
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