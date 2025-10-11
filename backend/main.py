from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from database import get_db, engine, Base
from models import Candidate, Job, Interview, Match
from schemas import (
    CandidateCreate, CandidateResponse, 
    JobCreate, JobResponse,
    InterviewCreate, InterviewResponse,
    MatchResponse
)
from services.resume_parser import ResumeParser
from services.matching_engine import MatchingEngine
from services.interview_ai import InterviewAI

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Recruitment Platform",
    description="AI-powered interview and recruitment helper",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    return {"message": "AI Recruitment Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Candidate endpoints
@app.post("/api/candidates/", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.get("/api/candidates/", response_model=List[CandidateResponse])
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return candidates

@app.post("/api/candidates/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse resume using AI
        parsed_data = await resume_parser.parse_resume(file_path)
        
        # Create candidate record
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
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/api/jobs/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# Matching endpoints
@app.get("/api/matches/{job_id}", response_model=List[MatchResponse])
async def get_matches(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    candidates = db.query(Candidate).all()
    matches = []
    
    for candidate in candidates:
        match_score, reasoning = await matching_engine.calculate_match(
            candidate, job
        )
        
        # Create or update match record
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
    
    # Sort by match score
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches

# Interview endpoints
@app.post("/api/interviews/", response_model=InterviewResponse)
async def create_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db)
):
    # Generate interview questions using AI
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
async def conduct_interview(
    interview_id: int,
    responses: List[str],
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Analyze responses using AI
    analysis = await interview_ai.analyze_responses(
        interview.questions, responses
    )
    
    # Update interview with results
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


