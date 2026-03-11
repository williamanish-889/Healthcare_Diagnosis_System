from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    O_POS = "O+"
    O_NEG = "O-"
    AB_POS = "AB+"
    AB_NEG = "AB-"


class VitalSigns(BaseModel):
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    heart_rate: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    bmi: Optional[float] = None


class LabResults(BaseModel):
    hemoglobin: Optional[float] = None
    wbc_count: Optional[float] = None
    rbc_count: Optional[float] = None
    platelet_count: Optional[float] = None
    blood_sugar_fasting: Optional[float] = None
    blood_sugar_pp: Optional[float] = None
    hba1c: Optional[float] = None
    cholesterol_total: Optional[float] = None
    cholesterol_hdl: Optional[float] = None
    cholesterol_ldl: Optional[float] = None
    triglycerides: Optional[float] = None
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    uric_acid: Optional[float] = None
    sgot: Optional[float] = None
    sgpt: Optional[float] = None
    alkaline_phosphatase: Optional[float] = None
    bilirubin_total: Optional[float] = None
    albumin: Optional[float] = None
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    vitamin_d: Optional[float] = None
    vitamin_b12: Optional[float] = None
    iron: Optional[float] = None
    calcium: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None


class PatientRecord(BaseModel):
    patient_id: Optional[str] = None
    first_name: str
    last_name: str
    age: int
    gender: Gender
    blood_group: Optional[BloodGroup] = None
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    smoking: bool = False
    alcohol: bool = False
    existing_conditions: list[str] = []
    family_history: list[str] = []
    current_medications: list[str] = []
    allergies: list[str] = []
    symptoms: list[str] = []
    symptom_duration_days: Optional[int] = None
    vital_signs: Optional[VitalSigns] = None
    lab_results: Optional[LabResults] = None
    diagnosis: Optional[str] = None
    severity: Optional[str] = None
    treatment: Optional[str] = None
    root_cause: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    age: int = Field(ge=0, le=120)
    gender: Gender
    blood_group: Optional[BloodGroup] = None
    country: str = "India"
    state: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    smoking: bool = False
    alcohol: bool = False
    existing_conditions: list[str] = []
    family_history: list[str] = []
    current_medications: list[str] = []
    allergies: list[str] = []
    symptoms: list[str] = []
    symptom_duration_days: Optional[int] = None
    vital_signs: Optional[VitalSigns] = None
    lab_results: Optional[LabResults] = None


class DiagnosisRequest(BaseModel):
    patient_id: Optional[str] = None
    age: int
    gender: str
    symptoms: list[str]
    symptom_duration_days: Optional[int] = None
    smoking: bool = False
    alcohol: bool = False
    existing_conditions: list[str] = []
    family_history: list[str] = []
    vital_signs: Optional[VitalSigns] = None
    lab_results: Optional[LabResults] = None


class DiagnosisResponse(BaseModel):
    predicted_disease: str
    confidence: float
    top_predictions: list[dict]
    ai_suggestion: Optional[str] = None
    root_cause: Optional[str] = None
    recommended_tests: list[str] = []
    recommended_treatments: list[str] = []


class ImageAnalysisResponse(BaseModel):
    image_type: str
    findings: str
    confidence: float
    abnormalities_detected: list[str]
    recommendation: str
