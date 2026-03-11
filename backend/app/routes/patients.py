"""Patient CRUD routes."""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.models.patient import PatientCreate, PatientRecord

router = APIRouter(prefix="/api/patients", tags=["patients"])


def serialize_doc(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", status_code=201)
async def create_patient(patient: PatientCreate):
    db = get_db()
    data = patient.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await db.patients.insert_one(data)
    data["id"] = str(result.inserted_id)
    return data


@router.get("/")
async def list_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search by name or patient_id"),
    diagnosis: str = Query("", description="Filter by diagnosis"),
    country: str = Query("", description="Filter by country"),
):
    db = get_db()
    query = {}
    if search:
        query["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"patient_id": {"$regex": search, "$options": "i"}},
        ]
    if diagnosis:
        query["diagnosis"] = {"$regex": diagnosis, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}

    skip = (page - 1) * limit
    total = await db.patients.count_documents(query)
    cursor = db.patients.find(query).sort("created_at", -1).skip(skip).limit(limit)
    patients = [serialize_doc(doc) async for doc in cursor]

    return {
        "patients": patients,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/stats")
async def get_stats():
    db = get_db()
    total = await db.patients.count_documents({})

    diagnosis_pipeline = [
        {"$group": {"_id": "$diagnosis", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    diagnosis_stats = []
    async for doc in db.patients.aggregate(diagnosis_pipeline):
        if doc["_id"]:
            diagnosis_stats.append({"disease": doc["_id"], "count": doc["count"]})

    country_pipeline = [
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    country_stats = []
    async for doc in db.patients.aggregate(country_pipeline):
        if doc["_id"]:
            country_stats.append({"country": doc["_id"], "count": doc["count"]})

    severity_pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    severity_stats = []
    async for doc in db.patients.aggregate(severity_pipeline):
        if doc["_id"]:
            severity_stats.append({"severity": doc["_id"], "count": doc["count"]})

    gender_pipeline = [
        {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
    ]
    gender_stats = []
    async for doc in db.patients.aggregate(gender_pipeline):
        if doc["_id"]:
            gender_stats.append({"gender": doc["_id"], "count": doc["count"]})

    age_pipeline = [
        {"$bucket": {
            "groupBy": "$age",
            "boundaries": [0, 18, 30, 45, 60, 75, 120],
            "default": "Unknown",
            "output": {"count": {"$sum": 1}},
        }},
    ]
    age_stats = []
    async for doc in db.patients.aggregate(age_pipeline):
        age_stats.append({"range": str(doc["_id"]), "count": doc["count"]})

    return {
        "total_patients": total,
        "diagnosis_distribution": diagnosis_stats,
        "country_distribution": country_stats,
        "severity_distribution": severity_stats,
        "gender_distribution": gender_stats,
        "age_distribution": age_stats,
    }


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    db = get_db()
    patient = None
    if ObjectId.is_valid(patient_id):
        patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        patient = await db.patients.find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(404, "Patient not found")
    return serialize_doc(patient)


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    db = get_db()
    result = None
    if ObjectId.is_valid(patient_id):
        result = await db.patients.delete_one({"_id": ObjectId(patient_id)})
    if not result or result.deleted_count == 0:
        result = await db.patients.delete_one({"patient_id": patient_id})
    if not result or result.deleted_count == 0:
        raise HTTPException(404, "Patient not found")
    return {"message": "Patient deleted"}
