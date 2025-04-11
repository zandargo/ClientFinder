import os
import re
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from unidecode import unidecode

class ClientTab:
    def __init__(self, parent):
        self.parent = parent

        # Main frame with two columns
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Column (Clients)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0,5))

        # Directory Selection Dropdown
        self.dir_label = tk.Label(self.left_frame, text="Selecionar Diretório:")
        self.dir_label.pack(pady=(10, 0))

        # Predefined directories
        self.directories = {
            'Desenhos': r'\\192.168.1.252\Desenhos',
            'Laser': r'\\192.168.1.252\Engenharia 1\Laser\\'
        }

        # Directory Combobox
        self.selected_dir = tk.StringVar()
        self.dir_combo = ttk.Combobox(
            self.left_frame, 
            textvariable=self.selected_dir, 
            values=list(self.directories.keys()),
            state="readonly",
            width=50
        )
        self.dir_combo.pack(pady=5)
        self.dir_combo.set("Selecione um diretório")
        self.dir_combo.bind("<<ComboboxSelected>>", self.on_directory_select)

        # Filter input for clients
        self.filter_label = tk.Label(self.left_frame, text="Pesquisar:")
        self.filter_label.pack(pady=(10, 0))

        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(self.left_frame, textvariable=self.filter_var, width=50)
        self.filter_entry.pack(pady=5)
        self.filter_var.trace('w', self.update_client_list)

        # Client Listbox with Scrollbar
        self.client_label = tk.Label(self.left_frame, text="Clientes:")
        self.client_label.pack(pady=(10, 0))

        # Create a frame to hold listbox and scrollbar
        self.client_listbox_frame = tk.Frame(self.left_frame)
        self.client_listbox_frame.pack(pady=5, expand=True, fill=tk.BOTH)

        # Scrollbar
        self.client_scrollbar = tk.Scrollbar(self.client_listbox_frame)
        self.client_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox with scrollbar
        self.client_listbox = tk.Listbox(
            self.client_listbox_frame, 
            width=70, 
            height=20, 
            yscrollcommand=self.client_scrollbar.set
        )
        self.client_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Configure scrollbar
        self.client_scrollbar.config(command=self.client_listbox.yview)

        # Bind selection event
        self.client_listbox.bind('<<ListboxSelect>>', self.on_client_select)

        # Right Column (Drawing Directories)
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(5,0))

        # Drawing Directories Label
        self.drawing_label = tk.Label(self.right_frame, text="Últimos Desenhos:")
        self.drawing_label.pack(pady=(10, 0))

        # Drawing Directories Listbox
        self.drawing_listbox = tk.Listbox(self.right_frame, width=70, height=20)
        self.drawing_listbox.pack(pady=5, expand=True, fill=tk.BOTH)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.right_frame)
        self.buttons_frame.pack(fill=tk.X, pady=5)

        self.open_folder_btn = tk.Button(
            self.buttons_frame, 
            text="Abrir Último Desenho", 
            command=self.open_last_drawing,
            state=tk.DISABLED
        )
        self.open_folder_btn.pack(side=tk.RIGHT)
    
    def on_directory_select(self, event=None):
        """Handle directory selection and load all clients"""
        selected_dir_name = self.selected_dir.get()
        if selected_dir_name in self.directories:
            # Clear the search filter when changing directories
            self.filter_var.set("")
            # Update client list with empty filter to show all
            self.update_client_list()
    
    def update_client_list(self, *args):
        """Update the client list based on the filter text"""
        search_text = self.filter_var.get().lower()
        
        # Get the selected directory
        selected_dir_name = self.selected_dir.get()
        if selected_dir_name not in self.directories:
            return
            
        selected_dir_path = self.directories[selected_dir_name]
        
        # Clear current list
        self.client_listbox.delete(0, tk.END)
        
        try:
            if os.path.exists(selected_dir_path):
                client_dirs = [d for d in os.listdir(selected_dir_path) 
                              if os.path.isdir(os.path.join(selected_dir_path, d))
                              and search_text in unidecode(d.lower())]
                
                for client in sorted(client_dirs):
                    self.client_listbox.insert(tk.END, client)
            else:
                messagebox.showwarning("Caminho Não Encontrado", f"O caminho {selected_dir_path} não existe.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar o diretório: {str(e)}")
    
    def on_client_select(self, event):
        """Handle client selection from the listbox"""
        selection = self.client_listbox.curselection()
        if not selection:
            return
            
        client = self.client_listbox.get(selection[0])
        selected_dir_name = self.selected_dir.get()
        selected_dir_path = self.directories[selected_dir_name]
        
        # Full path to client directory
        client_path = os.path.join(selected_dir_path, client)
        
        # Display client directory in drawing listbox
        self.populate_drawing_listbox(client_path)
    
    def populate_drawing_listbox(self, client_path):
        """Populate the drawing listbox with the latest files/folders"""
        self.drawing_listbox.delete(0, tk.END)
        
        try:
            # Get all subdirectories
            subdirs = [d for d in os.listdir(client_path) 
                      if os.path.isdir(os.path.join(client_path, d))]
            
            # Sort by modification time (newest first)
            subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(client_path, x)), 
                        reverse=True)
            
            # Add to listbox
            for subdir in subdirs[:10]:  # Show top 10 recent dirs
                self.drawing_listbox.insert(tk.END, subdir)
                
            if subdirs:
                self.open_folder_btn.config(state=tk.NORMAL)
            else:
                self.open_folder_btn.config(state=tk.DISABLED)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o diretório do cliente: {str(e)}")
    
    def open_last_drawing(self):
        """Open the selected drawing directory"""
        selection = self.drawing_listbox.curselection()
        if not selection:
            messagebox.showinfo("Seleção", "Por favor, selecione um diretório de desenho primeiro.")
            return
            
        drawing = self.drawing_listbox.get(selection[0])
        client = self.client_listbox.get(self.client_listbox.curselection()[0])
        selected_dir_name = self.selected_dir.get()
        selected_dir_path = self.directories[selected_dir_name]
        
        # Full path to drawing directory
        drawing_path = os.path.join(selected_dir_path, client, drawing)
        
        try:
            if os.path.exists(drawing_path):
                if sys.platform == 'win32':
                    subprocess.run(['explorer', drawing_path])
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', drawing_path])
                else:  # Linux
                    subprocess.run(['xdg-open', drawing_path])
            else:
                messagebox.showwarning("Caminho Não Encontrado", f"O caminho {drawing_path} não existe.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o diretório: {str(e)}")
