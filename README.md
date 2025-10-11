# TeamSync - Enterprise AI Recruitment Platform

## 🎯 Project Overview

An enterprise-level intelligent recruitment platform that uses AI to parse resumes, match candidates to jobs, and conduct automated interviews with real-time scoring and feedback. Features role-based authentication, user and admin dashboards, and advanced job matching algorithms.

## 🏗️ Architecture

```
Frontend (React) → Backend (FastAPI) → AI Services (NLP/LLM) → Database (PostgreSQL)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Setup

1. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt

# Create admin user for testing
python create_admin.py

# Start the server
uvicorn main:app --reload
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

3. **Environment Variables:**
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:password@localhost/teamsync
```

### 🚀 Quick Demo

1. **Start the application:**
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

2. **Login as Admin:**
   - Email: `admin@teamsync.com`
   - Password: `admin123`

3. **Register as User:**
   - Create a new user account
   - Upload your resume
   - View job matches with percentage scores

## 📁 Project Structure

```
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── ai-services/       # AI/ML modules
├── database/          # Database schemas and migrations
└── docs/             # Documentation
```

## 🎬 Enterprise Features

### 🔐 Authentication & Authorization
- **JWT-based Authentication:** Secure login with role-based access
- **User Registration:** Self-service user registration
- **Role-based Dashboards:** Separate interfaces for users and admins

### 👤 User Features
- **Resume Upload:** Upload and parse resumes with AI
- **Job Matching:** Get personalized job recommendations with match percentages
- **Skill Analysis:** Detailed breakdown of matched and missing skills
- **Match Reasoning:** AI-generated explanations for job matches

### 👨‍💼 Admin Features
- **Job Management:** Create and manage job postings
- **Candidate Overview:** View all candidates and their scores
- **Interview Management:** Schedule and track interviews
- **Analytics Dashboard:** Comprehensive recruitment insights

### 🤖 AI-Powered Features
- **Resume Parsing:** Upload PDF resumes and extract structured data
- **Smart Matching:** AI-powered candidate-job matching with percentage scores
- **AI Interviews:** Automated interview questions and real-time scoring
- **Skill Extraction:** Advanced NLP for skill identification and matching

## 🛠️ Tech Stack

- **Backend:** FastAPI, PostgreSQL, Redis
- **Frontend:** React, TypeScript, Tailwind CSS
- **AI/ML:** OpenAI GPT-4, spaCy, Transformers
- **Deployment:** Docker, Railway/Render


