# Winget App Installer UI

This project provides a graphical interface for installing Windows applications using `winget`.

## Prerequisites

- Python 3.10 or later.
- The `customtkinter` package.
- Windows with `winget` installed.

Install dependencies with:

```bash
pip install customtkinter
```

## Running the application

To launch the UI during development you can run the package as a module or
execute the provided script:

```bash
python -m app_installer  # run as a module
# or
python run_app.py        # run using the script entry point
```

The `run_app.py` script uses absolute imports and can be used directly with
PyInstaller:

```bash
pyinstaller run_app.py
```

