import streamlit as st
from config.database import init_database, get_database_connection

from ui_components import (
    apply_styles, hero_section, feature_card)

from config.job_roles import JOB_ROLES
#from components.resume_analyzer import ResumeAnalyzer
#from components.ai_resume_analyzer import AIResumeAnalyzer
#from dashboard.dashboard import DashboardManager

st.set_page_config(
    page_title="SkillMatch: Smart Resume Analyzer",
    page_icon="🚀",
    layout="wide"
)

class SkillMatchApp:
    def __init__(self):
        """
        Initialize the application
        """
        #Initialize form data template
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }
        
        #Initialize navigation state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'

        #Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

        #Define pages dictionary
        self.pages = {
            "🏠 HOME": self.render_home,
            #"🔍 RESUME ANALYZER": self.render_analyzer,
            #"📊 DASHBOARD": self.render_dashboard,
            #"🎯 JOB SEARCH": self.render_job_search,
            #"💬 FEEDBACK": self.render_feedback_page,
            #"📖 ABOUT": self.render_about
        }

        #Initialize dashboard manager
        #self.dashboard_manager = DashboardManager()
        #self.analyzer = ResumeAnalyzer()
        #self.ai_analyzer = AIResumeAnalyzer()
        self.job_roles = JOB_ROLES

        #Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

        #Initialize database
        #init_database()

        #Set up default session state
        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = []
        if 'ai_analysis_stats' not in st.session_state:
            st.session_state.ai_analysis_stats = {
                'score_distribution': {},
                'total_analyses': 0,
                'average_score': 0
            }

    def render_home(self):
        """
        Render the homepage
        """
        apply_styles()
        
        # Hero Section
        hero_section(
            "SkillMatch: Smart Resume Analyzer",
            "Transform your career with AI-powered resume tools to analyze and improve your resume. Get personalized insights tailored to your industry and career goals."
        )
        
        # Features Section
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        feature_card(
            "fas fa-robot",
            "AI-Powered Analysis",
            "Get instant feedback on your resume with advanced AI analysis that identifies strengths and areas for improvement."
        )
        
        feature_card(
            "fas fa-chart-line",
            "Career Insights",
            "Access detailed analytics and personalized recommendations to enhance your career prospects."
        )

        feature_card(
            "fas fa-magic",
            "Smart Resume Builder",
            "Create professional resumes with our intelligent builder that suggests optimal content and formatting."
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.toast("Check 1, 2, 3...", icon="ℹ️")

        # Call-to-Action with Streamlit navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Get Started", key="get_started_btn", 
                        help="Click to start analyzing your resume",
                        type="primary",
                        use_container_width=True):
                cleaned_name = "🔍 RESUME ANALYZER".lower().replace(" ", "_").replace("🔍", "").strip()
                st.session_state.page = cleaned_name
                st.rerun()

    def add_footer(self):
        """
        Add page footer
        """
        st.markdown("<hr style='margin-top: 50px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            #GitHub repo button
            st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 10px;'>
                <a href='https://github.com/kaveen-bandara/SkillMatch-Smart-Resume-Analyzer' target='_blank' style='text-decoration: none;'>
                    <div style='display: flex; align-items: center; background-color: #24292e; padding: 5px 10px; border-radius: 5px; transition: all 0.3s ease;'>
                        <svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='black' style='margin-right: 5px;'>
                            <path d='M12 .5C5.65.5.5 5.65.5 12.01c0 5.1 3.3 9.42 7.9 10.96.58.1.8-.25.8-.56 0-.28-.01-1.02-.01-2-3.22.7-3.9-1.55-3.9-1.55-.53-1.34-1.3-1.7-1.3-1.7-1.05-.72.08-.7.08-.7 1.17.08 1.79 1.2 1.79 1.2 1.04 1.78 2.74 1.26 3.4.96.1-.75.4-1.26.72-1.55-2.57-.29-5.27-1.28-5.27-5.7 0-1.26.45-2.29 1.2-3.1-.13-.3-.52-1.5.12-3.1 0 0 .98-.31 3.2 1.2a11.2 11.2 0 0 1 5.8 0c2.22-1.51 3.2-1.2 3.2-1.2.64 1.6.25 2.8.12 3.1.75.81 1.2 1.84 1.2 3.1 0 4.43-2.7 5.4-5.3 5.7.42.36.77 1.1.77 2.22 0 1.6-.01 2.9-.01 3.3 0 .3.2.66.8.55A11.52 11.52 0 0 0 23.5 12c0-6.36-5.15-11.5-11.5-11.5z' fill='gold' />
                        </svg>
                        <span style='color: white; font-size: 14px;'>Check this repository</span>
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            #Footer text
            st.markdown("""
            <p style='text-align: center;'>
                Powered by <b>Streamlit</b>, <b>Google Gemini</b>, <b>ChatGPT</b> and <b> </b>
                        <br /> Developed by 
                <a href="https://www.linkedin.com/in/kaveen-bandara/" target="_blank" style='text-decoration: none; color: #FFFFFF'>
                    <b>Kaveen Bandara</b>
                </a>
            </p>
            <p style='text-align: center; font-size: 14px; color: #888888;'>
                This project was made with the help of many YouTube tutorials, GitHub repositories and the shared knowledge of the developer community.<br />
                <strong  style="font-weight: 800">Thank you to everyone who contributed, knowingly or not.</strong>
            </p>
            """, unsafe_allow_html=True)




    def main(self):

        """Main application entry point"""

        self.render_home()
        #Add the footer
        self.add_footer()

if __name__ == "__main__":
    app = SkillMatchApp()
    app.main()