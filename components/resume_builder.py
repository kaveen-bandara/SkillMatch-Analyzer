from docx import Document
from io import BytesIO
import traceback

class ResumeBuilder:
    def __init__(self):

        """Initialize resumer builder templates"""

        self.templates = {
            "Modern": self.build_modern_template,
            "Professional": self.build_professional_template,
            "Minimal": self.build_minimal_template,
            "Creative": self.build_creative_template
        }

    def generate_resume(self, data):

        """Generate a resume based on the provided data and template"""

        try:
            print(f"Starting resume generation with template: {data['template']}")
            
            #Create a new document
            doc = Document()
            
            #Select and apply template
            template_name = data['template'].lower()
            print(f"Using template: {template_name}")
            
            if template_name == 'modern':
                doc = self.build_modern_template(doc, data)
            elif template_name == 'professional':
                doc = self.build_professional_template(doc, data)
            elif template_name == 'minimal':
                doc = self.build_minimal_template(doc, data)
            elif template_name == 'creative':
                doc = self.build_creative_template(doc, data)
            else:
                print(f"Warning: Unknown template '{template_name}', falling back to modern template")
                doc = self.build_modern_template(doc, data)
            
            #Save to buffer
            buffer = BytesIO()
            print("Saving document to buffer...")
            doc.save(buffer)
            buffer.seek(0)
            print("Resume generated successfully!")
            return buffer
            
        except Exception as e:
            print(f"Error in generate_resume: {str(e)}")
            print(f"Full traceback: {traceback.format_exc()}")
            print(f"Template data: {data}")
            raise

    def _format_list_items(self, items):

        """Helper function to handle both string and list inputs"""

        if isinstance(items, str):
            return [item.strip() for item in items.split('\n') if item.strip()]
        elif isinstance(items, list):
            return [item.strip() for item in items if item and item.strip()]
        return []

    def build_modern_template(self):

        """Build modern style resume"""

    def build_professional_template(self):

        """Build professional style resume"""

    def build_minimal_template(self):

        """Build minimal style resume"""

    def build_creative_template(self):

        """Build creative style resume"""
