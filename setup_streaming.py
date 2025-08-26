#!/usr/bin/env python3
"""
Setup script for the streaming WebSocket functionality with LangGraph agents
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr.strip()}")
        return False

def main():
    print("🚀 Setting up MCP-A2A Streaming with LangGraph")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Make sure you're in the project root directory.")
        return False
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install additional dependencies that might be needed
    additional_deps = [
        "statistics",  # Usually built-in, but just in case
    ]
    
    for dep in additional_deps:
        run_command(f"pip install {dep}", f"Installing {dep}")
    
    # Check if Node.js is available for UI
    if run_command("node --version", "Checking Node.js version"):
        print("\n📦 Setting up UI dependencies...")
        
        # Change to UI directory and install dependencies
        os.chdir("ui")
        
        if run_command("npm install", "Installing UI dependencies"):
            print("✅ UI dependencies installed successfully")
        else:
            print("⚠️  Warning: UI dependency installation failed")
        
        # Go back to root directory
        os.chdir("..")
    else:
        print("⚠️  Warning: Node.js not found. UI functionality may not work.")
    
    print("\n🎉 Setup completed!")
    print("\nTo start the application:")
    print("1. Backend: python -m uvicorn mcp_server.main:app --host 0.0.0.0 --port 8002 --reload")
    print("2. Frontend: cd ui && npm start")
    print("\nThen visit:")
    print("- Streaming Agent: http://localhost:3000")
    print("- API Documentation: http://localhost:8002/docs")
    print("- WebSocket Test: ws://localhost:8002/api/v1/ws/{session_id}")

if __name__ == "__main__":
    main()
