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

    challenges = [
        {
            "stage": 1,
            "type": "dataset",
            "title": "Dataset Analysis - Problem 1",
            "correct_p1": "142",     # Sample: Count of duplicate Transaction_IDs
            "correct_p2": "38",      # Sample: Percentage of fraudulent transactions
            "correct_p3": "1847",    # Sample: Count of transactions over $500
            "pdf_filename": "stage2.pdf"  # Completing stage 1 unlocks stage 2
        },
        {
            "stage": 2,
            "type": "website",
            "title": "Website Feature - Dashboard Enhancement",
            "correct_p1": "298",     # Sample: Number of components added
            "correct_p2": "345",     # Sample: Lines of code written
            "correct_p3": "231",     # Sample: Test cases passed
            "pdf_filename": "stage3.pdf"  # Completing stage 2 unlocks stage 3
        },
        {
            "stage": 3,
            "type": "dataset",
            "title": "Dataset Analysis - Problem 2",
            "correct_p1": "Tokyo",   # Sample: City with most fraudulent transactions
            "correct_p2": "67",      # Sample: Average transaction amount for fraud
            "correct_p3": "842",     # Sample: Transactions with failed authentication
            "pdf_filename": "stage4.pdf"  # Completing stage 3 unlocks stage 4
        },
        {
            "stage": 4,
            "type": "website",
            "title": "Website Feature - Fraud Detection Module",
            "correct_p1": "5",       # Sample: Number of fraud detection algorithms implemented
            "correct_p2": "94",      # Sample: Accuracy percentage achieved
            "correct_p3": "127",     # Sample: False positives detected
            "pdf_filename": "stage5.pdf"  # Completing stage 4 unlocks stage 5
        },
        {
            "stage": 5,
            "type": "dataset",
            "title": "Dataset Analysis - Problem 3 + Accessibility Tasks (FINAL)",
            "correct_p1": "Biometric",  # Sample: Most secure authentication method
            "correct_p2": "1456",       # Sample: Average transaction distance for fraud
            "correct_p3": "12",         # Sample: Accessibility issues fixed
            "pdf_filename": "stage5.pdf"  # Final stage with congrats + accessibility/usability tasks
        }
    ]

    result = await db.challenges.insert_many(challenges)
    print(f"   ✅ Seeded {len(result.inserted_ids)} challenges")

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
            "current_stage": 3,
            "stage_times": {
                "stage_1": 450.0,
                "stage_2": 820.0,
                "stage_3": 1200.0,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 2470.0,
            "last_submission_url": "ERFT_stage3_p1-answer1_p2-answer2_p3-answer3"
        },
        {
            "team_name": "FraudBusters_EU",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=4),
            "current_stage": 2,
            "stage_times": {
                "stage_1": 600.0,
                "stage_2": 950.0,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 1550.0,
            "last_submission_url": "ERFT_stage2_p1-feature1_p2-feature2_p3-feature3"
        },
        {
            "team_name": "DataNinjas_London",
            "password_hash": hash_password("demo123"),
            "region": "EMEA",
            "created_at": base_time - timedelta(hours=3),
            "current_stage": 1,
            "stage_times": {
                "stage_1": 720.0,
                "stage_2": None,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 720.0,
            "last_submission_url": "ERFT_stage1_p1-21_p2-69_p3-420"
        },
        # AMRS Teams
        {
            "team_name": "ByteForce_NYC",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=4, minutes=30),
            "current_stage": 4,
            "stage_times": {
                "stage_1": 380.0,
                "stage_2": 720.0,
                "stage_3": 1050.0,
                "stage_4": 1400.0,
                "stage_5": None
            },
            "total_time": 3550.0,
            "last_submission_url": "ERFT_stage4_p1-module1_p2-module2_p3-module3"
        },
        {
            "team_name": "AlgoWarriors_SF",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=3, minutes=45),
            "current_stage": 2,
            "stage_times": {
                "stage_1": 520.0,
                "stage_2": 890.0,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 1410.0,
            "last_submission_url": "ERFT_stage2_p1-feature1_p2-feature2_p3-feature3"
        },
        {
            "team_name": "HackSquad_Boston",
            "password_hash": hash_password("demo123"),
            "region": "AMRS",
            "created_at": base_time - timedelta(hours=2),
            "current_stage": 1,
            "stage_times": {
                "stage_1": 650.0,
                "stage_2": None,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 650.0,
            "last_submission_url": "ERFT_stage1_p1-21_p2-69_p3-420"
        },
        # APAC Teams
        {
            "team_name": "TechTitans_Tokyo",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=6),
            "current_stage": 5,
            "stage_times": {
                "stage_1": 420.0,
                "stage_2": 750.0,
                "stage_3": 1100.0,
                "stage_4": 1350.0,
                "stage_5": 1600.0
            },
            "total_time": 5220.0,
            "last_submission_url": "ERFT_stage5_p1-final1_p2-final2_p3-final3"  # Completed all stages!
        },
        {
            "team_name": "CodeSamurai_Singapore",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=5, minutes=15),
            "current_stage": 3,
            "stage_times": {
                "stage_1": 480.0,
                "stage_2": 810.0,
                "stage_3": 1180.0,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 2470.0,
            "last_submission_url": "ERFT_stage3_p1-answer1_p2-answer2_p3-answer3"
        },
        {
            "team_name": "DevDragons_Sydney",
            "password_hash": hash_password("demo123"),
            "region": "APAC",
            "created_at": base_time - timedelta(hours=2, minutes=30),
            "current_stage": 2,
            "stage_times": {
                "stage_1": 590.0,
                "stage_2": 920.0,
                "stage_3": None,
                "stage_4": None,
                "stage_5": None
            },
            "total_time": 1510.0,
            "last_submission_url": "ERFT_stage2_p1-feature1_p2-feature2_p3-feature3"
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

    # Get all teams and create leaderboard entries
    all_teams = await db.teams.find().to_list(None)

    leaderboard_entries = []
    for team in all_teams:
        if team["current_stage"] > 0:
            leaderboard_entries.append({
                "team_id": str(team["_id"]),
                "team_name": team["team_name"],
                "region": team["region"],
                "current_stage": team["current_stage"],
                "total_time": team["total_time"],
                "global_rank": 0,  # Will be calculated
                "regional_rank": 0,  # Will be calculated
                "last_updated": datetime.utcnow()
            })

    if leaderboard_entries:
        await db.leaderboard.insert_many(leaderboard_entries)

    # Calculate global ranks
    sorted_global = sorted(leaderboard_entries,
                          key=lambda x: (-x["current_stage"], x["total_time"]))
    for rank, entry in enumerate(sorted_global, start=1):
        await db.leaderboard.update_one(
            {"team_id": entry["team_id"]},
            {"$set": {"global_rank": rank}}
        )

    # Calculate regional ranks
    for region in ["EMEA", "AMRS", "APAC"]:
        regional_teams = [e for e in leaderboard_entries if e["region"] == region]
        sorted_regional = sorted(regional_teams,
                               key=lambda x: (-x["current_stage"], x["total_time"]))
        for rank, entry in enumerate(sorted_regional, start=1):
            await db.leaderboard.update_one(
                {"team_id": entry["team_id"]},
                {"$set": {"regional_rank": rank}}
            )

    print(f"   ✅ Built leaderboard with {len(leaderboard_entries)} entries")

    # ============================================================
    # 4. SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 DATABASE SEEDING SUMMARY")
    print("=" * 60)

    print("\n📋 Challenges:")
    async for challenge in db.challenges.find().sort("stage", 1):
        print(f"   Stage {challenge['stage']}: {challenge['title']}")
        print(f"     Type: {challenge['type']}")
        print(f"     URL: ERFT_stage{challenge['stage']}_p1-{challenge['correct_p1']}_p2-{challenge['correct_p2']}_p3-{challenge['correct_p3']}")

    print("\n👥 Sample Teams (password: demo123):")
    for region in ["EMEA", "AMRS", "APAC"]:
        region_teams = [t for t in sample_teams if t["region"] == region]
        print(f"\n   {region}:")
        for team in region_teams:
            print(f"     • {team['team_name']} - Stage {team['current_stage']}/5")

    print("\n🏆 Top 3 Global Leaderboard:")
    top_teams = await db.leaderboard.find().sort("global_rank", 1).limit(3).to_list(3)
    for team in top_teams:
        print(f"   {team['global_rank']}. {team['team_name']} ({team['region']}) - Stage {team['current_stage']}, Time: {team['total_time']}s")

    print("\n" + "=" * 60)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("=" * 60)
    print("\n📝 Quick Start:")
    print("   1. Start Backend: cd backend/app && uvicorn main:app --reload")
    print("   2. Start Frontend: cd frontend && python -m http.server 3000")
    print("   3. Open Browser: http://localhost:3000")
    print("\n🔐 Test Login: Use any team name above with password 'demo123'")
    print("\n")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
