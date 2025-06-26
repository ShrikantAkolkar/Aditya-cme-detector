#!/usr/bin/env python3
"""
Script to run the FastAPI server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the FastAPI server"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    
    # API module path
    api_module = "src.api.main:app"
    
    # Run uvicorn
    cmd = [
        "uvicorn", api_module,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ]
    
    print("Starting Aditya-L1 CME Detection API...")
    print(f"API will be available at: http://localhost:8000")
    print(f"API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the API server")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nAPI server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running API server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: uvicorn not found. Please install it with: pip install uvicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()