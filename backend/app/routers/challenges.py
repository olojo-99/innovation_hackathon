from fastapi import APIRouter, HTTPException
from datetime import datetime
from models import ChallengeValidation, ValidationResponse
from utils.auth import verify_password
from utils.url_validator import parse_challenge_url, count_correct_values
from utils.leaderboard_updater import update_leaderboard
from database import get_database

router = APIRouter(prefix="/challenges", tags=["challenges"])

@router.post("/validate", response_model=ValidationResponse)
async def validate_submission(validation: ChallengeValidation):
    """
    Validate a challenge submission URL.
    Returns count of correct values and PDF URL if all correct.
    """
    db = await get_database()

    # 1. Authenticate team
    team = await db.teams.find_one({"team_name": validation.team_name})
    if not team:
        raise HTTPException(status_code=401, detail="Invalid team credentials")

    if not verify_password(validation.password, team["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid team credentials")

    # 2. Parse URL
    parsed = parse_challenge_url(validation.submitted_url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid URL format. Expected: ERFT_stage{N}_p1-{val1}_p2-{val2}_p3-{val3}")

    stage, p1, p2, p3 = parsed

    # 3. Get challenge from database
    challenge = await db.challenges.find_one({"stage": stage})
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge stage {stage} not found")

    # 4. Count correct values
    correct_count = count_correct_values(p1, p2, p3, challenge)

    # 5. Update latest submission URL in team document
    await db.teams.update_one(
        {"_id": team["_id"]},
        {"$set": {"last_submission_url": validation.submitted_url}}
    )

    # 6. If all correct AND first time completing this stage
    if correct_count == 3 and team["current_stage"] < stage:
        # Calculate time for this stage
        completion_time = (datetime.utcnow() - team["created_at"]).total_seconds()
        new_total_time = team["total_time"] + completion_time

        # Update team document
        await db.teams.update_one(
            {"_id": team["_id"]},
            {"$set": {
                f"stage_times.stage_{stage}": completion_time,
                "current_stage": stage,
                "total_time": new_total_time
            }}
        )

        # Update leaderboard (persists to database)
        await update_leaderboard(
            db,
            str(team["_id"]),
            team["team_name"],
            team["region"],
            stage,
            new_total_time
        )

        return ValidationResponse(
            correct_count=3,
            message="All correct! Stage unlocked.",
            pdf_url=f"/pdfs/{challenge['pdf_filename']}"
        )

    # Return partial feedback
    return ValidationResponse(
        correct_count=correct_count,
        message=f"{correct_count} out of 3 values correct",
        pdf_url=None
    )
