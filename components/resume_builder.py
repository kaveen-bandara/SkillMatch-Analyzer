import traceback
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor
from io import BytesIO

class ResumeBuilder:
    def __init__(self):
        """
        Define template
        """
        self.template = self.build_resume_template

    def generate_resume(self, data):
        """
        Generate a resume
        """
        try:
            # Create a new document
            doc = Document()
            doc = self.template(doc, data)
                        
            # Save to buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error generating resume: {str(e)}")
            print(traceback.format_exc())
            raise

    def _format_list_items(self, items):
        """
        Helper function to handle both string and list inputs
        """
        if isinstance(items, str):
            return [item.strip() for item in items.split("\n") if item.strip()]
        elif isinstance(items, list):
            return [item.strip() for item in items if item and item.strip()]
        return []

    def build_resume_template(self, doc, data):
        """
        Build resume according to template
        """
        try:
            styles = doc.styles

            # Header style
            header_style = styles.add_style("Header", WD_STYLE_TYPE.PARAGRAPH) if "Header" not in styles else styles["Header"]
            header_style.font.size = Pt(24)
            header_style.font.bold = True
            header_style.font.color.rgb = RGBColor(0, 0, 0)
            header_style.paragraph_format.space_after = Pt(4)
            header_style.font.name = "Calibri"

            # Section style
            section_style = styles.add_style("Section", WD_STYLE_TYPE.PARAGRAPH) if "Section" not in styles else styles["Section"]
            section_style.font.size = Pt(14)
            section_style.font.bold = True
            section_style.font.color.rgb = RGBColor(0, 120, 215)
            section_style.paragraph_format.space_before = Pt(12)
            section_style.paragraph_format.space_after = Pt(6)
            section_style.font.name = "Calibri"

            # Normal text style
            normal_style = styles.add_style("Normal Text", WD_STYLE_TYPE.PARAGRAPH) if "Normal Text" not in styles else styles["Normal Text"]
            normal_style.font.size = Pt(10)
            normal_style.font.name = "Calibri"
            normal_style.paragraph_format.space_after = Pt(2)

            # Contact style
            contact_style = styles.add_style("Contact", WD_STYLE_TYPE.PARAGRAPH) if "Contact" not in styles else styles["Contact"]
            contact_style.font.size = Pt(10)
            contact_style.font.name = "Calibri"
            contact_style.paragraph_format.space_after = Pt(6)

            # Add full name at the top
            name_paragraph = doc.add_paragraph(data["personal_info"]["full_name"])
            name_paragraph.style = header_style
            name_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

            # Add contact in a single line
            contact_parts = []
            if data["personal_info"].get("email"): contact_parts.append(data["personal_info"]["email"])
            if data["personal_info"].get("phone"): contact_parts.append(data["personal_info"]["phone"])
            if data["personal_info"].get("location"): contact_parts.append(data["personal_info"]["location"])

            if contact_parts:
                contact = doc.add_paragraph()
                contact.style = contact_style
                contact.add_run(" | ".join(contact_parts))

            # Add links in a single line
            link_parts = []
            if data["personal_info"].get("linkedin"): link_parts.append(f"LinkedIn: {data['personal_info']['linkedin']}")
            if data["personal_info"].get("portfolio"): link_parts.append(f"Portfolio: {data['personal_info']['portfolio']}")            
            
            if link_parts:
                link = doc.add_paragraph(" | ".join(link_parts))
                link.style = contact_style

            # Summary
            if data.get("summary"):
                doc.add_paragraph("SUMMARY", style=section_style)
                summary = doc.add_paragraph(data["summary"])
                summary.style = normal_style

            # Experience
            if data.get("experience"):
                doc.add_paragraph("EXPERIENCE", style=section_style)
                for exp in data["experience"]:
                    p = doc.add_paragraph()
                    p.style = normal_style
                    p.add_run(f"{exp['position']} at {exp['company']}").bold = True
                    p.add_run(f" | {exp['start_date']} - {exp['end_date']}")

                    if exp.get("description"):
                        desc = doc.add_paragraph(exp["description"])
                        desc.style = normal_style
                        desc.paragraph_format.left_indent = Inches(0.2)

                    if exp.get("responsibilities"):
                        for resp in self._format_list_items(exp["responsibilities"]):
                            bullet = doc.add_paragraph()
                            bullet.style = normal_style
                            bullet.paragraph_format.left_indent = Inches(0.3)
                            bullet.add_run("• " + resp)

            # Projects
            if data.get("projects"):
                doc.add_paragraph("PROJECTS", style=section_style)
                for proj in data["projects"]:
                    p = doc.add_paragraph()
                    p.style = normal_style
                    p.add_run(proj["name"]).bold = True
                    if proj.get("technologies"):
                        p.add_run(f" | {proj['technologies']}")
                    
                    if proj.get("description"):
                        desc = doc.add_paragraph(proj["description"])
                        desc.style = normal_style
                        desc.paragraph_format.left_indent = Inches(0.2)
                    
                    if proj.get("responsibilities"):
                        for resp in self._format_list_items(proj["responsibilities"]):
                            bullet = doc.add_paragraph()
                            bullet.style = normal_style
                            bullet.paragraph_format.left_indent = Inches(0.3)
                            bullet.add_run("• " + resp)

            # Education
            if data.get("education"):
                doc.add_paragraph("EDUCATION", style=section_style)
                for edu in data["education"]:
                    p = doc.add_paragraph()
                    p.style = normal_style
                    p.add_run(f"{edu['school']}").bold = True
                    p.add_run(f"\n{edu['degree']} in {edu['field']}")
                    p.add_run(f" | Graduation: {edu['graduation_date']}")
                    if edu.get("gpa"):
                        p.add_run(f" | GPA: {edu['gpa']}")

            # Skills
            if data.get("skills"):
                doc.add_paragraph("SKILLS", style=section_style)
                skills = data["skills"]
                
                def add_skill_category(category_name, title):
                    if skills.get(category_name):
                        p = doc.add_paragraph()
                        p.style = normal_style
                        p.add_run(f"{title}: ").bold = True
                        skills_text = ", ".join(self._format_list_items(skills[category_name]))
                        p.add_run(skills_text)
                
                add_skill_category("technical", "Technical Skills")
                add_skill_category("soft", "Soft Skills")
                add_skill_category("languages", "Languages")
                add_skill_category("tools", "Tools & Technologies")

            # Margins
            for section in doc.sections:
                section.top_margin = Inches(0.5)
                section.bottom_margin = Inches(0.5)
                section.left_margin = Inches(0.7)
                section.right_margin = Inches(0.7)

            return doc

        except Exception as e:
            print(f"Error in build_resume_template: {str(e)}")
            raise