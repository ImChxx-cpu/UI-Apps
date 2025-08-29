#!/usr/bin/env python3
"""
Winget App Installer - Simple entry point
Usage: python main.py
"""

if __name__ == "__main__":
    try:
        from app_installer.ui.main_window import main
        main()
    except ImportError as e:
        print("Error: Missing dependencies. Please install them first:")
        print("pip install customtkinter")
        exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        exit(1)