#!/usr/bin/env python3
# Remote Input Simulator - Similar to AnyDesk's remote control functionality
# This script simulates keyboard typing and mouse movements/clicks

import time
import random
import argparse
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# Create controllers
keyboard = KeyboardController()
mouse = MouseController()

def get_screen_size():
    """Get screen size using user32.dll on Windows"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        return screen_width, screen_height
    except Exception:
        # Default fallback values if unable to get screen size
        return 1920, 1080

def simulate_mouse_movement(duration=5, smooth=True):
    """
    Simulate natural mouse movements across the screen
    
    Args:
        duration: How long to move the mouse (in seconds)
        smooth: If True, creates smoother motion with smaller steps
    """
    screen_width, screen_height = get_screen_size()
    start_time = time.time()
    
    # Get starting position
    start_x, start_y = mouse.position
    
    print(f"Simulating mouse movement for {duration} seconds")
    while time.time() - start_time < duration:
        # Generate random target position
        target_x = random.randint(10, screen_width - 10)
        target_y = random.randint(10, screen_height - 10)
        
        # Calculate distance and number of steps
        distance = ((target_x - mouse.position[0]) ** 2 + 
                    (target_y - mouse.position[1]) ** 2) ** 0.5
        
        # More steps for smoother movement
        steps = int(distance / (5 if smooth else 20)) + 1
        
        # Move in steps
        for step in range(1, steps + 1):
            # Calculate intermediate position with slight randomization for natural movement
            x = mouse.position[0] + (target_x - mouse.position[0]) * step / steps
            y = mouse.position[1] + (target_y - mouse.position[1]) * step / steps
            
            # Add small random jitter for more natural movement
            if smooth:
                x += random.uniform(-2, 2)
                y += random.uniform(-2, 2)
                
            mouse.position = (x, y)
            # Shorter sleep for smoother motion
            time.sleep(0.01 if smooth else 0.05)
        
        # Random pause between movements
        time.sleep(random.uniform(0.1, 0.3))

def simulate_mouse_clicks(num_clicks=5):
    """Simulate mouse clicks at current position"""
    print(f"Simulating {num_clicks} mouse clicks")
    for _ in range(num_clicks):
        # Randomly decide between left and right clicks
        button = Button.left if random.random() < 0.8 else Button.right
        
        # Click
        mouse.press(button)
        time.sleep(random.uniform(0.05, 0.15))  # Random duration press
        mouse.release(button)
        
        # Random pause between clicks
        time.sleep(random.uniform(0.3, 1.0))
        
        # Sometimes do a double-click
        if random.random() < 0.3:
            mouse.press(button)
            time.sleep(0.1)
            mouse.release(button)
            time.sleep(random.uniform(0.5, 1.0))

def simulate_typing(text=None):
    """
    Simulate keyboard typing with realistic timing
    
    Args:
        text: Specific text to type. If None, will type a sample text.
    """
    if text is None:
        text = "This is a remote input test simulating AnyDesk behavior.\nTesting keyboard input simulation with varying speeds.\nThe keylogger should capture all of these keystrokes!"
    
    print(f"Simulating typing: {text[:30]}...")
    
    for char in text:
        # Random delay between keystrokes (simulates varying typing speed)
        time.sleep(random.uniform(0.05, 0.2))
        
        if char == '\n':
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        else:
            # Type the character
            keyboard.press(char)
            keyboard.release(char)
            
    # Add a final enter
    time.sleep(0.5)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def simulate_special_keys():
    """Simulate various special key combinations"""
    print("Simulating special keys and key combinations")
    
    # List of special keys and combinations to test
    special_actions = [
        # Single special keys
        (Key.shift, None),
        (Key.ctrl, None),
        (Key.alt, None),
        (Key.tab, None),
        (Key.esc, None),
        (Key.backspace, None),
        (Key.delete, None),
        (Key.home, None),
        (Key.end, None),
        (Key.page_up, None),
        (Key.page_down, None),
        
        # Key combinations
        (Key.ctrl, 'c'),   # Ctrl+C
        (Key.ctrl, 'v'),   # Ctrl+V
        (Key.ctrl, 'z'),   # Ctrl+Z
        (Key.ctrl, 'a'),   # Ctrl+A
        (Key.alt, Key.tab),  # Alt+Tab
        (Key.alt, Key.f4),   # Alt+F4 (but we'll disable this one)
    ]
    
    # Skip dangerous combinations that might close programs
    skip_combos = [(Key.alt, Key.f4)]
    
    for combo in special_actions:
        if combo in skip_combos:
            print(f"Skipping potentially disruptive combination: {combo}")
            continue
            
        main_key, secondary_key = combo
        
        # Press the main modifier key if it exists
        keyboard.press(main_key)
        
        # If there's a secondary key, press and release it
        if secondary_key:
            time.sleep(0.1)
            keyboard.press(secondary_key)
            time.sleep(0.1)
            keyboard.release(secondary_key)
            
        time.sleep(0.2)
        
        # Release the main key
        keyboard.release(main_key)
        
        # Wait between combinations
        time.sleep(0.5)

def simulate_remote_session(duration=30):
    """
    Simulate a complete remote control session like AnyDesk
    
    Args:
        duration: Total duration of the simulation in seconds
    """
    print(f"Starting remote input simulation for {duration} seconds")
    
    start_time = time.time()
    activities = [
        (simulate_mouse_movement, {"duration": 3}),
        (simulate_mouse_clicks, {"num_clicks": 3}),
        (simulate_typing, {}),
        (simulate_special_keys, {}),
        (simulate_mouse_movement, {"duration": 2, "smooth": False}),
    ]
    
    activity_index = 0
    while time.time() - start_time < duration:
        # Get next activity with cycling through the list
        func, kwargs = activities[activity_index % len(activities)]
        
        # Execute the activity
        func(**kwargs)
        
        # Move to next activity
        activity_index += 1
        
        # Short pause between activities
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"Remote input simulation completed after {int(time.time() - start_time)} seconds")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Remote Input Simulator (AnyDesk-like)')
    parser.add_argument('--duration', type=int, default=30, help='Duration of simulation in seconds')
    parser.add_argument('--delay', type=int, default=3, help='Delay in seconds before starting simulation')
    parser.add_argument('--mode', choices=['all', 'mouse', 'keyboard'], default='all', 
                        help='Simulation mode: all, mouse only, or keyboard only')
                        
    args = parser.parse_args()
    
    print(f"Remote Input Simulator starting in {args.delay} seconds...")
    print("Position your mouse and prepare. Press Ctrl+C to cancel.")
    
    try:
        # Countdown
        for i in range(args.delay, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        if args.mode == 'all':
            simulate_remote_session(args.duration)
        elif args.mode == 'mouse':
            simulate_mouse_movement(min(args.duration // 2, 10))
            simulate_mouse_clicks(min(args.duration // 3, 5))
        elif args.mode == 'keyboard':
            simulate_typing()
            time.sleep(1)
            simulate_special_keys()
            
    except KeyboardInterrupt:
        print("\nSimulation canceled by user")
    
    print("Simulation complete!")
