from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

def get_database_connection():

    """Create and return a MongoDB database connection"""

    client = MongoClient("mongodb://localhost:27017/")
    db = client["skillmatch_app"]
    return db

def init_database():

    """Initialize MongoDB collections"""
    
    db = get_database_connection()

    #define validation rules
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
                    "education": {"bsonType": "string"},
                    "experience": {"bsonType": "string"},
                    "projects": {"bsonType": "string"},
                    "skills": {"bsonType": "string"},
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
                    "timestamp": {"bsonType": "date"}
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

    #create collections with validation rules
    for name, validator in collection_validations.items():
        if name not in db.list_collection_names():
            db.create_collection(name, validator=validator)
            print(f"Created collection: {name}")
        else:
            print(f"Collection already exists: {name}")

    print("MongoDB collections initialized with schema validation.")

    #define unique indexes
    create_unique_indexes()

def insert_resume_skill(skill_doc):

    """Insert resume skill"""

    db = get_database_connection()

    resume_id = skill_doc.get("resume_id")
    if not resume_id or not ObjectId.is_valid(resume_id):
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    resume_obj_id = ObjectId(resume_id)

    #check if the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_id} does not exist in resume_data!")
    
    #insert skill
    skill_doc["resume_id"] = resume_obj_id
    skill_doc["created_at"] = datetime.utcnow()
    db.resume_skills.insert_one(skill_doc)
    print("Skill inserted successfully!")

def insert_resume_analysis(analysis_doc):

    """Insert resume analysis"""

    db = get_database_connection()

    resume_id = analysis_doc.get("resume_id")
    if not resume_id or not ObjectId.is_valid(resume_id):
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    resume_obj_id = ObjectId(resume_id)

    #check if the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_id} does not exist in resume_data!")

    #insert analysis
    analysis_doc["resume_id"] = resume_obj_id
    analysis_doc["created_at"] = datetime.utcnow()
    db.resume_analysis.insert_one(analysis_doc)
    print("Analysis inserted successfully!")

def create_unique_indexes():

    """Define unique indexes"""

    db = get_database_connection()

    db.admin.create_index("email", unique=True)

    db.resume_skills.create_index(
        [("resume_id", 1), ("skill_name", 1)],
        unique=True
    )

    db.resume_analysis.create_index("resume_id", unique=True)

    print("Unique indexes created.")