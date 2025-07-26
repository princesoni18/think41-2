
from pymongo import MongoClient
import os


# MongoDB connection URL (set MONGODB_PASSWORD in your .env for security)
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "princezopis")
MONGODB_URL = f"mongodb+srv://ps983309:{MONGODB_PASSWORD}@cluster0.5fwgxdg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB = os.getenv("MONGODB_DB", "think41")

# Create MongoDB client and database
client = MongoClient(MONGODB_URL)
db = client[MONGODB_DB]

# Dependency for FastAPI
def get_db():
    try:
        yield db
    finally:
        pass