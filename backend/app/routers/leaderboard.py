from fastapi import APIRouter, HTTPException
from typing import List
from models import LeaderboardEntry
from database import get_database

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

def format_time(seconds: float) -> str:
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

@router.get("/global", response_model=List[LeaderboardEntry])
async def get_global_leaderboard():
    """
    Get global leaderboard (all teams across all regions).
    Teams with progress ranked first, then teams with 0 stages (tied, alphabetical).
    """
    db = await get_database()

    # Get all teams, sort by rank then alphabetically
    teams = await db.leaderboard.find().sort([("global_rank", 1), ("team_name", 1)]).to_list(1000)

    return [
        LeaderboardEntry(
            rank="T" if team["global_rank"] == 999 else str(team["global_rank"]),
            team_name=team["team_name"],
            region=team["region"],
            stages_unlocked=team.get("stages_unlocked", team.get("current_stage", 0)),
            total_time="-" if team.get("stages_unlocked", team.get("current_stage", 0)) == 0 else format_time(team["total_time"])
        )
        for team in teams
    ]

@router.get("/regional/{region}", response_model=List[LeaderboardEntry])
async def get_regional_leaderboard(region: str):
    """
    Get regional leaderboard for a specific region (EMEA, AMRS, or APAC).
    Teams with progress ranked first, then teams with 0 stages (tied, alphabetical).
    """
    # Validate region
    valid_regions = ["EMEA", "AMRS", "APAC"]
    if region not in valid_regions:
        raise HTTPException(status_code=400, detail=f"Region must be one of {valid_regions}")

    db = await get_database()

    teams = await db.leaderboard.find({"region": region}).sort([("regional_rank", 1), ("team_name", 1)]).to_list(1000)

    return [
        LeaderboardEntry(
            rank="T" if team["regional_rank"] == 999 else str(team["regional_rank"]),
            team_name=team["team_name"],
            region=team["region"],
            stages_unlocked=team.get("stages_unlocked", team.get("current_stage", 0)),
            total_time="-" if team.get("stages_unlocked", team.get("current_stage", 0)) == 0 else format_time(team["total_time"])
        )
        for team in teams
    ]
