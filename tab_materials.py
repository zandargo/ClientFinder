import tkinter as tk

class MaterialsTab:
    def __init__(self, parent):
        self.parent = parent
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # The tab is intentionally left empty for now.
