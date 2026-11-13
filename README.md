# FoodFresh AI

<<<<<<< HEAD
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

=======
FoodFresh AI is an intelligent computer vision and machine learning platform for food recognition, freshness classification, and shelf-life prediction.

## Architecture

- **`frontend/`**: Active React / Vite frontend application and user interface.
- **`backend/`**: FastAPI backend service providing REST API endpoints.
- **`ml/`**: Machine learning pipelines for food recognition, freshness assessment, and shelf-life prediction.
  - `ml/food_recognition/`: Food item classification.
  - `ml/freshness/`: Freshness quality grading.
  - `ml/shelf_life/`: Shelf-life estimation.
  - `ml/preprocessing/`: Data preparation and pipelines.
  - `ml/evaluation/`: Metric tracking and evaluation utilities.
- **`models/`**:
  - `models/pretrained/`: Pretrained model artifacts (git ignored).
  - `models/trained/`: Locally trained model weights (git ignored).
- **`data/`**: Datasets and metadata (git ignored).
  - `data/raw/`: Raw datasets.
  - `data/processed/`: Processed datasets.
  - `data/metadata/`: Dataset schemas and metadata.
- **`scripts/`**: Utility and verification scripts.
- **`notebooks/`**: Exploratory data analysis and experimental notebooks.

## Backend Setup

1. **Activate Virtual Environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify Environment**:
   ```powershell
   python scripts/check_environment.py
   ```

3. **Run Backend Service**:
   ```powershell
   uvicorn backend.app.main:app --reload
   ```

4. **Health Check Endpoint**:
   - `GET http://127.0.0.1:8000/api/health`
>>>>>>> frontend/main
