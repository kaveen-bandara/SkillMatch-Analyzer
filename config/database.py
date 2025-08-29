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
                    "linkedin": {"bsonType": ["string", "null"]},
                    "github": {"bsonType": ["string", "null"]},
                    "portfolio": {"bsonType": ["string", "null"]},
                    "summary": {"bsonType": ["string", "null"]},
                    "target_role": {"bsonType": ["string", "null"]},
                    "target_category": {"bsonType": ["string", "null"]},
                    "education": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "experience": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "projects": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "skills": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "template": {"bsonType": ["string", "null"]},
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
                    "proficiency_score": {"bsonType": ["double", "null"]},
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
                    "ats_score": {"bsonType": ["double", "null"]},
                    "keyword_match_score": {"bsonType": ["double", "null"]},
                    "format_score": {"bsonType": ["double", "null"]},
                    "section_score": {"bsonType": ["double", "null"]},
                    "missing_skills": {"bsonType": ["string", "null"]},
                    "recommendations": {"bsonType": ["string", "null"]},
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

    # Admin email must be unique
    db.admin.create_index([("email", 1)], unique=True, name="unique_admin_email")

    # No duplicate skills for the same resume
    db.resume_skills.create_index([("resume_id", 1), ("skill_name", 1)], unique=True, name="unique_resume_skill")

    # One analysis per resume
    db.resume_analysis.create_index([("resume_id", 1)], unique=True, name="unique_resume_analysis")

    print(f"✅ MongoDB collections initialized with schema validation.")

def insert_resume_data(data):
    """
    Save resume data into resume_data collection
    """
    db = get_database_connection()

    personal_info = data.get("personal_info", {})

    resume_doc = {
        "name": personal_info.get("full_name"),
        "email": personal_info.get("email"),
        "phone": personal_info.get("phone"),
        "linkedin": personal_info.get("linkedin"),
        "github": personal_info.get("github"),
        "portfolio": personal_info.get("portfolio"),
        "summary": data.get("summary"),
        "target_role": data.get("target_role"),
        "target_category": data.get("target_category"),
        "education": data.get("education"),
        "experience": data.get("experience"),
        "projects": data.get("projects"),
        "skills": data.get("skills"),
        "template": data.get("template"),
        "created_at": datetime.utcnow()
    }

    try:
        result = db.resume_data.insert_one(resume_doc)
        print(f"✅ Resume saved successfully with id {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        raise RuntimeError(f"Failed to save resume data: {e}")

def insert_resume_skill(skill):
    """
    Insert resume skill into the resume_skills collection
    """
    db = get_database_connection()

    # Validate and normalize resume_id
    resume_id = skill.get("resume_id")
    if isinstance(resume_id, ObjectId):
        resume_obj_id = resume_id
    elif resume_id and ObjectId.is_valid(str(resume_id)):
        resume_obj_id = ObjectId(str(resume_id))
    else:
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    # Ensure the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_obj_id} does not exist in resume_data!")
    
    # Validate required fields
    required_fields = ["skill_name", "skill_category"]
    for field in required_fields:
        if not skill.get(field):
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(skill["skill_name"], str):
        raise ValueError("skill_name must be a string!")
    if not isinstance(skill["skill_category"], str):
        raise ValueError("skill_category must be a string!")
    if "proficiency_score" in skill and not isinstance(skill["proficiency_score"], (int, float)):
        raise ValueError("proficiency_score must be a number if provided!")

    # Prepare document
    skill_doc = {
        "resume_id": resume_obj_id,
        "skill_name": skill["skill_name"],
        "skill_category": skill["skill_category"],
        "proficiency_score": skill.get("proficiency_score"),
        "created_at": datetime.utcnow()
    }
    
    try:
        result = db.resume_skills.insert_one(skill_doc)
        print(f"✅ Skill '{skill_doc['skill_name']}' inserted successfully!")
        return result.inserted_id
    except Exception as e:
        raise RuntimeError(f"Failed to insert skill: {e}")
    
def insert_resume_analysis(analysis):
    """
    Insert resume analysis document into resume_analysis collection
    """
    db = get_database_connection()

    # Validate and normalize resume_id
    resume_id = analysis.get("resume_id")
    if isinstance(resume_id, ObjectId):
        resume_obj_id = resume_id
    elif resume_id and ObjectId.is_valid(str(resume_id)):
        resume_obj_id = ObjectId(str(resume_id))
    else:
        raise ValueError("Invalid resume_id: must be a valid ObjectId!")

    # Ensure the resume exists
    if not db.resume_data.find_one({"_id": resume_obj_id}):
        raise ValueError(f"resume_id {resume_obj_id} does not exist in resume_data!")

    # Validate numeric fields
    numeric_fields = ["ats_score", "keyword_match_score", "format_score", "section_score"]
    for field in numeric_fields:
        if field in analysis and not isinstance(analysis[field], (int, float)):
            raise ValueError(f"{field} must be a number!")

    # Prepare document
    analysis_doc = {
        "resume_id": resume_obj_id,
        "ats_score": analysis.get("ats_score"),
        "keyword_match_score": analysis.get("keyword_match_score"),
        "format_score": analysis.get("format_score"),
        "section_score": analysis.get("section_score"),
        "missing_skills": analysis.get("missing_skills"),
        "recommendations": analysis.get("recommendations"),
        "created_at": datetime.utcnow()
    }

    try:
        result = db.resume_analysis.insert_one(analysis_doc)
        print(f"✅ Analysis inserted successfully for resume_id {resume_obj_id}")
        return result.inserted_id
    except Exception as e:
        raise RuntimeError(f"Failed to insert resume analysis: {e}")
    
def get_resume_stats():
    """
    Get statistics about resumes
    """
    db = get_database_connection()

    try:
        # Total resumes
        total_resumes = db.resume_data.count_documents({})

        # Average ATS score
        pipeline = [
            {"$group": {"_id": None, "avg_ats": {"$avg": "$ats_score"}}}
        ]
        avg_result = list(db.resume_analysis.aggregate(pipeline))
        avg_ats_score = round(avg_result[0]["avg_ats"], 2) if avg_result and avg_result[0]["avg_ats"] is not None else 0

        # Recent activity (last 5 resumes sorted by created_at desc)
        recent_activity_cursor = db.resume_data.find(
            {},
            {"name": 1, "target_role": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5)

        recent_activity = [
            {
                "name": doc.get("name"),
                "target_role": doc.get("target_role"),
                "created_at": doc.get("created_at")
            }
            for doc in recent_activity_cursor
        ]

        return {
            "total_resumes": total_resumes,
            "avg_ats_score": avg_ats_score,
            "recent_activity": recent_activity
        }
    except Exception as e:
        print(f"❌ Error getting resume stats: {str(e)}")
        return None