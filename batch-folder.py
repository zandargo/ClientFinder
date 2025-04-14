#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Batch Folder Creator

This script creates a batch of folders with a specific naming convention.
The folders are named in the format 'nnn-xxxx' where 'nnn' is the client number
and 'xxxx' is a sequence number from the initial folder to the final folder.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


def create_batch_folders():
    """
    Main function to create batch folders and subfolders.
    """
    # Create a root window and immediately hide it
    root = tk.Tk()
    root.withdraw()
    
    print("Batch Folder Creator")
    print("====================")

    # Step 1: Prompt for the location where folders will be created using a dialog
    print("Please select a folder where the batch folders will be created...")
    location = filedialog.askdirectory(title="Select folder location for batch creation")
    
    if not location:
        print("Error: No folder selected. Operation cancelled.")
        return

    # Verify the location exists (already done by the dialog, but double-check)
    if not os.path.exists(location):
        create_dir = messagebox.askyesno("Folder Not Found", 
                                         f"The location '{location}' does not exist. Create it?")
        if create_dir:
            try:
                os.makedirs(location, exist_ok=True)
                print(f"Created directory: {location}")
            except Exception as e:
                messagebox.showerror("Error", f"Error creating location: {e}")
                print(f"Error creating location: {e}")
                return
        else:
            print("Operation cancelled.")
            return    # Step 2: Prompt for the three required values using dialog boxes
    client_number = simpledialog.askstring("Client Number", "Enter client number (e.g., 123):", parent=root)
    
    if not client_number:
        print("Error: Operation cancelled.")
        return
        
    if not client_number.isdigit():
        messagebox.showerror("Invalid Input", "Client number must contain only digits.")
        print("Error: Client number must contain only digits.")
        return

    try:
        initial_folder = simpledialog.askinteger("Initial Folder", "Enter initial folder number:", parent=root)
        if initial_folder is None:
            print("Error: Operation cancelled.")
            return
            
        final_folder = simpledialog.askinteger("Final Folder", "Enter final folder number:", parent=root)
        if final_folder is None:
            print("Error: Operation cancelled.")
            return
        
        if final_folder < initial_folder:
            messagebox.showerror("Invalid Input", 
                               "Final folder number must be greater than or equal to initial folder number.")
            print("Error: Final folder number must be greater than or equal to initial folder number.")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")
        print(f"Error: {e}")
        return
        
    # Ask if user wants to create Rev-00 subfolders
    create_rev_subfolders = messagebox.askyesno("Rev-00 Subfolders", 
                                               "Do you want to create 'Rev-00' subfolders?", 
                                               parent=root)
    
    # Step 3: Create the folders
    print("\nCreating folders...")
    folders_created = 0
    created_folder_paths = []
    
    # Prepare progress information
    total_folders = final_folder - initial_folder + 1
    
    for folder_num in range(initial_folder, final_folder + 1):
        folder_name = f"{client_number}-{folder_num:04d}"
        folder_path = os.path.join(location, folder_name)
        
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")
            
            # Only create Rev-00 subfolder if user selected yes
            if create_rev_subfolders:
                rev_folder_path = os.path.join(folder_path, "Rev-00")
                os.makedirs(rev_folder_path, exist_ok=True)
                print(f"Created subfolder: {rev_folder_path}")
            
            created_folder_paths.append(folder_path)
            folders_created += 1
        except Exception as e:
            print(f"Error creating folder {folder_name}: {e}")
            messagebox.showerror("Error", f"Error creating folder {folder_name}: {e}")
    
    # Show completion message
    if create_rev_subfolders:
        message = f"Process complete. Created {folders_created} folders with 'Rev-00' subfolders."
    else:
        message = f"Process complete. Created {folders_created} folders."
    print(f"\n{message}")
    messagebox.showinfo("Batch Folder Creation Complete", message)
    
    # Display list of created folders in the console
    print("\nList of created folders:")
    print("-----------------------")
    for i, folder in enumerate(created_folder_paths, 1):
        print(f"{i}. {folder}")
    
    # Ask user to press Enter to exit
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    create_batch_folders()
