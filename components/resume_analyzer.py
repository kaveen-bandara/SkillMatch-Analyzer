import re

class ResumeAnalyzer:
    def __init__(self):

        """Identifiable document types"""
        
        self.document_types = {
            'resume': [
                'experience', 'education', 'skills', 'work', 'project', 'objective',
                'summary', 'employment', 'qualification', 'achievements'
            ],
            'marksheet': [
                'grade', 'marks', 'score', 'semester', 'cgpa', 'sgpa', 'examination',
                'result', 'academic year', 'percentage'
            ],
            'certificate': [
                'certificate', 'certification', 'awarded', 'completed', 'achievement',
                'training', 'course completion', 'qualified'
            ],
            'id_card': [
                'id card', 'identity', 'student id', 'employee id', 'valid until',
                'date of issue', 'identification'
            ]
        }

    def detect_document_type(self, text):

        """Detect type of given document"""

        text = text.lower()
        scores = {}
        
        #Calculate score for each document type
        for doc_type, keywords in self.document_types.items():
            matches = sum(1 for keyword in keywords if re.search(rf'\b{re.escape(keyword)}\b', text))
            density = matches / len(keywords)
            frequency = matches / (len(text.split()) + 1)
            scores[doc_type] = (density * 0.7) + (frequency * 0.3)
        
        #Get the highest scoring document type
        best_match = max(scores.items(), key=lambda x: x[1])
        
        #Only return a document type if the score is significant
        return best_match[0] if best_match[1] > 0.15 else 'unknown'
    
    def calculate_keyword_match(self, resume_text, required_skills):

        """Compare resume text to required skills"""

        resume_text = resume_text.lower()
        found_skills = []
        missing_skills = []
        
        words = set(resume_text.split())

        for skill in required_skills:
            skill_lower = skill.lower()

            #Check for exact match
            if skill_lower in resume_text:
                found_skills.append(skill)
            # Check for partial matches (e.g., "Python" in "Python programming")
            elif any(skill_lower in phrase for phrase in resume_text.split('.')):
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        match_score = (len(found_skills) / len(required_skills)) * 100 if required_skills else 0
        
        return {
            'score': match_score,
            'found_skills': found_skills,
            'missing_skills': missing_skills
        }