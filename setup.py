#!/usr/bin/env python3
"""
AI Recruitment Platform Setup Script
This script helps set up the development environment for the AI recruitment platform.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command: {command}")
        print(f"Exception: {e}")
        return False

def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/")
    return False

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Download spaCy model
    print("Downloading spaCy English model...")
    if not run_command("python -m spacy download en_core_web_sm", cwd=backend_dir):
        print("⚠️  Warning: Could not download spaCy model. You may need to install it manually.")
    
    # Create uploads directory
    uploads_dir = backend_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    print("✅ Frontend setup complete")
    return True

def create_env_files():
    """Create environment files from examples"""
    print("\n📝 Creating environment files...")
    
    # Backend .env
    backend_env = Path("backend/.env")
    backend_env_example = Path("backend/env.example")
    
    if backend_env_example.exists() and not backend_env.exists():
        backend_env.write_text(backend_env_example.read_text())
        print("✅ Created backend/.env from example")
    elif backend_env.exists():
        print("✅ backend/.env already exists")
    
    print("⚠️  Remember to update your API keys in backend/.env")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup complete! Next steps:")
    print("\n1. Update your API keys in backend/.env:")
    print("   - Set your OpenAI API key")
    print("   - Configure your database URL")
    print("   - Set up other environment variables")
    
    print("\n2. Start the backend server:")
    print("   cd backend")
    print("   python main.py")
    
    print("\n3. Start the frontend development server:")
    print("   cd frontend")
    print("   npm start")
    
    print("\n4. Open your browser to http://localhost:3000")
    
    print("\n📚 For more information, check the README.md file")

def main():
    """Main setup function"""
    print("🚀 AI Recruitment Platform Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Setup components
    if not setup_backend():
        print("❌ Backend setup failed")
        return False
    
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return False
    
    # Create environment files
    create_env_files()
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
