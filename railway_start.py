#!/usr/bin/env python3
"""Railway startup script - completely hardcoded"""
import subprocess
import sys

def main():
    print("🚀 Starting ZentrumHub server on hardcoded port 8080...")
    
    # Use subprocess to run uvicorn with hardcoded values
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8080"
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()