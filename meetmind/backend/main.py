from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from database.models import create_tables
from routes.analyze import router as analyze_router
from routes.meetings import router as meetings_router

# Create DB tables on startup
create_tables()

app = FastAPI(
    title="MeetMind API",
    description="AI Meeting Notes & Summarizer Backend",
    version="1.0.0"
)

# CORS — allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(meetings_router, prefix="/api", tags=["Meetings"])


@app.get("/")
def root():
    return {"message": "MeetMind API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
