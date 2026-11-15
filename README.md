# FoodFresh AI 🌱
*Know. Save. Waste Less.*

FoodFresh AI is an intelligent computer vision, machine learning, and culinary intelligence platform designed to eliminate household food waste, accurately predict produce freshness and shelf life, and provide grounded zero-waste guidance.

---

## 🌟 Key Features

1. **AI Vision & Freshness Detection**:
   - Computer vision pipelines classifying produce items, determining visible freshness status, and projecting remaining shelf-life days.
2. **FreshoBuddy AI (Groq & Qwen 2.5/3.8)**:
   - Intelligent kitchen companion with **Pantry Mode ON/OFF** toggle.
   - **Global Mode (Pantry OFF)**: Answers general culinary, storage, and food science questions without requiring saved pantry items.
   - **Pantry Mode (Pantry ON)**: Grounded in the user's authentic pantry inventory with deterministic Eat First urgency rankings.
3. **Themed Avatar Selection System**:
   - Custom-crafted profile avatar collection featuring 6 categories: *Fruit Buddies*, *Veggie Friends*, *Nature Lovers*, *Animal Pals*, *Little Chefs*, and *Eco Heroes*.
4. **Impact Analytics & Sustainability Metrics**:
   - Visual tracking of monthly money saved, food waste diverted (kg), CO₂ reduction, and waste reduction percentage.
5. **Packaged Food Scanner & OCR**:
   - Barcode lookup via OpenFoodFacts and nutritional label optical character recognition.
6. **Smart Recipe Recommendations**:
   - Dynamic recipe generator prioritizing produce approaching its quality limit.
7. **PWA & Offline Resilience**:
   - Service worker caching, offline status indicators, and background synchronization.

---

## 📁 Repository Structure

```
FoodFreshAI/
├─ frontend/          # React 19, Vite, Tailwind CSS application
│  ├─ src/
│  │  ├─ assets/avatars/   # Themed SVG avatar catalog
│  │  ├─ components/       # UI components & floating FreshoBuddy widget
│  │  ├─ pages/            # Dashboard, FreshoBuddy, Analytics, History, etc.
│  │  └─ services/         # API clients (auth, history, pantry, chatbot)
├─ backend/           # FastAPI REST API & SQLite persistence
│  ├─ app/
│  │  ├─ database/chat_db.py # SQLite database engine & schema management
│  │  ├─ deps/               # Authentication & dependency injection
│  │  ├─ routes/             # API routes (auth, chatbot, pantry, analytics, etc.)
│  │  └─ services/           # Intent classifier, triage engine, Groq client
├─ ml/                # Machine learning vision & freshness pipelines
├─ scripts/           # Automated verification suites & test tools
└─ README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Groq API Key (for FreshoBuddy AI)

### Backend Setup
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
# Copy .env.example to backend/.env and populate your GROQ_API_KEY

# 4. Start backend server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
# Running on http://localhost:3000
```

---

## 🔐 Authentication & API Flow

- **Register**: `POST /api/auth/register` (creates user account & initializes default avatar)
- **Login**: `POST /api/auth/login` (returns bearer session token & user profile)
- **Current User**: `GET /api/auth/me` (requires `Authorization: Bearer <token>`)
- **Avatar Selection**: `PATCH /api/auth/avatar` (persists chosen themed avatar across all devices)
- **Chat with FreshoBuddy**: `POST /api/fresho-buddy/chat` (supports `pantryMode: true/false`)
- **Health Check**: `GET /api/health`

---

## 🧪 Testing

Run comprehensive live verification:
```bash
python scripts/test_live_all_scenarios.py
python scripts/test_auth_full_verification.py
python scripts/test_avatar_integration.py
```
