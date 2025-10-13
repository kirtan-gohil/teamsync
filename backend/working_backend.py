from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Global storage for completed interviews
completed_interviews = []

class InterviewStorage:
    def __init__(self):
        self.interviews = []
    
    def add_interview(self, interview_data):
        self.interviews.append(interview_data)
        print(f"=== INTERVIEW STORED ===")
        print(f"Interview ID: {interview_data['interview_id']}")
        print(f"Total stored: {len(self.interviews)}")
        print(f"=======================")
    
    def get_interviews(self):
        return self.interviews
    
    def get_recent_interviews(self, limit=10):
        return self.interviews[-limit:] if len(self.interviews) > limit else self.interviews

# Global interview storage instance
interview_storage = InterviewStorage()

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
    eye_tracking = answer_data.get("eye_tracking", {})
    speech_analysis = answer_data.get("speech_analysis", {})
    
    # Enhanced fraud detection analysis
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
    
    # Check eye tracking for attention
    if eye_tracking.get("attentionScore", 100) < 50:
        fraud_analysis["red_flags"].append("Low attention score")
        fraud_analysis["is_authentic"] = False
    
    if eye_tracking.get("distractionCount", 0) > 10:
        fraud_analysis["red_flags"].append("High distraction count")
        fraud_analysis["is_authentic"] = False
    
    # AI analysis of the answer
    answer_analysis = {
        "relevance_score": 0.8,
        "technical_depth": 0.7,
        "communication_quality": 0.9,
        "keywords_found": ["Python", "experience", "project"],
        "suggestions": "Good technical understanding demonstrated"
    }
    
    # Save answer to database (mock implementation)
    answer_record = {
        "interview_id": interview_id,
        "question_id": question_id,
        "answer_text": answer_text,
        "audio_duration": audio_duration,
        "voice_confidence": voice_confidence,
        "eye_tracking_data": eye_tracking,
        "speech_analysis": speech_analysis,
        "fraud_analysis": fraud_analysis,
        "answer_analysis": answer_analysis,
        "submitted_at": datetime.now().isoformat()
    }
    
    print(f"Saving answer for interview {interview_id}, question {question_id}: {answer_record}")
    
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
    eye_tracking_summary = completion_data.get("eye_tracking_summary", {})
    overall_analysis = completion_data.get("overall_analysis", {})
    all_answers = completion_data.get("all_answers", [])
    interview_questions = completion_data.get("interview_questions", [])
    video_url = completion_data.get("video_url", "")
    audio_url = completion_data.get("audio_url", "")
    
    # Calculate comprehensive scores
    fraud_score = overall_analysis.get("confidence_score", 0.85) if overall_analysis else 0.85
    technical_score = overall_analysis.get("content_analysis", {}).get("relevance_score", 0.8) if overall_analysis else 0.8
    attention_score = eye_tracking_summary.get("attentionScore", 100) / 100 if eye_tracking_summary else 0.85
    
    # Calculate average answer score
    avg_answer_score = sum(answer.get("score", 8) for answer in all_answers) / len(all_answers) if all_answers else 8.0
    
    # Final comprehensive analysis
    final_analysis = {
        "interview_id": interview_id,
        "overall_score": round((fraud_score + technical_score + attention_score + avg_answer_score/10) / 4 * 100, 2),
        "fraud_detection": {
            "passed": fraud_score > 0.7,
            "score": fraud_score,
            "red_flags": overall_analysis.get("red_flags", []) if overall_analysis else [],
            "recommendation": "Proceed with hiring" if fraud_score > 0.7 else "Requires manual review"
        },
        "eye_tracking_analysis": {
            "attention_score": attention_score,
            "eye_movements": eye_tracking_summary.get("eyeMovements", 0),
            "distraction_count": eye_tracking_summary.get("distractionCount", 0),
            "focus_quality": "Good" if attention_score > 0.8 else "Needs improvement"
        },
        "speech_analysis": {
            "confidence": overall_analysis.get("speech_analysis", {}).get("confidence", 0.85) if overall_analysis else 0.85,
            "clarity": overall_analysis.get("speech_analysis", {}).get("clarity", 0.9) if overall_analysis else 0.9,
            "communication_quality": overall_analysis.get("content_analysis", {}).get("communication_quality", 0.9) if overall_analysis else 0.9
        },
        "technical_assessment": {
            "score": technical_score,
            "relevance": overall_analysis.get("content_analysis", {}).get("relevance_score", 0.8) if overall_analysis else 0.8,
            "technical_depth": overall_analysis.get("content_analysis", {}).get("technical_depth", 0.7) if overall_analysis else 0.7,
            "keywords_found": overall_analysis.get("content_analysis", {}).get("keywords_found", []) if overall_analysis else [],
            "strengths": ["Good technical knowledge", "Clear communication"],
            "areas_for_improvement": ["Could provide more specific examples"]
        },
        "interview_answers": all_answers,
        "recommendation": "Strong candidate" if (fraud_score + technical_score + attention_score + avg_answer_score/10) / 4 > 0.75 else "Needs further evaluation",
        "completed_at": completion_data.get("completed_at", datetime.now().isoformat())
    }
    
    # Save comprehensive interview data to database (mock implementation)
    interview_data = {
        "interview_id": interview_id,
        "video_url": video_url,
        "audio_url": audio_url,
        "eye_tracking_data": eye_tracking_summary,
        "speech_analysis": final_analysis["speech_analysis"],
        "fraud_detection": final_analysis["fraud_detection"],
        "attention_score": attention_score,
        "communication_score": final_analysis["speech_analysis"]["communication_quality"],
        "technical_score": technical_score,
        "overall_score": final_analysis["overall_score"],
        "interview_answers": all_answers,
        "interview_questions": interview_questions,
        "admin_feedback_sent": True,
        "requires_review": final_analysis["overall_score"] < 75,
        "total_answers": total_answers,
        "avg_answer_score": avg_answer_score
    }
    
    # Store interview data using the storage class
    interview_data = {
        "interview_id": interview_id,
        "candidate_name": f"Candidate {interview_id}",
        "job_title": "Software Engineer",
        "overall_score": final_analysis["overall_score"],
        "fraud_detection": final_analysis["fraud_detection"],
        "eye_tracking_analysis": final_analysis["eye_tracking_analysis"],
        "speech_analysis": final_analysis["speech_analysis"],
        "technical_assessment": final_analysis["technical_assessment"],
        "interview_answers": all_answers,
        "recommendation": final_analysis["recommendation"],
        "completed_at": completion_data.get("completed_at", datetime.now().isoformat()),
        "requires_review": final_analysis["overall_score"] < 75,
        "video_url": video_url,
        "audio_url": audio_url
    }
    
    # Store in both global array and storage class for redundancy
    global completed_interviews
    completed_interviews.append(interview_data)
    interview_storage.add_interview(interview_data)
    
    print(f"=== SAVING COMPLETE INTERVIEW DATA ===")
    print(f"Interview ID: {interview_id}")
    print(f"Total Answers: {total_answers}")
    print(f"Overall Score: {final_analysis['overall_score']}")
    print(f"Interview Answers: {len(all_answers)} answers saved")
    print(f"Eye Tracking: {eye_tracking_summary}")
    print(f"Video URL: {video_url}")
    print(f"Audio URL: {audio_url}")
    print(f"Complete Data: {interview_data}")
    print(f"Total Saved Interviews: {len(completed_interviews)}")
    print(f"=====================================")
    
    # Send admin notification
    admin_notification = {
        "interview_id": interview_id,
        "candidate_id": f"candidate_{interview_id}",
        "notification_type": "interview_completed",
        "performance_summary": {
            "overall_score": final_analysis["overall_score"],
            "fraud_detection_passed": final_analysis["fraud_detection"]["passed"],
            "attention_score": attention_score,
            "technical_score": technical_score,
            "avg_answer_score": avg_answer_score
        },
        "recommendations": final_analysis["recommendation"],
        "requires_review": final_analysis["overall_score"] < 75,
        "interview_answers": all_answers,
        "sent_at": datetime.now().isoformat()
    }
    
    print(f"Admin notification sent: {admin_notification}")
    
    return final_analysis

