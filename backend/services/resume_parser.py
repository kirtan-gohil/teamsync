import os
import re
import json
from typing import Dict, List, Any
import spacy
import PyPDF2
from docx import Document
import openai
from dotenv import load_dotenv

load_dotenv()

class ResumeParser:
    def __init__(self):
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Common skills database
        self.technical_skills = [
            "python", "javascript", "react", "node.js", "java", "c++", "sql", "mongodb",
            "aws", "docker", "kubernetes", "git", "linux", "html", "css", "typescript",
            "angular", "vue", "django", "flask", "fastapi", "spring", "express",
            "machine learning", "ai", "data science", "pandas", "numpy", "tensorflow",
            "pytorch", "scikit-learn", "tableau", "power bi", "excel", "r", "matlab"
        ]
        
        self.soft_skills = [
            "leadership", "communication", "teamwork", "problem solving", "project management",
            "time management", "adaptability", "creativity", "critical thinking", "analytical",
            "collaboration", "mentoring", "presentation", "negotiation", "strategic thinking"
        ]

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume and extract structured data"""
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            
            # Parse different sections
            parsed_data = {
                "name": self._extract_name(text),
                "email": self._extract_email(text),
                "phone": self._extract_phone(text),
                "skills": self._extract_skills(text),
                "experience_years": self._extract_experience_years(text),
                "education": self._extract_education(text),
                "location": self._extract_location(text),
                "summary": self._extract_summary(text),
                "work_experience": self._extract_work_experience(text),
                "raw_text": text
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return {"error": str(e)}

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_name(self, text: str) -> str:
        """Extract candidate name using NLP"""
        if not self.nlp:
            return "Unknown"
        
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return "Unknown"

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        return ''.join(phones[0]) if phones else ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        # Check for technical skills
        for skill in self.technical_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Check for soft skills
        for skill in self.soft_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Use NLP to find additional skills
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
                    if token.text.lower() not in [s.lower() for s in found_skills]:
                        # Check if it's likely a skill
                        if any(keyword in token.text.lower() for keyword in ["skill", "technology", "tool", "language"]):
                            found_skills.append(token.text)
        
        return list(set(found_skills))  # Remove duplicates

    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience"""
        # Look for patterns like "5 years", "3+ years", etc.
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?field'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        # If no explicit years found, estimate from work experience
        work_sections = re.findall(r'(?:work|professional|employment)\s*experience[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)', text, re.IGNORECASE | re.DOTALL)
        if work_sections:
            # Simple heuristic: count number of jobs * 2 years average
            job_count = len(re.findall(r'\d{4}\s*[-–]\s*\d{4}|present|current', work_sections[0], re.IGNORECASE))
            return min(job_count * 2, 20)  # Cap at 20 years
        
        return 0

    def _extract_education(self, text: str) -> str:
        """Extract education information"""
        education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd', 'diploma']
        
        for keyword in education_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""

    def _extract_location(self, text: str) -> str:
        """Extract location"""
        if not self.nlp:
            return ""
        
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity
                return ent.text
        return ""

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        summary_patterns = [
            r'summary[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'objective[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'profile[:\s]*(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""

    def _extract_work_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience details"""
        # This is a simplified version - in production, you'd want more sophisticated parsing
        experience = []
        
        # Look for date patterns and job titles
        date_pattern = r'\d{4}\s*[-–]\s*(?:\d{4}|present|current)'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        
        for i, date in enumerate(dates):
            # Extract text around each date
            start_idx = text.find(date)
            if start_idx != -1:
                # Get 200 characters before and after the date
                context = text[max(0, start_idx-100):start_idx+200]
                experience.append({
                    "period": date,
                    "description": context.strip()
                })
        
        return experience


