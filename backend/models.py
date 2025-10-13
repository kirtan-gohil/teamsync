from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import bcrypt

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    education = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interviews = relationship("Interview", back_populates="candidate")
    matches = relationship("Match", back_populates="candidate")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(JSON, default=list)
    skills_required = Column(JSON, default=list)
    experience_required = Column(Integer, default=0)
    location = Column(String, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    company = Column(String, nullable=True)
    status = Column(String, default="active")  # active, closed, filled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interviews = relationship("Interview", back_populates="job")
    matches = relationship("Match", back_populates="job")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    questions = Column(JSON, default=list)
    responses = Column(JSON, default=list)
    analysis = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed
    recording_url = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Enhanced interview data
    video_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    eye_tracking_data = Column(JSON, nullable=True)
    speech_analysis = Column(JSON, nullable=True)
    fraud_detection = Column(JSON, nullable=True)
    attention_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    admin_feedback_sent = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float, default=0.0)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="matches")
    job = relationship("Job", back_populates="matches")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="user")  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resumes = relationship("UserResume", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class UserResume(Base):
    __tablename__ = "user_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_url = Column(String)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    education = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    job_matches = relationship("UserJobMatch", back_populates="resume")

class UserJobMatch(Base):
    __tablename__ = "user_job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_id = Column(Integer, ForeignKey("user_resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_percentage = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    resume = relationship("UserResume", back_populates="job_matches")
    job = relationship("Job")


