from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.health import router as health_router

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


@app.get("/")
def root():
    return {
        "message": "Welcome to FoodFresh AI Backend",
        "health_check": "/api/health",
    }
