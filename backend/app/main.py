from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.health import router as health_router
from backend.app.routes.food_recognition import router as food_recognition_router
from backend.app.routes.fresho_buddy import router as fresho_buddy_router
from backend.app.routes.pantry_history import router as pantry_history_router
from backend.app.routes.auth import router as auth_router
from backend.app.routes.ml_feedback import router as ml_feedback_router

app = FastAPI(
    title="FoodFresh AI Backend",
    description="Backend API for FoodFresh AI food freshness detection and shelf-life prediction.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(food_recognition_router)
app.include_router(fresho_buddy_router)
app.include_router(pantry_history_router)
app.include_router(auth_router)
app.include_router(ml_feedback_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to FoodFresh AI Backend",
        "health_check": "/api/health",
    }
