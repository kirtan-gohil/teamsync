import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import docx2txt
import pdfplumber
from datetime import datetime

class ResumeParser:
    def __init__(self):
        # Comprehensive skills database
        self.technical_skills = {
            # Programming Languages
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "swift", 
            "kotlin", "go", "rust", "typescript", "scala", "perl", "r", "matlab",
            
            # Web Technologies
            "react", "angular", "vue", "vue.js", "node.js", "express", "django", 
            "flask", "fastapi", "spring boot", "asp.net", "laravel", "html", "css",
            "sass", "less", "bootstrap", "tailwind", "jquery", "webpack", "redux",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "cassandra", "oracle",
            "sqlite", "dynamodb", "firebase", "elasticsearch", "neo4j",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
            "ansible", "git", "github", "gitlab", "ci/cd", "linux", "unix",
            
            # Data Science & ML
            "machine learning", "deep learning", "ai", "data science", "pandas", 
            "numpy", "tensorflow", "pytorch", "scikit-learn", "keras", "opencv",
            "nlp", "computer vision", "tableau", "power bi", "excel", "spark",
            
            # Mobile Development
            "android", "ios", "react native", "flutter", "xamarin",
            
            # Other
            "restful api", "graphql", "microservices", "agile", "scrum", "jira"
        }
        
        self.soft_skills = {
            "leadership", "communication", "teamwork", "problem solving", 
            "project management", "time management", "adaptability", "creativity",
            "critical thinking", "analytical", "collaboration", "mentoring",
            "presentation", "negotiation", "strategic thinking", "decision making"
        }
        
        self.education_keywords = {
            "bachelor", "master", "phd", "doctorate", "mba", "associate",
            "b.tech", "m.tech", "b.e", "m.e", "b.s", "m.s", "b.a", "m.a",
            "diploma", "certificate", "degree"
        }

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured data from PDF or DOCX files
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing extracted resume data
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # Extract text based on file type
            text = self._extract_text(file_path)
            
            if not text or len(text.strip()) < 50:
                return {"error": "Could not extract text from resume or file is too short"}
            
            # Extract all information
            parsed_data = {
                "name": self._extract_name(text),
                "email": self._extract_email(text),
                "phone": self._extract_phone(text),
                "location": self._extract_location(text),
                "summary": self._extract_summary(text),
                "skills": self._extract_skills(text),
                "technical_skills": self._extract_technical_skills(text),
                "soft_skills": self._extract_soft_skills(text),
                "experience_years": self._extract_experience_years(text),
                "work_experience": self._extract_work_experience(text),
                "education": self._extract_education(text),
                "certifications": self._extract_certifications(text),
                "raw_text": text[:1000]  # First 1000 chars for reference
            }
            
            return parsed_data
            
        except Exception as e:
            return {"error": f"Error parsing resume: {str(e)}"}

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
                
            elif file_extension in ['.docx', '.doc']:
                text = docx2txt.process(file_path)
                return text
                
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")

    def _extract_name(self, text: str) -> str:
        """Extract candidate name from the first few lines"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look in first 5 lines
        for line in lines[:5]:
            # Skip lines with common keywords
            skip_keywords = ['resume', 'cv', 'curriculum', 'email', 'phone', 
                           'address', 'objective', 'summary', 'profile']
            
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue
            
            # Check if line looks like a name (2-4 words, mostly letters)
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(re.match(r'^[A-Za-z\.\-]+$', word) for word in words):
                    if len(line) > 5 and len(line) < 50:
                        return line
        
        return "Not Found"

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        # Multiple phone patterns
        phone_patterns = [
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # Clean up the phone number
                phone = re.sub(r'[^\d+]', '', phones[0])
                if len(phone) >= 10:
                    return phones[0]
        return ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract all skills (technical + soft) from resume"""
        text_lower = text.lower()
        found_skills = set()
        
        # Look for skills section
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'core competencies'])
        search_text = skills_section if skills_section else text
        search_text_lower = search_text.lower()
        
        # Check for technical skills
        for skill in self.technical_skills:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, search_text_lower):
                found_skills.add(skill.title())
        
        # Check for soft skills
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, search_text_lower):
                found_skills.add(skill.title())
        
        return sorted(list(found_skills))

    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract only technical skills"""
        text_lower = text.lower()
        found_skills = set()
        
        skills_section = self._extract_section(text, ['skills', 'technical skills'])
        search_text = skills_section if skills_section else text
        search_text_lower = search_text.lower()
        
        for skill in self.technical_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, search_text_lower):
                found_skills.add(skill.title())
        
        return sorted(list(found_skills))

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract only soft skills"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill.title())
        
        return sorted(list(found_skills))

    def _extract_section(self, text: str, section_names: List[str]) -> str:
        """Extract a specific section from resume"""
        text_lines = text.split('\n')
        
        for i, line in enumerate(text_lines):
            line_lower = line.lower().strip()
            
            for section_name in section_names:
                if section_name.lower() in line_lower and len(line_lower) < 50:
                    # Found section header, extract content until next section
                    section_content = []
                    for j in range(i + 1, len(text_lines)):
                        next_line = text_lines[j].strip()
                        # Stop at next section header (usually all caps or title case)
                        if next_line and (next_line.isupper() or 
                           (next_line[0].isupper() and ':' in next_line)):
                            break
                        section_content.append(text_lines[j])
                    
                    return '\n'.join(section_content)
        
        return ""

    def _extract_experience_years(self, text: str) -> int:
        """Extract total years of experience"""
        # Pattern 1: Explicit mention of years
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?field',
            r'over\s*(\d+)\s*years'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        # Pattern 2: Calculate from work history dates
        work_exp = self._extract_work_experience(text)
        if work_exp:
            total_years = 0
            for exp in work_exp:
                years = self._calculate_duration(exp.get('period', ''))
                total_years += years
            return int(total_years)
        
        return 0

    def _calculate_duration(self, period: str) -> float:
        """Calculate duration in years from a period string"""
        if not period:
            return 0
        
        try:
            # Extract years from patterns like "2020-2023", "Jan 2020 - Dec 2023"
            years = re.findall(r'\d{4}', period)
            if len(years) >= 2:
                start_year = int(years[0])
                end_year = int(years[-1]) if 'present' not in period.lower() and 'current' not in period.lower() else datetime.now().year
                return max(0, end_year - start_year)
        except:
            pass
        
        return 0

    def _extract_work_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience with company, role, and duration"""
        experience = []
        
        # Find experience section
        exp_section = self._extract_section(text, ['experience', 'work experience', 
                                                   'professional experience', 'employment history'])
        search_text = exp_section if exp_section else text
        
        # Look for date ranges
        date_patterns = [
            r'(\d{4}\s*[-–]\s*(?:\d{4}|present|current))',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|present|current))'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, search_text, re.IGNORECASE)
            
            for match in matches:
                date_str = match.group(1)
                start_idx = match.start()
                
                # Extract context around the date (company and role)
                context_before = search_text[max(0, start_idx-200):start_idx]
                context_after = search_text[start_idx:min(len(search_text), start_idx+300)]
                
                # Try to find company name and role
                lines_before = [l.strip() for l in context_before.split('\n') if l.strip()]
                lines_after = [l.strip() for l in context_after.split('\n')[:5] if l.strip()]
                
                role = ""
                company = ""
                
                # Look for role and company in lines before date
                if lines_before:
                    role = lines_before[-1] if lines_before[-1] else ""
                    company = lines_before[-2] if len(lines_before) > 1 else ""
                
                # Create description from context
                description = ' '.join(lines_after[1:3]) if len(lines_after) > 1 else ""
                
                experience.append({
                    "period": date_str,
                    "role": role,
                    "company": company,
                    "description": description[:200]  # Limit description length
                })
        
        return experience

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education details including degree, institution, and year"""
        education_list = []
        
        # Find education section
        edu_section = self._extract_section(text, ['education', 'academic background', 
                                                   'qualification', 'academic qualification'])
        search_text = edu_section if edu_section else text
        
        if not search_text:
            return []
        
        # Split into lines and process
        lines = [line.strip() for line in search_text.split('\n') if line.strip()]
        
        # Look for degree patterns
        degree_patterns = [
            r'\b((?:bachelor|master|phd|doctorate|mba|associate|diploma|certificate)(?:\'s)?(?:\s+of)?(?:\s+\w+)*)\b',
            r'\b(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)\b'
        ]
        
        current_edu = {}
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for degree
            for pattern in degree_patterns:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    degree = match.group(1)
                    
                    # Look for year
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    year = year_match.group(0) if year_match else ""
                    
                    # Look for institution in same line or next lines
                    institution = ""
                    if i < len(lines) - 1:
                        next_lines = ' '.join(lines[i+1:min(i+3, len(lines))])
                        # Institution often contains words like University, College, Institute
                        inst_match = re.search(r'([A-Z][A-Za-z\s&,.-]+(?:University|College|Institute|School))', next_lines)
                        if inst_match:
                            institution = inst_match.group(1).strip()
                    
                    education_list.append({
                        "degree": degree.title(),
                        "institution": institution,
                        "year": year
                    })
                    break
        
        return education_list if education_list else [{"degree": "Not specified", "institution": "", "year": ""}]

    def _extract_location(self, text: str) -> str:
        """Extract location (city, state/country)"""
        location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, ST
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',  # City, Country
        ]
        
        # Look in first 500 characters (usually contact info is at top)
        text_top = text[:500]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text_top)
            if matches:
                return f"{matches[0][0]}, {matches[0][1]}"
        
        return ""

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary or objective"""
        summary_section = self._extract_section(text, ['summary', 'objective', 
                                                       'profile', 'professional summary',
                                                       'career objective'])
        
        if summary_section:
            # Clean and limit to first 500 characters
            summary = ' '.join(summary_section.split())
            return summary[:500]
        
        return ""

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        cert_section = self._extract_section(text, ['certifications', 'certificates', 
                                                    'licenses', 'credentials'])
        search_text = cert_section if cert_section else text
        
        # Common certification patterns
        cert_patterns = [
            r'(?:AWS|Azure|Google Cloud|GCP)\s+(?:Certified\s+)?[\w\s-]+',
            r'(?:PMP|PRINCE2|Scrum Master|CSM|PMI)',
            r'(?:CISSP|CISM|Security\+|Network\+|CEH)',
            r'Certified\s+[\w\s]+(?:Professional|Specialist|Expert|Associate)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            certifications.extend([m.strip() for m in matches])
        
        return list(set(certifications))


# Usage Example
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Parse a resume
    resume_path = "path/to/resume.pdf"  # or .docx, .txt
    result = parser.parse_resume(resume_path)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    # Access specific fields
    if "error" not in result:
        print(f"\nName: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Technical Skills: {', '.join(result['technical_skills'])}")
        print(f"Years of Experience: {result['experience_years']}")
        print(f"\nEducation:")
        for edu in result['education']:
            print(f"  - {edu['degree']} from {edu['institution']} ({edu['year']})")


class SkillMatcher:
    """Match resume skills with job requirements"""
    
    def __init__(self):
        self.skill_synonyms = {
            'javascript': ['js', 'javascript', 'ecmascript'],
            'node.js': ['node', 'nodejs', 'node.js'],
            'react': ['react', 'reactjs', 'react.js'],
            'python': ['python', 'py'],
            'aws': ['aws', 'amazon web services'],
            'docker': ['docker', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s'],
            'machine learning': ['ml', 'machine learning', 'ai', 'artificial intelligence'],
        }
    
    def calculate_skill_match(self, resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """
        Calculate how well resume skills match job requirements
        
        Args:
            resume_skills: List of skills from resume
            required_skills: List of required skills for job
            
        Returns:
            Dictionary with match percentage and details
        """
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matched_skills = []
        missing_skills = []
        
        for req_skill in required_skills_lower:
            # Check direct match
            if req_skill in resume_skills_lower:
                matched_skills.append(req_skill)
            else:
                # Check synonyms
                found = False
                for skill_group in self.skill_synonyms.values():
                    if req_skill in skill_group:
                        for synonym in skill_group:
                            if synonym in resume_skills_lower:
                                matched_skills.append(req_skill)
                                found = True
                                break
                    if found:
                        break
                
                if not found:
                    missing_skills.append(req_skill)
        
        match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_required': len(required_skills),
            'total_matched': len(matched_skills)
        }
    
    def score_resume(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score resume against job requirements
        
        Args:
            resume_data: Parsed resume data
            job_requirements: Dict with required_skills, min_experience, required_education
            
        Returns:
            Overall score and breakdown
        """
        scores = {}
        
        # Skill match (50% weight)
        skill_match = self.calculate_skill_match(
            resume_data.get('technical_skills', []),
            job_requirements.get('required_skills', [])
        )
        scores['skill_score'] = skill_match['match_percentage']
        scores['skill_details'] = skill_match
        
        # Experience match (30% weight)
        min_exp = job_requirements.get('min_experience', 0)
        candidate_exp = resume_data.get('experience_years', 0)
        
        if min_exp == 0:
            exp_score = 100
        elif candidate_exp >= min_exp:
            exp_score = 100
        else:
            exp_score = (candidate_exp / min_exp) * 100
        
        scores['experience_score'] = round(exp_score, 2)
        scores['experience_details'] = {
            'required': min_exp,
            'candidate': candidate_exp,
            'meets_requirement': candidate_exp >= min_exp
        }
        
        # Education match (20% weight)
        required_education = job_requirements.get('required_education', '').lower()
        candidate_education = [edu['degree'].lower() for edu in resume_data.get('education', [])]
        
        education_score = 0
        education_levels = {
            'high school': 1,
            'diploma': 2,
            'associate': 3,
            'bachelor': 4,
            'master': 5,
            'phd': 6,
            'doctorate': 6
        }
        
        req_level = 0
        for edu_type, level in education_levels.items():
            if edu_type in required_education:
                req_level = level
                break
        
        candidate_level = 0
        for edu in candidate_education:
            for edu_type, level in education_levels.items():
                if edu_type in edu:
                    candidate_level = max(candidate_level, level)
        
        if req_level == 0:
            education_score = 100
        elif candidate_level >= req_level:
            education_score = 100
        else:
            education_score = (candidate_level / req_level) * 100 if req_level > 0 else 0
        
        scores['education_score'] = round(education_score, 2)
        scores['education_details'] = {
            'required': required_education,
            'candidate': candidate_education,
            'meets_requirement': candidate_level >= req_level
        }
        
        # Calculate weighted overall score
        overall_score = (
            scores['skill_score'] * 0.5 +
            scores['experience_score'] * 0.3 +
            scores['education_score'] * 0.2
        )
        
        scores['overall_score'] = round(overall_score, 2)
        scores['recommendation'] = self._get_recommendation(overall_score)
        
        return scores
    
    def _get_recommendation(self, score: float) -> str:
        """Get hiring recommendation based on score"""
        if score >= 80:
            return "Strong Match - Highly Recommended"
        elif score >= 60:
            return "Good Match - Recommended for Interview"
        elif score >= 40:
            return "Partial Match - Consider with Reservations"
        else:
            return "Weak Match - Not Recommended"


class BatchResumeProcessor:
    """Process multiple resumes at once"""
    
    def __init__(self):
        self.parser = ResumeParser()
        self.matcher = SkillMatcher()
    
    def process_folder(self, folder_path: str, job_requirements: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Process all resumes in a folder
        
        Args:
            folder_path: Path to folder containing resumes
            job_requirements: Optional job requirements for scoring
            
        Returns:
            List of parsed resume data with scores
        """
        results = []
        folder = Path(folder_path)
        
        # Supported file extensions
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
        
        # Get all resume files
        resume_files = []
        for ext in supported_extensions:
            resume_files.extend(list(folder.glob(f'*{ext}')))
        
        print(f"Found {len(resume_files)} resume(s) to process...")
        
        for resume_file in resume_files:
            print(f"\nProcessing: {resume_file.name}")
            
            # Parse resume
            parsed_data = self.parser.parse_resume(str(resume_file))
            
            if "error" in parsed_data:
                print(f"  Error: {parsed_data['error']}")
                results.append({
                    'filename': resume_file.name,
                    'error': parsed_data['error']
                })
                continue
            
            result = {
                'filename': resume_file.name,
                'parsed_data': parsed_data
            }
            
            # Score against job requirements if provided
            if job_requirements:
                scores = self.matcher.score_resume(parsed_data, job_requirements)
                result['scores'] = scores
                print(f"  Overall Score: {scores['overall_score']}% - {scores['recommendation']}")
            
            results.append(result)
        
        # Sort by score if available
        if job_requirements:
            results.sort(key=lambda x: x.get('scores', {}).get('overall_score', 0), reverse=True)
        
        return results
    
    def export_results(self, results: List[Dict[str, Any]], output_file: str):
        """Export results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults exported to: {output_file}")
    
    def generate_report(self, results: List[Dict[str, Any]], output_file: str = "resume_report.txt"):
        """Generate a text report of all processed resumes"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RESUME SCREENING REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            for i, result in enumerate(results, 1):
                if 'error' in result:
                    f.write(f"{i}. {result['filename']} - ERROR: {result['error']}\n\n")
                    continue
                
                data = result['parsed_data']
                f.write(f"{i}. {result['filename']}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Name: {data.get('name', 'N/A')}\n")
                f.write(f"Email: {data.get('email', 'N/A')}\n")
                f.write(f"Phone: {data.get('phone', 'N/A')}\n")
                f.write(f"Location: {data.get('location', 'N/A')}\n")
                f.write(f"Experience: {data.get('experience_years', 0)} years\n\n")
                
                f.write("Technical Skills:\n")
                for skill in data.get('technical_skills', []):
                    f.write(f"  • {skill}\n")
                f.write("\n")
                
                f.write("Education:\n")
                for edu in data.get('education', []):
                    f.write(f"  • {edu.get('degree', 'N/A')}")
                    if edu.get('institution'):
                        f.write(f" - {edu['institution']}")
                    if edu.get('year'):
                        f.write(f" ({edu['year']})")
                    f.write("\n")
                f.write("\n")
                
                if 'scores' in result:
                    scores = result['scores']
                    f.write("SCREENING SCORES:\n")
                    f.write(f"  Overall Score: {scores['overall_score']}%\n")
                    f.write(f"  Recommendation: {scores['recommendation']}\n")
                    f.write(f"  Skill Match: {scores['skill_score']}%\n")
                    f.write(f"  Experience Match: {scores['experience_score']}%\n")
                    f.write(f"  Education Match: {scores['education_score']}%\n\n")
                    
                    if scores['skill_details']['missing_skills']:
                        f.write("  Missing Skills:\n")
                        for skill in scores['skill_details']['missing_skills']:
                            f.write(f"    - {skill}\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        print(f"Report generated: {output_file}")


# Enhanced Usage Examples
if __name__ == "__main__":
    # Example 1: Parse single resume
    print("Example 1: Single Resume Parsing")
    print("-" * 50)
    parser = ResumeParser()
    result = parser.parse_resume("resume.pdf")
    print(json.dumps(result, indent=2))
    
    # Example 2: Match skills with job requirements
    print("\n\nExample 2: Skill Matching")
    print("-" * 50)
    matcher = SkillMatcher()
    
    job_requirements = {
        'required_skills': ['Python', 'React', 'AWS', 'Docker', 'PostgreSQL'],
        'min_experience': 3,
        'required_education': 'bachelor'
    }
    
    if "error" not in result:
        scores = matcher.score_resume(result, job_requirements)
        print(f"Overall Score: {scores['overall_score']}%")
        print(f"Recommendation: {scores['recommendation']}")
        print(f"\nMatched Skills: {', '.join(scores['skill_details']['matched_skills'])}")
        print(f"Missing Skills: {', '.join(scores['skill_details']['missing_skills'])}")
    
    # Example 3: Batch process multiple resumes
    print("\n\nExample 3: Batch Processing")
    print("-" * 50)
    processor = BatchResumeProcessor()
    
    # Process all resumes in a folder
    results = processor.process_folder(
        folder_path="./resumes",
        job_requirements=job_requirements
    )
    
    # Export results
    processor.export_results(results, "screening_results.json")
    processor.generate_report(results, "screening_report.txt")