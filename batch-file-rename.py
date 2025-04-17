import os
import re
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox

def select_folder():
    """
    Opens a dialog for the user to select a folder.
    Returns the selected folder path or None if canceled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Rename")
    return folder_path if folder_path else None

def get_current_revision():
    """
    Opens a dialog for the user to input the current revision number.
    Returns the revision as a string or None if canceled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    revision = simpledialog.askinteger("Input", "Enter the current revision number:", 
                                      minvalue=0, maxvalue=99)
    
    if revision is not None:
        # Format revision as a two-digit string (e.g., 0 -> '00', 9 -> '09')
        return f"{revision:02d}"
    return None

def find_and_rename_files(folder_path, current_revision):
    """
    Finds files containing "-xx" in their filename where xx is the current revision,
    and renames them by incrementing the revision.
    Returns a list of tuples containing the old and new filenames.
    """
    renamed_files = []
    next_revision = f"{int(current_revision) + 1:02d}"
    pattern = re.compile(f"-{current_revision}")
    
    for filename in os.listdir(folder_path):
        # Check if the file contains the current revision pattern
        if pattern.search(filename):
            # Create the new filename by replacing the revision
            new_filename = pattern.sub(f"-{next_revision}", filename)
            
            # Full paths for renaming
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Rename the file
            os.rename(old_path, new_path)
            
            # Add to the list of renamed files
            renamed_files.append((filename, new_filename))
    
    return renamed_files

def display_results(renamed_files):
    """
    Displays the list of renamed files in the console prompt.
    Asks the user to hit Enter to exit.
    """
    if not renamed_files:
        print("No files were found that matched the revision pattern.")
    else:
        print("The following files were renamed:")
        print("=" * 50)
        for old_name, new_name in renamed_files:
            print(f"Original: {old_name}")
            print(f"New:      {new_name}")
            print("-" * 50)
        print(f"Total files renamed: {len(renamed_files)}")
    
    input("\nPress Enter to exit...")

def main():
    # Step 1: Prompt user to select a folder
    folder_path = select_folder()
    if not folder_path:
        return
    
    # Step 2: Prompt user to input the current revision
    current_revision = get_current_revision()
    if not current_revision:
        return
    
    # Steps 3-4: Find and rename files
    renamed_files = find_and_rename_files(folder_path, current_revision)
    
    # Step 5: Display the list of renamed files
    display_results(renamed_files)

if __name__ == "__main__":
    main()
