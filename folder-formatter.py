import os
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def is_date_format(folder_name, pattern):
    """
    Check if the folder name matches the date pattern.
    """
    return bool(re.match(pattern, folder_name))

def convert_date_format(folder_name, from_pattern, to_format, with_suffix=False):
    """
    Convert folder name from dd-mm-yyyy format (with potential suffixes) to yyyy-mm-dd format.
    
    Examples of conversions:
    - '16-03-2023-01' to '2023-03-16 001'
    - '21-10-2024_3' to '2024-10-21 003'
    - '29-08-2023 2' to '2023-08-29 002'
    """
    try:
        # Parse the date using the provided pattern
        match = re.match(from_pattern, folder_name)
        if match:
            groups = match.groups()
            
            if with_suffix:
                day, month, year, suffix = groups
                # Convert suffix to 3-digit format
                suffix = suffix.strip()
                suffix_int = int(suffix)
                formatted_suffix = f" {suffix_int:03d}"
                
                # Validate the date
                date_obj = datetime(int(year), int(month), int(day))
                
                # Format to the target format with suffix
                return date_obj.strftime(to_format) + formatted_suffix
            else:
                day, month, year = groups
                
                # Validate the date
                date_obj = datetime(int(year), int(month), int(day))
                
                # Format to the target format
                return date_obj.strftime(to_format)
        return None
    except ValueError:
        # If the date is invalid (e.g., 31-02-2023)
        return None

def rename_date_folders(start_dir):
    """
    Recursively search for folders with dd-mm-yyyy pattern (and variations with suffixes) 
    and rename them to the appropriate format.
    """
    # Regular expression patterns
    # Standard pattern: dd-mm-yyyy
    standard_pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    
    # Patterns with suffixes:
    # dd-mm-yyyy-nn (hyphen separator)
    hyphen_suffix_pattern = r'^(\d{2})-(\d{2})-(\d{4})-(\d+)$'
    
    # dd-mm-yyyy_nn (underscore separator)
    underscore_suffix_pattern = r'^(\d{2})-(\d{2})-(\d{4})_(\d+)$'
    
    # dd-mm-yyyy nn (space separator)
    space_suffix_pattern = r'^(\d{2})-(\d{2})-(\d{4}) (\d+)$'
    
    to_format = '%Y-%m-%d'  # yyyy-mm-dd
    
    renamed_count = 0
    errors = []
    
    for root, dirs, _ in os.walk(start_dir):
        for dir_name in dirs:
            # Check for standard date format
            if is_date_format(dir_name, standard_pattern):
                new_name = convert_date_format(dir_name, standard_pattern, to_format, with_suffix=False)
            
            # Check for date format with hyphen suffix
            elif is_date_format(dir_name, hyphen_suffix_pattern):
                new_name = convert_date_format(dir_name, hyphen_suffix_pattern, to_format, with_suffix=True)
                
            # Check for date format with underscore suffix
            elif is_date_format(dir_name, underscore_suffix_pattern):
                new_name = convert_date_format(dir_name, underscore_suffix_pattern, to_format, with_suffix=True)
                
            # Check for date format with space suffix
            elif is_date_format(dir_name, space_suffix_pattern):
                new_name = convert_date_format(dir_name, space_suffix_pattern, to_format, with_suffix=True)
                
            else:
                # Not a matching pattern
                continue
                
            if new_name:
                old_path = os.path.join(root, dir_name)
                new_path = os.path.join(root, new_name)
                
                try:
                    # Check if destination already exists
                    if os.path.exists(new_path):
                        errors.append(f"Cannot rename {old_path} to {new_path}: Destination already exists")
                        continue
                        
                    os.rename(old_path, new_path)
                    renamed_count += 1
                    print(f"Renamed: {dir_name} -> {new_name}")
                except Exception as e:
                    errors.append(f"Error renaming {dir_name}: {str(e)}")
    
    return renamed_count, errors

def select_folder():
    """
    Open a dialog for the user to select a folder.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(
        title="Select the folder where you want to start the search"
    )
    
    return folder_path

def main():
    print("Folder Date Format Converter")
    print("This script will convert folders named dd-mm-yyyy to yyyy-mm-dd format")
    print("-" * 60)
    
    # Ask user to select a folder
    start_dir = select_folder()
    
    if not start_dir:
        print("No folder selected. Exiting.")
        return
    
    print(f"Starting search in: {start_dir}")
    print("Searching for folders with the pattern dd-mm-yyyy...")
    
    renamed_count, errors = rename_date_folders(start_dir)
    
    print("-" * 60)
    print(f"Process completed. {renamed_count} folders were renamed.")
    
    if errors:
        print(f"\nThe following errors occurred ({len(errors)}):")
        for error in errors:
            print(f"- {error}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
