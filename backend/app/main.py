from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
import app.models  # noqa: F401
from app.routers import auth, career, evaluate, interview, progress, quiz, resources, resume


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(career.router)
app.include_router(resources.router)
app.include_router(evaluate.router)
app.include_router(quiz.router)
app.include_router(progress.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "VidyaMitra backend is running"}
