import re
from typing import List, Dict, Tuple
from collections import Counter

class ResumeParser:
    def __init__(self):
        # Common tech skills and technologies
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust'],
            'web': ['react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
            'tools': ['git', 'github', 'gitlab', 'jira', 'slack', 'vscode', 'intellij', 'postman'],
            'concepts': ['api', 'rest', 'graphql', 'microservices', 'devops', 'agile', 'scrum', 'tdd', 'unit testing']
        }
        
        # Job role keywords
        self.role_keywords = {
            'Software Engineer': ['software engineer', 'developer', 'programmer', 'full stack', 'backend', 'frontend'],
            'Data Scientist': ['data scientist', 'machine learning', 'data analysis', 'analytics', 'statistics'],
            'Product Manager': ['product manager', 'product owner', 'product development', 'strategy'],
            'DevOps Engineer': ['devops', 'infrastructure', 'deployment', 'automation', 'ci/cd'],
            'UI/UX Designer': ['designer', 'ui', 'ux', 'user interface', 'user experience', 'figma', 'sketch'],
            'Project Manager': ['project manager', 'project coordination', 'management', 'planning'],
            'Business Analyst': ['business analyst', 'requirements', 'analysis', 'stakeholder'],
            'Marketing Manager': ['marketing', 'digital marketing', 'seo', 'sem', 'content marketing']
        }

    def extract_text(self, content_bytes: bytes) -> str:
        """Extract and clean text from file bytes"""
        try:
            content = content_bytes.decode('utf-8', errors='ignore')
        except:
            content = content_bytes.decode('latin-1', errors='ignore')
        
        # Clean common resume artifacts
        content = re.sub(r'\s+', ' ', content)  # Multiple spaces to single
        content = re.sub(r'[^\w\s\-\.\,\!\?\;\:\@]', ' ', content)  # Remove special chars
        content = content.strip()
        
        return content

    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text"""
        found_skills = set()
        text_lower = text.lower()
        
        # Check for each skill category
        for category, skills in self.tech_skills.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill.title())
        
        # Extract additional skills using simple keyword matching
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
        words = [word for word in words if word not in ['the', 'and', 'for', 'are', 'with', 'have', 'has', 'will', 'can'] and len(word) > 2]
        
        # Look for technical terms
        tech_terms = ['api', 'database', 'system', 'application', 'development', 'engineering']
        for term in tech_terms:
            if term in words and term not in found_skills:
                found_skills.add(term.title())
        
        return sorted(list(found_skills))

    def detect_role(self, text: str) -> str:
        """Detect most likely job role based on resume content"""
        text_lower = text.lower()
        role_scores = {}
        
        for role, keywords in self.role_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Normalize by text length
            role_scores[role] = score / len(text.split()) * 1000 if text.split() else 0
        
        # Return role with highest score, or default
        if role_scores:
            best_role = max(role_scores, key=role_scores.get)
            if role_scores[best_role] > 0:
                return best_role
        
        return "Software Engineer"  # Default fallback

    def calculate_score(self, text: str, skills: List[str], detected_role: str) -> int:
        """Calculate resume score based on various factors"""
        score = 0
        
        # Base score for having content
        if len(text) > 100:
            score += 20
        
        # Skills score
        skills_score = min(len(skills) * 5, 30)  # Max 30 points for skills
        score += skills_score
        
        # Experience indicators
        experience_patterns = [
            r'\d+\+?\s*years?',  # "5 years", "10+ years"
            r'january|february|march|april|may|june|july|august|september|october|november|december',
            r'20\d{2}',  # Years like 2020, 2021
        ]
        
        experience_score = 0
        for pattern in experience_patterns:
            matches = len(re.findall(pattern, text.lower()))
            experience_score += min(matches * 2, 20)  # Max 20 points for experience
        
        score += experience_score
        
        # Education indicators
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
        education_score = sum(1 for keyword in education_keywords if keyword in text.lower())
        score += min(education_score * 3, 15)  # Max 15 points for education
        
        # Professionalism indicators
        professional_keywords = ['managed', 'developed', 'implemented', 'led', 'created', 'designed']
        professional_score = sum(1 for keyword in professional_keywords if keyword in text.lower())
        score += min(professional_score * 1, 15)  # Max 15 points for professional language
        
        return min(score, 100)  # Cap at 100

    def parse_resume(self, content_bytes: bytes, filename: str) -> Dict:
        """Main resume parsing function"""
        text = self.extract_text(content_bytes)
        
        if not text or len(text.strip()) < 50:
            return {
                "filename": filename,
                "text_preview": "Unable to extract meaningful content from resume.",
                "detected_role": "Unknown",
                "skills": [],
                "score": 0
            }
        
        # Extract components
        skills = self.extract_skills(text)
        detected_role = self.detect_role(text)
        score = self.calculate_score(text, skills, detected_role)
        
        # Create preview (first 500 chars)
        preview = text[:500] + "..." if len(text) > 500 else text
        
        return {
            "filename": filename,
            "text_preview": preview,
            "detected_role": detected_role,
            "skills": skills,
            "score": score
        }

# Global parser instance
resume_parser = ResumeParser()
