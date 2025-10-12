from fastapi import APIRouter, HTTPException
from datetime import datetime
from models import TeamCreate, TeamResponse
from utils.auth import hash_password, verify_password
from utils.time_validator import is_challenge_open, format_utc_time
from utils.leaderboard_updater import update_leaderboard
from database import get_database

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/create", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """
    Create a new team with team name, password, and region.
    Team starts with 0 stages unlocked. Stage 1 becomes accessible when regional start time is reached.
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
        "timer_started_at": None,  # Will be set when Stage 1 PDF is accessed
        "stages_unlocked": 0,  # 0 stages unlocked (haven't completed stage 1)
        "stage_times": {
            "stage_1": None,
            "stage_2": None,
            "stage_3": None,
            "stage_4": None,
            "stage_5": None
        },
        "total_time": 0.0,
        "last_submission_url": "",
        "bitbucket_url": None
    }

    # Insert into database
    result = await db.teams.insert_one(team_doc)

    # Add team to leaderboard immediately (with 0 stages unlocked)
    await update_leaderboard(
        db,
        str(result.inserted_id),
        team.team_name,
        team.region,
        0,  # 0 stages unlocked
        0.0
    )

    # Check if challenge is open for this region
    challenge_open, start_time = await is_challenge_open(team.region, db)

    return TeamResponse(
        team_name=team.team_name,
        region=team.region,
        current_stage=0,
        total_time=0.0,
        challenge_open=challenge_open,
        start_time=format_utc_time(start_time) if start_time else None
    )

@router.post("/login", response_model=TeamResponse)
async def login_team(team: TeamCreate):
    """
    Login existing team and return their current progress.
    Checks if challenge is open for their region.
    """
    db = await get_database()

    # Find team
    team_doc = await db.teams.find_one({"team_name": team.team_name})
    if not team_doc:
        raise HTTPException(status_code=404, detail="Team not found")

    # Verify password
    if not verify_password(team.password, team_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Check if challenge is open for this region
    challenge_open, start_time = await is_challenge_open(team_doc["region"], db)

    return TeamResponse(
        team_name=team_doc["team_name"],
        region=team_doc["region"],
        current_stage=team_doc.get("stages_unlocked", team_doc.get("current_stage", 0)),
        total_time=team_doc["total_time"],
        challenge_open=challenge_open,
        start_time=format_utc_time(start_time) if start_time else None
    )

@router.post("/start-timer")
async def start_timer(team: TeamCreate):
    """
    Start the timer for a team when they access the Stage 1 PDF for the first time.
    This should be called when the user clicks to download/view the Stage 1 PDF.
    """
    db = await get_database()

    # Find team
    team_doc = await db.teams.find_one({"team_name": team.team_name})
    if not team_doc:
        raise HTTPException(status_code=404, detail="Team not found")

    # Verify password
    if not verify_password(team.password, team_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Check if timer already started
    if team_doc.get("timer_started_at") is not None:
        return {"message": "Timer already started", "timer_started": True}

    # Start the timer
    await db.teams.update_one(
        {"_id": team_doc["_id"]},
        {"$set": {"timer_started_at": datetime.utcnow()}}
    )

    return {"message": "Timer started successfully", "timer_started": True}
