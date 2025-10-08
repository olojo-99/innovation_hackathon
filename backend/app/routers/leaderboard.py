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
    Sorted by global_rank.
    """
    db = await get_database()

    teams = await db.leaderboard.find().sort("global_rank", 1).limit(100).to_list(100)

    return [
        LeaderboardEntry(
            rank=team["global_rank"],
            team_name=team["team_name"],
            region=team["region"],
            stages_completed=team["current_stage"],
            total_time=format_time(team["total_time"])
        )
        for team in teams
    ]

@router.get("/regional/{region}", response_model=List[LeaderboardEntry])
async def get_regional_leaderboard(region: str):
    """
    Get regional leaderboard for a specific region (EMEA, AMRS, or APAC).
    Sorted by regional_rank.
    """
    # Validate region
    valid_regions = ["EMEA", "AMRS", "APAC"]
    if region not in valid_regions:
        raise HTTPException(status_code=400, detail=f"Region must be one of {valid_regions}")

    db = await get_database()

    teams = await db.leaderboard.find({"region": region}).sort("regional_rank", 1).to_list(100)

    return [
        LeaderboardEntry(
            rank=team["regional_rank"],
            team_name=team["team_name"],
            region=team["region"],
            stages_completed=team["current_stage"],
            total_time=format_time(team["total_time"])
        )
        for team in teams
    ]
