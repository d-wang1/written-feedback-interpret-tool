from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import time
from collections import defaultdict

# Rate limiting storage (in-memory for simplicity)
user_requests = defaultdict(list)
RATE_LIMIT = 20  # 20 requests per user per hour
RATE_WINDOW = 3600  # 1 hour window in seconds

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Database connection
async def get_database():
    # Import database from the main app module
    from app.mongodb import database
    return database

def check_rate_limit(user_identifier: str):
    """Check if user has exceeded rate limit"""
    current_time = time.time()
    
    # Clean old requests (outside the window)
    user_requests[user_identifier] = [
        req_time for req_time in user_requests[user_identifier]
        if current_time - req_time < RATE_WINDOW
    ]
    
    # Check if user has exceeded the limit
    if len(user_requests[user_identifier]) >= RATE_LIMIT:
        return False
    
    # Add current request
    user_requests[user_identifier].append(current_time)
    return True

def get_user_identifier(request):
    """Extract user identifier from request"""
    # Try to get user from JWT token first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return decoded.get("sub", "anonymous")
        except:
            pass
    
    # Fallback to IP address
    return request.client.host or "unknown"

class UserLogin(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    submission_id: Optional[str] = None
    remember_me: Optional[bool] = False

class UserSignup(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    submission_id: Optional[str] = None
    role: Optional[str] = "user"  # Default role is "user"
    remember_me: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: Optional[str] = "user"

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup, request):
    db = await get_database()
    
    # Rate limiting check
    user_id = get_user_identifier(request)
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT} requests per {RATE_WINDOW//3600} hours."
        )
    
    # Debug logs
    print(f"=== BACKEND SIGNUP DEBUG ===")
    print(f"User ID: {user_id}")
    print(f"Email: '{user_data.email}'")
    print(f"Password: '{user_data.password}'")
    print(f"Submission ID: '{user_data.submission_id}'")
    print(f"Full Name: '{user_data.full_name}'")
    print(f"Full user_data: {user_data}")
    print(f"========================")
    
    # Require submission_id
    if not user_data.submission_id or not user_data.submission_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission ID is required"
        )
    
    # Check if submission ID already exists
    existing_submission = await db.users.find_one({"submission_id": user_data.submission_id})
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission ID already registered"
        )
    
    # Check if email already exists (only if email is provided and not empty)
    if user_data.email and user_data.email.strip():
        print(f"Checking for duplicate email: '{user_data.email}'")
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    else:
        print(f"Skipping email check - email is empty or None")
    
    # Hash password if provided, otherwise use default
    password_to_hash = user_data.password if user_data.password else 'defaultpassword'
    hashed_password = bcrypt.hashpw(password_to_hash.encode('utf-8'), bcrypt.gensalt())
    
    # Store user
    user_doc = {
        "email": user_data.email.strip() if user_data.email and user_data.email.strip() else f"user-{user_data.submission_id}@echoai.local",  # Use unique email for empty email
        "password": hashed_password,
        "full_name": user_data.full_name,
        "submission_id": user_data.submission_id,
        "role": user_data.role or "user",  # Store role or default to "user"
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Create token
    access_token_expires = timedelta(days=7 if user_data.remember_me else 1)
    email_for_token = user_data.email.strip() if user_data.email and user_data.email.strip() else f"user-{user_data.submission_id}@echoai.local"
    access_token = create_access_token(
        data={"sub": user_id, "email": email_for_token}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=user_id, role=user_data.role or "user")

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, request):
    db = await get_database()
    
    # Rate limiting check
    user_id = get_user_identifier(request)
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT} requests per {RATE_WINDOW//3600} hours."
        )
    
    # Check if user exists by submission_id or email
    user = None
    if user_data.submission_id:
        # Try to find user by submission_id first
        user = await db.users.find_one({"submission_id": user_data.submission_id})
    elif user_data.email:
        # Fallback to email lookup
        user = await db.users.find_one({"email": user_data.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check password if provided, otherwise allow login
    if user_data.password and not bcrypt.checkpw(user_data.password.encode('utf-8'), user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create token
    access_token_expires = timedelta(days=7 if user_data.remember_me else 1)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user_id=str(user["_id"]), role=user.get("role", "user"))

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