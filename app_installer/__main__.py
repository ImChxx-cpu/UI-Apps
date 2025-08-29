"""Run app_installer as a module: python -m app_installer"""

if __name__ == "__main__":
    try:
        from app_installer.ui.main_window import main
        main()
    except ImportError:
        print("Error: Missing dependencies. Please install them first:")
        print("pip install customtkinter")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
