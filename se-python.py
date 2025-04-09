import os
import win32com.client
import pythoncom
import time
import win32process
import subprocess

def open_solidedge_model(model_path=r"Y:\110-Perfisul\110-0110\Rev-00\110-0110-00.psm"):
    """
    Attempt to launch Siemens Solid Edge and optionally open a specific model file.
    
    Parameters:
    model_path (str, optional): Full path to the Solid Edge model file to be opened
    
    Returns:
    bool: True if Solid Edge was successfully launched, False otherwise
    """
    try:
        # Ensure the model file exists if a path is provided
        if model_path and not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            return False
        
        # Initialize COM libraries
        pythoncom.CoInitialize()
        
        try:
            # Try to get an existing Solid Edge application
            try:
                solid_edge = win32com.client.Dispatch("SolidEdge.Application")
                print("Solid Edge is already running.")
            except:
                # If not running, try to launch the application
                solid_edge_path = r"C:\Program Files\Siemens\Solid Edge 2020\Program\Edge.exe"
                
                # Verify the executable exists
                if not os.path.exists(solid_edge_path):
                    print("Solid Edge executable not found. Please check the installation path.")
                    return False
                
                # Launch Solid Edge
                subprocess.Popen(solid_edge_path)
                
                # Wait for the application to start
                time.sleep(5)  # Give some time for Solid Edge to launch
                
                # Retry getting the application
                solid_edge = win32com.client.Dispatch("SolidEdge.Application")
            
            # Make Solid Edge visible
            solid_edge.Visible = True
            
            # Open the model if a path is provided
            if model_path:
                try:
                    document = solid_edge.Documents.Open(model_path)
                    print(f"Successfully opened model: {model_path}")
                except Exception as doc_error:
                    print(f"Error opening model: {doc_error}")
            
            return True
        
        except Exception as e:
            print(f"Error launching Solid Edge: {e}")
            return False
        
        finally:
            # Uninitialize COM libraries
            pythoncom.CoUninitialize()
    
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return False

# Example usage
def main():
    # Option 1: Just launch Solid Edge
    success = open_solidedge_model()
    
    # Option 2: Launch and open a specific model
    # Replace with the full path to your Solid Edge model
    # model_file = r"C:\Path\To\Your\Model\ModelName.par"
    # success = open_solidedge_model(model_file)
    
    if not success:
        print("Failed to launch Solid Edge.")

if __name__ == "__main__":
    main()