"""OpenAI service for AI-powered diagnosis suggestions and root cause analysis."""
from openai import AsyncOpenAI
from app.config import get_settings


class OpenAIService:
    def __init__(self):
        self._client = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            settings = get_settings()
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def get_diagnosis_suggestion(
        self,
        predicted_disease: str,
        confidence: float,
        top_predictions: list[dict],
        patient_data: dict,
    ) -> dict:
        symptoms = ", ".join(patient_data.get("symptoms", []))
        existing = ", ".join(patient_data.get("existing_conditions", [])) or "None"
        family = ", ".join(patient_data.get("family_history", [])) or "None"

        vital_signs = patient_data.get("vital_signs", {}) or {}
        if hasattr(vital_signs, "model_dump"):
            vital_signs = vital_signs.model_dump()
        lab_results = patient_data.get("lab_results", {}) or {}
        if hasattr(lab_results, "model_dump"):
            lab_results = lab_results.model_dump()

        vitals_str = ", ".join(f"{k}: {v}" for k, v in vital_signs.items() if v) if vital_signs else "Not available"
        labs_str = ", ".join(f"{k}: {v}" for k, v in lab_results.items() if v) if lab_results else "Not available"
        preds_str = "\n".join(f"  - {p['disease']}: {p['confidence']}%" for p in top_predictions[:5])

        prompt = f"""You are a senior medical consultant AI assistant helping doctors with diagnosis.

PATIENT PROFILE:
- Age: {patient_data.get('age', 'N/A')}, Gender: {patient_data.get('gender', 'N/A')}
- Symptoms: {symptoms}
- Duration: {patient_data.get('symptom_duration_days', 'N/A')} days
- Existing conditions: {existing}
- Family history: {family}
- Smoking: {patient_data.get('smoking', False)}, Alcohol: {patient_data.get('alcohol', False)}
- Vital Signs: {vitals_str}
- Lab Results: {labs_str}

ML MODEL PREDICTIONS:
- Primary prediction: {predicted_disease} (confidence: {confidence}%)
- Top differential diagnoses:
{preds_str}

Provide a structured medical analysis with:
1. **Clinical Assessment**: Brief assessment of the ML prediction in context of patient data
2. **Root Cause Analysis**: Detailed root cause of the predicted disease for this patient
3. **Recommended Additional Tests**: List of tests to confirm diagnosis
4. **Treatment Plan**: Suggested treatment approach (medications, lifestyle, follow-up)
5. **Red Flags**: Any warning signs requiring immediate attention
6. **Differential Diagnoses to Consider**: Other conditions to rule out

Format the response as structured JSON with keys: assessment, root_cause, recommended_tests (array), treatment_plan, red_flags (array), differential_notes.
Respond ONLY with valid JSON, no markdown."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            import json
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            result = json.loads(content)
            return {
                "ai_suggestion": result.get("assessment", ""),
                "root_cause": result.get("root_cause", ""),
                "recommended_tests": result.get("recommended_tests", []),
                "recommended_treatments": [result.get("treatment_plan", "")],
                "red_flags": result.get("red_flags", []),
                "differential_notes": result.get("differential_notes", ""),
            }
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {
                "ai_suggestion": f"ML model predicts {predicted_disease} with {confidence}% confidence. Please consult with specialists for detailed analysis.",
                "root_cause": "Unable to generate AI analysis. Please review patient data manually.",
                "recommended_tests": [],
                "recommended_treatments": [],
                "red_flags": [],
                "differential_notes": "",
            }


openai_service = OpenAIService()
