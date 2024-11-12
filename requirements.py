import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

libraries = ['pandas', 'gspread' ,'oauth2client', 'numpy' ,'pyyaml' ,'docxtpl' ,'docx2pdf' ,'google-auth' ,'google-auth-oauthlib', 'google-auth-httplib2' ,'google-api-python-client']
for library in libraries:
    install_package(library)
