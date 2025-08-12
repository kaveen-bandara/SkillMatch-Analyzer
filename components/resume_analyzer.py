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

        """Detect given document type"""

        text = text.lower()
        scores = {}
        
        #Calculate score for each document type
        for doc_type, keywords in self.document_types.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            density = matches / len(keywords)
            frequency = matches / (len(text.split()) + 1)
            scores[doc_type] = (density * 0.7) + (frequency * 0.3)
        
        #Get the highest scoring document type
        best_match = max(scores.items(), key=lambda x: x[1])
        
        #Only return a document type if the score is significant
        return best_match[0] if best_match[1] > 0.15 else 'unknown'