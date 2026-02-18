import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import CollectionInvalid

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
database = client.feedback_db

# Collections (handles)
# test_items_collection = database.test_items
# test2_collection = database.test2

feedback_records_collection = database.feedback_records


async def connect_db():
    """Test MongoDB connection"""
    try:
        await client.admin.command("ping")
        print("Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")


async def disconnect_db():
    """Close MongoDB connection"""
    client.close()


async def ensure_collections():
    """
    Explicitly create required collections if they do not exist.
    Safe to call multiple times.
    """
    existing = await database.list_collection_names()

    # if "test_items" not in existing:
    #     await database.create_collection("test_items")

    # if "test2" not in existing:
    #     await database.create_collection("test2")

    if "feedback_records" not in existing:  # Add this block
        await database.create_collection("feedback_records")
