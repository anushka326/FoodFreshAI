# FoodFresh AI

A clean, modular starter project for the FoodFresh AI application.

## Overview
- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI (Python) with SQLite
- **Authentication**: JWT based, using FastAPI dependencies
- **Database**: SQLite via SQLAlchemy
- **AI Services**: Placeholder for Groq integration (later)

## Project Structure
```
FoodFreshAI/
├─ frontend/          # React app
├─ backend/           # FastAPI server
├─ docs/              # Documentation
├─ scripts/           # Helper scripts
├─ models/            # ML models (future)
├─ data/              # Datasets (future)
└─ README.md
```

## Setup
### Backend
```sh
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```sh
cd frontend
npm install
npm run dev
```

## Auth Flow
- Register: `POST /api/auth/register`
- Login: `POST /api/auth/login`
- Get current user: `GET /api/auth/me` (requires JWT)

See the `backend/app/routes/auth.py` and `frontend/src/pages/Auth` for implementation details.

