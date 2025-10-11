from typing import Tuple, List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class MatchingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def calculate_match(self, candidate, job) -> Tuple[float, str]:
        """Calculate match score between candidate and job"""
        try:
            # Extract features
            candidate_skills = candidate.skills or []
            job_skills = job.skills_required or []
            job_requirements = job.requirements or []
            
            # Calculate different match components
            skills_match = self._calculate_skills_match(candidate_skills, job_skills)
            experience_match = self._calculate_experience_match(
                candidate.experience_years, job.experience_required
            )
            education_match = self._calculate_education_match(
                candidate.education, job_requirements
            )
            location_match = self._calculate_location_match(
                candidate.location, job.location
            )
            
            # Weighted scoring
            weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'location': 0.1
            }
            
            overall_score = (
                skills_match * weights['skills'] +
                experience_match * weights['experience'] +
                education_match * weights['education'] +
                location_match * weights['location']
            )
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(
                candidate, job, skills_match, experience_match, 
                education_match, location_match
            )
            
            return min(overall_score, 1.0), reasoning
            
        except Exception as e:
            print(f"Error calculating match: {e}")
            return 0.0, f"Error in matching calculation: {str(e)}"

    def _calculate_skills_match(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skills matching score"""
        if not job_skills:
            return 0.5  # Neutral score if no skills specified
        
        if not candidate_skills:
            return 0.0
        
        # Normalize skills to lowercase
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate intersection
        matching_skills = set(candidate_skills_lower) & set(job_skills_lower)
        
        # Calculate score based on percentage of required skills matched
        match_percentage = len(matching_skills) / len(job_skills_lower)
        
        # Bonus for additional skills
        additional_skills = len(candidate_skills_lower) - len(matching_skills)
        bonus = min(additional_skills * 0.05, 0.2)  # Max 20% bonus
        
        return min(match_percentage + bonus, 1.0)

    def _calculate_experience_match(self, candidate_years: int, required_years: int) -> float:
        """Calculate experience matching score"""
        if required_years == 0:
            return 0.5  # Neutral score if no experience required
        
        if candidate_years >= required_years:
            # Full score if meets or exceeds requirements
            return 1.0
        else:
            # Partial score based on how close they are
            return candidate_years / required_years

    def _calculate_education_match(self, candidate_education: str, job_requirements: List[str]) -> float:
        """Calculate education matching score"""
        if not candidate_education or not job_requirements:
            return 0.5  # Neutral score
        
        education_lower = candidate_education.lower()
        
        # Check for degree levels
        degree_keywords = {
            'phd': ['phd', 'doctorate', 'ph.d'],
            'master': ['master', 'mba', 'ms', 'ma'],
            'bachelor': ['bachelor', 'bs', 'ba', 'b.s', 'b.a'],
            'associate': ['associate', 'aa', 'a.s', 'a.a'],
            'diploma': ['diploma', 'certificate', 'certification']
        }
        
        candidate_degree_level = 0
        for level, keywords in degree_keywords.items():
            if any(keyword in education_lower for keyword in keywords):
                candidate_degree_level = list(degree_keywords.keys()).index(level)
                break
        
        # Check job requirements for education level
        required_level = 0
        for requirement in job_requirements:
            req_lower = requirement.lower()
            for level, keywords in degree_keywords.items():
                if any(keyword in req_lower for keyword in keywords):
                    required_level = list(degree_keywords.keys()).index(level)
                    break
        
        if required_level == 0:
            return 0.5  # No specific education requirement
        
        if candidate_degree_level >= required_level:
            return 1.0
        else:
            return candidate_degree_level / required_level

    def _calculate_location_match(self, candidate_location: str, job_location: str) -> float:
        """Calculate location matching score"""
        if not candidate_location or not job_location:
            return 0.5  # Neutral score if location not specified
        
        candidate_lower = candidate_location.lower()
        job_lower = job_location.lower()
        
        # Exact match
        if candidate_lower == job_lower:
            return 1.0
        
        # Check for city/state matches
        candidate_parts = candidate_lower.split(',')
        job_parts = job_lower.split(',')
        
        # Check if any parts match
        for candidate_part in candidate_parts:
            for job_part in job_parts:
                if candidate_part.strip() == job_part.strip():
                    return 0.8
        
        # Check for remote work compatibility
        if 'remote' in job_lower or 'anywhere' in job_lower:
            return 0.7
        
        return 0.3  # Different locations

    async def _generate_reasoning(self, candidate, job, skills_match, experience_match, 
                                education_match, location_match) -> str:
        """Generate human-readable reasoning for the match score"""
        try:
            # Use OpenAI to generate reasoning
            prompt = f"""
            Analyze this candidate-job match and provide a brief reasoning:
            
            Candidate: {candidate.name}
            Skills: {', '.join(candidate.skills or [])}
            Experience: {candidate.experience_years} years
            Education: {candidate.education or 'Not specified'}
            Location: {candidate.location or 'Not specified'}
            
            Job: {job.title}
            Required Skills: {', '.join(job.skills_required or [])}
            Required Experience: {job.experience_required} years
            Location: {job.location or 'Not specified'}
            
            Match Scores:
            - Skills: {skills_match:.2f}
            - Experience: {experience_match:.2f}
            - Education: {education_match:.2f}
            - Location: {location_match:.2f}
            
            Provide a brief, professional reasoning for why this candidate is a good/bad match.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to simple reasoning
            return self._generate_simple_reasoning(
                skills_match, experience_match, education_match, location_match
            )

    def _generate_simple_reasoning(self, skills_match, experience_match, 
                                 education_match, location_match) -> str:
        """Generate simple reasoning without AI"""
        reasons = []
        
        if skills_match > 0.7:
            reasons.append("Strong skills match")
        elif skills_match > 0.4:
            reasons.append("Partial skills match")
        else:
            reasons.append("Limited skills match")
        
        if experience_match > 0.8:
            reasons.append("Meets experience requirements")
        elif experience_match > 0.5:
            reasons.append("Close to experience requirements")
        else:
            reasons.append("Below experience requirements")
        
        if location_match > 0.7:
            reasons.append("Location compatible")
        
        return "; ".join(reasons)

    async def calculate_user_job_match(self, user_resume, job) -> Tuple[float, List[str], List[str], str]:
        """Calculate match score between user resume and job with detailed skill analysis"""
        try:
            # Extract features
            user_skills = user_resume.skills or []
            job_skills = job.skills_required or []
            job_requirements = job.requirements or []
            
            # Calculate different match components
            skills_match, matched_skills, missing_skills = self._calculate_skills_match_detailed(
                user_skills, job_skills
            )
            experience_match = self._calculate_experience_match(
                user_resume.experience_years, job.experience_required
            )
            education_match = self._calculate_education_match(
                user_resume.education, job_requirements
            )
            location_match = self._calculate_location_match(
                None, job.location  # User location not stored in resume
            )
            
            # Weighted scoring
            weights = {
                'skills': 0.5,  # Higher weight for skills in user matching
                'experience': 0.25,
                'education': 0.15,
                'location': 0.1
            }
            
            overall_score = (
                skills_match * weights['skills'] +
                experience_match * weights['experience'] +
                education_match * weights['education'] +
                location_match * weights['location']
            )
            
            # Generate reasoning
            reasoning = await self._generate_user_job_reasoning(
                user_resume, job, skills_match, experience_match, 
                education_match, location_match, matched_skills, missing_skills
            )
            
            return min(overall_score, 1.0), matched_skills, missing_skills, reasoning
            
        except Exception as e:
            print(f"Error calculating user job match: {e}")
            return 0.0, [], [], f"Error in matching calculation: {str(e)}"

    def _calculate_skills_match_detailed(self, user_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate detailed skills matching with matched and missing skills"""
        if not job_skills:
            return 0.5, [], []  # Neutral score if no skills specified
        
        if not user_skills:
            return 0.0, [], job_skills
        
        # Normalize skills to lowercase
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate intersection
        matching_skills = set(user_skills_lower) & set(job_skills_lower)
        missing_skills = set(job_skills_lower) - set(user_skills_lower)
        
        # Calculate score based on percentage of required skills matched
        match_percentage = len(matching_skills) / len(job_skills_lower)
        
        # Bonus for additional skills
        additional_skills = len(user_skills_lower) - len(matching_skills)
        bonus = min(additional_skills * 0.05, 0.2)  # Max 20% bonus
        
        return min(match_percentage + bonus, 1.0), list(matching_skills), list(missing_skills)

    async def _generate_user_job_reasoning(self, user_resume, job, skills_match, experience_match, 
                                         education_match, location_match, matched_skills, missing_skills) -> str:
        """Generate detailed reasoning for user job match"""
        try:
            # Use OpenAI to generate reasoning
            prompt = f"""
            Analyze this user-job match and provide detailed reasoning:
            
            User Resume:
            Skills: {', '.join(user_resume.skills or [])}
            Experience: {user_resume.experience_years} years
            Education: {user_resume.education or 'Not specified'}
            
            Job: {job.title}
            Required Skills: {', '.join(job.skills_required or [])}
            Required Experience: {job.experience_required} years
            Location: {job.location or 'Not specified'}
            
            Match Analysis:
            - Skills Match: {skills_match:.2f}
            - Matched Skills: {', '.join(matched_skills)}
            - Missing Skills: {', '.join(missing_skills)}
            - Experience Match: {experience_match:.2f}
            - Education Match: {education_match:.2f}
            - Location Match: {location_match:.2f}
            
            Provide a detailed, professional reasoning for this match including:
            1. Strengths (what matches well)
            2. Areas for improvement (what's missing)
            3. Overall fit assessment
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to simple reasoning
            return self._generate_simple_user_job_reasoning(
                skills_match, experience_match, matched_skills, missing_skills
            )

    def _generate_simple_user_job_reasoning(self, skills_match, experience_match, 
                                           matched_skills, missing_skills) -> str:
        """Generate simple reasoning for user job match"""
        reasons = []
        
        if skills_match > 0.7:
            reasons.append(f"Excellent skills match ({len(matched_skills)}/{len(matched_skills) + len(missing_skills)} required skills)")
        elif skills_match > 0.4:
            reasons.append(f"Good skills match ({len(matched_skills)}/{len(matched_skills) + len(missing_skills)} required skills)")
        else:
            reasons.append(f"Limited skills match ({len(matched_skills)}/{len(matched_skills) + len(missing_skills)} required skills)")
        
        if matched_skills:
            reasons.append(f"Matched skills: {', '.join(matched_skills[:5])}")
        
        if missing_skills:
            reasons.append(f"Missing skills: {', '.join(missing_skills[:5])}")
        
        if experience_match > 0.8:
            reasons.append("Meets experience requirements")
        elif experience_match > 0.5:
            reasons.append("Close to experience requirements")
        else:
            reasons.append("Below experience requirements")
        
        return "; ".join(reasons)


