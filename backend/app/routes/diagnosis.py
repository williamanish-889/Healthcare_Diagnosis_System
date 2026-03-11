"""Diagnosis routes - ML prediction + AI suggestions."""
import io
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from datetime import datetime
from app.models.patient import DiagnosisRequest, DiagnosisResponse
from app.services.ml_service import ml_service
from app.services.openai_service import openai_service
from app.services.image_service import image_service
from app.database import get_db

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])


@router.post("/predict", response_model=DiagnosisResponse)
async def predict_diagnosis(req: DiagnosisRequest):
    """Predict disease from patient data using XGBoost model + OpenAI suggestions."""
    data = req.model_dump()
    if req.vital_signs:
        data["vital_signs"] = req.vital_signs.model_dump()
    if req.lab_results:
        data["lab_results"] = req.lab_results.model_dump()

    try:
        prediction = ml_service.predict(data)
    except FileNotFoundError:
        raise HTTPException(503, "ML model not trained yet. Please train the model first.")
    except Exception as e:
        raise HTTPException(500, f"Prediction error: {str(e)}")

    ai_result = await openai_service.get_diagnosis_suggestion(
        predicted_disease=prediction["predicted_disease"],
        confidence=prediction["confidence"],
        top_predictions=prediction["top_predictions"],
        patient_data=data,
    )

    db = get_db()
    record = {
        **data,
        "diagnosis": prediction["predicted_disease"],
        "confidence": prediction["confidence"],
        "ai_suggestion": ai_result.get("ai_suggestion", ""),
        "root_cause": ai_result.get("root_cause", ""),
        "created_at": datetime.utcnow(),
    }
    await db.diagnosis_history.insert_one(record)

    return DiagnosisResponse(
        predicted_disease=prediction["predicted_disease"],
        confidence=prediction["confidence"],
        top_predictions=prediction["top_predictions"],
        ai_suggestion=ai_result.get("ai_suggestion"),
        root_cause=ai_result.get("root_cause"),
        recommended_tests=ai_result.get("recommended_tests", []),
        recommended_treatments=ai_result.get("recommended_treatments", []),
    )


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Parse CSV/Excel patient data and return predictions for each row."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or Excel.")
    except Exception as e:
        raise HTTPException(400, f"Error parsing file: {str(e)}")

    results = []
    for _, row in df.iterrows():
        data = {}
        row_dict = row.to_dict()

        data["age"] = int(row_dict.get("age", 0))
        data["gender"] = str(row_dict.get("gender", "male"))
        data["smoking"] = bool(row_dict.get("smoking", False))
        data["alcohol"] = bool(row_dict.get("alcohol", False))

        symptoms_raw = row_dict.get("symptoms", "")
        if isinstance(symptoms_raw, str) and symptoms_raw:
            data["symptoms"] = [s.strip() for s in symptoms_raw.split("|")]
        else:
            data["symptoms"] = []

        conditions_raw = row_dict.get("existing_conditions", "")
        if isinstance(conditions_raw, str) and conditions_raw:
            data["existing_conditions"] = [s.strip() for s in conditions_raw.split("|")]
        else:
            data["existing_conditions"] = []

        family_raw = row_dict.get("family_history", "")
        if isinstance(family_raw, str) and family_raw:
            data["family_history"] = [s.strip() for s in family_raw.split("|")]
        else:
            data["family_history"] = []

        data["symptom_duration_days"] = int(row_dict.get("symptom_duration_days", 0) or 0)

        vital_signs = {}
        lab_results = {}
        for k, v in row_dict.items():
            if k.startswith("vs_") and pd.notna(v):
                vital_signs[k[3:]] = float(v)
            elif k.startswith("lab_") and pd.notna(v):
                lab_results[k[4:]] = float(v)
        data["vital_signs"] = vital_signs
        data["lab_results"] = lab_results

        try:
            prediction = ml_service.predict(data)
            results.append({
                "row": int(_ + 1),
                "patient_name": f"{row_dict.get('first_name', '')} {row_dict.get('last_name', '')}".strip(),
                **prediction,
            })
        except Exception as e:
            results.append({"row": int(_ + 1), "error": str(e)})

    return {"total_rows": len(df), "predictions": results}


@router.post("/analyze-image")
async def analyze_medical_image(
    file: UploadFile = File(...),
    image_type: str = Form("xray"),
):
    """Analyze medical image (X-ray, MRI, CT scan)."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    allowed_types = ["image/jpeg", "image/png", "image/dicom", "image/webp"]
    if file.content_type and file.content_type not in allowed_types:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".dcm")):
            raise HTTPException(400, f"Unsupported image type: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > 20 * 1024 * 1024:
        raise HTTPException(400, "Image too large. Max 20MB.")

    result = await image_service.analyze_image(image_bytes, image_type)

    db = get_db()
    await db.image_analysis_history.insert_one({
        "filename": file.filename,
        "image_type": image_type,
        "result": result,
        "created_at": datetime.utcnow(),
    })

    return result


@router.get("/symptoms")
async def get_symptoms():
    """Get list of all recognized symptoms."""
    try:
        return {"symptoms": ml_service.get_available_symptoms()}
    except Exception:
        from app.ml.train_model import ALL_SYMPTOMS
        return {"symptoms": ALL_SYMPTOMS}


@router.get("/diseases")
async def get_diseases():
    """Get list of all disease classes."""
    try:
        return {"diseases": ml_service.get_disease_classes()}
    except Exception:
        from app.utils.generate_synthetic_data import DISEASES
        return {"diseases": list(DISEASES.keys())}


@router.get("/history")
async def get_diagnosis_history(page: int = 1, limit: int = 20):
    """Get diagnosis history."""
    db = get_db()
    skip = (page - 1) * limit
    total = await db.diagnosis_history.count_documents({})
    cursor = db.diagnosis_history.find({}).sort("created_at", -1).skip(skip).limit(limit)
    history = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        history.append(doc)
    return {"history": history, "total": total, "page": page, "limit": limit}
