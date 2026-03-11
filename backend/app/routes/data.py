"""Data management routes - seed, export, train model."""
import json
import os
from fastapi import APIRouter, HTTPException
from app.database import get_db

router = APIRouter(prefix="/api/data", tags=["data"])

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data")


@router.post("/seed")
async def seed_database():
    """Seed database with synthetic patient data."""
    db = get_db()
    existing = await db.patients.count_documents({})
    if existing > 0:
        return {"message": f"Database already has {existing} records. Use /api/data/reseed to force.", "count": existing}

    data_path = os.path.join(DATA_DIR, "synthetic_patients.json")
    if not os.path.exists(data_path):
        from app.utils.generate_synthetic_data import generate_all, save_to_json
        records = generate_all(1000)
        save_to_json(records, data_path)
    else:
        with open(data_path) as f:
            records = json.load(f)

    from datetime import datetime
    for r in records:
        r["created_at"] = datetime.fromisoformat(r["created_at"]) if isinstance(r["created_at"], str) else r["created_at"]
        r["updated_at"] = datetime.fromisoformat(r["updated_at"]) if isinstance(r["updated_at"], str) else r["updated_at"]

    result = await db.patients.insert_many(records)
    return {"message": f"Seeded {len(result.inserted_ids)} patient records", "count": len(result.inserted_ids)}


@router.post("/reseed")
async def reseed_database():
    """Clear and reseed database with fresh synthetic data."""
    db = get_db()
    await db.patients.delete_many({})

    from app.utils.generate_synthetic_data import generate_all, save_to_json
    data_path = os.path.join(DATA_DIR, "synthetic_patients.json")
    records = generate_all(1000)
    save_to_json(records, data_path)

    from datetime import datetime
    for r in records:
        r["created_at"] = datetime.fromisoformat(r["created_at"]) if isinstance(r["created_at"], str) else r["created_at"]
        r["updated_at"] = datetime.fromisoformat(r["updated_at"]) if isinstance(r["updated_at"], str) else r["updated_at"]

    result = await db.patients.insert_many(records)
    return {"message": f"Reseeded {len(result.inserted_ids)} patient records", "count": len(result.inserted_ids)}


@router.post("/train")
async def train_model():
    """Train/retrain the XGBoost model on current data."""
    db = get_db()
    count = await db.patients.count_documents({"diagnosis": {"$exists": True, "$ne": None}})
    if count < 50:
        raise HTTPException(400, f"Need at least 50 labeled records to train. Currently have {count}.")

    cursor = db.patients.find({"diagnosis": {"$exists": True, "$ne": None}})
    records = []
    async for doc in cursor:
        doc.pop("_id", None)
        records.append(doc)

    data_path = os.path.join(DATA_DIR, "synthetic_patients.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(data_path, "w") as f:
        json.dump(records, f, indent=2, default=str)

    from app.ml.train_model import train
    model, le, meta = train()

    from app.services.ml_service import ml_service
    ml_service._loaded = False
    ml_service.load()

    return {
        "message": "Model trained successfully",
        "accuracy": meta["accuracy"],
        "n_classes": len(meta["classes"]),
        "classes": meta["classes"],
        "n_samples": len(records),
    }


@router.get("/export")
async def export_data(format: str = "json"):
    """Export patient data."""
    db = get_db()
    cursor = db.patients.find({})
    records = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        records.append(doc)

    if format == "json":
        return {"data": records, "count": len(records)}
    else:
        return {"data": records, "count": len(records)}
