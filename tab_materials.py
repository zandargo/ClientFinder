# filepath: c:\Users\madson.unias\Desktop\ClientFinder\tab_materials.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess

class MaterialsTab:
    def __init__(self, parent):
        self.parent = parent
        
        # Main frame
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Materials heading
        self.heading_label = tk.Label(
            self.main_frame, 
            text="Materials Management", 
            font=("Arial", 14, "bold")
        )
        self.heading_label.pack(pady=(0, 10))
        
        # Materials directory
        self.materials_dir = r'\\192.168.1.252\Engenharia 1\Chapas'
        
        # Create a frame for the left side (materials list)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Material type selection
        self.material_type_frame = tk.Frame(self.left_frame)
        self.material_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.material_type_label = tk.Label(self.material_type_frame, text="Material Type:")
        self.material_type_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.material_types = ["Aço Carbono", "Aço Inox", "Alumínio", "Outros"]
        self.material_type_var = tk.StringVar()
        
        self.material_type_combo = ttk.Combobox(
            self.material_type_frame,
            textvariable=self.material_type_var,
            values=self.material_types,
            state="readonly",
            width=20
        )
        self.material_type_combo.pack(side=tk.LEFT)
        self.material_type_combo.bind('<<ComboboxSelected>>', self.on_material_type_selected)
        
        # Search field
        self.search_frame = tk.Frame(self.left_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace('w', self.filter_materials)
        
        # Materials listbox with scrollbar
        self.materials_label = tk.Label(self.left_frame, text="Materials:")
        self.materials_label.pack(anchor=tk.W)
        
        self.materials_frame = tk.Frame(self.left_frame)
        self.materials_frame.pack(fill=tk.BOTH, expand=True)
        
        self.materials_scrollbar = tk.Scrollbar(self.materials_frame)
        self.materials_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.materials_listbox = tk.Listbox(
            self.materials_frame,
            yscrollcommand=self.materials_scrollbar.set
        )
        self.materials_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.materials_scrollbar.config(command=self.materials_listbox.yview)
        self.materials_listbox.bind('<<ListboxSelect>>', self.on_material_selected)
        
        # Create a frame for the right side (material details)
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Material details
        self.details_label = tk.Label(self.right_frame, text="Material Details:", font=("Arial", 11, "bold"))
        self.details_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Details frame with grid layout
        self.details_frame = tk.Frame(self.right_frame)
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create labels for material details
        self.detail_labels = {}
        self.detail_values = {}
        
        details = [
            ("Name", "name"),
            ("Thickness", "thickness"),
            ("Width", "width"),
            ("Length", "length"),
            ("Material", "material"),
            ("Quantity", "quantity"),
            ("Location", "location"),
            ("Last Updated", "updated")
        ]
        
        for i, (label_text, key) in enumerate(details):
            self.detail_labels[key] = tk.Label(self.details_frame, text=f"{label_text}:", anchor=tk.W)
            self.detail_labels[key].grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            self.detail_values[key] = tk.Label(self.details_frame, text="", anchor=tk.W)
            self.detail_values[key].grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # Actions frame
        self.actions_frame = tk.Frame(self.right_frame)
        self.actions_frame.pack(fill=tk.X, pady=10)
        
        self.open_folder_btn = tk.Button(
            self.actions_frame,
            text="Open Folder",
            command=self.open_material_folder,
            state=tk.DISABLED
        )
        self.open_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_material_btn = tk.Button(
            self.actions_frame,
            text="Add New Material",
            command=self.add_new_material
        )
        self.add_material_btn.pack(side=tk.LEFT)
        
        # Initialize materials data
        self.materials = []
        self.filtered_materials = []
        self.current_material = None
        
    def on_material_type_selected(self, event):
        """Load materials when a material type is selected"""
        self.load_materials()
        
    def load_materials(self):
        """Load materials for the selected type"""
        selected_type = self.material_type_var.get()
        if not selected_type:
            return
            
        # This would typically load from a database or file system
        # For now, we'll use dummy data
        self.materials = self.get_dummy_materials(selected_type)
        self.filter_materials()
        
    def get_dummy_materials(self, material_type):
        """Return dummy materials data for demonstration"""
        if material_type == "Aço Carbono":
            return [
                {"name": "Chapa AC 1.0mm", "thickness": "1.0mm", "width": "1000mm", "length": "2000mm", 
                 "material": "Aço Carbono", "quantity": "5", "location": "Estante A-1", "updated": "2025-03-15"},
                {"name": "Chapa AC 1.5mm", "thickness": "1.5mm", "width": "1200mm", "length": "2400mm", 
                 "material": "Aço Carbono", "quantity": "3", "location": "Estante A-2", "updated": "2025-03-20"},
                {"name": "Chapa AC 2.0mm", "thickness": "2.0mm", "width": "1500mm", "length": "3000mm", 
                 "material": "Aço Carbono", "quantity": "2", "location": "Estante B-1", "updated": "2025-04-01"}
            ]
        elif material_type == "Aço Inox":
            return [
                {"name": "Chapa Inox 304 1.0mm", "thickness": "1.0mm", "width": "1000mm", "length": "2000mm", 
                 "material": "Aço Inox 304", "quantity": "4", "location": "Estante C-1", "updated": "2025-03-25"},
                {"name": "Chapa Inox 316 1.5mm", "thickness": "1.5mm", "width": "1200mm", "length": "2400mm", 
                 "material": "Aço Inox 316", "quantity": "2", "location": "Estante C-2", "updated": "2025-04-05"}
            ]
        elif material_type == "Alumínio":
            return [
                {"name": "Chapa Alumínio 1.0mm", "thickness": "1.0mm", "width": "1000mm", "length": "2000mm", 
                 "material": "Alumínio 1100", "quantity": "6", "location": "Estante D-1", "updated": "2025-03-10"},
                {"name": "Chapa Alumínio 2.0mm", "thickness": "2.0mm", "width": "1200mm", "length": "2400mm", 
                 "material": "Alumínio 6061", "quantity": "3", "location": "Estante D-2", "updated": "2025-04-02"}
            ]
        else:  # Outros
            return [
                {"name": "Chapa Latão 1.0mm", "thickness": "1.0mm", "width": "600mm", "length": "1200mm", 
                 "material": "Latão", "quantity": "2", "location": "Estante E-1", "updated": "2025-03-28"},
                {"name": "Chapa Cobre 0.5mm", "thickness": "0.5mm", "width": "500mm", "length": "1000mm", 
                 "material": "Cobre", "quantity": "1", "location": "Estante E-2", "updated": "2025-04-03"}
            ]
        
    def filter_materials(self, *args):
        """Filter materials based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear current list
        self.materials_listbox.delete(0, tk.END)
        
        # Filter and display materials
        self.filtered_materials = []
        for material in self.materials:
            if search_text in material["name"].lower():
                self.materials_listbox.insert(tk.END, material["name"])
                self.filtered_materials.append(material)
        
        # Clear details when filter changes
        self.clear_details()
        
    def on_material_selected(self, event):
        """Handle material selection"""
        selection = self.materials_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        self.current_material = self.filtered_materials[index]
        self.display_material_details(self.current_material)
        self.open_folder_btn.config(state=tk.NORMAL)
        
    def display_material_details(self, material):
        """Display the details of the selected material"""
        for key, value in material.items():
            if key in self.detail_values:
                self.detail_values[key].config(text=value)
                
    def clear_details(self):
        """Clear all detail fields"""
        for value_label in self.detail_values.values():
            value_label.config(text="")
        self.open_folder_btn.config(state=tk.DISABLED)
        self.current_material = None
        
    def open_material_folder(self):
        """Open the folder containing the material files"""
        if not self.current_material:
            return
            
        material_name = self.current_material["name"]
        material_type = self.material_type_var.get()
        
        # In a real application, you'd determine the actual folder path
        folder_path = os.path.join(self.materials_dir, material_type, material_name)
        
        # For demonstration, we'll just show a message
        messagebox.showinfo("Open Folder", f"Opening folder: {folder_path}")
        
        # Uncomment to actually open the folder if it exists
        # if os.path.exists(folder_path):
        #     if sys.platform == 'win32':
        #         subprocess.run(['explorer', folder_path])
        #     elif sys.platform == 'darwin':  # macOS
        #         subprocess.run(['open', folder_path])
        #     else:  # Linux
        #         subprocess.run(['xdg-open', folder_path])
        # else:
        #     messagebox.showwarning("Not Found", f"Folder not found: {folder_path}")
        
    def add_new_material(self):
        """Add a new material (placeholder for future implementation)"""
        messagebox.showinfo("Add Material", "This feature will be implemented in a future version.")
