from docx import Document
from io import BytesIO
import traceback
import logging

#Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            template_name = data.get('template', '').strip().lower()
            logger.info(f"Starting resume generation with template: {template_name}")            
            
            #Create a new document
            doc = Document()
            
            #Select and apply template
            template_method = self.templates.get(template_name, self.build_modern_template)
            doc = template_method(doc, data)
            
            #Save to in-memory buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            logger.info("Resume generated successfully.")
            return buffer
            
        except Exception as e:
            logger.error(f"Error in generate_resume: {e}")
            logger.debug(traceback.format_exc())
            raise

    def _format_list_items(self, items):

        """Helper function to handle both string and list inputs"""

        if isinstance(items, str):
            return [item.strip() for item in items.split('\n') if item.strip()]
        elif isinstance(items, list):
            return [item.strip() for item in items if item and item.strip()]
        return []

    def build_modern_template(self, doc, data):

        """Build modern style resume"""

    def build_professional_template(self, doc, data):

        """Build professional style resume"""

    def build_minimal_template(self, doc, data):

        """Build minimal style resume"""

    def build_creative_template(self, doc, data):

        """Build creative style resume"""
