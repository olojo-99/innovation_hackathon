# International Hackathon Platform

A multi-regional hackathon platform featuring challenge tracking, URL-based stage unlocking, and real-time leaderboards for EMEA, AMRS, and APAC regions.

## Features

- **Multi-Regional Support**: Teams from EMEA, AMRS, and APAC compete with regional and global leaderboards
- **5-Stage Challenge System**: Mix of website features and dataset analysis problems
- **URL-Based Validation**: Submit answers in format `ERFT_stage{N}_p1-{val1}_p2-{val2}_p3-{val3}`
- **Partial Feedback**: System tells you how many values are correct (not which ones)
- **PDF Rewards**: Unlock next stage requirements via PDF download
- **Persistent Leaderboards**: Rankings survive server restarts
- **Real-Time Updates**: Leaderboards auto-refresh every 30 seconds

## Tech Stack

- **Backend**: FastAPI + Python + MongoDB
- **Frontend**: Plain JavaScript (no frameworks)
- **Database**: MongoDB (3 collections: teams, challenges, leaderboard)
- **Authentication**: Simple team name + password (bcrypt hashing)

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── database.py             # MongoDB connection
│   │   ├── models.py               # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── teams.py            # Team creation
│   │   │   ├── challenges.py       # URL validation
│   │   │   └── leaderboard.py      # Rankings
│   │   └── utils/
│   │       ├── auth.py             # Password hashing
│   │       ├── url_validator.py    # URL parsing
│   │       └── leaderboard_updater.py
│   ├── requirements.txt
│   └── seed_challenges.py          # Database seeding script
├── frontend/
│   ├── index.html                  # Team creation
│   ├── challenge.html              # Challenge submission
│   ├── leaderboard.html            # Rankings display
│   ├── css/styles.css
│   └── js/
│       ├── home.js
│       ├── challenge.js
│       └── leaderboard.js
└── pdfs/
    └── stage1.pdf → stage5.pdf     # Pre-generated PDFs
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- Modern web browser

### 1. Install MongoDB

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Windows:**
Download from https://www.mongodb.com/try/download/community

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with challenges
python seed_challenges.py

# Start the FastAPI server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

Simply open the frontend in a web browser:

```bash
cd frontend

# Option 1: Using Python's built-in server
python -m http.server 3000

# Option 2: Using Node.js http-server (if installed)
npx http-server -p 3000

# Option 3: Just open index.html in your browser
```

Access the frontend at `http://localhost:3000`

### 4. Customize Challenge Answers

Edit `backend/seed_challenges.py` and update the `correct_p1`, `correct_p2`, `correct_p3` values for each stage, then re-run:

```bash
python seed_challenges.py
```

## Usage Guide

### For Participants

1. **Create a Team**
   - Go to home page (`index.html`)
   - Enter team name, password, and select region (EMEA/AMRS/APAC)
   - Submit to create team

2. **Submit Challenges**
   - Go to challenge page (`challenge.html`)
   - Enter team name and password
   - Submit URL in format: `ERFT_stage1_p1-21_p2-69_p3-420`
   - Get feedback: "X out of 3 values correct"
   - If all correct: Download PDF with next stage requirements

3. **View Rankings**
   - Go to leaderboard page (`leaderboard.html`)
   - Switch between Global, EMEA, AMRS, APAC tabs
   - Page auto-refreshes every 30 seconds

### For Organizers

**Create Dataset Challenges:**
Use the provided fraud detection dataset to create analysis problems:

```python
import pandas as pd
df = pd.read_csv("hackathon_fraud_payment.csv")

# Example challenges:
# 1. Count duplicate Transaction_IDs
# 2. Average transaction amount for fraudulent transactions
# 3. Most common location for fraud
```

**Monitor Teams:**
Query MongoDB directly:
```bash
mongo
use hackathon_db
db.teams.find().pretty()
db.leaderboard.find().sort({global_rank: 1})
```

## API Endpoints

### Teams
- `POST /teams/create` - Create new team
  ```json
  {
    "team_name": "TeamName",
    "password": "password123",
    "region": "EMEA"
  }
  ```

### Challenges
- `POST /challenges/validate` - Validate submission
  ```json
  {
    "team_name": "TeamName",
    "password": "password123",
    "submitted_url": "ERFT_stage1_p1-21_p2-69_p3-420"
  }
  ```

### Leaderboards
- `GET /leaderboard/global` - Global rankings
- `GET /leaderboard/regional/{region}` - Regional rankings (EMEA/AMRS/APAC)

### Static Files
- `GET /pdfs/stage{N}.pdf` - Download stage PDFs

## Database Collections

### teams
```json
{
  "team_name": "string (unique)",
  "password_hash": "bcrypt hash",
  "region": "EMEA|AMRS|APAC",
  "created_at": "datetime",
  "current_stage": 0-5,
  "stage_times": {"stage_1": null, ...},
  "total_time": 0.0,
  "last_submission_url": ""
}
```

### challenges
```json
{
  "stage": 1-5,
  "type": "website|dataset",
  "title": "string",
  "correct_p1": "answer1",
  "correct_p2": "answer2",
  "correct_p3": "answer3",
  "pdf_filename": "stage1.pdf"
}
```

### leaderboard
```json
{
  "team_id": "ObjectId",
  "team_name": "string",
  "region": "EMEA|AMRS|APAC",
  "current_stage": 0-5,
  "total_time": 0.0,
  "global_rank": 1,
  "regional_rank": 1,
  "last_updated": "datetime"
}
```

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `brew services list` (macOS) or `sudo systemctl status mongodb` (Linux)
- Check connection string in `backend/app/database.py`

**CORS Issues:**
- Make sure backend CORS middleware is configured in `main.py`
- Check that frontend API_URL matches backend URL

**Leaderboard Not Updating:**
- Check browser console for JavaScript errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check MongoDB: `mongo` → `use hackathon_db` → `db.leaderboard.find()`

**PDF Download Not Working:**
- Ensure PDFs exist in `pdfs/` directory
- Check StaticFiles mount path in `main.py`
- Verify file permissions

## Customization

### Change Challenge Count
Update stage logic in:
- `backend/app/models.py` - Update `stage_times` dictionary
- `backend/seed_challenges.py` - Add/remove challenges
- Frontend table headers

### Modify Regions
Update region lists in:
- `backend/app/routers/teams.py` - Valid regions
- `frontend/index.html` - Region dropdown options
- `frontend/leaderboard.html` - Tab buttons

### Adjust Auto-Refresh Rate
In `frontend/js/leaderboard.js`, change:
```javascript
refreshInterval = setInterval(() => {
    loadLeaderboard(currentRegion);
}, 30000); // Change 30000 to desired milliseconds
```

## Security Notes

- Passwords are hashed using bcrypt
- No JWT/sessions for simplicity (suitable for hackathon, not production)
- CORS allows all origins (restrict in production)
- MongoDB has no authentication configured (add in production)

## License

This project is created for the Innovation Summit Hackathon 2025.

## Support

For issues or questions, contact the hackathon organizers.
# innovation_hackathon
