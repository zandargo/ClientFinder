#!/usr/bin/env python3
# Remote Input Test Launcher
# This script provides a simple GUI to launch different remote input test scripts

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class RemoteInputTestLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Input Test Launcher")
        self.root.geometry("500x420")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.running_process = None
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="AnyDesk-like Remote Input Simulation", 
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Description
        desc_text = (
            "This tool simulates remote input similar to what AnyDesk would send.\n"
            "Use it to test how your keylogger responds to various input events."
        )
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=450)
        desc_label.pack(pady=(0, 15))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Test Options")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Test type selection
        ttk.Label(options_frame, text="Test Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.test_type_var = tk.StringVar(value="standard")
        test_types = [
            ("Standard Test (Python Input)", "standard"),
            ("Advanced Test (Windows API)", "advanced"),
            ("Keylogger Verification", "verify")
        ]
        
        for i, (text, value) in enumerate(test_types):
            ttk.Radiobutton(
                options_frame,
                text=text,
                value=value,
                variable=self.test_type_var
            ).grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Input mode selection
        ttk.Label(options_frame, text="Input Mode:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_mode_var = tk.StringVar(value="all")
        input_modes = [
            ("All (Mouse & Keyboard)", "all"),
            ("Mouse Only", "mouse"),
            ("Keyboard Only", "keyboard")
        ]
        
        for i, (text, value) in enumerate(input_modes):
            ttk.Radiobutton(
                options_frame,
                text=text,
                value=value,
                variable=self.input_mode_var
            ).grid(row=i+3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Duration selection
        ttk.Label(options_frame, text="Duration:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        duration_frame = ttk.Frame(options_frame)
        duration_frame.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.duration_var = tk.IntVar(value=15)
        self.duration_scale = ttk.Scale(
            duration_frame, 
            from_=5, 
            to=60, 
            variable=self.duration_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.duration_scale.pack(side=tk.LEFT)
        
        self.duration_label = ttk.Label(duration_frame, text="15 seconds")
        self.duration_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update duration label when scale changes
        self.duration_var.trace("w", self.update_duration_label)
        
        # Delay before start
        ttk.Label(options_frame, text="Start Delay:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        delay_frame = ttk.Frame(options_frame)
        delay_frame.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.delay_var = tk.IntVar(value=3)
        self.delay_scale = ttk.Scale(
            delay_frame, 
            from_=1, 
            to=10, 
            variable=self.delay_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.delay_scale.pack(side=tk.LEFT)
        
        self.delay_label = ttk.Label(delay_frame, text="3 seconds")
        self.delay_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update delay label when scale changes
        self.delay_var.trace("w", self.update_delay_label)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Start button
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Simulation", 
            command=self.start_test,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            foreground="green"
        )
        self.status_label.pack(pady=(10, 0))
    
    def update_duration_label(self, *args):
        self.duration_label.config(text=f"{self.duration_var.get()} seconds")
    
    def update_delay_label(self, *args):
        self.delay_label.config(text=f"{self.delay_var.get()} seconds")
    
    def start_test(self):
        test_type = self.test_type_var.get()
        input_mode = self.input_mode_var.get()
        duration = self.duration_var.get()
        delay = self.delay_var.get()
          # Disable the button while running
        self.start_button.state(["disabled"])
        self.status_var.set("Starting simulation...")
        self.status_label.config(foreground="blue")
        
        # Run the test in a separate thread
        threading.Thread(target=self.run_test, args=(test_type, input_mode, duration, delay)).start()
    
    def run_test(self, test_type, input_mode, duration, delay):
        try:
            # Get the current directory where the launcher script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            if test_type == "standard":
                script = os.path.join(current_dir, "remote_input_test.py")
                cmd = [sys.executable, script, "--mode", input_mode, "--duration", str(duration), "--delay", str(delay)]
            elif test_type == "advanced":
                script = os.path.join(current_dir, "anydesk_simulator.py")
                cmd = [sys.executable, script, "--mode", input_mode, "--duration", str(duration), "--delay", str(delay)]
            elif test_type == "verify":
                script = os.path.join(current_dir, "test_keylogger.py")
                cmd = [sys.executable, script, "--mode", input_mode, "--duration", str(duration)]
            else:
                self.show_error("Invalid test type selected")
                return
                
            self.running_process = subprocess.Popen(cmd)
            self.running_process.wait()
            
            # Update UI when finished
            self.root.after(0, self.on_test_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error running test: {str(e)}"))
        finally:
            self.running_process = None
    
    def on_test_completed(self):
        self.status_var.set("Simulation completed")
        self.status_label.config(foreground="green")
        self.start_button.state(["!disabled"])
    
    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
        self.status_label.config(foreground="red")
        self.start_button.state(["!disabled"])

def main():
    try:
        from tkinter import ttk
        style = ttk.Style()
        # Try to use a modern theme if available
        try:
            style.theme_use("clam")  # Try clam first for a more modern look
        except:
            try:
                style.theme_use("vista")  # Vista theme on Windows
            except:
                pass  # Use default theme if others are not available
    except:
        pass
    
    root = tk.Tk()
    app = RemoteInputTestLauncher(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (root.quit() if app.running_process is None 
                                             else messagebox.showinfo("Process Running", 
                                                                    "Please wait for the test to complete")))
    root.mainloop()

if __name__ == "__main__":
    main()
