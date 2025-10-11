from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# Candidate schemas
class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    education: Optional[str] = None
    location: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    resume_url: Optional[str] = None
    score: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Job schemas
class JobBase(BaseModel):
    title: str
    description: str
    requirements: List[str] = []
    skills_required: List[str] = []
    experience_required: int = 0
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    company: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Interview schemas
class InterviewBase(BaseModel):
    candidate_id: int
    job_id: int
    scheduled_at: Optional[datetime] = None

class InterviewCreate(InterviewBase):
    pass

class InterviewResponse(InterviewBase):
    id: int
    questions: List[str] = []
    responses: List[str] = []
    analysis: Optional[Dict[str, Any]] = None
    score: float = 0.0
    status: str = "scheduled"
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Match schemas
class MatchResponse(BaseModel):
    candidate: CandidateResponse
    job: JobResponse
    match_score: float
    reasoning: Optional[str] = None
    
    class Config:
        from_attributes = True

# Resume upload response
class ResumeUploadResponse(BaseModel):
    message: str
    candidate_id: int
    parsed_data: Dict[str, Any]

# Interview analysis response
class InterviewAnalysisResponse(BaseModel):
    message: str
    analysis: Dict[str, Any]
    score: float


