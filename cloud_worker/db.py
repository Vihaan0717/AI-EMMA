import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jarvis")

try:
    # Use ServerApi parameter for MongoDB Atlas
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    # Explicitly specify the database name "jarvis" since Atlas URIs usually don't have a default
    db = client.get_database("jarvis") 
    knowledge_collection = db["cloud_knowledge"]
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    db = None

def save_knowledge(data: dict):
    if db is None:
        logging.error("Cannot save knowledge, DB connection failed.")
        return False
    try:
        knowledge_collection.insert_one(data)
        logging.info(f"Saved new knowledge snippet to DB.")
        return True
    except Exception as e:
        logging.error(f"Error saving to DB: {e}")
        return False
