import os
import sys
import subprocess
import platform

def main():
    """
    Main function to set up chromedriver and run the application
    """
    print(f"🚀 Starting SkillMatch: Smart Resume Analyzer...")
    
    # Detect operating system
    system = platform.system()
    print(f"Detected OS: {system}")

    # Path to setup script
    setup_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "skip_for_now.py"
    )
    
    # Run chromedriver setup if script exists
    if os.path.exists(setup_script):
        try:
            result = subprocess.run(
                [sys.executable, setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode != 0:
                print(f"❌ Chromedriver setup failed")
        except Exception as e:
            if result.returncode != 0:
                print(f"❌ Chromedriver error: {e}")
    else:
        print(f"No chromedriver setup script found. Skipping...")
    
    # Path to Streamlit application
    app_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "app.py"
    )
    
    # Run streamlit application
    print(f"🎯 Launching Streamlit application...")
    if os.path.exists(app_script):
        try:
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", app_script]
            )
            print("✅ Application launched! Check your browser.")
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            sys.exit(1)
    else:
        print(f"❌ Application script not found at {app_script}")
        sys.exit(1)

if __name__ == "__main__":
    main() 