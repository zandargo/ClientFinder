import os
import re
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from unidecode import unidecode  # Added import for accent removal

class ClientFolderFinder:
    def __init__(self, master):
        self.master = master
        master.title("Client Folder Finder")
        master.geometry("1000x600")

        # Main frame with two columns
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Column (Clients)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0,5))

        # Directory Selection Dropdown
        self.dir_label = tk.Label(self.left_frame, text="Select Directory:")
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
        self.dir_combo.set("Select a directory")

        # Filter input for clients
        self.filter_label = tk.Label(self.left_frame, text="Search:")
        self.filter_label.pack(pady=(10, 0))

        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(self.left_frame, textvariable=self.filter_var, width=50)
        self.filter_entry.pack(pady=5)
        self.filter_var.trace('w', self.update_client_list)

        # Client Listbox with Scrollbar
        self.client_label = tk.Label(self.left_frame, text="Clients:")
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
        self.drawing_label = tk.Label(self.right_frame, text="Last Drawing Directories:")
        self.drawing_label.pack(pady=(10, 0))

        # Drawing Directories Listbox
        self.drawing_listbox = tk.Listbox(self.right_frame, width=70, height=20)
        self.drawing_listbox.pack(pady=5, expand=True, fill=tk.BOTH)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.right_frame)
        self.buttons_frame.pack(fill=tk.X, pady=5)

        self.open_folder_btn = tk.Button(
            self.buttons_frame, 
            text="Open Last Drawing", 
            command=self.open_last_drawing,
            state=tk.DISABLED
        )
        self.open_folder_btn.pack(side=tk.LEFT, expand=True, padx=2)

        self.create_drawing_btn = tk.Button(
            self.buttons_frame, 
            text="Create New Drawing", 
            command=self.create_new_drawing,
            state=tk.DISABLED
        )
        self.create_drawing_btn.pack(side=tk.RIGHT, expand=True, padx=2)

        # Bind events
        self.dir_combo.bind('<<ComboboxSelected>>', self.on_directory_selected)

        # Initialize variables
        self.client_folders = []
        self.filtered_clients = []
        self.current_selected_client = None
        self.current_last_drawing = None

    def on_directory_selected(self, event):
        """Clear previous results when a new directory is selected"""
        self.client_listbox.delete(0, tk.END)
        self.drawing_listbox.delete(0, tk.END)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.create_drawing_btn.config(state=tk.DISABLED)
        self.find_client_folders()

    def find_client_folders(self):
        """Find and list folders matching the client folder pattern"""
        # Check if a directory is selected
        selected_key = self.selected_dir.get()
        if selected_key not in self.directories:
            messagebox.showerror("Error", "Please select a directory first")
            return

        # Get the full directory path
        directory = self.directories[selected_key]

        # Clear previous list
        self.client_listbox.delete(0, tk.END)

        try:
            # List all folders in the directory
            folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
            
            # Filter and store matching folders based on directory type
            self.client_folders = []
            if selected_key == 'Desenhos':
                # Pattern for Desenhos: xxx - client name or xxx-client name
                pattern = re.compile(r'^(\d{3})\s*-\s*(.+)$')
                for folder in folders:
                    match = pattern.match(folder)
                    if match:
                        code, client_name = match.groups()
                        self.client_folders.append({
                            'full_name': folder,
                            'code': code,
                            'client_name': client_name,
                            'path': os.path.join(directory, folder)
                        })
            else:  # Laser directory
                # For Laser, use the folder name as client name directly
                for folder in folders:
                    self.client_folders.append({
                        'full_name': folder,
                        'code': '',  # No code for Laser directory
                        'client_name': folder,
                        'path': os.path.join(directory, folder)
                    })
            
            # Initial population of client listbox
            self.update_client_list()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_client_list(self, *args):
        """Update client listbox based on filter, ignoring accents"""
        # Normalize the filter text by removing accents and converting to lowercase
        filter_text = unidecode(self.filter_var.get().lower())
        
        # Clear previous list
        self.client_listbox.delete(0, tk.END)
        
        # Populate listbox with filtered results
        self.filtered_clients = []
        for folder in self.client_folders:
            # Normalize client name attributes for comparison
            normalized_name = unidecode(folder['client_name'].lower())
            normalized_code = unidecode(folder['code'].lower())
            normalized_full_name = unidecode(folder['full_name'].lower())
            
            # Check if the normalized filter text matches any of the normalized attributes
            if (filter_text in normalized_name or 
                filter_text in normalized_code or 
                filter_text in normalized_full_name):
                self.client_listbox.insert(tk.END, folder['full_name'])
                self.filtered_clients.append(folder)

    def on_client_select(self, event):
        """Find and display drawing directories when a client is selected"""
        # Clear previous drawing directories
        self.drawing_listbox.delete(0, tk.END)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.create_drawing_btn.config(state=tk.DISABLED)

        # Reset current selections
        self.current_selected_client = None
        self.current_last_drawing = None

        # Check if a client is selected
        if not self.client_listbox.curselection():
            return

        # Get the selected client
        selected_index = self.client_listbox.curselection()[0]
        self.current_selected_client = self.filtered_clients[selected_index]

        # Pattern to match drawing directories (xxx-xxxx)
        drawing_pattern = re.compile(r'^\d{3}-\d{4}$')
        drawing_dirs = []

        try:
            # List all subdirectories in the client folder
            for item in os.listdir(self.current_selected_client['path']):
                item_path = os.path.join(self.current_selected_client['path'], item)
                if os.path.isdir(item_path) and drawing_pattern.match(item):
                    drawing_dirs.append(item)

            # Sort drawing directories to find the last one
            if drawing_dirs:
                # Improved sorting to handle multi-digit drawing numbers correctly
                sorted_drawing_dirs = sorted(drawing_dirs, 
                    key=lambda x: tuple(map(int, x.split('-'))), 
                    reverse=False
                )
                last_drawing_dir = sorted_drawing_dirs[-1]
                last_drawing_path = os.path.join(self.current_selected_client['path'], last_drawing_dir)
                
                # Check for Rev-xx subfolders
                rev_folders = [f for f in os.listdir(last_drawing_path) 
                               if os.path.isdir(os.path.join(last_drawing_path, f)) 
                               and re.match(r'^Rev-\d{2}$', f)]
                
                # Store current last drawing info
                self.current_last_drawing = last_drawing_dir

                # Display the last drawing directory
                self.drawing_listbox.insert(tk.END, f"Last Drawing Directory: {last_drawing_dir}")
                self.drawing_listbox.insert(tk.END, f"Full Path: {last_drawing_path}")
                
                # Display Rev folders if exist
                if rev_folders:
                    self.drawing_listbox.insert(tk.END, "Revision Folders:")
                    for rev in sorted(rev_folders):
                        self.drawing_listbox.insert(tk.END, f"- {rev}")

                # Enable buttons
                self.open_folder_btn.config(state=tk.NORMAL)
                self.create_drawing_btn.config(state=tk.NORMAL)
            else:
                self.drawing_listbox.insert(tk.END, "No drawing directories found.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def open_last_drawing(self):
        """Open the last drawing folder, prioritizing the highest Rev-xx subfolder"""
        if not self.current_last_drawing:
            messagebox.showerror("Error", "No drawing selected")
            return

        full_path = os.path.join(self.current_selected_client['path'], self.current_last_drawing)
        
        try:
            # Check for Rev-xx subfolders
            rev_folders = [f for f in os.listdir(full_path) 
                           if os.path.isdir(os.path.join(full_path, f)) 
                           and re.match(r'^Rev-\d{2}$', f)]
            
            # If Rev folders exist, find and open the highest numbered one
            if rev_folders:
                # Sort Rev folders numerically
                sorted_rev_folders = sorted(rev_folders, 
                    key=lambda x: int(x.split('-')[1]), 
                    reverse=True
                )
                highest_rev_folder = sorted_rev_folders[0]
                path_to_open = os.path.join(full_path, highest_rev_folder)
            else:
                # If no Rev folders, open the main drawing directory
                path_to_open = full_path

            # Cross-platform method to open folder
            if os.name == 'nt':  # Windows
                os.startfile(path_to_open)
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.Popen(['open', path_to_open])
                else:  # Linux
                    subprocess.Popen(['xdg-open', path_to_open])
            else:
                messagebox.showerror("Error", "Unsupported operating system")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def create_new_drawing(self):
        """Create a new drawing directory and Rev-00 subfolder"""
        if not self.current_selected_client:
            messagebox.showerror("Error", "No client selected")
            return

        try:
            # Find the next drawing number
            drawing_pattern = re.compile(r'^\d{3}-\d{4}$')
            existing_drawings = [
                f for f in os.listdir(self.current_selected_client['path']) 
                if os.path.isdir(os.path.join(self.current_selected_client['path'], f)) 
                and drawing_pattern.match(f)
            ]

            # Sort and get the last drawing number
            if existing_drawings:
                sorted_drawings = sorted(existing_drawings, 
                    key=lambda x: tuple(map(int, x.split('-'))), 
                    reverse=True
                )
                last_drawing = sorted_drawings[0]
                last_number = int(last_drawing.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1

            # Create new drawing directory
            new_drawing_name = f"{self.current_selected_client['code'] or '000'}-{new_number:04d}"
            new_drawing_path = os.path.join(self.current_selected_client['path'], new_drawing_name)
            
            # Create the directory
            os.makedirs(new_drawing_path, exist_ok=True)

            # For Desenhos, create Rev-00 subfolder
            if self.selected_dir.get() == 'Desenhos':
                rev_path = os.path.join(new_drawing_path, 'Rev-00')
                os.makedirs(rev_path, exist_ok=True)

            # Refresh the view
            self.on_client_select(None)

            # Open the Rev-00 folder for Desenhos, otherwise open the new drawing directory
            path_to_open = rev_path if self.selected_dir.get() == 'Desenhos' else new_drawing_path
            if os.name == 'nt':  # Windows
                os.startfile(path_to_open)
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.Popen(['open', path_to_open])
                else:  # Linux
                    subprocess.Popen(['xdg-open', path_to_open])

        except Exception as e:
            messagebox.showerror("Error", f"Could not create new drawing: {str(e)}")

def main():
    root = tk.Tk()
    app = ClientFolderFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
