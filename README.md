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

## 📦 Dataset Download and Setup

FoodFresh AI relies on comprehensive multi-modal food datasets combining real-world produce images, laboratory visual datasets, USDA food safety benchmarks, and synthetic regression data.

### 1. Datasets Included Directly in this Repository

The following supporting datasets and metadata are committed directly to the repository:

- **Synthetic Freshness & Shelf-Life Dataset** (`data/raw/Synthetic data/`): 41,280 annotated entries across 43 food classes covering produce, bakery, and environmental condition variations. Includes schema and evaluation documentation.
- **USDA FoodKeeper Database** (`data/raw/foodkeeper/FoodKeeper.json`): Ground-truth storage guidelines, maximum shelf-life intervals, and refrigerated/pantry thresholds from the USDA Food Safety and Inspection Service.
- **Processed Split Manifests & Label Maps** (`data/processed/`): 35 train/validation/test CSV manifests and JSON mappings partitioning AgriFreshNET and Fruits-360 for reproducible training.
- **Real-World Evaluation Sets** (`data/real_world_eval/` & `data/real_world_food/`): Consumer smartphone images across kitchen environments to evaluate model generalization under domain shift.

### 2. Why the Complete Image Dataset is Distributed Separately

The full visual dataset consists of **approximately 199,560 images** across two primary computer vision datasets:
- **AgriFreshNET**: 14,160 real-world images across 24 produce freshness stages and shelf-life categories.
- **Fruits-360**: High-resolution classification images across fruit and vegetable categories.

The complete packaged archive ([`data.zip`](https://github.com/anushka326/FoodFreshAI/releases/download/v1.0.0-data/data.zip)) is **1.16 GB (1,218,547,758 bytes)**. Committing nearly 200,000 raw image files directly to the Git repository would exceed GitHub's 100 MiB single-file limit, severely bloat the repository object database, and degrade cloning performance.

To provide clean, fast cloning while keeping the full dataset accessible, the complete dataset is published as an official release asset on GitHub Releases:
- **GitHub Release**: [FoodFreshAI Complete Dataset v1.0.0 (tag: v1.0.0-data)](https://github.com/anushka326/FoodFreshAI/releases/tag/v1.0.0-data)
- **Direct Download URL**: [https://github.com/anushka326/FoodFreshAI/releases/download/v1.0.0-data/data.zip](https://github.com/anushka326/FoodFreshAI/releases/download/v1.0.0-data/data.zip)
- **Archive Size**: 1,218,547,758 bytes (1,162.10 MB)
- **SHA-256 Checksum**: `dffbb071227a40c20d140a6a60c38872947ed5ec8ce9b3158338474816a145b2`

### 3. Automatic Download & Setup

To download, verify, and extract the complete dataset in one step, run:

```bash
python scripts/download_datasets.py
```

The script will:
1. Verify whether the dataset is already extracted locally.
2. Download `data.zip` from the official GitHub Release with a live progress display.
3. Validate the archive against the expected SHA-256 checksum (`dffbb0...`).
4. Safely extract all image directories into `data/raw/` preserving the original directory layout.

#### Expected Directory Layout After Extraction:
```text
data/
├── raw/
│   ├── AgriFreshNET Freshness and Shelf-Life Image Datase/
│   │   └── Processed Data/Processed Data/
│   │       ├── Fresh Banana(1-4)/
│   │       ├── Rotten banana(7-13)/
│   │       └── ... (24 produce categories)
│   ├── fruits-360-100x100-main/
│   │   ├── Training/
│   │   └── Test/
│   ├── Synthetic data/
│   │   ├── FoodFreshAI_Synthetic_Freshness_ShelfLife_Dataset.csv
│   │   └── ...
│   └── foodkeeper/
│       └── FoodKeeper.json
├── processed/
│   ├── agrifreshnet/
│   ├── cross_dataset/
│   ├── food_recognition_v3/
│   ├── freshness_v2/
│   ├── fruits360/
│   └── fruits360_v2/
├── real_world_eval/
└── real_world_food/
```

After extraction, you can verify dataset integrity at any time with:
```bash
python scripts/validate_all_datasets.py
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
