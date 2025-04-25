#!/usr/bin/env python3
# Keylogger Test Runner - Tests the klog.py functionality with simulated remote input
# This script uses the remote_input_test.py to generate input and verifies the logs

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def read_log_file(log_path):
    """Read and return the contents of the log file"""
    try:
        with open(log_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading log file: {e}")
        return ""

def start_keylogger():
    """Start the keylogger in a separate process"""
    try:
        # Using Python instead of pythonw to see output for testing purposes
        process = subprocess.Popen([sys.executable, "klog.py"], 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        
        # Give the keylogger time to initialize
        time.sleep(2)
        
        return process
    except Exception as e:
        print(f"Failed to start keylogger: {e}")
        return None

def run_input_simulation(mode='all', duration=10):
    """Run the input simulation script"""
    try:
        # Run the remote input test script
        cmd = [sys.executable, "remote_input_test.py", 
               "--mode", mode, 
               "--duration", str(duration),
               "--delay", "2"]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error running input simulation: {stderr}")
            return False
            
        print(f"Input simulation completed: {stdout}")
        return True
    except Exception as e:
        print(f"Failed to run input simulation: {e}")
        return False

def verify_log_contents(log_path, expected_patterns, timeout=5):
    """
    Verify that the log file contains the expected patterns within the timeout period
    
    Args:
        log_path: Path to the log file
        expected_patterns: List of strings to look for in the log
        timeout: Maximum seconds to wait for the patterns to appear
    
    Returns:
        tuple: (success_flag, found_patterns, missing_patterns)
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout)
    found_patterns = []
    missing_patterns = expected_patterns.copy()
    
    print(f"Verifying log contents at: {log_path}")
    print(f"Looking for {len(expected_patterns)} patterns with {timeout}s timeout...")
    
    while datetime.now() < end_time and missing_patterns:
        log_content = read_log_file(log_path)
        
        # Check each pattern
        for pattern in missing_patterns.copy():
            if pattern in log_content:
                found_patterns.append(pattern)
                missing_patterns.remove(pattern)
                print(f"Found pattern: {pattern}")
        
        # If all patterns found, break early
        if not missing_patterns:
            break
            
        # Short pause before checking again
        time.sleep(0.5)
    
    # Report results
    success = len(missing_patterns) == 0
    if success:
        print("✓ SUCCESS: All expected patterns found in the log file!")
    else:
        print(f"✗ FAIL: {len(missing_patterns)}/{len(expected_patterns)} patterns not found:")
        for pattern in missing_patterns:
            print(f"  - Missing: {pattern}")
    
    return success, found_patterns, missing_patterns

def stop_process(process):
    """Safely stop a process"""
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

def main():
    parser = argparse.ArgumentParser(description='Test Keylogger with Simulated Remote Input')
    parser.add_argument('--mode', choices=['all', 'mouse', 'keyboard'], default='all',
                        help='Test mode: all, mouse, or keyboard')
    parser.add_argument('--duration', type=int, default=15, 
                        help='Duration of input simulation in seconds')
    parser.add_argument('--manual', action='store_true',
                        help='Manual mode - does not start/stop keylogger automatically')
                        
    args = parser.parse_args()
    
    # Get user's home directory for log file location
    home_dir = Path.home()
    log_file = home_dir / "notas.txt"
    
    keylogger_process = None
    
    try:
        print("\n=== KEYLOGGER TEST WITH SIMULATED ANYDESK INPUT ===\n")
        
        # Only start keylogger if not in manual mode
        if not args.manual:
            # Start the keylogger
            print("Starting keylogger...")
            keylogger_process = start_keylogger()
            if not keylogger_process:
                print("Failed to start keylogger. Exiting.")
                return 1
            
            print("Waiting for keylogger to initialize...")
            time.sleep(3)  # Give the keylogger time to initialize
        else:
            print("Manual mode: Assuming keylogger is already running")
        
        # Check if log file exists
        if not os.path.exists(log_file):
            print(f"Log file not found at {log_file}")
            print("Please make sure the keylogger is running and configured correctly.")
            return 1
            
        # Run the input simulation
        print(f"\nRunning input simulation in {args.mode} mode for {args.duration} seconds...")
        success = run_input_simulation(args.mode, args.duration)
        if not success:
            print("Input simulation failed. Exiting.")
            return 1
            
        # Give some time for the keylogger to process all inputs and write to the log
        print("Waiting for keylogger to finish processing events...")
        time.sleep(5)
        
        # Define expected patterns in the log file based on the test mode
        expected_patterns = []
        
        if args.mode in ['all', 'keyboard']:
            expected_patterns.extend([
                "This is a remote input test",  # Regular typing
                "\\n",                          # Enter key
                "<shift>",                      # Special keys
                "<ctrl>"
            ])
        
        # Verify log contents
        print("\nChecking log file for expected patterns...")
        verify_log_contents(log_file, expected_patterns)
        
        print("\nTest completed!")
        return 0
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        return 1
    finally:
        # Clean up
        if not args.manual and keylogger_process:
            print("Stopping keylogger...")
            stop_process(keylogger_process)

if __name__ == "__main__":
    sys.exit(main())
