from datetime import datetime
from typing import Any

async def update_leaderboard(db: Any, team_id: str, team_name: str, region: str, stages_unlocked: int, total_time: float):
    """
    Updates leaderboard collection with both global and regional ranks.
    Called after each successful stage completion (stages 1-4 only).
    """
    now = datetime.utcnow()

    # 1. Upsert team entry in leaderboard
    await db.leaderboard.update_one(
        {"team_id": team_id},
        {"$set": {
            "team_name": team_name,
            "region": region,
            "stages_unlocked": stages_unlocked,
            "total_time": total_time,
            "last_updated": now
        }},
        upsert=True
    )

    # 2. Recalculate global ranks (all teams)
    await recalculate_global_ranks(db)

    # 3. Recalculate regional ranks (just this region)
    await recalculate_regional_ranks(db, region)


async def recalculate_global_ranks(db: Any):
    """
    Recalculates global ranks based on stages_unlocked (desc) and total_time (asc).
    Teams with 0 stages get rank 999 and are sorted alphabetically.
    """
    # Get teams with progress
    teams_with_progress = await db.leaderboard.find({"stages_unlocked": {"$gt": 0}}).sort([
        ("stages_unlocked", -1),
        ("total_time", 1)
    ]).to_list(None)

    # Get teams with no progress
    teams_no_progress = await db.leaderboard.find({"stages_unlocked": 0}).sort([
        ("team_name", 1)
    ]).to_list(None)

    # Rank teams with progress
    for rank, team in enumerate(teams_with_progress, start=1):
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"global_rank": rank}}
        )

    # Teams with no progress get rank 999
    for team in teams_no_progress:
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"global_rank": 999}}
        )


async def recalculate_regional_ranks(db: Any, region: str):
    """
    Recalculates regional ranks for a specific region.
    Teams with 0 stages get rank 999 and are sorted alphabetically.
    """
    # Get teams with progress in this region
    teams_with_progress = await db.leaderboard.find({
        "region": region,
        "stages_unlocked": {"$gt": 0}
    }).sort([
        ("stages_unlocked", -1),
        ("total_time", 1)
    ]).to_list(None)

    # Get teams with no progress in this region
    teams_no_progress = await db.leaderboard.find({
        "region": region,
        "stages_unlocked": 0
    }).sort([
        ("team_name", 1)
    ]).to_list(None)

    # Rank teams with progress
    for rank, team in enumerate(teams_with_progress, start=1):
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"regional_rank": rank}}
        )

    # Teams with no progress get rank 999
    for team in teams_no_progress:
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"regional_rank": 999}}
        )
