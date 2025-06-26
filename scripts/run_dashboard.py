#!/usr/bin/env python3
"""
Script to run the Streamlit dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit dashboard"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Dashboard script path
    dashboard_script = project_root / "src" / "dashboard" / "streamlit_app.py"
    
    if not dashboard_script.exists():
        print(f"Error: Dashboard script not found at {dashboard_script}")
        sys.exit(1)
    
    # Run Streamlit
    cmd = [
        "streamlit", "run", str(dashboard_script),
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("Starting Aditya-L1 CME Detection Dashboard...")
    print(f"Dashboard will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()