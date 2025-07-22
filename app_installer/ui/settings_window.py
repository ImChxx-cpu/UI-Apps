import json
import customtkinter as ctk
from .components.neumorph import NeumorphButton, apply_neumorph_style
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'data' / 'apps_catalog.json'
DEFAULT_PATH = CATALOG_PATH.with_name('apps_catalog_default.json')


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title('Configuraci\u00f3n')
        self.geometry('600x500')
        self.configure(fg_color="#e0e5ec")
        self.text = ctk.CTkTextbox(self)
        apply_neumorph_style(self.text)
        self.text.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        self.status = ctk.CTkLabel(self, text='')
        apply_neumorph_style(self.status)
        self.status.pack(fill='x', padx=10)
        self.restore_btn = NeumorphButton(self, text='Restaurar por defecto', command=self.restore_default)
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
