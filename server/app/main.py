import os
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
    test_items_collection,
    test2_collection,
)
from bson import ObjectId

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

client = None

def get_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set. Please set it in your environment variables (`.env file`).")
        client = Groq(api_key=api_key)
    return client

app = FastAPI(title="Written Feedback Interpretation API")

@app.on_event("startup")
async def startup():
    await connect_db()
    await ensure_collections()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# Only 1 test model
class TestItem(BaseModel):
    name: str
    description: Optional[str] = None

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/db-status")
async def db_status():
    """Check MongoDB connection"""
    try:
        await test_items_collection.count_documents({})
        return {"database": "connected", "type": "MongoDB Atlas"}
    except Exception as e:
        return {"database": "error", "message": str(e)}

# MongoDB CRUD operations
@app.post("/api/test-items")
async def create_test_item(item: TestItem):
    """Add a new test item to MongoDB"""
    item_dict = {
        "name": item.name,
        "description": item.description,
        "created_at": datetime.utcnow()
    }
    
    result = await test_items_collection.insert_one(item_dict)
    created_item = await test_items_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    return {
        "id": str(created_item["_id"]),
        "name": created_item["name"],
        "description": created_item["description"],
        "created_at": created_item["created_at"].isoformat()
    }

@app.post("/api/test2")
async def create_test2_item(item: TestItem):
    """Add a new item to test2 collection"""
    item_dict = {
        "name": item.name,
        "description": item.description,
        "created_at": datetime.utcnow()
    }

    result = await test2_collection.insert_one(item_dict)
    created_item = await test2_collection.find_one({"_id": result.inserted_id})

    return {
        "id": str(created_item["_id"]),
        "name": created_item["name"],
        "description": created_item.get("description"),
        "created_at": created_item["created_at"].isoformat()
    }

@app.get("/api/test-items")
async def get_test_items():
    """Get all test items from MongoDB"""
    cursor = test_items_collection.find({}).sort("created_at", -1)
    items = []
    
    async for document in cursor:
        items.append({
            "id": str(document["_id"]),
            "name": document["name"],
            "description": document.get("description"),
            "created_at": document["created_at"].isoformat()
        })
    
    return items

@app.get("/api/test2")
async def get_test2_items():
    """Get all items from test2 collection"""
    cursor = test2_collection.find({}).sort("created_at", -1)
    items = []

    async for document in cursor:
        items.append({
            "id": str(document["_id"]),
            "name": document["name"],
            "description": document.get("description"),
            "created_at": document["created_at"].isoformat()
        })

    return items

@app.delete("/api/test-items/{item_id}")
async def delete_test_item(item_id: str):
    """Delete a test item by ID from MongoDB"""
    try:
        result = await test_items_collection.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Test item not found")
        
        return {"message": f"Test item {item_id} deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid item ID")

# Your existing interpret route
@app.post("/api/interpret")
def interpret(req: dict):
    text = req.get("text", "")
    options = req.get("options", {})
    
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

        output = resp.choices[0].message.content or ""
        return {"output": output}

    except HTTPException:
        raise
    except Exception as e:
        print("interpret() error:", repr(e))
        raise HTTPException(status_code=500, detail="LLM request failed")
