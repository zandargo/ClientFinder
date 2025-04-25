#!/usr/bin/env python3
# Advanced Remote Input Simulator - Simulates AnyDesk-like low-level input
# This script uses SendInput on Windows to directly inject input events

import time
import random
import argparse
import ctypes
from ctypes import wintypes
import sys

# Windows API Constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

# Input Type
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# Virtual Key Codes
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # ALT
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

# Define C structures for the various input types
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    )

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    )

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )

class INPUT_UNION(ctypes.Union):
    _fields_ = (
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    )

class INPUT(ctypes.Structure):
    _fields_ = (
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    )

# Get screen size
def get_screen_size():
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

# Convert coordinates for MOUSEINPUT
def absolute_coordinate(x, y):
    screen_width, screen_height = get_screen_size()
    # Convert to normalized coordinates required by MOUSEEVENTF_ABSOLUTE
    # (0,0) is top left, (65535,65535) is bottom right
    normalized_x = int(x * 65535 / screen_width)
    normalized_y = int(y * 65535 / screen_height)
    return normalized_x, normalized_y

def send_mouse_event(x, y, flags):
    """
    Send a mouse event using SendInput with absolute coordinates
    
    Args:
        x, y: Screen coordinates
        flags: Mouse event flags (MOUSEEVENTF_*)
    """
    x_abs, y_abs = absolute_coordinate(x, y)
    
    extra = ctypes.pointer(wintypes.ULONG(0))
    input_struct = INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(
            mi=MOUSEINPUT(
                dx=x_abs, 
                dy=y_abs, 
                mouseData=0,
                dwFlags=flags | MOUSEEVENTF_ABSOLUTE, 
                time=0, 
                dwExtraInfo=extra
            )
        )
    )
    
    # Send the input
    if ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct)) != 1:
        error = ctypes.get_last_error()
        print(f"SendInput failed with error code {error}")

def send_key_event(vk_code, flags=0):
    """
    Send a keyboard event using SendInput
    
    Args:
        vk_code: Virtual key code
        flags: Additional flags like KEYEVENTF_KEYUP
    """
    extra = ctypes.pointer(wintypes.ULONG(0))
    input_struct = INPUT(
        type=INPUT_KEYBOARD,
        union=INPUT_UNION(
            ki=KEYBDINPUT(
                wVk=vk_code, 
                wScan=0, 
                dwFlags=flags, 
                time=0, 
                dwExtraInfo=extra
            )
        )
    )
    
    # Send the input
    if ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct)) != 1:
        error = ctypes.get_last_error()
        print(f"SendInput failed with error code {error}")

def simulate_mouse_movement(duration=5, points=20):
    """
    Simulate mouse movement using SendInput, similar to how AnyDesk would
    
    Args:
        duration: Time in seconds to move the mouse
        points: Number of points to generate
    """
    screen_width, screen_height = get_screen_size()
    start_time = time.time()
    
    print(f"Simulating mouse movement for {duration} seconds")
    
    # Generate a series of points for the mouse to move through
    x_positions = [random.randint(10, screen_width-10) for _ in range(points)]
    y_positions = [random.randint(10, screen_height-10) for _ in range(points)]
    
    # Move through each point with timing to match the duration
    point_index = 0
    while time.time() - start_time < duration:
        # Get next position
        x = x_positions[point_index % points]
        y = y_positions[point_index % points]
        
        # Send the mouse move event
        send_mouse_event(x, y, MOUSEEVENTF_MOVE)
        
        # Sleep a random amount to make movement more natural
        time.sleep(duration / points * random.uniform(0.7, 1.3))
        
        point_index += 1

def simulate_mouse_clicks(num_clicks=5):
    """
    Simulate mouse clicks at the current position
    
    Args:
        num_clicks: Number of clicks to simulate
    """
    print(f"Simulating {num_clicks} mouse clicks")
    
    for _ in range(num_clicks):
        # Get current mouse position (no movement)
        x, y = ctypes.wintypes.POINT(), ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(x), ctypes.byref(y))
        
        # Randomize between left and right clicks
        if random.random() < 0.8:  # 80% left clicks
            down_flag = MOUSEEVENTF_LEFTDOWN
            up_flag = MOUSEEVENTF_LEFTUP
        else:  # 20% right clicks
            down_flag = MOUSEEVENTF_RIGHTDOWN
            up_flag = MOUSEEVENTF_RIGHTUP
            
        # Send the mouse down event
        send_mouse_event(x.value, y.value, down_flag)
        
        # Random press duration
        time.sleep(random.uniform(0.05, 0.15))
        
        # Send the mouse up event
        send_mouse_event(x.value, y.value, up_flag)
        
        # Wait between clicks
        time.sleep(random.uniform(0.3, 0.8))

