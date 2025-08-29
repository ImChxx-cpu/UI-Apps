#!/usr/bin/env python3
"""
Simple entry point for the App Installer application.
Usage: python app.py
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main application
try:
    from app_installer.ui.main_window import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Make sure you have installed the requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting the application: {e}")
    sys.exit(1)