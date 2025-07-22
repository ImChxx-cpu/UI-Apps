import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List

from app_installer.core import installer, file_manager, scanner

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'data' / 'apps_catalog.json'


narrow = 40
class AppInstallerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Winget App Installer')
        self.geometry('600x500')
        self.minsize(500, 400)
        self.catalog = file_manager.load_catalog(CATALOG_PATH)
        self.selected_apps: List[Dict[str, str]] = []
        self.create_widgets()

    def create_widgets(self):
        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text='Buscar:').pack(side='left')
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self.refresh_app_list())

        list_container = ttk.Frame(self)
        list_container.pack(fill='both', expand=True, padx=5, pady=5)

        self.app_canvas = tk.Canvas(list_container, borderwidth=0)
        vscroll = ttk.Scrollbar(list_container, orient='vertical', command=self.app_canvas.yview)
        self.app_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side='right', fill='y')
        self.app_canvas.pack(side='left', fill='both', expand=True)

        self.app_frame = ttk.Frame(self.app_canvas)
        self.app_frame_id = self.app_canvas.create_window((0, 0), window=self.app_frame, anchor='nw')
        self.app_frame.bind(
            '<Configure>',
            lambda e: self.app_canvas.configure(scrollregion=self.app_canvas.bbox('all'))
        )
        self.app_canvas.bind(
            '<Configure>',
            lambda e: self.app_canvas.itemconfig(self.app_frame_id, width=e.width)
        )

        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x')
        ttk.Button(button_frame, text='Instalar', command=self.install_selected).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text='Exportar', command=self.export_selected).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text='Importar', command=self.import_list).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text='Escanear', command=self.scan_system).pack(side='left', padx=5, pady=5)

        self.status = tk.Text(self, height=8)
        self.status.pack(fill='x', padx=5, pady=5)

        self.refresh_app_list()

    def refresh_app_list(self):
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        search = self.search_var.get().lower()
        self.check_vars = {}
        for category, apps in self.catalog.items():
            cat_frame = ttk.LabelFrame(self.app_frame, text=category)
            cat_frame.pack(fill='x', padx=5, pady=5)
            for app in apps:
                if search and search not in app['name'].lower():
                    continue
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(cat_frame, text=app['name'], variable=var)
                chk.pack(anchor='w')
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
            self.status.insert('end', f"{res.args[3]} -> {res.returncode}\n")
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


def main():
    app = AppInstallerUI()
    app.mainloop()


if __name__ == '__main__':
    main()
