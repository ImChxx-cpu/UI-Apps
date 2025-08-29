import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pathlib import Path
from typing import Dict, List



from app_installer.core import installer, file_manager, scanner
from .settings_window import SettingsWindow

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'data' / 'apps_catalog.json'


class AppInstallerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        self.title("Winget App Installer")
        self.geometry("800x600")
        self.catalog = file_manager.load_catalog(CATALOG_PATH)
        self.selected_apps: List[Dict[str, str]] = []
        self.check_vars = {}
        self.category_frames = {}
        self.create_widgets()

    def create_widgets(self):
        self.search_var = tk.StringVar()

        # Top frame with search and selection controls
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        # Search section
        ctk.CTkLabel(top_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var, placeholder_text="Buscar aplicaciones...")
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_app_list())
        
        # Clear search button
        clear_btn = ctk.CTkButton(top_frame, text="Limpiar", width=60, command=self.clear_search)
        clear_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Selection controls frame
        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(fill="x", padx=10, pady=(0, 10))
        selection_frame.grid_columnconfigure(2, weight=1)
        
        # Selection counter
        self.selection_label = ctk.CTkLabel(selection_frame, text="0 aplicaciones seleccionadas", 
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.selection_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Selection buttons
        select_all_btn = ctk.CTkButton(selection_frame, text="Seleccionar Todo", 
                                     command=self.select_all, fg_color="#2b9348", hover_color="#52b788")
        select_all_btn.grid(row=0, column=3, padx=5, pady=5)
        
        deselect_all_btn = ctk.CTkButton(selection_frame, text="Deseleccionar Todo", 
                                       command=self.deselect_all, fg_color="#d62828", hover_color="#f77f00")
        deselect_all_btn.grid(row=0, column=4, padx=5, pady=5)

        self.app_scroll = ctk.CTkScrollableFrame(self)
        self.app_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.app_scroll.grid_columnconfigure(0, weight=1)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)
        for r in range(2, 4):
            bottom_frame.grid_rowconfigure(r, weight=0)

        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)

        # Install button with counter
        self.install_btn = ctk.CTkButton(button_frame, text="Instalar (0)", 
                                       command=self.install_selected, 
                                       fg_color="#2b9348", hover_color="#52b788",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.install_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Other buttons
        ctk.CTkButton(button_frame, text="Configuraci\u00f3n", command=self.open_settings).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(button_frame, text="Exportar", command=self.export_selected).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(button_frame, text="Importar", command=self.import_list).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.status = ctk.CTkTextbox(bottom_frame, height=120)
        self.status.grid(row=1, column=0, sticky="nsew")

        self.current_pkg = ctk.CTkLabel(bottom_frame, text="")
        self.current_pkg.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        self.result_msg = ctk.CTkLabel(bottom_frame, text="")
        self.result_msg.grid(row=3, column=0, sticky="ew", pady=5)

        self.refresh_app_list()

    def refresh_app_list(self):
        for widget in self.app_scroll.winfo_children():
            widget.destroy()
        search = self.search_var.get().lower()
        self.check_vars = {}
        self.category_frames = {}
        
        for category, apps in self.catalog.items():
            # Filter apps by search
            filtered_apps = []
            for app in apps:
                if not search or search in app['name'].lower():
                    filtered_apps.append(app)
            
            # Skip empty categories
            if not filtered_apps:
                continue
                
            # Category frame
            cat_frame = ctk.CTkFrame(self.app_scroll)
            cat_frame.pack(fill="x", padx=5, pady=5)
            self.category_frames[category] = cat_frame
            
            # Category header with selection button
            header_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=5, pady=(5, 2))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Category title
            cat_label = ctk.CTkLabel(header_frame, text=f"{category} ({len(filtered_apps)})", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
            cat_label.grid(row=0, column=0, sticky="w")
            
            # Category select/deselect button
            cat_btn = ctk.CTkButton(header_frame, text=f"Seleccionar {category}", 
                                  command=lambda c=category: self.toggle_category_selection(c),
                                  width=140, height=25, 
                                  font=ctk.CTkFont(size=11))
            cat_btn.grid(row=0, column=2, sticky="e", padx=(5, 0))
            
            # Apps in category
            for app in filtered_apps:
                var = tk.BooleanVar()
                var.trace('w', lambda *args: self.update_selection_counter())
                chk = ctk.CTkCheckBox(cat_frame, text=app['name'], variable=var,
                                    font=ctk.CTkFont(size=12))
                chk.pack(anchor="w", padx=20, pady=2)
                self.check_vars[app['id']] = (var, app, category)
                
        self.update_selection_counter()

    def gather_selection(self) -> List[Dict[str, str]]:
        selected = []
        for data in self.check_vars.values():
            var, app = data[0], data[1]
            if var.get():
                selected.append(app)
        return selected
    
    def update_selection_counter(self):
        """Update the selection counter and install button text"""
        count = sum(1 for data in self.check_vars.values() if data[0].get())
        self.selection_label.configure(text=f"{count} aplicaciones seleccionadas")
        self.install_btn.configure(text=f"Instalar ({count})")
        
        # Update button state
        if count > 0:
            self.install_btn.configure(state="normal")
        else:
            self.install_btn.configure(state="disabled")
    
    def clear_search(self):
        """Clear the search field"""
        self.search_var.set("")
        self.refresh_app_list()
    
    def select_all(self):
        """Select all visible applications"""
        for data in self.check_vars.values():
            data[0].set(True)
        self.update_selection_counter()
    
    def deselect_all(self):
        """Deselect all applications"""
        for data in self.check_vars.values():
            data[0].set(False)
        self.update_selection_counter()
    
    def toggle_category_selection(self, category):
        """Toggle selection of all apps in a category"""
        category_apps = [data for data in self.check_vars.values() if len(data) > 2 and data[2] == category]
        
        # Check if all apps in category are selected
        all_selected = all(data[0].get() for data in category_apps)
        
        # Toggle: if all selected, deselect all; otherwise select all
        new_state = not all_selected
        for data in category_apps:
            data[0].set(new_state)
        
        self.update_selection_counter()

    def install_selected(self):
        apps = self.gather_selection()
        if not apps:
            self.result_msg.configure(text="No hay aplicaciones seleccionadas", text_color="orange")
            return
        if not installer.is_winget_available():
            self.result_msg.configure(text="Error: winget no está disponible", text_color="red")
            return
            
        # Clear previous status
        self.status.delete("1.0", "end")
        self.current_pkg.configure(text="")
        self.result_msg.configure(text="")
        
        # Disable install button during installation
        self.install_btn.configure(state="disabled", text="Instalando...")
        
        threading.Thread(target=self._install_thread, args=(apps,), daemon=True).start()

    def _install_thread(self, apps):
        total = len(apps)
        self.after(0, lambda: self.status.insert('end', f'Iniciando instalación de {total} aplicaciones...\n\n'))
        error = False
        success_count = 0
        
        for idx, app in enumerate(apps, start=1):
            app_name = app.get('name', app['id'])
            self.after(0, lambda i=idx, n=app_name, t=total: 
                      self.current_pkg.configure(text=f"Instalando {n} ({i}/{t})"))
            
            result = installer.install_app(app, interactive=False)
            if result.returncode == 0:
                success_count += 1
            else:
                error = True
            self.after(0, lambda r=result: self._log_result(r))
        
        # Final status
        if error:
            msg = f'Instalación completada con errores: {success_count}/{total} exitosas'
            color = 'orange'
        else:
            msg = f'Instalación completada exitosamente: {success_count}/{total} aplicaciones'
            color = 'green'
            
        self.after(0, lambda: self.status.insert('end', f'\n{msg}\n'))
        self.after(0, lambda: self.current_pkg.configure(text=''))
        self.after(0, lambda: self.result_msg.configure(text=msg, text_color=color))
        
        # Re-enable install button and update counter
        self.after(0, lambda: self.update_selection_counter())
        
        # Show completion popup
        self.after(0, lambda: self.show_completion_popup(success_count, total, error))

    def _log_result(self, res):
        marker = '[OK]' if res.returncode == 0 else '[ERROR]'
        self.status.insert('end', f"{marker} {res.name} ({res.id})\n")
        self.status.insert('end', f"Inicio: {res.start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.status.insert('end', f"Duración: {res.duration:.1f}s\n")
        if res.stderr and res.returncode != 0:
            self.status.insert('end', res.stderr.strip() + '\n')
        self.status.insert('end', '─────────────────────\n')
        self.status.see('end')
    
    def show_completion_popup(self, success_count, total, has_errors):
        """Show a completion notification popup"""
        if has_errors:
            title = "Instalación Completada con Errores"
            message = f"Se instalaron {success_count} de {total} aplicaciones correctamente.\n\nRevisar el log para más detalles sobre los errores."
            messagebox.showwarning(title, message)
        else:
            title = "Instalación Completada"
            message = f"Se instalaron exitosamente {success_count} aplicaciones."
            messagebox.showinfo(title, message)

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
