from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import connect_to_mongo, close_mongo_connection, get_database
from routers import teams, challenges, leaderboard
from utils.leaderboard_updater import update_leaderboard
from utils.url_validator import parse_challenge_url, count_correct_values
from utils.auth import verify_password
from utils.time_validator import is_challenge_open, format_utc_time
from models import FinalSubmission
from datetime import datetime

app = FastAPI(title="Hackathon Platform API")
templates = Jinja2Templates(directory="templates")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/pdfs", StaticFiles(directory="../../pdfs"), name="pdfs")
app.mount("/css", StaticFiles(directory="../../frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="../../frontend/js"), name="js")

# Include routers
app.include_router(teams.router)
app.include_router(challenges.router, prefix="/api")
app.include_router(leaderboard.router)

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def root_redirect():
    """Redirect root to register"""
    return HTMLResponse(content='<script>window.location.href="/register"</script>')

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Serve registration page"""
    with open("../../frontend/register.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve login page"""
    with open("../../frontend/login.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page():
    """Serve leaderboard page"""
    with open("../../frontend/leaderboard_page.html", "r") as f:
        return HTMLResponse(content=f.read())

# URL-based Challenge Validation Route
@app.get("/ERFT_stage{stage}_p1-{p1}_p2-{p2}_p3-{p3}", response_class=HTMLResponse)
async def validate_challenge_url(request: Request, stage: int, p1: str, p2: str, p3: str, team: str = None, pwd: str = None):
    """
    Direct URL validation - users visit this URL to validate their challenge answers.
    Enforces sequential stage progression and regional time gates.
    """
    db = await get_database()
    challenge_url = f"ERFT_stage{stage}_p1-{p1}_p2-{p2}_p3-{p3}"

    # If no auth params, show auth form
    if not team or not pwd:
        return templates.TemplateResponse("auth_required.html", {
            "request": request,
            "challenge_url": challenge_url,
            "stage": stage
        })

    # Authenticate team
    team_doc = await db.teams.find_one({"team_name": team})
    if not team_doc or not verify_password(pwd, team_doc["password_hash"]):
        return templates.TemplateResponse("auth_required.html", {
            "request": request,
            "challenge_url": challenge_url,
            "stage": stage,
            "error": "Invalid credentials"
        })

    # Check if challenge is open for this region
    challenge_open, start_time = await is_challenge_open(team_doc["region"], db)
    if not challenge_open:
        return templates.TemplateResponse("challenge_not_open.html", {
            "request": request,
            "region": team_doc["region"],
            "start_time": format_utc_time(start_time) if start_time else "TBD"
        })

    # Get challenge
    challenge = await db.challenges.find_one({"stage": stage})
    if not challenge:
        return HTMLResponse(content="<h1>Invalid challenge stage</h1>", status_code=404)

    # Get current progress
    stages_unlocked = team_doc.get("stages_unlocked", team_doc.get("current_stage", 0))

    # Count correct values first (needed for all paths)
    correct_count = count_correct_values(p1, p2, p3, challenge)

    # Determine what stage would be unlocked by this URL
    # Stage 2 URL unlocks stage 1, Stage 3 URL unlocks stage 2, etc.
    stage_being_unlocked = stage - 1

    # Sequential progression check:
    # - If stages_unlocked = 0, they can unlock stage 1 (visit stage 2 URL)
    # - If stages_unlocked = 1, they can unlock stage 2 (visit stage 3 URL)
    # - etc.
    # So: stage_being_unlocked should equal (stages_unlocked + 1) for next stage

    # Check if trying to skip ahead
    if stage_being_unlocked > stages_unlocked + 1:
        # Trying to unlock a stage beyond the next one
        return templates.TemplateResponse("sequential_error.html", {
            "request": request,
            "stages_unlocked": stages_unlocked,
            "attempted_stage": stage
        })

    # Update latest submission URL
    await db.teams.update_one(
        {"_id": team_doc["_id"]},
        {"$set": {"last_submission_url": challenge_url}}
    )

    # Handle correct values - show same UI for first-time and revisits
    if correct_count == 3:
        is_first_time = (stage_being_unlocked == stages_unlocked + 1)

        # Only update DB on first-time completion
        if is_first_time:
            # Use timer_started_at if available, otherwise fall back to created_at
            timer_start = team_doc.get("timer_started_at") or team_doc["created_at"]
            completion_time = (datetime.utcnow() - timer_start).total_seconds()
            new_total_time = team_doc["total_time"] + completion_time

            # Update team document
            await db.teams.update_one(
                {"_id": team_doc["_id"]},
                {"$set": {
                    f"stage_times.stage_{stage_being_unlocked}": completion_time,
                    "stages_unlocked": stage_being_unlocked,
                    "total_time": new_total_time
                }}
            )

            # Update leaderboard
            await update_leaderboard(
                db,
                str(team_doc["_id"]),
                team_doc["team_name"],
                team_doc["region"],
                stage_being_unlocked,
                new_total_time
            )

        # Show consistent UI for both first-time and revisits
        is_final_stage = (stage_being_unlocked == 4)

        return templates.TemplateResponse("validation_result.html", {
            "request": request,
            "all_correct": True,
            "stage": stage,
            "stage_unlocked": stage_being_unlocked,
            "pdf_url": f"/pdfs/{challenge['pdf_filename']}",
            "is_final_stage": is_final_stage
        })

    # Return partial feedback for incorrect values
    return templates.TemplateResponse("validation_result.html", {
        "request": request,
        "all_correct": False,
        "correct_count": correct_count,
        "stage": stage
    })

# Final Submission Routes
@app.get("/submit", response_class=HTMLResponse)
async def submit_final_page():
    """Serve final submission page"""
    with open("../../frontend/final_submission.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/submit")
async def submit_final(submission: FinalSubmission):
    """
    Submit final BitBucket URL after completing stage 5.
    """
    db = await get_database()

    # Authenticate team
    team_doc = await db.teams.find_one({"team_name": submission.team_name})
    if not team_doc or not verify_password(submission.password, team_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify team has completed all stages (needs 4/4 stages unlocked and stage 5 completed)
    stages_unlocked = team_doc.get("stages_unlocked", 0)

    if stages_unlocked < 4:
        raise HTTPException(
            status_code=400,
            detail=f"Team must complete all stages before final submission. Current: {stages_unlocked}/4 unlocked."
        )

    # Update team with BitBucket URL
    await db.teams.update_one(
        {"_id": team_doc["_id"]},
        {"$set": {"bitbucket_url": submission.bitbucket_url}}
    )

    return {"message": "Final submission successful!", "bitbucket_url": submission.bitbucket_url}

@app.on_event("startup")
async def startup_event():
    """
    Connect to MongoDB and rebuild leaderboard from teams collection.
    Ensures persistence after server restarts.
    Now includes ALL teams (even those with 0 stages unlocked).
    """
    await connect_to_mongo()

    print("Rebuilding leaderboard from teams collection...")
    db = await get_database()

    # Clear existing leaderboard
    await db.leaderboard.delete_many({})

    # Rebuild from ALL teams (including those with 0 stages)
    teams_list = await db.teams.find().to_list(None)

    for team in teams_list:
        await update_leaderboard(
            db,
            str(team["_id"]),
            team["team_name"],
            team["region"],
            team.get("stages_unlocked", team.get("current_stage", 0)),
            team["total_time"]
        )

    print(f"✅ Leaderboard rebuilt successfully with {len(teams_list)} teams")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "ok"}
