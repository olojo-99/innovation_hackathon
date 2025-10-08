from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class TeamCreate(BaseModel):
    team_name: str
    password: str
    region: str  # EMEA, AMRS, APAC

class TeamResponse(BaseModel):
    team_name: str
    region: str
    current_stage: int
    total_time: float
    stage1_pdf_url: str = "/pdfs/stage1.pdf"  # Always provide stage 1 PDF on registration

class ChallengeValidation(BaseModel):
    team_name: str
    password: str
    submitted_url: str

class ValidationResponse(BaseModel):
    correct_count: int
    message: str
    pdf_url: Optional[str] = None

class LeaderboardEntry(BaseModel):
    rank: int
    team_name: str
    region: str
    stages_completed: int
    total_time: str

class Challenge(BaseModel):
    stage: int
    type: str  # "website" or "dataset"
    title: str
    correct_p1: str
    correct_p2: str
    correct_p3: str
    pdf_filename: str

# Database document schemas
class TeamDocument(BaseModel):
    team_name: str
    password_hash: str
    region: str
    created_at: datetime
    current_stage: int = 0
    stage_times: Dict[str, Optional[float]] = Field(default_factory=lambda: {
        "stage_1": None,
        "stage_2": None,
        "stage_3": None,
        "stage_4": None,
        "stage_5": None
    })
    total_time: float = 0.0
    last_submission_url: str = ""

class LeaderboardDocument(BaseModel):
    team_id: str
    team_name: str
    region: str
    current_stage: int
    total_time: float
    global_rank: int = 0
    regional_rank: int = 0
    last_updated: datetime
