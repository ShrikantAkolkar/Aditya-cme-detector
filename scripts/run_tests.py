#!/usr/bin/env python3
"""
Script to run tests for the CME detection system
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the test suite"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Test directory
    test_dir = project_root / "tests"
    
    if not test_dir.exists():
        print(f"Error: Test directory not found at {test_dir}")
        sys.exit(1)
    
    # Run pytest
    cmd = [
        "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    print("Running Aditya-L1 CME Detection System Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("Coverage report generated in htmlcov/index.html")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            
        sys.exit(result.returncode)
        
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with: pip install pytest pytest-cov pytest-asyncio")
        sys.exit(1)

if __name__ == "__main__":
    main()