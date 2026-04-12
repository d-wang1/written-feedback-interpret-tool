import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from app.prompt_cfg import prompt_store, build_system_prompt, build_user_prompt
from app.model_cfg import model_config_store
from app.mongodb import (
    connect_db,
    disconnect_db,
    ensure_collections,
    feedback_records_collection,
    database
)
import time
from bson import ObjectId
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

client = None

async def get_database():
    return database

__all__ = ["database", "get_database"]

def get_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set. Please set it in your environment variables (`.env file`).")
        client = Groq(api_key=api_key)
    return client

app = FastAPI(title="Written Feedback Interpretation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://34.132.214.188:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)



@app.on_event("startup")
async def startup():
    await connect_db()
    await ensure_collections()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()


class TestItem(BaseModel):
    name: str
    description: Optional[str] = None

class FeedbackRecord(BaseModel):
    input_text: str
    methods: list[str]
    output_text: str
    input_length: int
    output_length: int

@app.get("/api/health")
def health():
    return {"ok": True}

# @app.get("/api/db-status")
# async def db_status():
#     """Check MongoDB connection"""
#     try:
#         await test_items_collection.count_documents({})
#         return {"database": "connected", "type": "MongoDB Atlas"}
#     except Exception as e:
#         return {"database": "error", "message": str(e)}

# # MongoDB CRUD operations
# @app.post("/api/test-items")
# async def create_test_item(item: TestItem):
#     """Add a new test item to MongoDB"""
#     item_dict = {
#         "name": item.name,
#         "description": item.description,
#         "created_at": datetime.utcnow()
#     }
    
#     result = await test_items_collection.insert_one(item_dict)
#     created_item = await test_items_collection.find_one({"_id": result.inserted_id})
    
#     # Convert ObjectId to string
#     return {
#         "id": str(created_item["_id"]),
#         "name": created_item["name"],
#         "description": created_item["description"],
#         "created_at": created_item["created_at"].isoformat()
#     }

# @app.post("/api/test2")
# async def create_test2_item(item: TestItem):
#     """Add a new item to test2 collection"""
#     item_dict = {
#         "name": item.name,
#         "description": item.description,
#         "created_at": datetime.utcnow()
#     }

#     result = await test2_collection.insert_one(item_dict)
#     created_item = await test2_collection.find_one({"_id": result.inserted_id})

#     return {
#         "id": str(created_item["_id"]),
#         "name": created_item["name"],
#         "description": created_item.get("description"),
#         "created_at": created_item["created_at"].isoformat()
#     }

# @app.get("/api/test-items")
# async def get_test_items():
#     """Get all test items from MongoDB"""
#     cursor = test_items_collection.find({}).sort("created_at", -1)
#     items = []
    
#     async for document in cursor:
#         items.append({
#             "id": str(document["_id"]),
#             "name": document["name"],
#             "description": document.get("description"),
#             "created_at": document["created_at"].isoformat()
#         })
    
#     return items

# @app.get("/api/test2")
# async def get_test2_items():
#     """Get all items from test2 collection"""
#     cursor = test2_collection.find({}).sort("created_at", -1)
#     items = []

#     async for document in cursor:
#         items.append({
#             "id": str(document["_id"]),
#             "name": document["name"],
#             "description": document.get("description"),
#             "created_at": document["created_at"].isoformat()
#         })

#     return items

# @app.delete("/api/test-items/{item_id}")
# async def delete_test_item(item_id: str):
#     """Delete a test item by ID from MongoDB"""
#     try:
#         result = await test_items_collection.delete_one({"_id": ObjectId(item_id)})
        
#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="Test item not found")
        
#         return {"message": f"Test item {item_id} deleted successfully"}
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid item ID")

@app.post("/api/interpret")
async def interpret(req: dict):
    text = req.get("text", "")
    options = req.get("options", {})
    user_info = req.get("user_info", {})  # Get user information
    
    # If user is logged in, fetch their submission_id from database
    user_submission_id = None
    if user_info.get("email") and user_info.get("email") != "Guest":
        try:
            db = await get_database()
            user_record = await db.users.find_one({"email": user_info["email"]})
            if user_record:
                user_submission_id = user_record.get("submission_id")
        except Exception as e:
            print(f"Error fetching user submission_id: {e}")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    try:
        prompt_cfg = prompt_store.load()
        system_prompt = build_system_prompt(prompt_cfg)
        user_prompt = build_user_prompt(text, options, prompt_cfg)

        model_cfg = model_config_store.load()
        generation = model_cfg.get("generation", {})

        model_name = model_cfg.get("model")
        temperature = generation.get("temperature", 0.2)
        top_p = generation.get("top_p", 1.0)
        max_tokens = generation.get("max_tokens", 512)
        stop = model_cfg.get("stop_sequences") or None

        resp = get_client().chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )

        raw_output = resp.choices[0].message.content or ""
        output = re.sub(r"<think>[\s\S]*?</think>", "", raw_output).strip()
        
        # Calculate lengths
        input_length = len(text)
        output_length = len(output)
        
        methods = []
        if options:
            if options.get("simplify"):
                methods.append("simplify")
            if options.get("caseSupport"):
                methods.append("caseSupport")
            if options.get("soften"):
                methods.append("soften")
            
        record = {
            "input_text": text,
            "methods": methods,
            "output_text": output,
            "input_length": input_length,
            "output_length": output_length,
            "user_email": user_info.get("email", "Guest"),
            "user_id": user_info.get("id", None),
            "submission_id": user_submission_id,
            "created_at": datetime.utcnow()
        }
        
        await feedback_records_collection.insert_one(record)
        
        return {"output": output}

    except HTTPException:
        raise
    except Exception as e:
        print("interpret() error:", repr(e))
        raise HTTPException(status_code=500, detail="LLM request failed")
    

@app.get("/api/feedback-records")
async def get_feedback_records():
    """Get all feedback records from MongoDB"""
    cursor = feedback_records_collection.find({}).sort("created_at", -1)
    records = []
    
    async for document in cursor:
        records.append({
            "id": str(document["_id"]),
            "input_text": document["input_text"],
            "methods": document["methods"],
            "output_text": document["output_text"],
            "input_length": document.get("input_length", 0),
            "output_length": document.get("output_length", 0),
            "user_email": document.get("user_email", "Guest"),
            "user_id": document.get("user_id"),
            "submission_id": document.get("submission_id"),
            "created_at": document["created_at"].isoformat()
        })
    
    return records

@app.delete("/api/feedback-records/{record_id}")
async def delete_feedback_record(record_id: str):
    """Delete a specific feedback record"""
    try:
        from bson import ObjectId
        object_id = ObjectId(record_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format"
        )
    
    result = await feedback_records_collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback record not found"
        )
    
    return {"message": f"Feedback record {record_id} deleted successfully"}
