from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import connect_to_mongo, close_mongo_connection, get_database
from routers import teams, challenges, leaderboard
from utils.leaderboard_updater import update_leaderboard
from utils.url_validator import parse_challenge_url, count_correct_values
from utils.auth import verify_password
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
    """
    db = await get_database()
    challenge_url = f"ERFT_stage{stage}_p1-{p1}_p2-{p2}_p3-{p3}"

    # If no auth params, show auth form
    if not team or not pwd:
        return templates.TemplateResponse("auth_required.html", {
            "request": request,
            "challenge_url": challenge_url
        })

    # Authenticate team
    team_doc = await db.teams.find_one({"team_name": team})
    if not team_doc or not verify_password(pwd, team_doc["password_hash"]):
        return templates.TemplateResponse("auth_required.html", {
            "request": request,
            "challenge_url": challenge_url,
            "error": "Invalid credentials"
        })

    # Get challenge
    challenge = await db.challenges.find_one({"stage": stage})
    if not challenge:
        return HTMLResponse(content="<h1>Invalid challenge stage</h1>", status_code=404)

    # Count correct values
    correct_count = count_correct_values(p1, p2, p3, challenge)

    # Update latest submission URL
    await db.teams.update_one(
        {"_id": team_doc["_id"]},
        {"$set": {"last_submission_url": challenge_url}}
    )

    # If all correct AND first time completing this stage
    if correct_count == 3 and team_doc["current_stage"] < stage:
        completion_time = (datetime.utcnow() - team_doc["created_at"]).total_seconds()
        new_total_time = team_doc["total_time"] + completion_time

        # Update team document
        await db.teams.update_one(
            {"_id": team_doc["_id"]},
            {"$set": {
                f"stage_times.stage_{stage}": completion_time,
                "current_stage": stage,
                "total_time": new_total_time
            }}
        )

        # Update leaderboard
        await update_leaderboard(
            db,
            str(team_doc["_id"]),
            team_doc["team_name"],
            team_doc["region"],
            stage,
            new_total_time
        )

        return templates.TemplateResponse("validation_result.html", {
            "request": request,
            "all_correct": True,
            "stage": stage,
            "pdf_url": f"/pdfs/{challenge['pdf_filename']}"
        })

    # Return partial feedback
    return templates.TemplateResponse("validation_result.html", {
        "request": request,
        "all_correct": False,
        "correct_count": correct_count,
        "stage": stage
    })

@app.on_event("startup")
async def startup_event():
    """
    Connect to MongoDB and rebuild leaderboard from teams collection.
    Ensures persistence after server restarts.
    """
    await connect_to_mongo()

    print("Rebuilding leaderboard from teams collection...")
    db = await get_database()

    # Clear existing leaderboard
    await db.leaderboard.delete_many({})

    # Rebuild from teams with progress
    teams_list = await db.teams.find({"current_stage": {"$gt": 0}}).to_list(None)

    for team in teams_list:
        await update_leaderboard(
            db,
            str(team["_id"]),
            team["team_name"],
            team["region"],
            team["current_stage"],
            team["total_time"]
        )

    print(f"✅ Leaderboard rebuilt successfully with {len(teams_list)} teams")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Hackathon Platform API is running", "status": "healthy"}

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "ok"}
