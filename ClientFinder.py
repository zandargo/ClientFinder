import tkinter as tk
from tkinter import ttk
import sys
from tab_client import ClientTab
from tab_materials import MaterialsTab

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Engineering Tools")
        self.root.geometry("1000x600")

        # Create the tab control
        self.tabControl = ttk.Notebook(root)
        
        # Create tabs
        self.client_tab = tk.Frame(self.tabControl)
        self.materials_tab = tk.Frame(self.tabControl)
        
        # Add the tabs to the notebook with their names
        self.tabControl.add(self.client_tab, text='Clientes')
        self.tabControl.add(self.materials_tab, text='Chapas')
        
        # Pack the tab control to make it visible
        self.tabControl.pack(expand=1, fill="both")
        
        # Initialize the content of each tab
        ClientTab(self.client_tab)
        MaterialsTab(self.materials_tab)

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
