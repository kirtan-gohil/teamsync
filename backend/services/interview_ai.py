from typing import List, Dict, Any
import openai
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import Candidate, Job

load_dotenv()

class InterviewAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate_questions(self, candidate_id: int, job_id: int, db: Session) -> List[str]:
        """Generate interview questions based on candidate and job"""
        try:
            # Get candidate and job data
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not candidate or not job:
                return self._get_default_questions()
            
            # Generate questions using AI
            prompt = f"""
            Generate 5 interview questions for this candidate and job:
            
            Candidate:
            - Name: {candidate.name}
            - Skills: {', '.join(candidate.skills or [])}
            - Experience: {candidate.experience_years} years
            - Education: {candidate.education or 'Not specified'}
            
            Job:
            - Title: {job.title}
            - Description: {job.description}
            - Required Skills: {', '.join(job.skills_required or [])}
            - Experience Required: {job.experience_required} years
            
            Generate 5 questions:
            1. One technical question related to the role
            2. One behavioral question
            3. One situational question
            4. One question about their experience
            5. One question about their motivation
            
            Return only the questions, one per line, without numbering.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            questions = [q.strip() for q in questions if q.strip()]
            
            return questions[:5]  # Ensure we have exactly 5 questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_default_questions()

    async def analyze_responses(self, questions: List[str], responses: List[str]) -> Dict[str, Any]:
        """Analyze interview responses and provide scoring"""
        try:
            if len(questions) != len(responses):
                return {"error": "Mismatch between questions and responses"}
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze these interview responses and provide a comprehensive evaluation:
            
            Questions and Responses:
            """
            
            for i, (question, response) in enumerate(zip(questions, responses), 1):
                analysis_prompt += f"\n{i}. Question: {question}\n   Response: {response}\n"
            
            analysis_prompt += """
            
            Provide analysis in this format:
            - Technical Knowledge: [score 0-10]
            - Communication Skills: [score 0-10]
            - Problem Solving: [score 0-10]
            - Cultural Fit: [score 0-10]
            - Overall Score: [score 0-10]
            
            Also provide:
            - Strengths: [list key strengths]
            - Areas for Improvement: [list areas to improve]
            - Recommendation: [Hire/Maybe/No Hire with brief reason]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the analysis
            analysis = self._parse_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing responses: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "technical_knowledge": 0,
                "communication_skills": 0,
                "problem_solving": 0,
                "cultural_fit": 0,
                "strengths": [],
                "areas_for_improvement": [],
                "recommendation": "Unable to analyze"
            }

    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI analysis into structured format"""
        analysis = {
            "overall_score": 0,
            "technical_knowledge": 0,
            "communication_skills": 0,
            "problem_solving": 0,
            "cultural_fit": 0,
            "strengths": [],
            "areas_for_improvement": [],
            "recommendation": "No Hire"
        }
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extract scores
            if "Technical Knowledge:" in line:
                analysis["technical_knowledge"] = self._extract_score(line)
            elif "Communication Skills:" in line:
                analysis["communication_skills"] = self._extract_score(line)
            elif "Problem Solving:" in line:
                analysis["problem_solving"] = self._extract_score(line)
            elif "Cultural Fit:" in line:
                analysis["cultural_fit"] = self._extract_score(line)
            elif "Overall Score:" in line:
                analysis["overall_score"] = self._extract_score(line)
            
            # Extract strengths
            elif "Strengths:" in line:
                analysis["strengths"] = self._extract_list_items(line)
            
            # Extract areas for improvement
            elif "Areas for Improvement:" in line:
                analysis["areas_for_improvement"] = self._extract_list_items(line)
            
            # Extract recommendation
            elif "Recommendation:" in line:
                analysis["recommendation"] = line.split(":", 1)[1].strip()
        
        return analysis

    def _extract_score(self, line: str) -> int:
        """Extract numerical score from line"""
        import re
        match = re.search(r'(\d+)', line)
        if match:
            score = int(match.group(1))
            return min(max(score, 0), 10)  # Clamp between 0 and 10
        return 0

    def _extract_list_items(self, line: str) -> List[str]:
        """Extract list items from line"""
        content = line.split(":", 1)[1].strip()
        items = [item.strip() for item in content.split(',')]
        return [item for item in items if item]

    def _get_default_questions(self) -> List[str]:
        """Get default questions if AI generation fails"""
        return [
            "Tell me about yourself and your background.",
            "What interests you most about this role?",
            "Describe a challenging project you worked on and how you overcame obstacles.",
            "How do you stay updated with the latest technologies in your field?",
            "Where do you see yourself in 5 years?"
        ]

    async def generate_feedback(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed feedback for the candidate"""
        try:
            feedback_prompt = f"""
            Generate constructive feedback for this interview candidate:
            
            Overall Score: {analysis.get('overall_score', 0)}/10
            Technical Knowledge: {analysis.get('technical_knowledge', 0)}/10
            Communication Skills: {analysis.get('communication_skills', 0)}/10
            Problem Solving: {analysis.get('problem_solving', 0)}/10
            Cultural Fit: {analysis.get('cultural_fit', 0)}/10
            
            Strengths: {', '.join(analysis.get('strengths', []))}
            Areas for Improvement: {', '.join(analysis.get('areas_for_improvement', []))}
            Recommendation: {analysis.get('recommendation', 'No Hire')}
            
            Provide constructive, professional feedback that would help the candidate improve.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": feedback_prompt}],
                max_tokens=400,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Thank you for your time. We will be in touch soon regarding the next steps."


