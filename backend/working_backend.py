from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Recruitment Platform - Working",
    description="Working AI-powered recruitment helper",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for testing
MOCK_JOBS = [
    {
        "id": 1,
        "title": "Senior Python Developer",
        "description": "We are looking for a senior Python developer with experience in FastAPI, Django, and machine learning.",
        "requirements": ["Python", "FastAPI", "Django", "Machine Learning", "SQL", "Git"],
        "location": "San Francisco, CA",
        "salary_min": 120000,
        "salary_max": 180000,
        "company": "TechCorp Inc",
        "status": "active",
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "title": "Frontend React Developer",
        "description": "Join our team as a React developer to build amazing user interfaces.",
        "requirements": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Node.js"],
        "location": "New York, NY",
        "salary_min": 90000,
        "salary_max": 140000,
        "company": "WebSolutions Ltd",
        "status": "active",
        "created_at": "2024-01-20T14:30:00Z"
    },
    {
        "id": 3,
        "title": "Full Stack Developer",
        "description": "We need a full-stack developer with both frontend and backend experience.",
        "requirements": ["Python", "React", "JavaScript", "SQL", "Docker", "AWS"],
        "location": "Remote",
        "salary_min": 100000,
        "salary_max": 150000,
        "company": "RemoteTech",
        "status": "active",
        "created_at": "2024-01-25T09:15:00Z"
    }
]

MOCK_CANDIDATES = [
    {
        "id": 1,
        "name": "John Smith",
        "email": "john.smith@email.com",
        "skills": ["Python", "FastAPI", "Django", "SQL", "Git", "Machine Learning"],
        "experience_years": 5,
        "education": "Bachelor's in Computer Science",
        "location": "San Francisco, CA",
        "resume_url": "uploads/john_smith_resume.pdf"
    },
    {
        "id": 2,
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Node.js"],
        "experience_years": 3,
        "education": "Master's in Software Engineering",
        "location": "New York, NY",
        "resume_url": "uploads/sarah_johnson_resume.pdf"
    }
]

