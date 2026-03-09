# VidyaMitra

VidyaMitra is an AI-powered career support platform built to help students, graduates, and job seekers improve employability through resume analysis, skill evaluation, mock interviews, quizzes, career planning, and learning guidance.

It combines a FastAPI backend, a React frontend, database persistence, and AI-driven generation/evaluation features.

## What This Project Does

VidyaMitra helps users:

- upload and analyze resumes
- identify skill gaps for a target role
- evaluate role readiness dynamically
- practice AI-generated mock interviews
- generate dynamic quizzes by topic and level
- create career transition roadmaps
- view progress metrics across modules
- explore learning resources and market insights

## Main Features

### 1. Resume Analysis
- Upload PDF resumes
- Extract text from the uploaded file
- Analyze identified skills and missing skills for a target role
- Generate AI summary and structured guidance
- Suggest recommended learning resources

### 2. Dynamic Skills Evaluation
- Evaluate role readiness using:
  - current skills
  - years of experience
  - education level
  - project highlights
  - certifications
- Generate:
  - eligibility score
  - skill breakdown
  - improvement areas
  - recommendations
  - confidence reasoning
- Save evaluation history to the database

### 3. Interview Simulator
- Generate dynamic interview questions for a chosen role
- Create interview sessions
- Submit answers one by one
- Get evaluation on:
  - tone
  - confidence
  - accuracy
- Persist interview session history

### 4. Career Planner
- Generate dynamic role transition roadmaps
- Show:
  - transferable strengths
  - skill gaps
  - certifications
  - learning path
  - weekly plan
- Save career plans for later review

### 5. Dynamic Quiz
- Generate AI-powered MCQ quizzes by topic and level
- Submit answers and calculate score
- Show feedback
- Save quiz history

### 6. Dashboard
- Display progress and engagement summary
- Show counts for:
  - resumes
  - interviews
  - roadmaps
  - quizzes
  - skill evaluations
- Show average scores

### 7. Learning Resources and Market Insights
- Resource-related backend services exist for learning support, visual resources, and market/news integrations
- These depend on configured provider/API keys

## Tech Stack

### Frontend
- React
- Vite
- React Router
- Axios
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Python

### Database
- SQLite by default
- PostgreSQL supported via `DATABASE_URL`

### AI / External Integrations
- Groq API
- xAI/Grok-compatible configuration aliases
- YouTube API
- Google Custom Search API
- Pexels API
- News API
- Supabase Storage

## Project Structure

```text
VidyaMitra/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
└── README.md