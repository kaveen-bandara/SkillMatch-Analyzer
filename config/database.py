import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

# Create a global variable
client = None

# Load environment variables from .env
load_dotenv()

def get_database_connection():
    """
    Create and return a MongoDB database connection
    """
    global client
    if client is None:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri)
    return client["skillmatch-smart-resume-analyzer"]

def init_database():
    """
    Initialize MongoDB collections with schema validation
    """
    db = get_database_connection()

    # Define validation rules
    collection_validations = {
        "resume_data": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "email", "phone"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "phone": {"bsonType": "string"},
                    "linkedin": {"bsonType": "string"},
                    "github": {"bsonType": "string"},
                    "portfolio": {"bsonType": "string"},
                    "summary": {"bsonType": "string"},
                    "target_role": {"bsonType": "string"},
                    "target_category": {"bsonType": "string"},
                    "education": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "experience": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "projects": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "skills": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "template": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        "resume_skills": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["resume_id", "skill_name", "skill_category"],
                "properties": {
                    "resume_id": {"bsonType": "objectId"},
                    "skill_name": {"bsonType": "string"},
                    "skill_category": {"bsonType": "string"},
                    "proficiency_score": {"bsonType": "double"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        "resume_analysis": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["resume_id"],
                "properties": {
                    "resume_id": {"bsonType": "objectId"},
                    "ats_score": {"bsonType": "double"},
                    "keyword_match_score": {"bsonType": "double"},
                    "format_score": {"bsonType": "double"},
                    "section_score": {"bsonType": "double"},
                    "missing_skills": {"bsonType": "string"},
                    "recommendations": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        "admin_logs": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["admin_email", "action"],
                "properties": {
                    "admin_email": {"bsonType": "string"},
                    "action": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        "admin": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "password": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
    }

    # Create collections with validation rules
    for name, validator in collection_validations.items():
        if name not in db.list_collection_names():
            db.create_collection(name, validator={"$jsonSchema": validator["$jsonSchema"]})
            print(f"✅ Created collection: {name}")
        else:
            db.command("collMod", name, validator={"$jsonSchema": validator["$jsonSchema"]})
            print(f"🔄 Updated schema for: {name}")

    print("MongoDB collections initialized with schema validation.")
    create_unique_indexes()

def create_unique_indexes():
    """
    Create unique indexes for important collections 
    to ensures data integrity and avoids duplicates
    """
    db = get_database_connection()

    # Admin email must be unique
    db.admin.create_index(
        [("email", 1)],
        unique=True,
        name="unique_admin_email"
    )

    # No duplicate skills for the same resume
    db.resume_skills.create_index(
        [("resume_id", 1), ("skill_name", 1)],
        unique=True,
        name="unique_resume_skill"
    )

    # One analysis per resume
    db.resume_analysis.create_index(
        [("resume_id", 1)],
        unique=True,
        name="unique_resume_analysis"
    )

    print("✅ Unique indexes ensured.")

def insert_resume_skill(skill_doc):
    """
    Insert resume skill into the resume_skills collection
    """
    db = get_database_connection()

      # Validate and normalize resume_id
    resume_id = skill_doc.get("resume_id")
    if isinstance(resume_id, ObjectId):
        resume_obj_id = resume_id
    elif resume_id and ObjectId.is_valid(str(resume_id)):
        resume_obj_id = ObjectId(str(resume_id))
    else:
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    # Ensure the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_id} does not exist in resume_data!")
    
    # Validate required fields
    required_fields = ["skill_name", "skill_category"]
    for field in required_fields:
        if not skill_doc.get(field):
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(skill_doc["skill_name"], str):
        raise ValueError("skill_name must be a string!")
    if not isinstance(skill_doc["skill_category"], str):
        raise ValueError("skill_category must be a string!")
    if "proficiency_score" in skill_doc and not isinstance(skill_doc["proficiency_score"], (int, float)):
        raise ValueError("proficiency_score must be a number if provided!")

    # Insert skill
    skill_doc["resume_id"] = resume_obj_id
    skill_doc["created_at"] = datetime.utcnow()
    
    try:
        db.resume_skills.insert_one(skill_doc)
        print(f"✅ Skill '{skill_doc['skill_name']}' inserted successfully!")
    except Exception as e:
        raise RuntimeError(f"Failed to insert skill: {e}")
    
def insert_resume_analysis(analysis_doc):
    """
    Insert resume analysis document into resume_analysis collection
    """
    db = get_database_connection()

    # Validate and normalize resume_id
    resume_id = analysis_doc.get("resume_id")
    if isinstance(resume_id, ObjectId):
        resume_obj_id = resume_id
    elif resume_id and ObjectId.is_valid(str(resume_id)):
        resume_obj_id = ObjectId(str(resume_id))
    else:
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    # Ensure the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_id} does not exist in resume_data!")

    # Validate numeric fields
    numeric_fields = [
        "ats_score", "keyword_match_score",
        "format_score", "section_score"
    ]
    for field in numeric_fields:
        if field in analysis_doc and not isinstance(analysis_doc[field], (int, float)):
            raise ValueError(f"{field} must be a number!")

    # Insert analysis
    analysis_doc["resume_id"] = resume_obj_id
    analysis_doc["created_at"] = datetime.utcnow()

    try:
        db.resume_analysis.insert_one(analysis_doc)
        print(f"✅ Analysis inserted successfully for resume_id {resume_obj_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to insert analysis: {e}")