def map_char_to_vk(char):
    """Map a character to its virtual key code"""
    # This is a simplified mapping - a complete mapping would be much larger
    if char.isalpha():
        # For letters, use the uppercase ASCII value
        return ord(char.upper())
    elif char.isdigit():
        return ord(char)
    elif char == ' ':
        return VK_SPACE
    elif char == '\n':
        return VK_RETURN
    elif char == '\t':
        return VK_TAB
    else:
        # For other characters, we would need a more complete mapping
        # This is simplified for demonstration
        return ord(char) if ord(char) < 256 else 0

def simulate_typing(text=None):
    """
    Simulate keyboard typing using SendInput
    
    Args:
        text: Text to type. If None, uses a default text.
    """
    if text is None:
        text = "This is an advanced remote input simulation test.\nIt uses SendInput API to directly inject keyboard events similar to AnyDesk."
    
    print(f"Simulating typing: {text[:30]}...")
    
    for char in text:
        # Map the character to a virtual key code
        vk_code = map_char_to_vk(char)
        
        if vk_code:
            # Send key down event
            send_key_event(vk_code)
            
            # Random typing delay
            time.sleep(random.uniform(0.05, 0.2))
            
            # Send key up event
            send_key_event(vk_code, KEYEVENTF_KEYUP)
        
        # Add a small delay between characters
        time.sleep(random.uniform(0.01, 0.05))

def simulate_special_keys():
    """Simulate special key combinations"""
    print("Simulating special keys")
    
    special_keys = [
        VK_SHIFT,
        VK_CONTROL,
        VK_MENU,  # ALT
        VK_TAB,
        VK_ESCAPE,
        VK_LEFT,
        VK_RIGHT,
        VK_UP,
        VK_DOWN
    ]
    
    # Single keys
    for vk in special_keys:
        # Press
        send_key_event(vk)
        time.sleep(0.1)
        
        # Release
        send_key_event(vk, KEYEVENTF_KEYUP)
        time.sleep(0.3)
    
    # Key combinations (except Alt+F4 which could close applications)
    combinations = [
        (VK_CONTROL, ord('C')),  # Ctrl+C
        (VK_CONTROL, ord('V')),  # Ctrl+V
        (VK_CONTROL, ord('A')),  # Ctrl+A
        (VK_SHIFT, VK_TAB),      # Shift+Tab
    ]
    
    for mod_key, vk in combinations:
        # Press modifier
        send_key_event(mod_key)
        time.sleep(0.1)
        
        # Press and release main key
        send_key_event(vk)
        time.sleep(0.1)
        send_key_event(vk, KEYEVENTF_KEYUP)
        time.sleep(0.1)
        
        # Release modifier
        send_key_event(mod_key, KEYEVENTF_KEYUP)
        time.sleep(0.5)

def simulate_anydesk_session(duration=30):
    """
    Simulate a complete AnyDesk-like remote control session
    
    Args:
        duration: Total session duration in seconds
    """
    print(f"Starting AnyDesk-like remote control simulation for {duration} seconds")
    
    start_time = time.time()
    
    # Define a sequence of activities
    activities = [
        (simulate_mouse_movement, {"duration": 3, "points": 10}),
        (simulate_mouse_clicks, {"num_clicks": 2}),
        (simulate_mouse_movement, {"duration": 2, "points": 5}),
        (simulate_typing, {}),
        (simulate_special_keys, {}),
    ]
    
    # Run activities in sequence until the duration is reached
    while time.time() - start_time < duration:
        # Choose a random activity
        activity_func, kwargs = random.choice(activities)
        
        # Execute the activity
        activity_func(**kwargs)
        
        # Add a short pause between activities
        time.sleep(random.uniform(0.5, 1.0))
        
        # Check if we're out of time
        if time.time() - start_time >= duration:
            break
    
    print(f"Remote session simulation completed after {int(time.time() - start_time)} seconds")

if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform != 'win32':
        print("This script uses Windows-specific APIs and can only run on Windows.")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='Simulate AnyDesk-like remote input')
    parser.add_argument('--duration', type=int, default=20, 
                        help='Duration of simulation in seconds')
    parser.add_argument('--mode', choices=['all', 'mouse', 'keyboard'],
                        default='all', help='Simulation mode')
    parser.add_argument('--delay', type=int, default=3,
                        help='Delay before starting (seconds)')
    
    args = parser.parse_args()
    
    print(f"Advanced Remote Input Simulator starting in {args.delay} seconds...")
    print("Move your cursor to a safe position. Press Ctrl+C to abort.")
    
    try:
        # Countdown
        for i in range(args.delay, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        # Run the requested simulation
        if args.mode == 'all':
            simulate_anydesk_session(args.duration)
        elif args.mode == 'mouse':
            simulate_mouse_movement(min(args.duration * 0.6, 10))
            simulate_mouse_clicks(min(args.duration // 3, 5))
        elif args.mode == 'keyboard':
            simulate_typing()
            time.sleep(1)
            simulate_special_keys()
            
    except KeyboardInterrupt:
        print("\nSimulation aborted by user")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        
    print("\nSimulation complete")
