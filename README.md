# Winget App Installer

Modern GUI application for installing Windows applications using winget package manager.

## Features

- Easy-to-use graphical interface built with CustomTkinter
- Browse and install applications from the Windows Package Manager
- Installation progress tracking with detailed logs
- Settings management and app catalog customization

## Requirements

- Windows 10/11
- Python 3.7+
- Winget (Windows Package Manager)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

Or run as a module:
```bash
python -m app_installer
```

## Build Executable

```bash
pyinstaller WingetAppInstaller.spec
```


