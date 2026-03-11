import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export interface VitalSigns {
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  bmi?: number;
}

export interface LabResults {
  hemoglobin?: number;
  wbc_count?: number;
  rbc_count?: number;
  platelet_count?: number;
  blood_sugar_fasting?: number;
  blood_sugar_pp?: number;
  hba1c?: number;
  cholesterol_total?: number;
  cholesterol_hdl?: number;
  cholesterol_ldl?: number;
  triglycerides?: number;
  creatinine?: number;
  urea?: number;
  uric_acid?: number;
  sgot?: number;
  sgpt?: number;
  alkaline_phosphatase?: number;
  bilirubin_total?: number;
  albumin?: number;
  tsh?: number;
  t3?: number;
  t4?: number;
  vitamin_d?: number;
  vitamin_b12?: number;
  iron?: number;
  calcium?: number;
  sodium?: number;
  potassium?: number;
}

export interface Patient {
  id?: string;
  patient_id?: string;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  blood_group?: string;
  country: string;
  state?: string;
  city?: string;
  smoking: boolean;
  alcohol: boolean;
  existing_conditions: string[];
  family_history: string[];
  current_medications: string[];
  allergies: string[];
  symptoms: string[];
  symptom_duration_days?: number;
  vital_signs?: VitalSigns;
  lab_results?: LabResults;
  diagnosis?: string;
  severity?: string;
  treatment?: string;
  root_cause?: string;
}

export interface DiagnosisRequest {
  age: number;
  gender: string;
  symptoms: string[];
  symptom_duration_days?: number;
  smoking: boolean;
  alcohol: boolean;
  existing_conditions: string[];
  family_history: string[];
  vital_signs?: VitalSigns;
  lab_results?: LabResults;
}

export interface DiagnosisResponse {
  predicted_disease: string;
  confidence: number;
  top_predictions: { disease: string; confidence: number }[];
  ai_suggestion?: string;
  root_cause?: string;
  recommended_tests: string[];
  recommended_treatments: string[];
}

export interface StatsData {
  total_patients: number;
  diagnosis_distribution: { disease: string; count: number }[];
  country_distribution: { country: string; count: number }[];
  severity_distribution: { severity: string; count: number }[];
  gender_distribution: { gender: string; count: number }[];
  age_distribution: { range: string; count: number }[];
}

export const getHealth = () => api.get("/api/health");

export const getPatients = (params: {
  page?: number;
  limit?: number;
  search?: string;
  diagnosis?: string;
}) => api.get("/api/patients", { params });

export const getPatient = (id: string) => api.get(`/api/patients/${id}`);

export const createPatient = (data: Partial<Patient>) =>
  api.post("/api/patients/", data);

export const getStats = () => api.get<StatsData>("/api/patients/stats");

export const predictDiagnosis = (data: DiagnosisRequest) =>
  api.post<DiagnosisResponse>("/api/diagnosis/predict", data);

export const uploadCSV = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/api/diagnosis/upload-csv", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const analyzeImage = (file: File, imageType: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("image_type", imageType);
  return api.post("/api/diagnosis/analyze-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getSymptoms = () => api.get("/api/diagnosis/symptoms");

export const getDiseases = () => api.get("/api/diagnosis/diseases");

export const getDiagnosisHistory = (params: { page?: number; limit?: number }) =>
  api.get("/api/diagnosis/history", { params });

export const seedDatabase = () => api.post("/api/data/seed");

export const trainModel = () => api.post("/api/data/train");

export default api;
