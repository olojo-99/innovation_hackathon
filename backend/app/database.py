from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None

db_instance = Database()

async def get_database():
    return db_instance.client.hackathon_db

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    db_instance.client = AsyncIOMotorClient("mongodb://localhost:27017")
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    db_instance.client.close()
    print("Closed MongoDB connection")
