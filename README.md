# Outfit Project

AI-powered outfit recommendation system with React frontend and FastAPI backend.

## Quick Start

### 1. Backend

```powershell
cd backend
# First time only: initialize database
$env:PYTHONPATH = "."
python scripts/init_db.py

# Start server
.\run.bat
# Or: $env:PYTHONPATH = "."; python -m uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000**

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

### 3. Try it

1. Open http://localhost:3000
2. Click **Get started** and register
3. Add items to your wardrobe, then generate outfit recommendations

## Project Structure

```
Outfit_Project/
├── backend/          # FastAPI + SQLAlchemy
│   ├── app/
│   ├── scripts/
│   └── run.bat
├── frontend/         # React + Vite + Tailwind
│   └── src/
└── README.md
```

## Configuration

- **Backend**: Copy `backend/.env.example` to `backend/.env`. Default uses SQLite (no setup).
- **Stripe/Weather**: Optional for local dev. Add keys for checkout and weather-based recommendations.
