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
    challenge_open: bool = False  # Whether challenge has started for this region
    start_time: Optional[str] = None  # UTC start time for display

class ChallengeValidation(BaseModel):
    team_name: str
    password: str
    submitted_url: str

class ValidationResponse(BaseModel):
    correct_count: int
    message: str
    pdf_url: Optional[str] = None

class LeaderboardEntry(BaseModel):
    rank: str  # Can be number or "T" for tied
    team_name: str
    region: str
    stages_unlocked: int  # Renamed from stages_completed
    total_time: str  # Will show "-" for teams with 0 stages

class Challenge(BaseModel):
    stage: int
    type: str  # "website" or "dataset"
    title: str
    correct_p1: str
    correct_p2: str
    correct_p3: str
    pdf_filename: str

class FinalSubmission(BaseModel):
    team_name: str
    password: str
    bitbucket_url: str

# Database document schemas
class TeamDocument(BaseModel):
    team_name: str
    password_hash: str
    region: str
    created_at: datetime
    current_stage: int = 0  # Represents stages unlocked (0-5)
    stage_times: Dict[str, Optional[float]] = Field(default_factory=lambda: {
        "stage_1": None,
        "stage_2": None,
        "stage_3": None,
        "stage_4": None,
        "stage_5": None
    })
    total_time: float = 0.0
    last_submission_url: str = ""
    bitbucket_url: Optional[str] = None  # Final submission URL

class LeaderboardDocument(BaseModel):
    team_id: str
    team_name: str
    region: str
    current_stage: int
    total_time: float
    global_rank: int = 0
    regional_rank: int = 0
    last_updated: datetime
