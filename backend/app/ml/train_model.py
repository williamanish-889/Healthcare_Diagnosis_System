"""
Train XGBoost disease classification model on synthetic patient data.
Features: demographics, symptoms, vitals, lab results -> predict disease.
"""
import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../../data/synthetic_patients.json")
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")

ALL_SYMPTOMS = [
    "frequent urination", "excessive thirst", "blurred vision", "fatigue",
    "slow wound healing", "numbness in extremities", "weight loss", "headache",
    "dizziness", "chest pain", "shortness of breath", "nosebleeds",
    "vision problems", "palpitations", "sweating", "nausea", "pain radiating to arm",
    "cough with phlegm", "fever", "chills", "rapid breathing",
    "swelling in ankles", "decreased urine output", "loss of appetite",
    "muscle cramps", "itching", "cold intolerance", "constipation",
    "dry skin", "hair loss", "depression", "muscle weakness",
    "rapid heartbeat", "anxiety", "tremors", "heat intolerance", "insomnia",
    "diarrhea", "pale skin", "weakness", "cold hands",
    "wheezing", "chest tightness", "cough", "difficulty breathing at night",
    "exercise intolerance", "abdominal pain", "jaundice", "swelling in legs",
    "dark urine", "high fever", "severe headache", "pain behind eyes",
    "joint pain", "rash", "vomiting", "persistent cough",
    "coughing blood", "night sweats", "high fever with chills",
    "light sensitivity", "sound sensitivity", "visual aura", "throbbing pain",
    "chronic cough", "frequent respiratory infections", "blue lips",
    "burning urination", "cloudy urine", "pelvic pain", "strong urine odor",
    "blood in urine", "heartburn", "acid regurgitation", "difficulty swallowing",
    "sore throat", "bloating", "joint swelling", "morning stiffness",
    "joint deformity", "bone pain", "frequent infections",
    "persistent sadness", "loss of interest", "sleep disturbance",
    "appetite changes", "difficulty concentrating", "feelings of worthlessness",
    "social withdrawal",
]

VITAL_FEATURES = [
    "blood_pressure_systolic", "blood_pressure_diastolic", "heart_rate",
    "temperature", "respiratory_rate", "oxygen_saturation", "bmi",
]

LAB_FEATURES = [
    "hemoglobin", "wbc_count", "rbc_count", "platelet_count",
    "blood_sugar_fasting", "blood_sugar_pp", "hba1c",
    "cholesterol_total", "cholesterol_hdl", "cholesterol_ldl", "triglycerides",
    "creatinine", "urea", "uric_acid", "sgot", "sgpt",
    "alkaline_phosphatase", "bilirubin_total", "albumin",
    "tsh", "t3", "t4", "vitamin_d", "vitamin_b12",
    "iron", "calcium", "sodium", "potassium",
]


def load_data():
    with open(DATA_PATH) as f:
        records = json.load(f)
    return records


def build_features(records: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    symptom_set = {s: i for i, s in enumerate(ALL_SYMPTOMS)}
    rows = []
    labels = []

    for r in records:
        feat = []
        feat.append(r["age"])
        feat.append(1 if r["gender"] == "male" else 0)
        feat.append(1 if r["smoking"] else 0)
        feat.append(1 if r["alcohol"] else 0)
        feat.append(len(r.get("existing_conditions", [])))
        feat.append(len(r.get("family_history", [])))
        feat.append(r.get("symptom_duration_days", 0) or 0)

        sym_vec = [0] * len(ALL_SYMPTOMS)
        for s in r.get("symptoms", []):
            if s in symptom_set:
                sym_vec[symptom_set[s]] = 1
        feat.extend(sym_vec)

        vs = r.get("vital_signs", {}) or {}
        for vf in VITAL_FEATURES:
            feat.append(vs.get(vf, 0) or 0)

        lab = r.get("lab_results", {}) or {}
        for lf in LAB_FEATURES:
            feat.append(lab.get(lf, 0) or 0)

        rows.append(feat)
        labels.append(r["diagnosis"])

    return np.array(rows, dtype=np.float32), np.array(labels)


def get_feature_names() -> list[str]:
    names = ["age", "gender_male", "smoking", "alcohol",
             "num_existing_conditions", "num_family_history", "symptom_duration_days"]
    names.extend([f"sym_{s.replace(' ', '_')}" for s in ALL_SYMPTOMS])
    names.extend([f"vs_{v}" for v in VITAL_FEATURES])
    names.extend([f"lab_{l}" for l in LAB_FEATURES])
    return names


def train():
    print("Loading data...")
    records = load_data()
    print(f"Loaded {len(records)} records")

    print("Building features...")
    X, y = build_features(records)
    feature_names = get_feature_names()
    print(f"Feature matrix shape: {X.shape}")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    n_classes = len(le.classes_)
    print(f"Number of disease classes: {n_classes}")
    print(f"Classes: {list(le.classes_)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    print("Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob",
        num_class=n_classes,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=True,
    )

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "xgb_disease_classifier.json")
    model.save_model(model_path)

    le_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
    joblib.dump(le, le_path)

    meta = {
        "feature_names": feature_names,
        "all_symptoms": ALL_SYMPTOMS,
        "vital_features": VITAL_FEATURES,
        "lab_features": LAB_FEATURES,
        "classes": list(le.classes_),
        "accuracy": float(acc),
        "n_features": X.shape[1],
    }
    meta_path = os.path.join(MODEL_DIR, "model_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nModel saved to {model_path}")
    print(f"Label encoder saved to {le_path}")
    print(f"Metadata saved to {meta_path}")
    return model, le, meta


if __name__ == "__main__":
    train()
