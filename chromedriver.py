#!/usr/bin/env python3
"""
Setup script to download and install the correct chromedriver version.
Automatically fetches the latest driver matching your Chrome version
"""

import os
import sys
import subprocess
import platform
import tempfile
import zipfile
import shutil
import json
from urllib.request import urlopen, urlretrieve

def get_chrome_version():
    """
    Get the installed Chrome/Chromium version
    """
    system = platform.system()
        
    try:
        if system == "Windows":
            # Try to find Chrome in Program Files
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ]
            
            for path in chrome_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    output = subprocess.check_output(
                        [expanded_path, "--version"], stderr=subprocess.STDOUT
                    )
                    version = output.decode().strip().split()[2]
                    return version.split(".")[0]

        elif system == "Darwin":  # macOS
            output = subprocess.check_output(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stderr=subprocess.STDOUT,
            )
            version = output.decode().strip().split()[-1]
            return version.split(".")[0]
        
        else:  # Linux
            for binary in ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]:
                if os.path.exists(binary):
                    output = subprocess.check_output([binary, "--version"], stderr=subprocess.STDOUT)
                    version = output.decode().strip().split()[-1]
                    return version.split(".")[0]
                
    except Exception as e:
        print(f"Could not detect Chrome version automatically: {e}")

    # Fallback: ask user
    user_version = input("Enter your Chrome major version: ").strip()
    if user_version.isdigit():
        return user_version
    
    print(f"Defaulting to Chrome version 120")
    return "120"

def get_latest_chromedriver_version(chrome_version):
    """
    Query Google for the latest chromedriver matching the Chrome major version
    """
    url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}"
    try:
        with urlopen(url) as response:
            return response.read().decode().strip()
    except Exception:
        print(f"Could not fetch latest driver for Chrome {chrome_version}, using latest overall")
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        with urlopen(url) as response:
            return response.read().decode().strip()

def download_chromedriver(driver_version):
    """
    Download and install chromedriver for the given version
    """
    system = platform.system()
    if system == "Windows":
        platform_name = "win32"
    elif system == "Darwin":
        platform_name = "mac64"
    elif system == "Linux":
        platform_name = "linux64"
    else:
        print(f"Unsupported platform: {system}")
        return None

    url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_{platform_name}.zip"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "chromedriver.zip")

    try:
        print(f"Downloading Chromedriver {driver_version} from {url}")
        urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        chromedriver_path = os.path.join(
            temp_dir, "chromedriver.exe" if system == "Windows" else "chromedriver"
        )
        if system != "Windows":
            os.chmod(chromedriver_path, 0o755)

        # Install location
        if system == "Windows":
            install_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ChromeDriver")
        else:
            install_dir = os.path.join(os.path.expanduser("~"), ".chromedriver")

        os.makedirs(install_dir, exist_ok=True)
        install_path = os.path.join(install_dir, os.path.basename(chromedriver_path))
        shutil.copy2(chromedriver_path, install_path)

        print(f"✅ Installed Chromedriver to {install_path}")
        return install_path

    except Exception as e:
        print(f"❌ Error installing Chromedriver: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """
    Detect Chrome, download and install matching Chromedriver
    """
    print(f"Setting up Chromedriver...")

    chrome_version = get_chrome_version()
    print(f"Detected Chrome version: {chrome_version}")

    driver_version = get_latest_chromedriver_version(chrome_version)
    print(f"Latest matching Chromedriver version: {driver_version}")

    chromedriver_path = download_chromedriver(driver_version)
    if not chromedriver_path:
        print(f"❌ Failed to install Chromedriver")
        sys.exit(1)

    os.environ["PATH"] = os.path.dirname(chromedriver_path) + os.pathsep + os.environ["PATH"]

    try:
        version_output = subprocess.check_output([chromedriver_path, "--version"], stderr=subprocess.STDOUT)
        print(f"Chromedriver version: {version_output.decode().strip()}")
        print(f"✅ Chromedriver setup completed successfully!")
    except Exception as e:
        print(f"❌ Error testing Chromedriver: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()