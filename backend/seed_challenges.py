"""
Seed script to populate MongoDB with all demo data.
Run this to initialize the database with challenges, sample teams, and leaderboard entries.
"""
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from datetime import datetime, timedelta
import asyncio

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_database():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.hackathon_db

    print("=" * 60)
    print("🌱 SEEDING HACKATHON DATABASE")
    print("=" * 60)

    # ============================================================
    # 1. SEED CHALLENGES
    # ============================================================
    print("\n📋 Step 1: Seeding Challenges...")
    await db.challenges.delete_many({})

    # Regional start times configuration
    # Note: Answers from Stage N are used to build the URL for Stage N+1
    regional_config = {
        "regional_start_times": {
            "EMEA": "2025-10-10T08:00:00Z",    # 8:00 AM UTC
            "AMRS": "2025-10-15T14:00:00Z",    # 2:00 PM UTC (9:00 AM EST)
            "APAC": "2025-10-15T00:00:00Z"     # 12:00 AM UTC (8:00 AM SGT)
        }
    }

    # IMPORTANT: Stage N problems produce values used to build the URL for Stage N+1
    # Flow:
    # - Login → Get Stage 1 PDF
    # - Solve Stage 1 problems → produces values (1,2,3)
    # - Visit ERFT_stage2_p1-1_p2-2_p3-3 → Validates against Stage 1 answers → Unlock Stage 2 PDF
    # - Solve Stage 2 problems → produces values (4,5,6)
    # - Visit ERFT_stage3_p1-4_p2-5_p3-6 → Validates against Stage 2 answers → Unlock Stage 3 PDF
    # - Solve Stage 3 problems → produces values (7,8,9)
    # - Visit ERFT_stage4_p1-7_p2-8_p3-9 → Validates against Stage 3 answers → Unlock Stage 4 PDF
    # - Solve Stage 4 problems → produces values (10,11,12)
    # - Visit ERFT_stage5_p1-10_p2-11_p3-12 → Validates against Stage 4 answers → Unlock Stage 5 PDF
    # - Stage 5 is accessibility review → Submit via /submit (no URL validation needed)
    #
    # Database schema: Each challenge stores:
    # - stage: The stage NUMBER being unlocked by this URL
    # - correct_p1/p2/p3: The answers from the PREVIOUS stage (used to validate the URL)
    # - pdf_filename: The PDF given when this stage is unlocked

    challenges = [
        {
            "stage": 1,
            "type": "dataset",
            "title": "Dataset Analysis - Fraud Detection Basics",
            "correct_p1": None,       # Given by default
            "correct_p2": None,
            "correct_p3": None,
            "pdf_filename": "stage1.pdf"  # Given when team logs in (initial PDF)
        },
        {
            "stage": 2,
            "type": "website",
            "title": "Website Feature - Dashboard Enhancement",
            "correct_p1": "1",       # ERFT_stage2_p1-1_p2-2_p3-3 (from Stage 1)
            "correct_p2": "2",
            "correct_p3": "3",
            "pdf_filename": "stage2.pdf"  # Given after submitting correct Stage 2 URL
        },
        {
            "stage": 3,
            "type": "dataset",
            "title": "Dataset Analysis - Advanced Patterns",
            "correct_p1": "4",       # ERFT_stage3_p1-4_p2-5_p3-6 (from Stage 2)
            "correct_p2": "5",
            "correct_p3": "6",
            "pdf_filename": "stage3.pdf"  # Given after submitting correct Stage 3 URL
        },
        {
            "stage": 4,
            "type": "website",
            "title": "Website Feature - Fraud Detection Module",
            "correct_p1": "7",       # ERFT_stage4_p1-7_p2-8_p3-9 (from Stage 3)
            "correct_p2": "8",
            "correct_p3": "9",
            "pdf_filename": "stage4.pdf"  # Given after submitting correct Stage 4 URL
        },
        {
            "stage": 5,
            "type": "accessibility",
            "title": "Accessibility & Usability - Final Round",
            "correct_p1": "10",      # ERFT_stage5_p1-10_p2-11_p3-12 (from Stage 4)
            "correct_p2": "11",
            "correct_p3": "12",
            "pdf_filename": "stage5.pdf"  # Given after submitting correct Stage 5 URL
        }
    ]

    # Insert regional config first
    await db.challenges.insert_one(regional_config)

    # Insert challenges
    result = await db.challenges.insert_many(challenges)
    print(f"   ✅ Seeded {len(result.inserted_ids)} challenges")
    print(f"   ✅ Configured regional start times for EMEA, AMRS, APAC")

    # ============================================================
    # 2. SEED SAMPLE TEAMS
    # ============================================================
    print("\n👥 Step 2: Seeding Sample Teams...")
    await db.teams.delete_many({})

    base_time = datetime.utcnow()

    sample_teams = [
        # EMEA Teams
        {
            "team_name": "CodeMasters_EMEA",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=5),
            "timer_started_at": base_time - timedelta(hours=5),  # Timer started when they accessed PDF
            "stages_unlocked": 3,  # 3 stages unlocked (completed stages 1-3)
            "stage_times": {
                "stage_1": 450.0,
                "stage_2": 820.0,
                "stage_3": 1200.0,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 2470.0,
            "last_submission_url": "ERFT_stage4_p1-7_p2-8_p3-9",  # Last submitted Stage 4 URL (with Stage 3 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "FraudBusters_EU",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=4),
            "timer_started_at": base_time - timedelta(hours=4),  # Timer started when they accessed PDF
            "stages_unlocked": 2,  # 2 stages unlocked (completed stages 1-2)
            "stage_times": {
                "stage_1": 600.0,
                "stage_2": 950.0,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 1550.0,
            "last_submission_url": "ERFT_stage3_p1-4_p2-5_p3-6",  # Last submitted Stage 3 URL (with Stage 2 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "DataNinjas_London",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=3),
            "timer_started_at": base_time - timedelta(hours=3),  # Timer started when they accessed PDF
            "stages_unlocked": 1,  # 1 stage unlocked (completed stage 1)
            "stage_times": {
                "stage_1": 720.0,
                "stage_2": None,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 720.0,
            "last_submission_url": "ERFT_stage2_p1-1_p2-2_p3-3",  # Last submitted Stage 2 URL (with Stage 1 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "NewTeam_EMEA",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=1),
            "timer_started_at": None,  # Haven't accessed PDF yet
            "stages_unlocked": 0,  # Registered, 0 stages unlocked (haven't completed stage 1)
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
        },
        # AMRS Teams
        {
            "team_name": "ByteForce_NYC",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=4, minutes=30),
            "timer_started_at": base_time - timedelta(hours=4, minutes=30),  # Timer started when they accessed PDF
            "stages_unlocked": 4,  # 4 stages unlocked (completed all - stages 1-4, stage 5 done but not counted)
            "stage_times": {
                "stage_1": 380.0,
                "stage_2": 720.0,
                "stage_3": 1050.0,
                "stage_4": 1400.0,
                "stage_5": None
            },
            "total_time": 3550.0,
            "last_submission_url": "ERFT_stage5_p1-10_p2-11_p3-12",  # Last submitted Stage 5 URL (with Stage 4 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "AlgoWarriors_SF",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=3, minutes=45),
            "timer_started_at": base_time - timedelta(hours=3, minutes=45),  # Timer started when they accessed PDF
            "stages_unlocked": 2,  # 2 stages unlocked (completed stages 1-2)
            "stage_times": {
                "stage_1": 520.0,
                "stage_2": 890.0,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 1410.0,
            "last_submission_url": "ERFT_stage3_p1-4_p2-5_p3-6",  # Last submitted Stage 3 URL (with Stage 2 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "HackSquad_Boston",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=2),
            "timer_started_at": None,  # Haven't accessed PDF yet
            "stages_unlocked": 0,  # Registered, 0 stages unlocked (haven't completed stage 1)
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
        },
        # APAC Teams
        {
            "team_name": "TechTitans_Mumbai",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=6),
            "timer_started_at": base_time - timedelta(hours=6),  # Timer started when they accessed PDF
            "stages_unlocked": 4,  # 4 stages unlocked (completed all including stage 5)
            "stage_times": {
                "stage_1": 420.0,
                "stage_2": 750.0,
                "stage_3": 1100.0,
                "stage_4": 1350.0,
                "stage_5": 1600.0
            },
            "total_time": 3620.0,  # Only stages 1-4 count (420+750+1100+1350)
            "last_submission_url": "ERFT_stage5_p1-10_p2-11_p3-12",  # Last submitted Stage 5 URL (with Stage 4 answers)
            "bitbucket_url": "https://bitbucket.org/techtitans/innovation-summit"  # Already submitted via /submit
        },
        {
            "team_name": "CodeSamurai_Chennai",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=5, minutes=15),
            "timer_started_at": base_time - timedelta(hours=5, minutes=15),  # Timer started when they accessed PDF
            "stages_unlocked": 3,  # 3 stages unlocked (completed stages 1-3)
            "stage_times": {
                "stage_1": 480.0,
                "stage_2": 810.0,
                "stage_3": 1180.0,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 2470.0,
            "last_submission_url": "ERFT_stage4_p1-7_p2-8_p3-9",  # Last submitted Stage 4 URL (with Stage 3 answers)
            "bitbucket_url": None
        },
        {
            "team_name": "DevDragons",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=2, minutes=30),
            "timer_started_at": base_time - timedelta(hours=2, minutes=30),  # Timer started when they accessed PDF
            "stages_unlocked": 1,  # 1 stage unlocked (completed stage 1)
            "stage_times": {
                "stage_1": 590.0,
                "stage_2": None,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 590.0,
            "last_submission_url": "ERFT_stage2_p1-1_p2-2_p3-3",  # Last submitted Stage 2 URL (with Stage 1 answers)
            "bitbucket_url": None
        }
    ]

    result = await db.teams.insert_many(sample_teams)
    print(f"   ✅ Seeded {len(result.inserted_ids)} sample teams")
    print(f"      Password for all demo teams: demo123")

    # ============================================================
    # 3. BUILD LEADERBOARD
    # ============================================================
    print("\n🏆 Step 3: Building Leaderboard...")
    await db.leaderboard.delete_many({})

    # Get ALL teams (including those with 0 stages unlocked)
    all_teams = await db.teams.find().to_list(None)

    leaderboard_entries = []
    for team in all_teams:
        leaderboard_entries.append({
            "team_id": str(team["_id"]),
            "team_name": team["team_name"],
            "region": team["region"],
            "stages_unlocked": team["stages_unlocked"],
            "total_time": team["total_time"],
            "global_rank": 0,  # Will be calculated
            "regional_rank": 0,  # Will be calculated
            "last_updated": datetime.utcnow()
        })

    if leaderboard_entries:
        await db.leaderboard.insert_many(leaderboard_entries)

    # Calculate global ranks
    # Teams with 0 stages: tied, sorted alphabetically
    # Teams with progress: sorted by stages DESC, then time ASC
    teams_with_progress = [e for e in leaderboard_entries if e["stages_unlocked"] > 0]
    teams_no_progress = [e for e in leaderboard_entries if e["stages_unlocked"] == 0]

    sorted_global = sorted(teams_with_progress,
                          key=lambda x: (-x["stages_unlocked"], x["total_time"]))
    sorted_no_progress = sorted(teams_no_progress, key=lambda x: x["team_name"])

    # Rank teams with progress
    for rank, entry in enumerate(sorted_global, start=1):
        await db.leaderboard.update_one(
            {"team_id": entry["team_id"]},
            {"$set": {"global_rank": rank}}
        )

    # Teams with no progress get rank 999 (will sort to bottom)
    for entry in sorted_no_progress:
        await db.leaderboard.update_one(
            {"team_id": entry["team_id"]},
            {"$set": {"global_rank": 999}}
        )

    # Calculate regional ranks
    for region in ["EMEA", "AMRS", "APAC"]:
        regional_teams_progress = [e for e in teams_with_progress if e["region"] == region]
        regional_teams_no_progress = [e for e in teams_no_progress if e["region"] == region]

        sorted_regional = sorted(regional_teams_progress,
                               key=lambda x: (-x["stages_unlocked"], x["total_time"]))
        sorted_regional_no_progress = sorted(regional_teams_no_progress,
                                           key=lambda x: x["team_name"])

        for rank, entry in enumerate(sorted_regional, start=1):
            await db.leaderboard.update_one(
                {"team_id": entry["team_id"]},
                {"$set": {"regional_rank": rank}}
            )

        for entry in sorted_regional_no_progress:
            await db.leaderboard.update_one(
                {"team_id": entry["team_id"]},
                {"$set": {"regional_rank": 999}}
            )

    print(f"   ✅ Built leaderboard with {len(leaderboard_entries)} entries (including teams with 0 stages)")

    # ============================================================
    # 4. SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 DATABASE SEEDING SUMMARY")
    print("=" * 60)

    print("\n📋 Challenges:")
    async for challenge in db.challenges.find({"stage": {"$exists": True}}).sort("stage", 1):
        print(f"   Stage {challenge['stage']}: {challenge['title']}")
        print(f"     Type: {challenge['type']}")
        print(f"     URL: ERFT_stage{challenge['stage']}_p1-{challenge['correct_p1']}_p2-{challenge['correct_p2']}_p3-{challenge['correct_p3']}")

    print("\n👥 Sample Teams (password: demo123):")
    for region in ["EMEA", "AMRS", "APAC"]:
        region_teams = [t for t in sample_teams if t["region"] == region]
        print(f"\n   {region}:")
        for team in region_teams:
            print(f"     • {team['team_name']} - {team['stages_unlocked']}/4 stages unlocked")

    print("\n🏆 Top 3 Global Leaderboard:")
    top_teams = await db.leaderboard.find().sort("global_rank", 1).limit(3).to_list(3)
    for team in top_teams:
        print(f"   {team['global_rank']}. {team['team_name']} ({team['region']}) - {team['stages_unlocked']}/4 unlocked, Time: {team['total_time']}s")

    print("\n" + "=" * 60)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("=" * 60)
    print("\n📝 Quick Start:")
    print("   1. Start Backend: cd backend/app && uvicorn main:app --reload")
    print("   2. Open Browser: http://localhost:8000")
    print("   (Frontend is served as static files from FastAPI)")
    print("\n🔐 Test Login: Use any team name above with password 'demo123'")
    print("\n")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
