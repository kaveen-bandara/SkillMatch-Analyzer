import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

def get_database_connection():
    """
    Create and return a MongoDB database connection
    """
    # Load environment variables from .env
    load_dotenv()

    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client["skillmatch-smart-resume-analyzer"]
    return db