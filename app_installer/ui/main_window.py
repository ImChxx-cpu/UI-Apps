import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pathlib import Path
from typing import Dict, List

from app_installer.core import installer, file_manager, scanner
from .settings_window import SettingsWindow

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'data' / 'apps_catalog.json'


narrow = 40


class AppInstallerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        self.title("Winget App Installer")
        self.geometry("800x600")
        self.catalog = file_manager.load_catalog(CATALOG_PATH)
        self.selected_apps: List[Dict[str, str]] = []
        self.create_widgets()

    def create_widgets(self):
        self.search_var = tk.StringVar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_app_list())

        self.app_scroll = ctk.CTkScrollableFrame(self)
        self.app_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.app_scroll.grid_columnconfigure(0, weight=1)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)

        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.grid(row=0, column=0, sticky="ew")
        for i in range(2):
            button_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkButton(button_frame, text="Instalar", command=self.install_selected).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Configuraci\u00f3n", command=self.open_settings).grid(row=0, column=1, padx=5, pady=5)

        self.status = ctk.CTkTextbox(bottom_frame, height=120)
        self.status.grid(row=1, column=0, sticky="nsew")

        self.refresh_app_list()

    def refresh_app_list(self):
        for widget in self.app_scroll.winfo_children():
            widget.destroy()
        search = self.search_var.get().lower()
        self.check_vars = {}
        for category, apps in self.catalog.items():
            cat_frame = ctk.CTkFrame(self.app_scroll)
            cat_frame.pack(fill="x", padx=5, pady=5)
            ctk.CTkLabel(cat_frame, text=category, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 2))
            for app in apps:
                if search and search not in app['name'].lower():
                    continue
                var = tk.BooleanVar()
                chk = ctk.CTkCheckBox(cat_frame, text=app['name'], variable=var)
                chk.pack(anchor="w")
                self.check_vars[app['id']] = (var, app)

    def gather_selection(self) -> List[Dict[str, str]]:
        selected = []
        for var, app in self.check_vars.values():
            if var.get():
                selected.append(app)
        return selected

    def install_selected(self):
        apps = self.gather_selection()
        if not apps:
            messagebox.showinfo('Info', 'No hay aplicaciones seleccionadas')
            return
        if not installer.is_winget_available():
            messagebox.showerror('Error', 'winget no está disponible')
            return
        threading.Thread(target=self._install_thread, args=(apps,), daemon=True).start()

    def _install_thread(self, apps):
        self.status.insert('end', 'Iniciando instalación...\n')
        results = installer.install_apps(apps)
        for res in results:
            marker = '🟢' if res.returncode == 0 else '🔴'
            self.status.insert('end', f"{marker} {res.name} ({res.id})\n")
            self.status.insert('end', f"Inicio: {res.start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.status.insert('end', f"Duración: {res.duration:.1f}s\n")
            if res.stderr and res.returncode != 0:
                self.status.insert('end', res.stderr.strip() + '\n')
            self.status.insert('end', '─────────────────────\n')
        self.status.insert('end', 'Instalación finalizada\n')

    def export_selected(self):
        apps = self.gather_selection()
        if not apps:
            messagebox.showinfo('Info', 'No hay aplicaciones seleccionadas')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json')
        if not path:
            return
        file_manager.export_selection(Path(path), apps)
        messagebox.showinfo('Info', 'Exportado correctamente')

    def import_list(self):
        path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return
        apps = file_manager.import_selection(Path(path))
        for app in apps:
            if app['id'] in self.check_vars:
                self.check_vars[app['id']][0].set(True)
        messagebox.showinfo('Info', 'Lista importada')

    def scan_system(self):
        if not installer.is_winget_available():
            messagebox.showerror('Error', 'winget no está disponible')
            return
        apps = scanner.list_installed_apps()
        path = filedialog.asksaveasfilename(defaultextension='.json')
        if not path:
            return
        file_manager.save_backup(Path(path), apps)
        messagebox.showinfo('Info', 'Respaldo guardado')

    def open_settings(self):
        win = SettingsWindow(self)
        win.grab_set()
        win.protocol('WM_DELETE_WINDOW', lambda w=win: self._close_settings(w))

    def _close_settings(self, win):
        win.destroy()
        self.reload_catalog()

    def reload_catalog(self):
        self.catalog = file_manager.load_catalog(CATALOG_PATH)
        self.refresh_app_list()

def main():
    app = AppInstallerUI()
    app.mainloop()


if __name__ == '__main__':
    main()
