# 🚀 Quick Start Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or use Docker)
- OpenAI API key

## 🏃‍♂️ Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd ai-recruitment-platform

# Run the setup script
python setup.py
```

### 2. Configure Environment
```bash
# Copy environment file
cp backend/env.example backend/.env

# Edit backend/.env and add your API keys
# - OpenAI API key
# - Database URL
# - Other configuration
```

### 3. Start Services

**Option A: Using Docker (Recommended)**
```bash
# Start all services with Docker
docker-compose up -d

# Check services are running
docker-compose ps
```

**Option B: Manual Setup**
```bash
# Terminal 1: Start Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Start Frontend
cd frontend
npm install
npm start

# Terminal 3: Start Database (if not using Docker)
# Install and start PostgreSQL
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎬 Demo Data Setup

### 1. Create Sample Jobs
```bash
# Use the API or frontend to create jobs:
# - Senior Software Engineer
# - Product Manager
# - UX Designer
```

### 2. Upload Sample Resumes
```bash
# Place sample resumes in backend/uploads/
# The system will automatically parse them
```

### 3. Test the Flow
1. Create a job posting
2. Upload candidate resumes
3. View AI-generated matches
4. Conduct an AI interview
5. Review results and scoring

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version

# Install dependencies
pip install -r backend/requirements.txt

# Check database connection
# Update DATABASE_URL in .env
```

**Frontend won't start:**
```bash
# Check Node.js version
node --version

# Install dependencies
cd frontend
npm install

# Clear cache if needed
npm start -- --reset-cache
```

**AI services not working:**
```bash
# Check OpenAI API key in .env
# Ensure you have credits in your OpenAI account
# Check internet connection
```

**Database connection issues:**
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Create database if needed
```

## 📊 Demo Preparation

### 1. Load Sample Data
```bash
# Create sample jobs and candidates
# Use the frontend interface or API
```

### 2. Test AI Features
```bash
# Upload a resume and check parsing
# Create a job and view matches
# Start an interview and test scoring
```

### 3. Prepare Presentation
```bash
# Review DEMO_SCRIPT.md
# Practice the demo flow
# Prepare backup plans
```

## 🎯 Production Deployment

### Using Railway/Render
```bash
# Deploy backend to Railway
# Deploy frontend to Vercel
# Set up production database
# Configure environment variables
```

### Using Docker
```bash
# Build production images
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Additional Resources

- [Full Documentation](README.md)
- [Demo Script](DEMO_SCRIPT.md)
- [API Documentation](http://localhost:8000/docs)
- [Architecture Overview](docs/architecture.md)

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review the demo script for common issues
3. Ensure all prerequisites are installed
4. Verify API keys and database connections
5. Check logs for specific error messages

## 🏆 Ready to Demo!

Once everything is running:
1. Open http://localhost:3000
2. Follow the demo script
3. Show off your AI recruitment platform!
4. Win the hackathon! 🎉
