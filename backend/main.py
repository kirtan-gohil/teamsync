from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv
from datetime import timedelta

from database import get_db, engine, Base
from models import Candidate, Job, Interview, Match, User, UserResume, UserJobMatch
from schemas import (
    CandidateCreate, CandidateResponse, 
    JobCreate, JobResponse,
    InterviewCreate, InterviewResponse,
    MatchResponse, UserLogin, UserRegister, Token, UserResponse,
    UserResumeResponse, JobMatchResponse
)
from services.resume_parser import ResumeParser
from services.matching_engine import MatchingEngine
from services.interview_ai import InterviewAI
from services.auth import authenticate_user, create_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies import get_current_active_user, get_admin_user

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Recruitment Platform",
    description="AI-powered interview and recruitment helper",
    version="1.0.0"
)

# CORS middleware - Fixed to allow proper CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Initialize AI services
resume_parser = ResumeParser()
matching_engine = MatchingEngine()
interview_ai = InterviewAI()

@app.get("/")
async def root():
    return {"message": "AI Recruitment Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_user = create_user(
        db=db,
        email=user.email,
        password=user.password,
        full_name=user.full_name,
        role="user"
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user

# Candidate endpoints
@app.post("/api/candidates/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.get("/api/candidates/", response_model=List[CandidateResponse])
async def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return candidates

@app.post("/api/candidates/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        parsed_data = await resume_parser.parse_resume(file_path)
        
        candidate = Candidate(
            name=parsed_data.get("name", "Unknown"),
            email=parsed_data.get("email", ""),
            resume_url=file_path,
            skills=parsed_data.get("skills", []),
            experience_years=parsed_data.get("experience_years", 0),
            education=parsed_data.get("education", ""),
            raw_data=parsed_data
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "candidate_id": candidate.id,
            "parsed_data": parsed_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Job endpoints
@app.post("/api/jobs/", response_model=JobResponse)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/api/jobs/", response_model=List[JobResponse])
async def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/matches/{job_id}", response_model=List[MatchResponse])
async def get_matches(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    candidates = db.query(Candidate).all()
    matches = []
    
    for candidate in candidates:
        match_score, reasoning = await matching_engine.calculate_match(candidate, job)
        
        match = db.query(Match).filter(
            Match.candidate_id == candidate.id,
            Match.job_id == job_id
        ).first()
        
        if not match:
            match = Match(
                candidate_id=candidate.id,
                job_id=job_id,
                match_score=match_score,
                reasoning=reasoning
            )
            db.add(match)
        else:
            match.match_score = match_score
            match.reasoning = reasoning
        
        db.commit()
        
        matches.append(MatchResponse(
            candidate=candidate,
            job=job,
            match_score=match_score,
            reasoning=reasoning
        ))
    
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches

@app.post("/api/interviews/", response_model=InterviewResponse)
async def create_interview(interview: InterviewCreate, db: Session = Depends(get_db)):
    questions = await interview_ai.generate_questions(
        interview.candidate_id, interview.job_id, db
    )
    
    db_interview = Interview(
        **interview.dict(),
        questions=questions,
        status="scheduled"
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

@app.post("/api/interviews/{interview_id}/conduct")
async def conduct_interview(interview_id: int, responses: List[str], db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    analysis = await interview_ai.analyze_responses(interview.questions, responses)
    
    interview.responses = responses
    interview.analysis = analysis
    interview.status = "completed"
    interview.score = analysis.get("overall_score", 0)
    
    db.commit()
    
    return {
        "message": "Interview completed successfully",
        "analysis": analysis,
        "score": interview.score
    }

@app.get("/api/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@app.post("/api/user/upload-resume", response_model=UserResumeResponse)
async def upload_user_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        file_path = f"uploads/user_{current_user.id}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        parsed_data = await resume_parser.parse_resume(file_path)
        
        user_resume = UserResume(
            user_id=current_user.id,
            resume_url=file_path,
            skills=parsed_data.get("skills", []),
            experience_years=parsed_data.get("experience_years", 0),
            education=parsed_data.get("education", ""),
            raw_data=parsed_data
        )
        
        db.add(user_resume)
        db.commit()
        db.refresh(user_resume)
        
        return user_resume
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/user/resumes", response_model=List[UserResumeResponse])
async def get_user_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resumes = db.query(UserResume).filter(UserResume.user_id == current_user.id).all()
    return resumes

@app.get("/api/user/job-matches", response_model=List[JobMatchResponse])
async def get_user_job_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(UserResume).filter(
        UserResume.user_id == current_user.id
    ).order_by(UserResume.created_at.desc()).first()
    
    if not latest_resume:
        raise HTTPException(status_code=404, detail="No resume found. Please upload a resume first.")
    
    jobs = db.query(Job).filter(Job.status == "active").all()
    matches = []
    
    for job in jobs:
        match_score, matched_skills, missing_skills, reasoning = await matching_engine.calculate_user_job_match(
            latest_resume, job
        )
        
        existing_match = db.query(UserJobMatch).filter(
            UserJobMatch.user_id == current_user.id,
            UserJobMatch.job_id == job.id
        ).first()
        
        if not existing_match:
            match_record = UserJobMatch(
                user_id=current_user.id,
                resume_id=latest_resume.id,
                job_id=job.id,
                match_percentage=match_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                reasoning=reasoning
            )
            db.add(match_record)
        else:
            existing_match.match_percentage = match_score
            existing_match.matched_skills = matched_skills
            existing_match.missing_skills = missing_skills
            existing_match.reasoning = reasoning
        
        db.commit()
        
        matches.append(JobMatchResponse(
            job=job,
            match_percentage=match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reasoning=reasoning,
            created_at=existing_match.created_at if existing_match else None
        ))
    
    matches.sort(key=lambda x: x.match_percentage, reverse=True)
    return matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)