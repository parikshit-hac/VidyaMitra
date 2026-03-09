import requests
from typing import List, Dict, Optional
from app.settings import settings

class JobService:
    def __init__(self):
        self.google_api_key = settings.google_api_key
        
    def search_jobs_with_google(self, query: str, location: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search for jobs using Google Custom Search API"""
        if not self.google_api_key:
            return self._get_fallback_jobs(query, limit)
        
        # Construct search query for jobs
        search_query = f"{query} jobs careers employment"
        if location:
            search_query += f" {location}"
        
        # Use Google Custom Search API (you'll need to set up a Custom Search Engine)
        # For now, we'll use a more direct approach with job boards
        job_results = []
        
        # Search multiple job sources
        sources = [
            f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}",
            f"https://www.linkedin.com/jobs/search?keywords={query.replace(' ', '+')}",
            f"https://stackoverflow.com/jobs?q={query.replace(' ', '+')}"
        ]
        
        # Get job listings from a mock API (in real implementation, you'd use actual job APIs)
        mock_jobs = self._get_mock_job_listings(query, location, limit)
        
        return mock_jobs
    
    def _get_mock_job_listings(self, query: str, location: Optional[str], limit: int) -> List[Dict]:
        """Generate realistic mock job listings based on query"""
        
        # Job templates based on common tech roles
        job_templates = {
            'software engineer': [
                {
                    'title': 'Senior Software Engineer',
                    'company': 'TechCorp Solutions',
                    'location': location or 'San Francisco, CA',
                    'description': 'We are looking for a Senior Software Engineer to join our growing team. You will work on cutting-edge projects and help shape our technical direction.',
                    'requirements': ['5+ years of experience', 'Strong programming skills', 'Team collaboration'],
                    'salary': '$120,000 - $180,000',
                    'type': 'Full-time',
                    'posted': '2 days ago'
                },
                {
                    'title': 'Full Stack Developer',
                    'company': 'Digital Innovations Inc',
                    'location': location or 'New York, NY',
                    'description': 'Join our team as a Full Stack Developer and work on exciting web applications using modern technologies.',
                    'requirements': ['React/Node.js experience', 'Database knowledge', 'Problem-solving skills'],
                    'salary': '$100,000 - $150,000',
                    'type': 'Full-time',
                    'posted': '1 week ago'
                }
            ],
            'data scientist': [
                {
                    'title': 'Data Scientist',
                    'company': 'Analytics Pro',
                    'location': location or 'Boston, MA',
                    'description': 'We are seeking a Data Scientist to help us derive insights from complex datasets and build predictive models.',
                    'requirements': ['Python/R expertise', 'Machine learning knowledge', 'Statistics background'],
                    'salary': '$110,000 - $160,000',
                    'type': 'Full-time',
                    'posted': '3 days ago'
                }
            ],
            'product manager': [
                {
                    'title': 'Product Manager',
                    'company': 'Innovation Labs',
                    'location': location or 'Seattle, WA',
                    'description': 'Looking for an experienced Product Manager to drive product strategy and work with cross-functional teams.',
                    'requirements': ['Product management experience', 'Technical background', 'Leadership skills'],
                    'salary': '$130,000 - $180,000',
                    'type': 'Full-time',
                    'posted': '1 day ago'
                }
            ]
        }
        
        # Default jobs if no specific match
        default_jobs = [
            {
                'title': 'Software Developer',
                'company': 'Tech Startup',
                'location': location or 'Remote',
                'description': 'Join our innovative team and help build the next generation of software solutions.',
                'requirements': ['Programming experience', 'Problem-solving skills', 'Team player'],
                'salary': '$80,000 - $120,000',
                'type': 'Full-time',
                'posted': '4 days ago'
            },
            {
                'title': 'Junior Developer',
                'company': 'Growth Company',
                'location': location or 'Austin, TX',
                'description': 'Great opportunity for junior developers to grow their skills and advance their careers.',
                'requirements': ['Basic programming knowledge', 'Eagerness to learn', 'Good communication'],
                'salary': '$60,000 - $80,000',
                'type': 'Full-time',
                'posted': '1 week ago'
            }
        ]
        
        # Find matching jobs
        query_lower = query.lower()
        matched_jobs = []
        
        for role, jobs in job_templates.items():
            if role in query_lower:
                matched_jobs.extend(jobs)
        
        # If no specific matches, use default jobs
        if not matched_jobs:
            matched_jobs = default_jobs
        
        # Limit results
        return matched_jobs[:limit]
    
    def _get_fallback_jobs(self, query: str, limit: int) -> List[Dict]:
        """Fallback job listings when API is unavailable"""
        return self._get_mock_job_listings(query, None, limit)
    
    def get_job_recommendations(self, skills: List[str], experience_level: str = "mid") -> List[Dict]:
        """Get job recommendations based on user skills"""
        
        # Map skills to job roles
        skill_to_jobs = {
            'python': ['Python Developer', 'Data Scientist', 'Backend Engineer'],
            'javascript': ['Frontend Developer', 'Full Stack Developer', 'JavaScript Developer'],
            'react': ['React Developer', 'Frontend Developer', 'UI Engineer'],
            'sql': ['Database Developer', 'Data Analyst', 'Backend Engineer'],
            'aws': ['DevOps Engineer', 'Cloud Engineer', 'Solutions Architect'],
            'machine learning': ['ML Engineer', 'Data Scientist', 'AI Researcher']
        }
        
        recommended_jobs = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in skill_to_jobs:
                for job_title in skill_to_jobs[skill_lower]:
                    job = {
                        'title': job_title,
                        'company': 'Tech Company',
                        'location': 'Remote/Hybrid',
                        'description': f'Perfect match for your {skill} skills!',
                        'requirements': [f'Experience with {skill}', 'Team collaboration', 'Problem-solving'],
                        'salary': '$90,000 - $140,000',
                        'type': 'Full-time',
                        'posted': 'Recently',
                        'match_score': 85
                    }
                    recommended_jobs.append(job)
        
        return recommended_jobs[:8]  # Return top 8 recommendations

# Global job service instance
job_service = JobService()
