from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import (
    curriculum_router, quiz_router, mistakes_router,
    learner_router, teachback_router, recommendations_router,
    history_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="AI Student Study API",
    description="Explainable Multi-Signal Learning Diagnosis and Personalization Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Health Check
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Student Study API",
        "environment": settings.ENVIRONMENT
    }

# Register all Routers under /api
app.include_router(curriculum_router.router, prefix="/api")
app.include_router(quiz_router.router, prefix="/api")
app.include_router(mistakes_router.router, prefix="/api")
app.include_router(learner_router.router, prefix="/api")
app.include_router(teachback_router.router, prefix="/api")
app.include_router(recommendations_router.router, prefix="/api")
app.include_router(history_router.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
