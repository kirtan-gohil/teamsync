# AI-Powered Interview & Recruitment Helper

## 🎯 Project Overview

An intelligent recruitment platform that uses AI to parse resumes, match candidates to jobs, and conduct automated interviews with real-time scoring and feedback.

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
uvicorn main:app --reload
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

3. **AI Services:**
```bash
cd ai-services
pip install -r requirements.txt
python main.py
```

## 📁 Project Structure

```
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── ai-services/       # AI/ML modules
├── database/          # Database schemas and migrations
└── docs/             # Documentation
```

## 🎬 Demo Features

- **Resume Parsing:** Upload PDF resumes and extract structured data
- **Smart Matching:** AI-powered candidate-job matching with scores
- **AI Interviews:** Automated interview questions and real-time scoring
- **Analytics Dashboard:** Insights and recommendations for recruiters

## 🛠️ Tech Stack

- **Backend:** FastAPI, PostgreSQL, Redis
- **Frontend:** React, TypeScript, Tailwind CSS
- **AI/ML:** OpenAI GPT-4, spaCy, Transformers
- **Deployment:** Docker, Railway/Render


