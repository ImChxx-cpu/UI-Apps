import json
import customtkinter as ctk
from pathlib import Path
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CATALOG_PATH = Path(get_resource_path('app_installer/data/apps_catalog.json'))
DEFAULT_PATH = Path(get_resource_path('app_installer/data/apps_catalog_default.json'))


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title('Configuraci\u00f3n')
        self.geometry('600x500')
        self.text = ctk.CTkTextbox(self)
        self.text.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        self.status = ctk.CTkLabel(self, text='')
        self.status.pack(fill='x', padx=10)
        self.restore_btn = ctk.CTkButton(self, text='Restaurar por defecto', command=self.restore_default)
        self.restore_btn.pack(pady=5)
        self.load_content()
        self.text.bind('<KeyRelease>', self.validate_and_save)

    def load_content(self):
        try:
            content = CATALOG_PATH.read_text(encoding='utf-8')
        except FileNotFoundError:
            content = '{}'
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.validate_and_save()

    def validate_and_save(self, event=None):
        content = self.text.get('1.0', 'end').strip()
        try:
            json.loads(content)
            self.status.configure(text='JSON v\u00e1lido', text_color='green')
            with CATALOG_PATH.open('w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.status.configure(text=f'JSON inv\u00e1lido: {e}', text_color='red')

    def restore_default(self):
        if not DEFAULT_PATH.exists():
            return
        content = DEFAULT_PATH.read_text(encoding='utf-8')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.validate_and_save()
