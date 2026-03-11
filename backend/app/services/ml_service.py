"""ML prediction service - loads XGBoost model and makes disease predictions."""
import os
import json
import numpy as np
import joblib
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../ml/trained_models")


class MLService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.meta = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        model_path = os.path.join(MODEL_DIR, "xgb_disease_classifier.json")
        le_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
        meta_path = os.path.join(MODEL_DIR, "model_meta.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run training first."
            )

        self.model = XGBClassifier()
        self.model.load_model(model_path)
        self.label_encoder = joblib.load(le_path)
        with open(meta_path) as f:
            self.meta = json.load(f)
        self._loaded = True
        print("ML model loaded successfully")

    def build_feature_vector(self, data: dict) -> np.ndarray:
        all_symptoms = self.meta["all_symptoms"]
        vital_features = self.meta["vital_features"]
        lab_features = self.meta["lab_features"]
        symptom_set = {s: i for i, s in enumerate(all_symptoms)}

        feat = []
        feat.append(data.get("age", 0))
        feat.append(1 if data.get("gender", "").lower() == "male" else 0)
        feat.append(1 if data.get("smoking", False) else 0)
        feat.append(1 if data.get("alcohol", False) else 0)
        feat.append(len(data.get("existing_conditions", [])))
        feat.append(len(data.get("family_history", [])))
        feat.append(data.get("symptom_duration_days", 0) or 0)

        sym_vec = [0] * len(all_symptoms)
        for s in data.get("symptoms", []):
            if s in symptom_set:
                sym_vec[symptom_set[s]] = 1
        feat.extend(sym_vec)

        vs = data.get("vital_signs", {}) or {}
        if hasattr(vs, "model_dump"):
            vs = vs.model_dump()
        for vf in vital_features:
            feat.append(vs.get(vf, 0) or 0)

        lab = data.get("lab_results", {}) or {}
        if hasattr(lab, "model_dump"):
            lab = lab.model_dump()
        for lf in lab_features:
            feat.append(lab.get(lf, 0) or 0)

        return np.array([feat], dtype=np.float32)

    def predict(self, data: dict) -> dict:
        self.load()
        X = self.build_feature_vector(data)
        probas = self.model.predict_proba(X)[0]
        pred_idx = np.argmax(probas)
        pred_disease = self.label_encoder.inverse_transform([pred_idx])[0]
        confidence = float(probas[pred_idx])

        top_indices = np.argsort(probas)[::-1][:5]
        top_predictions = []
        for i in top_indices:
            disease = self.label_encoder.inverse_transform([i])[0]
            top_predictions.append({
                "disease": disease,
                "confidence": round(float(probas[i]) * 100, 2),
            })

        return {
            "predicted_disease": pred_disease,
            "confidence": round(confidence * 100, 2),
            "top_predictions": top_predictions,
        }

    def get_available_symptoms(self) -> list[str]:
        self.load()
        return self.meta["all_symptoms"]

    def get_disease_classes(self) -> list[str]:
        self.load()
        return self.meta["classes"]


ml_service = MLService()
