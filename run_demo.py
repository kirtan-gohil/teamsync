#!/usr/bin/env python3
"""
AI Recruitment Platform Demo Runner
This script helps you quickly set up and run the demo.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def print_banner():
    print("🚀 AI Recruitment Platform Demo")
    print("=" * 50)
    print("Setting up your demo environment...")
    print()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    print("✅ Python version OK")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js detected")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    return True

def setup_environment():
    """Set up the environment"""
    print("\n🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path("backend/.env")
    env_example = Path("backend/env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created backend/.env from example")
        print("⚠️  Please update your API keys in backend/.env")
    
    # Create uploads directory
    uploads_dir = Path("backend/uploads")
    uploads_dir.mkdir(exist_ok=True)
    print("✅ Created uploads directory")

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Backend dependencies
    print("Installing Python dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install Python dependencies: {result.stderr}")
        return False
    print("✅ Python dependencies installed")
    
    # Frontend dependencies
    print("Installing Node.js dependencies...")
    result = subprocess.run([
        "npm", "install"
    ], cwd="frontend", capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install Node.js dependencies: {result.stderr}")
        return False
    print("✅ Node.js dependencies installed")
    
    return True

def start_services():
    """Start the demo services"""
    print("\n🚀 Starting services...")
    
    print("Starting backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
    ], cwd="backend")
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    print("Starting frontend server...")
    frontend_process = subprocess.Popen([
        "npm", "start"
    ], cwd="frontend")
    
    print("\n🎉 Services starting up!")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("API Docs: http://localhost:8000/docs")
    
    print("\n⏳ Waiting for services to be ready...")
    print("This may take a few minutes on first run...")
    
    return backend_process, frontend_process

def print_demo_instructions():
    """Print demo instructions"""
    print("\n🎬 Demo Instructions:")
    print("=" * 30)
    print("1. Open http://localhost:3000 in your browser")
    print("2. Follow the demo script in DEMO_SCRIPT.md")
    print("3. Create a job posting")
    print("4. Upload sample resumes")
    print("5. View AI-generated matches")
    print("6. Conduct an AI interview")
    print("7. Review results and scoring")
    
    print("\n📚 Key Demo Points:")
    print("- AI resume parsing and skill extraction")
    print("- Intelligent candidate-job matching")
    print("- Automated interview generation")
    print("- Real-time scoring and analysis")
    print("- Bias reduction and objective evaluation")
    
    print("\n🛠️ Troubleshooting:")
    print("- If services don't start, check the logs above")
    print("- Ensure all dependencies are installed")
    print("- Check that ports 3000 and 8000 are available")
    print("- Verify your API keys in backend/.env")

def main():
    """Main demo runner function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please install missing dependencies.")
        return False
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies.")
        return False
    
    # Start services
    try:
        backend_process, frontend_process = start_services()
        
        print_demo_instructions()
        
        print("\n🎯 Press Ctrl+C to stop the demo")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping demo services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Demo stopped")
            
    except Exception as e:
        print(f"\n❌ Error starting services: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
