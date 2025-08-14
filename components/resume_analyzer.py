import re

class ResumeAnalyzer:
    def __init__(self):

        """Define identifiable document types and their keywords"""
        
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

        """
        Detect the type of a given document based on keyword matches
        
        Args:
            text (str): Extracted document text.

        Returns:
            str: Detected document type, or unknown if no strong match is found.
        """

        text = text.lower()
        scores = {}
        
        # Calculate the score for each document type
        for doc_type, keywords in self.document_types.items():
            matches = sum(
                1 for keyword in keywords
                if re.search(rf'\b{re.escape(keyword)}\b', text)
            )
            density = matches / len(keywords)
            frequency = matches / (len(text.split()) + 1)
            scores[doc_type] = (density * 0.7) + (frequency * 0.3)
        
        # Get the highest scoring document type
        best_match = max(scores.items(), key=lambda x: x[1])
        
        # Return the most significant document type and if none, return unknown
        return best_match[0] if best_match[1] > 0.15 else 'unknown document type'
    
    def calculate_keyword_match(self, resume_text, required_skills):

        """
        Compare resume text to required skills
        
        Args:
            resume_text (str): Extracted resume text.
            required_skills (list[str]): List of skills to check for.

        Returns:
            dict: Match score, found skills, and missing skills.
        """

        resume_text = resume_text.lower()

        # Normalize separators
        resume_text = re.sub(r'[-_/]', ' ', resume_text)

        found_skills = []
        missing_skills = []
        
        for skill in required_skills:
            skill_lower = skill.lower()

            # Whole-word match, works for multi-word skills too
            if re.search(rf'\b{re.escape(skill_lower)}\b', resume_text):
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        match_score = (len(found_skills) / len(required_skills)) * 100 if required_skills else 0
        
        return {
            'score': match_score,
            'found_skills': found_skills,
            'missing_skills': missing_skills
        }
    
    def check_resume_sections(self, text):

        """"""

        text = text.lower()
        essential_sections = {
            'contact': ['email', 'phone', 'address', 'linkedin'],
            'education': ['education', 'university', 'college', 'degree', 'academic'],
            'experience': ['experience', 'work', 'employment', 'job', 'internship'],
            'skills': ['skills', 'technologies', 'tools', 'proficiencies', 'expertise']
        }
        
        section_scores = {}
        for section, keywords in essential_sections.items():
            found = sum(1 for keyword in keywords if keyword in text)
            section_scores[section] = min(25, (found / len(keywords)) * 25)
            
        return sum(section_scores.values())