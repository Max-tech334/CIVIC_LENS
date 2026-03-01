from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Absolute imports to avoid those earlier relative import errors
from app import models, schemas
from app.database import SessionLocal, engine

# Initialize the FastAPI app
app = FastAPI(
    title="Civic Lens API",
    description="Laboratory endpoints for Donors, Candidates, and Donations",
    version="1.0.0"
)

# CORS Middleware: This is CRUCIAL. It allows your React app (running on a different port) 
# to talk to this Python backend without the browser blocking it for security reasons.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], # React/Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- THE ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "success", "message": "Welcome to the Civic Lens Laboratory API"}

@app.get("/api/candidates")
def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetches a list of political candidates."""
    candidates = db.query(models.Candidate).offset(skip).limit(limit).all()
    return candidates

@app.get("/api/donors")
def get_donors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetches a list of donors."""
    donors = db.query(models.Donor).offset(skip).limit(limit).all()
    return donors

@app.get("/api/donations")
def get_donations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetches a list of donations linking donors to candidates."""
    donations = db.query(models.Donation).offset(skip).limit(limit).all()
    return donations