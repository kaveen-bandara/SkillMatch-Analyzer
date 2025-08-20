import re
import PyPDF2
import io

class ResumeAnalyzer:
    def __init__(self):
        """
        Define identifiable document types and their keywords
        """
        self.document_types = {
            "resume": [
                "experience", "education", "skills", "work", "project", "objective",
                "summary", "employment", "qualification", "achievements"
            ],
            "marksheet": [
                "grade", "marks", "score", "semester", "cgpa", "sgpa", "examination",
                "result", "academic year", "percentage"
            ],
            "certificate": [
                "certificate", "certification", "awarded", "completed", "achievement",
                "training", "course completion", "qualified"
            ],
            "id card": [
                "id card", "identity", "student id", "employee id", "valid until",
                "date of issue", "identification"
            ]
        }

    def detect_document_type(self, text):
        """
        Detect the type of a given document based on keyword matches
        """
        text = text.lower()
        scores = {}
        
        # Calculate the score for each document type
        for doc_type, keywords in self.document_types.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            density = matches / len(keywords)
            frequency = matches / (len(text.split()) + 1)
            scores[doc_type] = (density * 0.7) + (frequency * 0.3)
        
        # Get the highest scoring document type
        best_match = max(scores.items(), key=lambda x: x[1])
        
        # Return the most significant document type and if none, return unknown
        return best_match[0] if best_match[1] > 0.15 else "Unknown document type"
    
    def calculate_keyword_match(self, resume_text, required_skills):
        """
        Compare resume text to required skills
        """
        resume_text = resume_text.lower()

        # Normalize separators
        resume_text = re.sub(r"[-_/]", " ", resume_text)

        found_skills = []
        missing_skills = []
        
        for skill in required_skills:
            skill_lower = skill.lower()

            # Whole-word match, works for multi-word skills too
            if re.search(rf"\b{re.escape(skill_lower)}\b", resume_text):
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        match_score = (len(found_skills) / len(required_skills)) * 100 if required_skills else 0
        
        return {
            "score": match_score,
            "found_skills": found_skills,
            "missing_skills": missing_skills
        }
    
    def check_resume_sections(self, text):
        """
        Look for keywords to match resume sections
        """
        text = text.lower()
        essential_sections = {
            "contact": ["email", "phone", "address", "linkedin"],
            "education": ["education", "university", "college", "degree", "academic"],
            "experience": ["experience", "work", "employment", "job", "internship"],
            "skills": ["skills", "technologies", "tools", "proficiencies", "expertise"]
        }
        
        section_scores = {}
        for section, keywords in essential_sections.items():
            found = sum(1 for keyword in keywords if keyword in text)
            section_scores[section] = min(25, (found / len(keywords)) * 25)
            
        return sum(section_scores.values())
    
    def check_formatting(self, text):
        """
        Score the resume based on formatting to check for proper format
        """
        lines = text.split("\n")
        score = 100
        deductions = []
        
        # Check for minimum content
        if len(text) < 300:
            score -= 30
            deductions.append("Resume is too short!")
            
        # Check for section headers
        if not any(
            re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)*$", line.strip()) or line.isupper() 
            for line in lines
        ):
            score -= 20
            deductions.append("No clear section headers found!")
            
        # Check for bullet points
        bullet_chars = ("•", "-", "*", "→", "‣", "·")
        if not any(line.strip().startswith(bullet_chars) for line in lines if line.strip()):
            score -= 20
            deductions.append("No bullet points found for listing details!")
            
        # Check for consistent spacing
        if any(len(line.strip()) == 0 and len(next_line.strip()) == 0 
               for line, next_line in zip(lines[:-1], lines[1:])):
            score -= 15
            deductions.append("Inconsistent spacing between sections!")
            
        # Check for contact information format
        contact_patterns = [
            r"\b[\w\.-]+@[\w\.-]+\.\w+\b",  # email
            r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}",  # phone
            r"linkedin\.com/\w+",  # LinkedIn
        ]
        if not any(re.search(pattern, text) for pattern in contact_patterns):
            score -= 15
            deductions.append("Missing or improperly formatted contact information!")
            
        return max(0, score), deductions
    
    def extract_text_from_pdf(self, pdf_file):
        """
        Code to extract text from PDF files
        """
        try:       
            # Handle file input
            if hasattr(pdf_file, "read"):
                file_content = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer
            else:
                file_content = pdf_file
                
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            # Extract text
            text = ""
            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"
                
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
    def extract_text_from_docx(self, docx_file):
        """
        Code to extract text from DOCX files
        """
        try:
            from docx import Document
            doc = Document(docx_file)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            return '\n'.join(full_text)
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX file: {str(e)}")
        
    def extract_personal_info(self, text):
        """
        Extract personal information from resume text
        """
        # Basic patterns for personal info
        email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
        phone_pattern = r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}"
        linkedin_pattern = r"linkedin\.com/in/[\w-]+"
        github_pattern = r"github\.com/[\w-]+"
        
        # Extract information
        email = re.search(email_pattern, text)
        phone = re.search(phone_pattern, text)
        linkedin = re.search(linkedin_pattern, text)
        github = re.search(github_pattern, text)
        
        # Get the first line as name (basic assumption)
        name = text.split("\n")[0].strip()
        
        return {
            "name": name if len(name) > 0 else "Unknown name",
            "email": email.group(0) if email else "",
            "phone": phone.group(0) if phone else "",
            "linkedin": linkedin.group(0) if linkedin else "",
            "github": github.group(0) if github else ""
        }
    
    def extract_education(self, text):
        """
        Extract education information from resume text
        """
        education = []
        lines = text.split("\n")
        education_keywords = [
            "education", "academic", "qualification", "degree", "university", "college",
            "school", "institute", "certification", "diploma", "bachelor", "master",
            "phd", "b.tech", "m.tech", "b.e", "m.e", "b.sc", "m.sc","bca", "mca", "b.com",
            "m.com", "b.cs-it", "imca", "bba", "mba", "honors", "scholarship"
        ]
        in_education_section = False
        current_entry = []

        for line in lines:
            line = line.strip()

            # Check for section header
            if any(keyword.lower() in line.lower() for keyword in education_keywords):
                if not any(keyword.lower() == line.lower() for keyword in education_keywords):
                    # This line contains education info, not just a header
                    current_entry.append(line)

                in_education_section = True
                continue
            
            if in_education_section:
                # Check if we've hit another section
                if line and any(keyword.lower() in line.lower() for keyword in self.document_types["resume"]):
                    if not any(edu_key.lower() in line.lower() for edu_key in education_keywords):
                        in_education_section = False
                        if current_entry:
                            education.append(" ".join(current_entry))
                            current_entry = []
                        continue
                
                if line:
                    current_entry.append(line)
                elif current_entry:
                    education.append(" ".join(current_entry))
                    current_entry = []
        
        if current_entry:
            education.append(" ".join(current_entry))
        
        return education
    
    def extract_experience(self, text):
        """
        Extract work experience information from resume text
        """
        experience = []
        lines = text.split("\n")
        experience_keywords = [
            "experience", "employment", "work history", "professional experience",
            "work experience", "career history", "professional background",
            "employment history", "job history", "positions held", "job title",
            "job responsibilities", "job description", "job summary"
        ]
        in_experience_section = False
        current_entry = []

        for line in lines:
            line = line.strip()

            # Check for section header
            if any(keyword.lower() in line.lower() for keyword in experience_keywords):
                if not any(keyword.lower() == line.lower() for keyword in experience_keywords):
                    # This line contains experience info, not just a header
                    current_entry.append(line)

                in_experience_section = True
                continue
            
            if in_experience_section:
                # Check if we've hit another section
                if line and any(keyword.lower() in line.lower() for keyword in self.document_types["resume"]):
                    if not any(exp_key.lower() in line.lower() for exp_key in experience_keywords):
                        in_experience_section = False
                        if current_entry:
                            experience.append(" ".join(current_entry))
                            current_entry = []

                        continue
                
                if line:
                    current_entry.append(line)
                elif current_entry:
                    experience.append(" ".join(current_entry))
                    current_entry = []
        
        if current_entry:
            experience.append(" ".join(current_entry))
        
        return experience
    
    def extract_projects(self, text):
        """
        Extract project information from resume text
        """
        projects = []
        lines = text.split("\n")
        project_keywords = [
            "projects", "personal projects", "academic projects", "key projects",
            "major projects", "professional projects", "project experience",
            "relevant projects", "featured projects", "latest projects",
            "top projects"
        ]
        in_project_section = False
        current_entry = []

        for line in lines:
            line = line.strip()
            # Check for section header
            if any(keyword.lower() in line.lower() for keyword in project_keywords):
                if not any(keyword.lower() == line.lower() for keyword in project_keywords):
                    # This line contains project info, not just a header
                    current_entry.append(line)
                in_project_section = True
                continue
            
            if in_project_section:
                # Check if we've hit another section
                if line and any(keyword.lower() in line.lower() for keyword in self.document_types["resume"]):
                    if not any(proj_key.lower() in line.lower() for proj_key in project_keywords):
                        in_project_section = False
                        if current_entry:
                            projects.append(" ".join(current_entry))
                            current_entry = []
                        continue
                
                if line:
                    current_entry.append(line)
                elif current_entry:
                    projects.append(" ".join(current_entry))
                    current_entry = []
        
        if current_entry:
            projects.append(" ".join(current_entry))
        
        return projects
    
    def extract_skills(self, text):
        """
        Extract skills from resume text
        """
        skills = set()  # Use set to avoid duplicates
        lines = text.split('\n')
        skills_keywords = [
            'skills', 'technical skills', 'competencies', 'expertise',
            'core competencies', 'professional skills', 'key skills',
            'technical expertise', 'proficiencies', 'qualifications',
            'top skills', 'key skill', 'major skill', 'personal skill',
            'soft skills', 'soft skill', 'soft skillset'
        ]
        in_skills_section = False
        current_entry = []

        # Common skill separators
        separators = [',', '•', '|', '/', '\\', '·', '>', '-', '–', '―']

        for line in lines:
            line = line.strip()
            # Check for section header
            if any(keyword.lower() in line.lower() for keyword in skills_keywords):
                if not any(keyword.lower() == line.lower() for keyword in skills_keywords):
                    # This line contains skills, not just a header
                    current_entry.append(line)

                in_skills_section = True
                continue
            
            if in_skills_section:
                # Check if we've hit another section
                if line and any(keyword.lower() in line.lower() for keyword in self.document_types["resume"]):
                    if not any(skill_key.lower() in line.lower() for skill_key in skills_keywords):
                        in_skills_section = False
                        if current_entry:
                            # Process the current entry
                            text_to_process = " ".join(current_entry)
                            # Split by common separators
                            for separator in separators:
                                if separator in text_to_process:
                                    skills.update(skill.strip() for skill in text_to_process.split(separator) if skill.strip())
                            current_entry = []
                        continue
                
                if line:
                    current_entry.append(line)
                elif current_entry:
                    # Process the current entry
                    text_to_process = " ".join(current_entry)
                    # Split by common separators
                    for separator in separators:
                        if separator in text_to_process:
                            skills.update(skill.strip() for skill in text_to_process.split(separator) if skill.strip())
                    current_entry = []
        
        if current_entry:
            # Process any remaining skills
            text_to_process = " ".join(current_entry)
            for separator in separators:
                if separator in text_to_process:
                    skills.update(skill.strip() for skill in text_to_process.split(separator) if skill.strip())
        
        return list(skills)
    
    def extract_summary(self, text):
        """
        Extract summary from resume text
        """
        summary = []
        lines = text.split("\n")
        summary_keywords = [
            'summary', 'professional summary', 'career summary', 'objective',
            'career objective', 'professional objective', 'about me', 'profile',
            'professional profile', 'career profile', 'overview', 'skill summary'
        ]
        in_summary_section = False
        current_entry = []

        # Try to find summary at the beginning of the resume
        start_index = 0
        while start_index < min(10, len(lines)) and not lines[start_index].strip():
            start_index += 1

        # Check first few non-empty lines for potential summary
        first_lines = []
        lines_checked = 0
        for line in lines[start_index:]:
            if line.strip():
                first_lines.append(line.strip())
                lines_checked += 1
                if lines_checked >= 5:  # Check first 5 non-empty lines
                    break

        # If first few lines look like a summary (no special formatting, no contact info)
        if first_lines and not any(keyword in first_lines[0].lower() for keyword in summary_keywords):
            potential_summary = " ".join(first_lines)
            if len(potential_summary.split()) > 10:  # More than 10 words
                if not re.search(r"\b(?:email|phone|address|tel|mobile|linkedin)\b", potential_summary.lower()):
                    summary.append(potential_summary)

        # Look for explicitly marked summary section
        for line in lines:
            line = line.strip()
            # Check for section header
            if any(keyword.lower() in line.lower() for keyword in summary_keywords):
                if not any(keyword.lower() == line.lower() for keyword in summary_keywords):
                    # This line contains summary info, not just a header
                    current_entry.append(line)
                in_summary_section = True
                continue
            
            if in_summary_section:
                # Check if we've hit another section
                if line and any(keyword.lower() in line.lower() for keyword in self.document_types["resume"]):
                    if not any(sum_key.lower() in line.lower() for sum_key in summary_keywords):
                        in_summary_section = False
                        if current_entry:
                            summary.append(" ".join(current_entry))
                            current_entry = []
                        continue
                
                if line:
                    current_entry.append(line)
                elif current_entry:
                    summary.append(" ".join(current_entry))
                    current_entry = []
        
        if current_entry:
            summary.append(" ".join(current_entry))
        
        return " ".join(summary) if summary else ""