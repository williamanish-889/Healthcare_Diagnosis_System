from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import connect_db, close_db
from app.routes import patients, diagnosis, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    try:
        from app.services.ml_service import ml_service
        ml_service.load()
        print("ML model pre-loaded")
    except Exception as e:
        print(f"ML model not yet trained: {e}")
    yield
    await close_db()


app = FastAPI(
    title="Euron Healthcare Diagnosis Support System",
    description="AI-powered assistant for doctors to analyze patient data, predict diagnoses, and suggest treatments",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(diagnosis.router)
app.include_router(data.router)


@app.get("/")
async def root():
    return {
        "name": "Euron Healthcare Diagnosis Support System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "patients": "/api/patients",
            "diagnosis": "/api/diagnosis/predict",
            "image_analysis": "/api/diagnosis/analyze-image",
            "csv_upload": "/api/diagnosis/upload-csv",
            "seed_data": "/api/data/seed",
            "train_model": "/api/data/train",
        },
    }


@app.get("/api/health")
async def health():
    from app.database import get_db
    db = get_db()
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    from app.services.ml_service import ml_service
    model_status = "loaded" if ml_service._loaded else "not loaded"

    return {
        "status": "healthy",
        "database": db_status,
        "ml_model": model_status,
    }
