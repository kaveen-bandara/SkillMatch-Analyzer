import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_database_connection():
    """
    Create and return a PostgreSQL database connection
    """
    uri = os.getenv("POSTGRES_URI")
    conn = psycopg2.connect(uri)
    return conn

def init_database():
    """
    Initialize PostgreSQL tables
    """
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
    
            # Create resume_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_data(
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    linkedin TEXT,
                    github TEXT,
                    portfolio TEXT,
                    summary TEXT,
                    target_role TEXT,
                    target_category TEXT,
                    education TEXT,
                    experience TEXT,
                    projects TEXT,
                    skills TEXT,
                    template TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create resume_skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_skills(
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
                    skill_name TEXT NOT NULL,
                    skill_category TEXT NOT NULL,
                    proficiency_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create resume_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_analysis(
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
                    ats_score REAL,
                    keyword_match_score REAL,
                    format_score REAL,
                    section_score REAL,
                    missing_skills TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create admin_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_logs(
                    id SERIAL PRIMARY KEY,
                    admin_email VARCHAR(255) NOT NULL,
                    action TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create admin table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin(
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create ai_analysis table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis(
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
                    resume_score INTEGER,
                    job_role TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

def save_resume_data(data):
    """
    Save resume data to PostgreSQL database
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                personal_info = data.get("personal_info", {})

                cursor.execute("""
                    INSERT INTO resume_data (
                        name, email, phone, linkedin, github, portfolio,
                        summary, target_role, target_category, education, 
                        experience, projects, skills, template
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, 
                (
                    personal_info.get("full_name", ""),
                    personal_info.get("email", ""),
                    personal_info.get("phone", ""),
                    personal_info.get("linkedin", ""),
                    personal_info.get("github", ""),
                    personal_info.get("portfolio", ""),
                    data.get("summary", ""),
                    data.get("target_role", ""),
                    data.get("target_category", ""),
                    str(data.get("education", [])),
                    str(data.get("experience", [])),
                    str(data.get("projects", [])),
                    str(data.get("skills", [])),
                    data.get("template", "")
                ))

                # Get the inserted row's ID
                resume_id = cursor.fetchone()[0]
                return resume_id

    except Exception as e:
        print(f"Error saving resume data: {str(e)}")
        return None

def save_analysis_data(resume_id, analysis):
    """
    Save resume analysis data to PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO resume_analysis (
                        resume_id, ats_score, keyword_match_score,
                        format_score, section_score, missing_skills,
                        recommendations
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, 
                (
                    resume_id,
                    float(analysis.get("ats_score", 0)),
                    float(analysis.get("keyword_match_score", 0)),
                    float(analysis.get("format_score", 0)),
                    float(analysis.get("section_score", 0)),
                    analysis.get("missing_skills", ""),
                    analysis.get("recommendations", "")
                ))

    except Exception as e:
        print(f"Error saving analysis data: {str(e)}")

def get_resume_stats():
    """
    Get statistics about resumes from PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:

                # Get total resumes
                cursor.execute("SELECT COUNT(*) FROM resume_data")
                total_resumes = cursor.fetchone()[0]

                # Get average ATS score
                cursor.execute("SELECT AVG(ats_score) FROM resume_analysis")
                avg_ats_score = cursor.fetchone()[0] or 0

                # Get recent activity
                cursor.execute("""
                    SELECT name, target_role, created_at 
                    FROM resume_data 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                recent_activity = cursor.fetchall()

                return {
                    "total_resumes": total_resumes,
                    "avg_ats_score": round(avg_ats_score, 2),
                    "recent_activity": recent_activity
                }

    except Exception as e:
        print(f"Error getting resume stats: {str(e)}")
        return None

def log_admin_action(admin_email, action):
    """
    Log admin login/logout actions to PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO admin_logs (admin_email, action)
                    VALUES (%s, %s)
                """, 
                (
                    admin_email, 
                    action
                ))

    except Exception as e:
        print(f"Error logging admin action: {str(e)}")

def get_admin_logs():
    """
    Get all admin login/logout logs from PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT admin_email, action, created_at
                    FROM admin_logs
                    ORDER BY created_at DESC
                """)
                return cursor.fetchall()

    except Exception as e:
        print(f"Error getting admin logs: {str(e)}")
        return []

def get_all_resume_data():
    """
    Get all resume data for admin dashboard from PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:

                # Get resume data joined with analysis data
                cursor.execute("""
                    SELECT 
                        r.id,
                        r.name,
                        r.email,
                        r.phone,
                        r.linkedin,
                        r.github,
                        r.portfolio,
                        r.target_role,
                        r.target_category,
                        r.created_at,
                        a.ats_score,
                        a.keyword_match_score,
                        a.format_score,
                        a.section_score
                    FROM resume_data r
                    LEFT JOIN resume_analysis a ON r.id = a.resume_id
                    ORDER BY r.created_at DESC
                """)
                return cursor.fetchall()

    except Exception as e:
        print(f"Error getting resume data: {str(e)}")
        return []

def verify_admin(email, password):
    """
    Verify admin credentials in PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM admin WHERE email = %s AND password = %s",
                    (email, password)
                )
                result = cursor.fetchone()
                return bool(result)

    except Exception as e:
        print(f"Error verifying admin: {str(e)}")
        return False

def add_admin(email, password):
    """
    Add a new admin to PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO admin (email, password) VALUES (%s, %s)",
                    (email, password)
                )
                return True

    except Exception as e:
        print(f"Error adding admin: {str(e)}")
        return False

def save_ai_analysis_data(resume_id, analysis_data):
    """
    Save AI analysis data to PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:

                # Insert the analysis data
                cursor.execute("""
                    INSERT INTO ai_analysis (
                        resume_id, resume_score, job_role
                    ) 
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, 
                (
                    resume_id,
                    analysis_data.get("resume_score", 0),
                    analysis_data.get("job_role", "")
                ))

                # Get inserted row ID
                ai_analysis_id = cursor.fetchone()[0]
                return ai_analysis_id

    except Exception as e:
        print(f"Error saving AI analysis data: {e}")
        raise

def get_ai_analysis_stats():
    """
    Get statistics about AI analyzer usage from PostgreSQL
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:

                # Get total number of analyses
                cursor.execute("SELECT COUNT(*) FROM ai_analysis")
                total_analyses = cursor.fetchone()[0]

                if total_analyses == 0:
                    return {
                        "total_analyses": 0,
                        "average_score": 0,
                        "top_job_roles": []
                    }

                # Get average resume score
                cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
                average_score = cursor.fetchone()[0] or 0

                # Get top job roles
                cursor.execute("""
                    SELECT job_role, COUNT(*) as count
                    FROM ai_analysis
                    GROUP BY job_role
                    ORDER BY count DESC
                    LIMIT 5
                """)
                top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]

                return {
                    "total_analyses": total_analyses,
                    "average_score": round(average_score, 1),
                    "top_job_roles": top_job_roles
                }

    except Exception as e:
        print(f"Error getting AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "average_score": 0,
            "top_job_roles": []
        }

def get_detailed_ai_analysis_stats():
    """
    Get detailed statistics about AI analyzer usage including daily trends
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                
                # Get total number of analyses
                cursor.execute("SELECT COUNT(*) FROM ai_analysis")
                total_analyses = cursor.fetchone()[0]

                if total_analyses == 0:
                    return {
                        "total_analyses": 0,
                        "average_score": 0,
                        "top_job_roles": [],
                        "daily_trend": [],
                        "score_distribution": [],
                        "recent_analyses": []
                    }

                # Get average resume score
                cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
                average_score = cursor.fetchone()[0] or 0

                # Get top job roles
                cursor.execute("""
                    SELECT job_role, COUNT(*) as count
                    FROM ai_analysis
                    GROUP BY job_role
                    ORDER BY count DESC
                    LIMIT 5
                """)
                top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]

                # Get daily trend for the last 7 days
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM ai_analysis
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                daily_trend = [{"date": str(row[0]), "count": row[1]} for row in cursor.fetchall()]

                # Get score distribution
                score_ranges = [
                    {"min": 0, "max": 20, "range": "0-20"},
                    {"min": 21, "max": 40, "range": "21-40"},
                    {"min": 41, "max": 60, "range": "41-60"},
                    {"min": 61, "max": 80, "range": "61-80"},
                    {"min": 81, "max": 100, "range": "81-100"}
                ]

                score_distribution = []
                for range_info in score_ranges:
                    cursor.execute("""
                        SELECT COUNT(*) FROM ai_analysis 
                        WHERE resume_score BETWEEN %s AND %s
                    """, 
                    (range_info["min"], range_info["max"]))
                    count = cursor.fetchone()[0]
                    score_distribution.append({"range": range_info["range"], "count": count})

                # Get recent analyses
                cursor.execute("""
                    SELECT resume_score, job_role, created_at
                    FROM ai_analysis
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_analyses = [
                    {
                        "score": row[0],
                        "job_role": row[1],
                        "date": str(row[2])
                    } for row in cursor.fetchall()
                ]

                return {
                    "total_analyses": total_analyses,
                    "average_score": round(average_score, 1),
                    "top_job_roles": top_job_roles,
                    "daily_trend": daily_trend,
                    "score_distribution": score_distribution,
                    "recent_analyses": recent_analyses
                }

    except Exception as e:
        print(f"Error getting detailed AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "average_score": 0,
            "top_job_roles": [],
            "daily_trend": [],
            "score_distribution": [],
            "recent_analyses": []
        }

def reset_ai_analysis_stats():
    """
    Reset AI analysis statistics by truncating the ai_analysis table
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:

                # Truncate the table
                cursor.execute("TRUNCATE TABLE ai_analysis RESTART IDENTITY CASCADE;")

                return {"success": True, "message": "AI analysis statistics have been reset successfully."}
    
    except Exception as e:
        print(f"Error resetting AI analysis stats: {e}")
        return {"success": False, "message": f"Error resetting AI analysis statistics: {str(e)}"}