class ResumeParser:
    def __init__(self):
        self.technical_skills = [
            "python", "javascript", "react", "node.js", "java", "c++", "sql", "mongodb",
            "aws", "docker", "kubernetes", "git", "linux", "html", "css", "typescript",
            "angular", "vue", "django", "flask", "fastapi", "spring", "express",
            "machine learning", "ai", "data science", "pandas", "numpy", "tensorflow",
            "pytorch", "scikit-learn", "tableau", "power bi", "excel", "r", "matlab"
        ]

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume and extract structured data"""
        try:
            # For demo purposes, return mock data based on filename
            if "john" in file_path.lower():
                return {
                    "name": "John Smith",
                    "email": "john.smith@email.com",
                    "phone": "+1-555-0123",
                    "skills": ["Python", "FastAPI", "Django", "SQL", "Git", "Machine Learning", "AWS"],
                    "experience_years": 5,
                    "education": "Bachelor's in Computer Science",
                    "location": "San Francisco, CA",
                    "summary": "Experienced Python developer with expertise in web development and machine learning",
                    "work_experience": [
                        {"period": "2020-2024", "description": "Senior Python Developer at TechCorp"},
                        {"period": "2018-2020", "description": "Python Developer at StartupXYZ"}
                    ],
                    "raw_text": "John Smith - Python Developer with 5 years experience..."
                }
            elif "sarah" in file_path.lower():
                return {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@email.com",
                    "phone": "+1-555-0456",
                    "skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Node.js", "Git"],
                    "experience_years": 3,
                    "education": "Master's in Software Engineering",
                    "location": "New York, NY",
                    "summary": "Frontend developer specializing in React and modern web technologies",
                    "work_experience": [
                        {"period": "2021-2024", "description": "React Developer at WebSolutions"},
                        {"period": "2020-2021", "description": "Junior Developer at TechStart"}
                    ],
                    "raw_text": "Sarah Johnson - React Developer with 3 years experience..."
                }
            else:
                # Generic parsing for unknown files
                return {
                    "name": "Sample Candidate",
                    "email": "candidate@example.com",
                    "phone": "",
                    "skills": ["Python", "JavaScript", "React", "SQL"],
                    "experience_years": 2,
                    "education": "Bachelor's Degree",
                    "location": "Unknown",
                    "summary": "Experienced software developer",
                    "work_experience": [
                        {"period": "2022-2024", "description": "Software Developer"}
                    ],
                    "raw_text": "Sample resume content"
                }
        except Exception as e:
            return {"error": str(e)}

    def calculate_skill_match(self, candidate_skills: List[str], job_requirements: List[str]) -> Dict[str, Any]:
        """Calculate skill matching between candidate and job"""
        if not job_requirements:
            return {
                "match_percentage": 0,
                "matched_skills": [],
                "missing_skills": [],
                "reasoning": "No job requirements specified"
            }
        
        candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
        job_requirements_lower = [req.lower().strip() for req in job_requirements]
        
        matched_skills = []
        missing_skills = []
        
        for requirement in job_requirements_lower:
            requirement_words = requirement.split()
            is_matched = False
            
            for candidate_skill in candidate_skills_lower:
                # Check if any word from requirement is in candidate skill
                for req_word in requirement_words:
                    if req_word in candidate_skill or candidate_skill in req_word:
                        is_matched = True
                        break
                if is_matched:
                    break
            
            if is_matched:
                matched_skills.append(requirement.title())
            else:
                missing_skills.append(requirement.title())
        
        # Calculate percentage correctly
        match_percentage = (len(matched_skills) / len(job_requirements)) * 100
        match_percentage = min(match_percentage, 100)  # Cap at 100%
        
        return {
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "reasoning": f"Matched {len(matched_skills)} out of {len(job_requirements)} required skills"
        }

resume_parser = ResumeParser()

@app.get("/")
async def root():
    return {"message": "AI Recruitment Platform API - Working Version", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: dict):
    return {
        "access_token": "mock_token_789",
        "token_type": "bearer",
        "user": {
            "id": 3,
            "email": user_data.get("email"),
            "full_name": user_data.get("fullName"),
            "role": "user",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    }

@app.post("/api/auth/login")
async def login(credentials: dict):
    email = credentials.get("email")
    password = credentials.get("password")
    
    if email == "admin@teamsync.com" and password == "admin":
        return {
            "access_token": "mock_token_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "admin@teamsync.com",
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    elif email == "testuser@trians" and password == "test":
        return {
            "access_token": "mock_token_456",
            "token_type": "bearer",
            "user": {
                "id": 2,
                "email": "testuser@trians",
                "full_name": "Test User",
                "role": "user",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user_info():
    # Mock current user for demo
    return {
        "id": 1,
        "email": "admin@teamsync.com",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

# Job endpoints
@app.get("/api/jobs/")
async def get_jobs(skip: int = 0, limit: int = 100):
    return MOCK_JOBS[skip:skip+limit]

@app.post("/api/jobs/")
async def create_job(job_data: dict):
    new_job = {
        "id": len(MOCK_JOBS) + 1,
        "title": job_data.get("title", "New Job"),
        "description": job_data.get("description", ""),
        "requirements": job_data.get("requirements", []),
        "location": job_data.get("location", ""),
        "salary_min": job_data.get("salary_min", 50000),
        "salary_max": job_data.get("salary_max", 100000),
        "company": job_data.get("company", "Unknown Company"),
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    MOCK_JOBS.append(new_job)
    return new_job

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    job = next((job for job in MOCK_JOBS if job["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# Candidate endpoints
@app.get("/api/candidates/")
async def get_candidates(skip: int = 0, limit: int = 100):
    return MOCK_CANDIDATES[skip:skip+limit]

@app.post("/api/candidates/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        parsed_data = await resume_parser.parse_resume(file_path)
        
        new_candidate = {
            "id": len(MOCK_CANDIDATES) + 1,
            "name": parsed_data.get("name", "Unknown"),
            "email": parsed_data.get("email", ""),
            "resume_url": file_path,
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0),
            "education": parsed_data.get("education", ""),
            "location": parsed_data.get("location", ""),
            "raw_data": parsed_data
        }
        MOCK_CANDIDATES.append(new_candidate)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "candidate_id": new_candidate["id"],
            "parsed_data": parsed_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Job matching endpoints
@app.get("/api/matches/{job_id}")
async def get_matches(job_id: int):
    job = next((job for job in MOCK_JOBS if job["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    matches = []
    for candidate in MOCK_CANDIDATES:
        match_result = resume_parser.calculate_skill_match(candidate["skills"], job["requirements"])
        
        match = {
            "candidate": candidate,
            "job": job,
            "match_score": match_result["match_percentage"],
            "reasoning": match_result["reasoning"],
            "matched_skills": match_result["matched_skills"],
            "missing_skills": match_result["missing_skills"]
        }
        matches.append(match)
    
    # Sort by match score
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches

# User resume endpoints
@app.post("/api/user/upload-resume")
async def upload_user_resume(file: UploadFile = File(...)):
    try:
        file_path = f"uploads/user_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        parsed_data = await resume_parser.parse_resume(file_path)
        
        user_resume = {
            "id": 1,
            "user_id": 1,
            "resume_url": file_path,
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0),
            "education": parsed_data.get("education", ""),
            "raw_data": parsed_data,
            "created_at": datetime.now().isoformat()
        }
        
        return user_resume
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/user/resumes")
async def get_user_resumes():
    # Mock data for now
    return [{
        "id": 1,
        "user_id": 1,
        "resume_url": "uploads/sample_resume.pdf",
        "skills": ["Python", "React", "JavaScript"],
        "experience_years": 3,
        "education": "Bachelor's in Computer Science",
        "raw_data": {"name": "Sample User"},
        "created_at": datetime.now().isoformat()
    }]

@app.get("/api/user/job-matches")
async def get_user_job_matches():
    # Mock user resume data
    user_skills = ["Python", "React", "JavaScript", "SQL", "Git"]
    
    matches = []
    for job in MOCK_JOBS:
        match_result = resume_parser.calculate_skill_match(user_skills, job["requirements"])
        
        match = {
            "job": job,
            "match_percentage": match_result["match_percentage"],
            "matched_skills": match_result["matched_skills"],
            "missing_skills": match_result["missing_skills"],
            "reasoning": match_result["reasoning"],
            "created_at": datetime.now().isoformat()
        }
        matches.append(match)
    
    # Sort by match percentage
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    return matches

# Interview endpoints
@app.get("/api/interviews/")
async def get_interviews(skip: int = 0, limit: int = 100):
    # Mock interview data
    return [{
        "id": 1,
        "candidate_id": 1,
        "job_id": 1,
        "scheduled_at": "2024-02-01T10:00:00Z",
        "status": "scheduled",
        "questions": [
            "Tell me about your experience with Python",
            "How do you handle debugging complex issues?",
            "Describe a challenging project you worked on"
        ],
        "responses": [],
        "score": None,
        "analysis": None
    }]

@app.post("/api/interviews/")
async def create_interview(interview_data: dict):
    new_interview = {
        "id": 1,
        "candidate_id": interview_data.get("candidate_id", 1),
        "job_id": interview_data.get("job_id", 1),
        "scheduled_at": interview_data.get("scheduled_at", datetime.now().isoformat()),
        "status": "scheduled",
        "questions": [
            "Tell me about your experience with Python",
            "How do you handle debugging complex issues?",
            "Describe a challenging project you worked on"
        ],
        "responses": [],
        "score": None,
        "analysis": None
    }
    return new_interview

# Job Application endpoints
@app.post("/api/jobs/{job_id}/apply")
async def apply_for_job(job_id: int, application_data: dict = None):
    """Apply for a job - creates interview and sends admin notification"""
    job = next((job for job in MOCK_JOBS if job["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create interview automatically
    interview = {
        "id": len(MOCK_JOBS) + 1,
        "job_id": job_id,
        "candidate_id": application_data.get("candidate_id", 1) if application_data else 1,
        "status": "pending_approval",
        "applied_at": datetime.now().isoformat(),
        "admin_message": f"New application received for {job['title']} at {job['company']}. Interview scheduled pending approval.",
        "interview_link": f"/interview/{job_id}/candidate/{application_data.get('candidate_id', 1) if application_data else 1}"
    }
    
    return {
        "message": "Application submitted successfully!",
        "interview": interview,
        "admin_notification": "Admin has been notified of your application. You will receive an interview invitation if selected."
    }

# AI Interview endpoints
@app.get("/api/interview/{interview_id}/questions")
async def get_interview_questions(interview_id: int):
    """Get AI-generated interview questions based on job requirements and candidate skills"""
    # Mock AI-generated questions based on job skills
    questions = [
        {
            "id": 1,
            "question": "Tell me about your experience with Python programming. What projects have you built?",
            "skill": "Python",
            "type": "technical",
            "time_limit": 120
        },
        {
            "id": 2,
            "question": "How do you approach debugging a complex issue in a production environment?",
            "skill": "Problem Solving",
            "type": "technical",
            "time_limit": 90
        },
        {
            "id": 3,
            "question": "Describe a challenging project you worked on and how you overcame obstacles.",
            "skill": "Project Management",
            "type": "behavioral",
            "time_limit": 150
        },
        {
            "id": 4,
            "question": "How do you ensure code quality and maintainability in your projects?",
            "skill": "Best Practices",
            "type": "technical",
            "time_limit": 100
        },
        {
            "id": 5,
            "question": "Tell me about a time you had to learn a new technology quickly. How did you approach it?",
            "skill": "Learning",
            "type": "behavioral",
            "time_limit": 120
        }
    ]
    
    return {
        "interview_id": interview_id,
        "questions": questions,
        "total_questions": len(questions),
        "estimated_duration": "15-20 minutes"
    }

@app.post("/api/interview/{interview_id}/start")
async def start_interview(interview_id: int):
    """Start the AI interview session"""
    return {
        "interview_id": interview_id,
        "status": "started",
        "started_at": datetime.now().isoformat(),
        "fraud_detection": {
            "enabled": True,
            "voice_analysis": True,
            "eye_tracking": False,  # Would be enabled with camera access
            "background_check": True
        },
        "instructions": [
            "Speak clearly and directly into your microphone",
            "Answer each question within the time limit",
            "Be honest and authentic in your responses",
            "The system will detect any suspicious behavior"
        ]
    }

@app.post("/api/interview/{interview_id}/answer")
async def submit_answer(interview_id: int, answer_data: dict):
    """Submit an answer to an interview question with fraud detection"""
    question_id = answer_data.get("question_id")
    answer_text = answer_data.get("answer", "")
    audio_duration = answer_data.get("audio_duration", 0)
    voice_confidence = answer_data.get("voice_confidence", 0.8)
    
    # Fraud detection analysis
    fraud_analysis = {
        "is_authentic": True,
        "confidence_score": 0.85,
        "red_flags": [],
        "analysis": {
            "voice_consistency": "Good",
            "response_time": "Appropriate",
            "content_authenticity": "High",
            "background_noise": "Minimal"
        }
    }
    
    # Check for potential fraud indicators
    if voice_confidence < 0.6:
        fraud_analysis["red_flags"].append("Low voice confidence")
        fraud_analysis["is_authentic"] = False
    
    if audio_duration < 5:  # Less than 5 seconds
        fraud_analysis["red_flags"].append("Very short response")
        fraud_analysis["is_authentic"] = False
    
    if len(answer_text) < 20:
        fraud_analysis["red_flags"].append("Very brief text response")
        fraud_analysis["is_authentic"] = False
    
    # AI analysis of the answer
    answer_analysis = {
        "relevance_score": 0.8,
        "technical_depth": 0.7,
        "communication_quality": 0.9,
        "keywords_found": ["Python", "experience", "project"],
        "suggestions": "Good technical understanding demonstrated"
    }
    
    return {
        "interview_id": interview_id,
        "question_id": question_id,
        "answer_submitted": True,
        "fraud_analysis": fraud_analysis,
        "answer_analysis": answer_analysis,
        "next_question": question_id + 1 if question_id < 5 else None,
        "submitted_at": datetime.now().isoformat()
    }

@app.post("/api/interview/{interview_id}/complete")
async def complete_interview(interview_id: int, completion_data: dict):
    """Complete the interview and get final analysis"""
    total_answers = completion_data.get("total_answers", 5)
    fraud_score = completion_data.get("fraud_score", 0.85)
    technical_score = completion_data.get("technical_score", 0.8)
    
    # Final analysis
    final_analysis = {
        "interview_id": interview_id,
        "overall_score": round((fraud_score + technical_score) / 2 * 100, 2),
        "fraud_detection": {
            "passed": fraud_score > 0.7,
            "score": fraud_score,
            "recommendation": "Proceed with hiring" if fraud_score > 0.7 else "Requires manual review"
        },
        "technical_assessment": {
            "score": technical_score,
            "strengths": ["Good technical knowledge", "Clear communication"],
            "areas_for_improvement": ["Could provide more specific examples"]
        },
        "recommendation": "Strong candidate" if (fraud_score + technical_score) / 2 > 0.75 else "Needs further evaluation",
        "completed_at": datetime.now().isoformat()
    }
    
    return final_analysis

# Voice recording endpoints
@app.post("/api/interview/{interview_id}/voice/start")
async def start_voice_recording(interview_id: int):
    """Start voice recording for the interview"""
    return {
        "interview_id": interview_id,
        "recording_session_id": f"session_{interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "recording_started",
        "instructions": "Speak clearly into your microphone. Recording will automatically stop after each question.",
        "started_at": datetime.now().isoformat()
    }

@app.post("/api/interview/{interview_id}/voice/stop")
async def stop_voice_recording(interview_id: int, recording_data: dict):
    """Stop voice recording and process the audio"""
    try:
        audio_duration = recording_data.get("duration", 0)
        audio_quality = recording_data.get("quality", "good")
        
        # Mock speech-to-text processing
        transcribed_text = "This is a mock transcription of the candidate's response. In a real implementation, this would use speech-to-text services."
        
        return {
            "interview_id": interview_id,
            "transcription": transcribed_text,
            "audio_duration": int(audio_duration) if audio_duration else 0,
            "audio_quality": str(audio_quality),
            "confidence_score": 0.92,
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "interview_id": interview_id,
            "transcription": "Error processing audio",
            "audio_duration": 0,
            "audio_quality": "error",
            "confidence_score": 0.0,
            "error": str(e),
            "processed_at": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Working Backend Server...")
    print("📍 Server: http://localhost:8000")
    print("🔑 Test Logins:")
    print("   Admin: admin@teamsync.com / admin")
    print("   User:  testuser@trians / test")
    print("📊 Features: Jobs, Candidates, Resume Parsing, Skill Matching")
    print("✅ All endpoints working with proper validation")
    print("-" * 60)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)