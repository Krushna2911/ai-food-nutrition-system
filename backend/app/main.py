from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.nutrition import router as nutrition_router
from app.routers.food import router as food_router
from app.routers.analysis import router as analysis_router

from app.routers.user_profile import router as user_profile_router


app = FastAPI(
    title="AI Food Nutrition System API",
    description="Backend API for food detection, nutrition estimation, and personalized diet planning.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(food_router)
app.include_router(user_profile_router)


@app.get("/")
def root():
    return {
        "message": "AI Food Nutrition System API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(nutrition_router)
app.include_router(analysis_router)