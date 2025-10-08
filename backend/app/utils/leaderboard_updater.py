from datetime import datetime
from typing import Any

async def update_leaderboard(db: Any, team_id: str, team_name: str, region: str, current_stage: int, total_time: float):
    """
    Updates leaderboard collection with both global and regional ranks.
    Called after each successful stage completion.
    """
    now = datetime.utcnow()

    # 1. Upsert team entry in leaderboard
    await db.leaderboard.update_one(
        {"team_id": team_id},
        {"$set": {
            "team_name": team_name,
            "region": region,
            "current_stage": current_stage,
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
    Recalculates global ranks based on current_stage (desc) and total_time (asc).
    Updates the global_rank field in leaderboard.
    """
    teams = await db.leaderboard.find().sort([
        ("current_stage", -1),
        ("total_time", 1)
    ]).to_list(None)

    for rank, team in enumerate(teams, start=1):
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"global_rank": rank}}
        )


async def recalculate_regional_ranks(db: Any, region: str):
    """
    Recalculates regional ranks for a specific region.
    """
    teams = await db.leaderboard.find({"region": region}).sort([
        ("current_stage", -1),
        ("total_time", 1)
    ]).to_list(None)

    for rank, team in enumerate(teams, start=1):
        await db.leaderboard.update_one(
            {"_id": team["_id"]},
            {"$set": {"regional_rank": rank}}
        )