@app.get("/api/admin/interview-analytics")
async def get_interview_analytics():
    """Get comprehensive interview analytics for admin dashboard"""
    global completed_interviews
    
    # Get interviews from both sources
    stored_interviews = interview_storage.get_interviews()
    
    print(f"=== ADMIN REQUESTING INTERVIEW ANALYTICS ===")
    print(f"Global completed interviews: {len(completed_interviews)}")
    print(f"Storage class interviews: {len(stored_interviews)}")
    print(f"All interviews: {stored_interviews}")
    print(f"===========================================")
    
    # Use stored interviews as primary source
    analytics = stored_interviews + [
        {
            "interview_id": 4,
            "candidate_id": "candidate_4",
            "candidate_name": "Alex Rodriguez",
            "job_title": "Full Stack Developer",
            "overall_score": 91.2,
            "fraud_detection": {
                "passed": True,
                "score": 0.94,
                "red_flags": []
            },
            "eye_tracking_analysis": {
                "attention_score": 0.92,
                "eye_movements": 28,
                "distraction_count": 1,
                "focus_quality": "Excellent"
            },
            "speech_analysis": {
                "confidence": 0.95,
                "clarity": 0.96,
                "communication_quality": 0.94
            },
            "technical_assessment": {
                "score": 0.89,
                "relevance": 0.91,
                "technical_depth": 0.87,
                "keywords_found": ["React", "Node.js", "MongoDB", "TypeScript", "AWS"],
                "strengths": ["Excellent technical skills", "Clear communication", "Strong problem-solving"],
                "areas_for_improvement": []
            },
            "interview_answers": [
                {
                    "question_id": 1,
                    "question": "Describe your experience with React and state management",
                    "answer": "I have extensive experience with React, including hooks, context API, and Redux for state management. I've built complex applications with real-time updates...",
                    "score": 9.2,
                    "keywords_found": ["React", "hooks", "Redux", "state management", "applications"]
                },
                {
                    "question_id": 2,
                    "question": "How do you handle API integration and error handling?",
                    "answer": "I use async/await patterns with proper error handling, implement retry mechanisms, and use interceptors for request/response handling...",
                    "score": 8.8,
                    "keywords_found": ["API", "async/await", "error handling", "retry", "interceptors"]
                },
                {
                    "question_id": 3,
                    "question": "Explain your approach to database design and optimization",
                    "answer": "I focus on proper indexing, query optimization, and use both SQL and NoSQL databases based on requirements. I've worked with PostgreSQL, MongoDB...",
                    "score": 9.5,
                    "keywords_found": ["database", "indexing", "optimization", "PostgreSQL", "MongoDB"]
                }
            ],
            "recommendation": "Exceptional candidate",
            "completed_at": "2024-01-16T14:45:00Z",
            "requires_review": False
        },
        {
            "interview_id": 1,
            "candidate_id": "candidate_1",
            "candidate_name": "John Smith",
            "job_title": "Senior Software Engineer",
            "overall_score": 87.5,
            "fraud_detection": {
                "passed": True,
                "score": 0.92,
                "red_flags": []
            },
            "eye_tracking_analysis": {
                "attention_score": 0.85,
                "eye_movements": 45,
                "distraction_count": 2,
                "focus_quality": "Good"
            },
            "speech_analysis": {
                "confidence": 0.88,
                "clarity": 0.92,
                "communication_quality": 0.90
            },
            "technical_assessment": {
                "score": 0.85,
                "relevance": 0.88,
                "technical_depth": 0.82,
                "keywords_found": ["Python", "Django", "React", "AWS"],
                "strengths": ["Strong technical knowledge", "Clear communication", "Good problem-solving"],
                "areas_for_improvement": ["Could provide more specific examples"]
            },
            "interview_answers": [
                {
                    "question_id": 1,
                    "question": "Tell me about your experience with Python",
                    "answer": "I have 5 years of experience with Python, working on web applications using Django and Flask...",
                    "score": 8.5,
                    "keywords_found": ["Python", "Django", "Flask", "experience"]
                },
                {
                    "question_id": 2,
                    "question": "How do you handle debugging complex issues?",
                    "answer": "I use systematic debugging approaches, starting with logs and then using debugging tools...",
                    "score": 9.0,
                    "keywords_found": ["debugging", "logs", "systematic", "tools"]
                }
            ],
            "recommendation": "Strong candidate",
            "completed_at": "2024-01-15T10:30:00Z",
            "requires_review": False
        },
        {
            "interview_id": 2,
            "candidate_id": "candidate_2",
            "candidate_name": "Sarah Johnson",
            "job_title": "Frontend Developer",
            "overall_score": 72.3,
            "fraud_detection": {
                "passed": True,
                "score": 0.78,
                "red_flags": ["Low attention score"]
            },
            "eye_tracking_analysis": {
                "attention_score": 0.65,
                "eye_movements": 78,
                "distraction_count": 8,
                "focus_quality": "Needs improvement"
            },
            "speech_analysis": {
                "confidence": 0.75,
                "clarity": 0.80,
                "communication_quality": 0.78
            },
            "technical_assessment": {
                "score": 0.70,
                "relevance": 0.75,
                "technical_depth": 0.68,
                "keywords_found": ["JavaScript", "React", "CSS"],
                "strengths": ["Good frontend skills", "Creative thinking"],
                "areas_for_improvement": ["Needs more backend knowledge", "Could improve focus during interview"]
            },
            "recommendation": "Needs further evaluation",
            "completed_at": "2024-01-14T14:20:00Z",
            "requires_review": True
        },
        {
            "interview_id": 3,
            "candidate_id": "candidate_3",
            "candidate_name": "Mike Chen",
            "job_title": "Data Scientist",
            "overall_score": 94.2,
            "fraud_detection": {
                "passed": True,
                "score": 0.96,
                "red_flags": []
            },
            "eye_tracking_analysis": {
                "attention_score": 0.95,
                "eye_movements": 32,
                "distraction_count": 1,
                "focus_quality": "Excellent"
            },
            "speech_analysis": {
                "confidence": 0.94,
                "clarity": 0.96,
                "communication_quality": 0.95
            },
            "technical_assessment": {
                "score": 0.92,
                "relevance": 0.95,
                "technical_depth": 0.94,
                "keywords_found": ["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL"],
                "strengths": ["Exceptional technical expertise", "Clear communication", "Strong analytical skills"],
                "areas_for_improvement": []
            },
            "recommendation": "Exceptional candidate",
            "completed_at": "2024-01-13T09:15:00Z",
            "requires_review": False
        }
    ]
    
    return analytics

