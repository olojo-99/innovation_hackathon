from fastapi import APIRouter, HTTPException
from datetime import datetime
from models import TeamCreate, TeamResponse
from utils.auth import hash_password
from database import get_database

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/create", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """
    Create a new team with team name, password, and region.
    """
    db = await get_database()

    # Check if team name already exists
    existing_team = await db.teams.find_one({"team_name": team.team_name})
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")

    # Validate region
    valid_regions = ["EMEA", "AMRS", "APAC"]
    if team.region not in valid_regions:
        raise HTTPException(status_code=400, detail=f"Region must be one of {valid_regions}")

    # Create team document
    team_doc = {
        "team_name": team.team_name,
        "password_hash": hash_password(team.password),
        "region": team.region,
        "created_at": datetime.utcnow(),
        "current_stage": 0,
        "stage_times": {
            "stage_1": None,
            "stage_2": None,
            "stage_3": None,
            "stage_4": None,
            "stage_5": None
        },
        "total_time": 0.0,
        "last_submission_url": ""
    }

    # Insert into database
    await db.teams.insert_one(team_doc)

    return TeamResponse(
        team_name=team.team_name,
        region=team.region,
        current_stage=0,
        total_time=0.0
    )