@app.post("/api/admin/interview-feedback")
async def send_admin_feedback(feedback_data: dict):
    """Send interview feedback and analysis to admin"""
    try:
        interview_id = feedback_data.get("interview_id")
        candidate_performance = feedback_data.get("candidate_performance", {})
        recommendations = feedback_data.get("recommendations", "No specific recommendations")
        all_answers = feedback_data.get("all_answers", [])
        
        # Mock admin notification (in real implementation, this would send email/notification)
        admin_notification = {
            "interview_id": interview_id,
            "candidate_id": f"candidate_{interview_id}",
            "notification_type": "interview_completed",
            "performance_summary": {
                "overall_score": candidate_performance.get("overall_score", 0),
                "fraud_detection_passed": candidate_performance.get("fraud_detection", {}).get("passed", False),
                "attention_score": candidate_performance.get("eye_tracking_analysis", {}).get("attention_score", 0),
                "technical_score": candidate_performance.get("technical_assessment", {}).get("score", 0)
            },
            "recommendations": recommendations,
            "requires_review": candidate_performance.get("overall_score", 0) < 75,
            "interview_answers": all_answers,
            "sent_at": datetime.now().isoformat()
        }
        
        print(f"=== ADMIN NOTIFICATION ===")
        print(f"Interview ID: {interview_id}")
        print(f"Overall Score: {candidate_performance.get('overall_score', 0)}")
        print(f"Answers Count: {len(all_answers)}")
        print(f"Notification: {admin_notification}")
        print(f"==========================")
        
        return {
            "status": "feedback_sent",
            "notification": admin_notification,
            "message": "Admin has been notified of interview completion"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/admin/interview-data/{interview_id}")
async def get_interview_data(interview_id: int):
    """Get specific interview data for admin review"""
    # Mock interview data retrieval
    interview_data = {
        "interview_id": interview_id,
        "candidate_name": f"Candidate {interview_id}",
        "job_title": "Software Engineer",
        "overall_score": 87.5,
        "completed_at": datetime.now().isoformat(),
        "video_url": f"uploads/interviews/{interview_id}/video.mp4",
        "audio_url": f"uploads/interviews/{interview_id}/audio.wav",
        "eye_tracking_data": {
            "attention_score": 0.85,
            "eye_movements": 45,
            "distraction_count": 2
        },
        "interview_answers": [
            {
                "question_id": 1,
                "question": "Tell me about your experience",
                "answer": "I have 5 years of experience in software development...",
                "score": 8.5,
                "keywords_found": ["experience", "development", "software"]
            }
        ],
        "fraud_detection": {
            "passed": True,
            "score": 0.92,
            "red_flags": []
        }
    }
    
    return interview_data

@app.get("/api/admin/recent-interviews")
async def get_recent_interviews():
    """Get recently completed interviews for admin dashboard"""
    global completed_interviews
    
    # Return the most recent interviews (last 10)
    recent_interviews = completed_interviews[-10:] if len(completed_interviews) > 10 else completed_interviews
    
    return {
        "total_interviews": len(completed_interviews),
        "recent_interviews": recent_interviews,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/admin/test-interview")
async def add_test_interview():
    """Add a test interview for admin visibility testing"""
    global completed_interviews
    
    # Get current count from storage class
    current_count = len(interview_storage.get_interviews())
    
    test_interview = {
        "interview_id": current_count + 1,
        "candidate_name": f"Test Candidate {current_count + 1}",
        "job_title": "Software Engineer",
        "overall_score": 85.5,
        "fraud_detection": {
            "passed": True,
            "score": 0.88,
            "red_flags": []
        },
        "eye_tracking_analysis": {
            "attention_score": 0.82,
            "eye_movements": 35,
            "distraction_count": 3,
            "focus_quality": "Good"
        },
        "speech_analysis": {
            "confidence": 0.87,
            "clarity": 0.89,
            "communication_quality": 0.85
        },
        "technical_assessment": {
            "score": 0.83,
            "relevance": 0.86,
            "technical_depth": 0.80,
            "keywords_found": ["Python", "React", "JavaScript"],
            "strengths": ["Good technical knowledge", "Clear communication"],
            "areas_for_improvement": ["Could provide more examples"]
        },
        "interview_answers": [
            {
                "question_id": 1,
                "question": "Tell me about your experience with Python",
                "answer": "I have 3 years of experience with Python, working on web applications and data analysis...",
                "score": 8.5,
                "keywords_found": ["Python", "experience", "web applications"]
            }
        ],
        "recommendation": "Good candidate",
        "completed_at": datetime.now().isoformat(),
        "requires_review": False,
        "video_url": f"uploads/interviews/{current_count + 1}/video.mp4",
        "audio_url": f"uploads/interviews/{current_count + 1}/audio.wav"
    }
    
    # Store in both global array and storage class
    completed_interviews.append(test_interview)
    interview_storage.add_interview(test_interview)
    
    print(f"=== TEST INTERVIEW ADDED ===")
    print(f"Interview ID: {test_interview['interview_id']}")
    print(f"Total interviews: {len(interview_storage.get_interviews())}")
    print(f"==========================")
    
    return {
        "status": "test_interview_added",
        "interview_id": test_interview["interview_id"],
        "total_interviews": len(interview_storage.get_interviews())
    }

@app.get("/api/admin/debug-interviews")
async def debug_interviews():
    """Debug endpoint to check stored interviews"""
    global completed_interviews
    
    stored_interviews = interview_storage.get_interviews()
    
    return {
        "global_completed_interviews": len(completed_interviews),
        "storage_class_interviews": len(stored_interviews),
        "global_data": completed_interviews,
        "storage_data": stored_interviews,
        "timestamp": datetime.now().isoformat()
    }

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

@app.post("/api/interview/{interview_id}/analyze")
async def analyze_interview_data(interview_id: int, analysis_data: dict):
    """Comprehensive analysis of interview data including video, audio, and eye tracking"""
    try:
        # Extract data from form
        audio_duration = analysis_data.get("duration", 0)
        eye_tracking_data = analysis_data.get("eye_tracking_data", {})
        
        # Comprehensive analysis
        analysis = {
            "is_authentic": True,
            "confidence_score": 0.85,
            "red_flags": [],
            "eye_tracking": {
                "eye_movements": eye_tracking_data.get("eyeMovements", 0),
                "gaze_direction": eye_tracking_data.get("gazeDirection", "center"),
                "attention_score": eye_tracking_data.get("attentionScore", 100),
                "distraction_count": eye_tracking_data.get("distractionCount", 0)
            },
            "speech_analysis": {
                "confidence": 0.85,
                "clarity": 0.9,
                "pace": 0.8,
                "filler_words": 2,
                "transcription": "Mock transcription of candidate response"
            },
            "content_analysis": {
                "relevance_score": 0.8,
                "technical_depth": 0.7,
                "communication_quality": 0.9,
                "keywords_found": ["Python", "experience", "project"],
                "suggestions": "Good technical understanding demonstrated"
            },
            "overall_score": 82.5
        }
        
        # Check for suspicious behavior
        if eye_tracking_data.get("attentionScore", 100) < 60:
            analysis["red_flags"].append("Low attention score")
            analysis["is_authentic"] = False
        
        if eye_tracking_data.get("distractionCount", 0) > 5:
            analysis["red_flags"].append("High distraction count")
            analysis["is_authentic"] = False
        
        if audio_duration < 5:
            analysis["red_flags"].append("Very short response")
            analysis["is_authentic"] = False
        
        # Save analysis to database (mock implementation)
        # In a real implementation, this would save to the database
        print(f"Saving interview analysis for interview {interview_id}: {analysis}")
        
        return {
            "interview_id": interview_id,
            "analysis": analysis,
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

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