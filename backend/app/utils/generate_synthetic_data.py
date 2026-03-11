"""
Generate 1000 synthetic patient records with realistic medical data
covering both Indian and international patients across diverse diseases.
"""
import random
import json
import os
from datetime import datetime, timedelta
from faker import Faker

fake_in = Faker("en_IN")
fake_us = Faker("en_US")
fake_uk = Faker("en_GB")

DISEASES = {
    "Type 2 Diabetes": {
        "symptoms": ["frequent urination", "excessive thirst", "blurred vision", "fatigue", "slow wound healing", "numbness in extremities", "weight loss"],
        "root_cause": "Insulin resistance due to genetic predisposition, obesity, and sedentary lifestyle leading to impaired glucose metabolism",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.5, "Severe": 0.2},
        "treatments": ["Metformin", "lifestyle modification", "dietary control", "regular exercise", "blood sugar monitoring"],
        "lab_markers": {"blood_sugar_fasting": (140, 300), "blood_sugar_pp": (200, 450), "hba1c": (6.5, 12.0)},
        "risk_factors": ["obesity", "family history of diabetes", "sedentary lifestyle", "PCOS"],
    },
    "Hypertension": {
        "symptoms": ["headache", "dizziness", "chest pain", "shortness of breath", "nosebleeds", "fatigue", "vision problems"],
        "root_cause": "Sustained elevated arterial pressure from arterial stiffness, excess sodium, stress, or renal dysfunction",
        "severity_weights": {"Mild": 0.35, "Moderate": 0.4, "Severe": 0.25},
        "treatments": ["ACE inhibitors", "ARBs", "calcium channel blockers", "diuretics", "low-sodium diet", "stress management"],
        "vital_markers": {"blood_pressure_systolic": (140, 200), "blood_pressure_diastolic": (90, 130)},
        "risk_factors": ["high salt intake", "obesity", "stress", "family history of hypertension"],
    },
    "Coronary Artery Disease": {
        "symptoms": ["chest pain", "shortness of breath", "fatigue", "palpitations", "sweating", "nausea", "pain radiating to arm"],
        "root_cause": "Atherosclerotic plaque buildup in coronary arteries reducing myocardial blood supply",
        "severity_weights": {"Mild": 0.2, "Moderate": 0.4, "Severe": 0.4},
        "treatments": ["statins", "aspirin", "beta-blockers", "angioplasty", "CABG surgery", "lifestyle changes"],
        "lab_markers": {"cholesterol_total": (240, 350), "cholesterol_ldl": (160, 250), "triglycerides": (200, 400)},
        "risk_factors": ["smoking", "diabetes", "hypertension", "high cholesterol"],
    },
    "Pneumonia": {
        "symptoms": ["cough with phlegm", "fever", "chest pain", "shortness of breath", "fatigue", "chills", "rapid breathing"],
        "root_cause": "Bacterial or viral infection causing alveolar inflammation and fluid accumulation in lungs",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.4, "Severe": 0.3},
        "treatments": ["antibiotics", "antiviral medication", "rest", "hydration", "oxygen therapy", "bronchodilators"],
        "lab_markers": {"wbc_count": (12000, 25000)},
        "risk_factors": ["smoking", "weakened immune system", "chronic lung disease"],
    },
    "Chronic Kidney Disease": {
        "symptoms": ["fatigue", "swelling in ankles", "decreased urine output", "nausea", "loss of appetite", "muscle cramps", "itching"],
        "root_cause": "Progressive nephron damage from diabetes, hypertension, or glomerulonephritis impairing filtration",
        "severity_weights": {"Mild": 0.25, "Moderate": 0.45, "Severe": 0.3},
        "treatments": ["ACE inhibitors", "dietary protein restriction", "dialysis", "erythropoietin", "phosphate binders"],
        "lab_markers": {"creatinine": (2.0, 8.0), "urea": (60, 200), "potassium": (5.5, 7.0)},
        "risk_factors": ["diabetes", "hypertension", "family history of kidney disease"],
    },
    "Hypothyroidism": {
        "symptoms": ["fatigue", "weight gain", "cold intolerance", "constipation", "dry skin", "hair loss", "depression", "muscle weakness"],
        "root_cause": "Autoimmune thyroid destruction (Hashimoto's) or iodine deficiency causing insufficient thyroid hormone",
        "severity_weights": {"Mild": 0.4, "Moderate": 0.4, "Severe": 0.2},
        "treatments": ["levothyroxine", "regular thyroid monitoring", "iodine supplementation"],
        "lab_markers": {"tsh": (5.0, 50.0), "t3": (0.3, 0.8), "t4": (0.2, 0.7)},
        "risk_factors": ["family history of thyroid disease", "autoimmune conditions", "iodine deficiency"],
    },
    "Hyperthyroidism": {
        "symptoms": ["weight loss", "rapid heartbeat", "anxiety", "tremors", "heat intolerance", "sweating", "insomnia", "diarrhea"],
        "root_cause": "Excess thyroid hormone production from Graves' disease or toxic nodular goiter",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.45, "Severe": 0.25},
        "treatments": ["antithyroid drugs", "radioactive iodine", "beta-blockers", "thyroidectomy"],
        "lab_markers": {"tsh": (0.01, 0.3), "t3": (2.5, 6.0), "t4": (1.8, 4.5)},
        "risk_factors": ["family history", "autoimmune conditions", "female gender"],
    },
    "Anemia": {
        "symptoms": ["fatigue", "pale skin", "weakness", "dizziness", "shortness of breath", "cold hands", "headache", "chest pain"],
        "root_cause": "Insufficient hemoglobin from iron deficiency, B12 deficiency, chronic disease, or bone marrow dysfunction",
        "severity_weights": {"Mild": 0.35, "Moderate": 0.4, "Severe": 0.25},
        "treatments": ["iron supplements", "vitamin B12 injections", "folic acid", "dietary changes", "blood transfusion"],
        "lab_markers": {"hemoglobin": (5.0, 10.5), "rbc_count": (2.5, 3.8), "iron": (20, 50)},
        "risk_factors": ["poor diet", "heavy menstruation", "chronic disease", "vegetarian diet"],
    },
    "Asthma": {
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "cough", "difficulty breathing at night", "exercise intolerance"],
        "root_cause": "Chronic airway inflammation with bronchial hyperresponsiveness triggered by allergens or irritants",
        "severity_weights": {"Mild": 0.4, "Moderate": 0.35, "Severe": 0.25},
        "treatments": ["inhaled corticosteroids", "bronchodilators", "leukotriene modifiers", "allergen avoidance", "immunotherapy"],
        "lab_markers": {},
        "risk_factors": ["allergies", "family history of asthma", "air pollution exposure"],
    },
    "Liver Disease (NAFLD)": {
        "symptoms": ["fatigue", "abdominal pain", "jaundice", "swelling in legs", "nausea", "dark urine", "loss of appetite"],
        "root_cause": "Fat accumulation in hepatocytes from metabolic syndrome, obesity, or alcohol causing hepatic inflammation",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.4, "Severe": 0.3},
        "treatments": ["weight loss", "dietary changes", "avoid alcohol", "vitamin E", "ursodeoxycholic acid"],
        "lab_markers": {"sgot": (60, 300), "sgpt": (65, 400), "bilirubin_total": (2.0, 8.0), "alkaline_phosphatase": (130, 400), "albumin": (2.0, 3.2)},
        "risk_factors": ["obesity", "diabetes", "alcohol consumption", "hepatitis"],
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain", "muscle pain", "rash", "nausea", "vomiting", "fatigue"],
        "root_cause": "Infection by Dengue virus transmitted through Aedes aegypti mosquito bite causing systemic inflammation",
        "severity_weights": {"Mild": 0.35, "Moderate": 0.4, "Severe": 0.25},
        "treatments": ["fluid replacement", "paracetamol", "platelet monitoring", "rest", "hospitalization if severe"],
        "lab_markers": {"platelet_count": (20000, 90000), "wbc_count": (2000, 4000)},
        "risk_factors": ["tropical region", "monsoon season", "poor sanitation"],
    },
    "Tuberculosis": {
        "symptoms": ["persistent cough", "coughing blood", "night sweats", "weight loss", "fever", "fatigue", "chest pain"],
        "root_cause": "Mycobacterium tuberculosis infection causing granulomatous inflammation primarily in lungs",
        "severity_weights": {"Mild": 0.2, "Moderate": 0.45, "Severe": 0.35},
        "treatments": ["DOTS therapy", "isoniazid", "rifampicin", "pyrazinamide", "ethambutol"],
        "lab_markers": {"hemoglobin": (8.0, 11.0)},
        "risk_factors": ["overcrowded living", "HIV", "malnutrition", "immunosuppression"],
    },
    "Malaria": {
        "symptoms": ["high fever with chills", "sweating", "headache", "nausea", "vomiting", "muscle pain", "fatigue", "jaundice"],
        "root_cause": "Plasmodium parasite infection via Anopheles mosquito destroying red blood cells cyclically",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.4, "Severe": 0.3},
        "treatments": ["chloroquine", "artemisinin combination therapy", "primaquine", "supportive care"],
        "lab_markers": {"hemoglobin": (7.0, 10.0), "platelet_count": (50000, 120000), "bilirubin_total": (1.5, 5.0)},
        "risk_factors": ["tropical region", "lack of mosquito protection", "travel to endemic areas"],
    },
    "Migraine": {
        "symptoms": ["severe headache", "nausea", "vomiting", "light sensitivity", "sound sensitivity", "visual aura", "throbbing pain"],
        "root_cause": "Neurovascular disorder with cortical spreading depression and trigeminal nerve activation",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.45, "Severe": 0.25},
        "treatments": ["triptans", "NSAIDs", "preventive beta-blockers", "anticonvulsants", "stress management", "adequate sleep"],
        "lab_markers": {},
        "risk_factors": ["stress", "hormonal changes", "sleep irregularity", "family history"],
    },
    "COPD": {
        "symptoms": ["chronic cough", "shortness of breath", "wheezing", "chest tightness", "frequent respiratory infections", "fatigue", "blue lips"],
        "root_cause": "Irreversible airflow obstruction from chronic bronchitis and emphysema, primarily caused by smoking",
        "severity_weights": {"Mild": 0.2, "Moderate": 0.4, "Severe": 0.4},
        "treatments": ["bronchodilators", "inhaled steroids", "pulmonary rehabilitation", "oxygen therapy", "smoking cessation"],
        "lab_markers": {},
        "risk_factors": ["smoking", "air pollution", "occupational dust exposure"],
    },
    "Urinary Tract Infection": {
        "symptoms": ["burning urination", "frequent urination", "cloudy urine", "pelvic pain", "strong urine odor", "blood in urine", "fever"],
        "root_cause": "Bacterial colonization of urinary tract, commonly E. coli ascending from perineum",
        "severity_weights": {"Mild": 0.5, "Moderate": 0.35, "Severe": 0.15},
        "treatments": ["antibiotics", "increased fluid intake", "cranberry supplements", "urinary analgesics"],
        "lab_markers": {"wbc_count": (11000, 18000)},
        "risk_factors": ["female gender", "poor hygiene", "catheter use", "diabetes"],
    },
    "Gastroesophageal Reflux Disease": {
        "symptoms": ["heartburn", "acid regurgitation", "chest pain", "difficulty swallowing", "chronic cough", "sore throat", "bloating"],
        "root_cause": "Lower esophageal sphincter dysfunction allowing gastric acid reflux causing esophageal mucosal damage",
        "severity_weights": {"Mild": 0.4, "Moderate": 0.4, "Severe": 0.2},
        "treatments": ["proton pump inhibitors", "H2 blockers", "antacids", "dietary modifications", "weight loss", "elevate head during sleep"],
        "lab_markers": {},
        "risk_factors": ["obesity", "smoking", "spicy food", "late-night eating"],
    },
    "Rheumatoid Arthritis": {
        "symptoms": ["joint pain", "joint swelling", "morning stiffness", "fatigue", "fever", "loss of appetite", "joint deformity"],
        "root_cause": "Autoimmune synovial inflammation causing progressive joint cartilage and bone erosion",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.4, "Severe": 0.3},
        "treatments": ["DMARDs", "methotrexate", "biologics", "NSAIDs", "corticosteroids", "physical therapy"],
        "lab_markers": {},
        "risk_factors": ["female gender", "family history", "smoking", "autoimmune conditions"],
    },
    "Vitamin D Deficiency": {
        "symptoms": ["bone pain", "muscle weakness", "fatigue", "depression", "frequent infections", "slow wound healing", "hair loss"],
        "root_cause": "Insufficient vitamin D from limited sun exposure, dietary deficiency, or malabsorption",
        "severity_weights": {"Mild": 0.45, "Moderate": 0.4, "Severe": 0.15},
        "treatments": ["vitamin D3 supplements", "sun exposure", "calcium supplements", "dietary changes"],
        "lab_markers": {"vitamin_d": (5, 19), "calcium": (7.5, 8.5)},
        "risk_factors": ["indoor lifestyle", "dark skin", "obesity", "vegetarian diet"],
    },
    "Depression": {
        "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep disturbance", "appetite changes", "difficulty concentrating", "feelings of worthlessness", "social withdrawal"],
        "root_cause": "Neurochemical imbalance (serotonin, norepinephrine) combined with psychosocial stressors and genetic vulnerability",
        "severity_weights": {"Mild": 0.3, "Moderate": 0.4, "Severe": 0.3},
        "treatments": ["SSRIs", "cognitive behavioral therapy", "counseling", "exercise", "mindfulness", "social support"],
        "lab_markers": {"tsh": (0.5, 4.5), "vitamin_d": (10, 25), "vitamin_b12": (150, 300)},
        "risk_factors": ["family history", "chronic illness", "trauma", "social isolation"],
    },
}

INDIAN_STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Kerala", "Delhi",
    "Uttar Pradesh", "Gujarat", "Rajasthan", "West Bengal", "Telangana",
    "Andhra Pradesh", "Madhya Pradesh", "Punjab", "Haryana", "Bihar",
]

INDIAN_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Varanasi"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    "West Bengal": ["Kolkata", "Howrah", "Siliguri"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
}

INTERNATIONAL_LOCATIONS = [
    {"country": "United States", "state": "California", "city": "Los Angeles"},
    {"country": "United States", "state": "New York", "city": "New York City"},
    {"country": "United States", "state": "Texas", "city": "Houston"},
    {"country": "United Kingdom", "state": "England", "city": "London"},
    {"country": "United Kingdom", "state": "Scotland", "city": "Edinburgh"},
    {"country": "Canada", "state": "Ontario", "city": "Toronto"},
    {"country": "Australia", "state": "New South Wales", "city": "Sydney"},
    {"country": "Germany", "state": "Bavaria", "city": "Munich"},
    {"country": "UAE", "state": "Dubai", "city": "Dubai"},
    {"country": "Singapore", "state": "Central", "city": "Singapore"},
]

ALL_SYMPTOMS = list(set(s for d in DISEASES.values() for s in d["symptoms"]))
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

MEDICATIONS = [
    "Paracetamol", "Ibuprofen", "Metformin", "Amlodipine", "Atorvastatin",
    "Omeprazole", "Levothyroxine", "Aspirin", "Lisinopril", "Metoprolol",
    "Amoxicillin", "Azithromycin", "Cetirizine", "Pantoprazole", "Montelukast",
]

ALLERGIES = [
    "Penicillin", "Sulfa drugs", "Aspirin", "NSAIDs", "Latex",
    "Peanuts", "Shellfish", "Dust", "Pollen", "None",
]


def weighted_choice(weights: dict) -> str:
    items = list(weights.keys())
    probs = list(weights.values())
    return random.choices(items, weights=probs, k=1)[0]


def gen_normal_lab(low: float, high: float) -> float:
    mid = (low + high) / 2
    std = (high - low) / 4
    return round(random.gauss(mid, std), 2)


def generate_record(idx: int) -> dict:
    is_indian = idx < 700  # 70% Indian, 30% international
    disease_name = random.choice(list(DISEASES.keys()))
    disease = DISEASES[disease_name]

    if is_indian:
        fake = fake_in
        country = "India"
        state = random.choice(INDIAN_STATES)
        city = random.choice(INDIAN_CITIES.get(state, ["Unknown"]))
    else:
        loc = random.choice(INTERNATIONAL_LOCATIONS)
        country = loc["country"]
        state = loc["state"]
        city = loc["city"]
        fake = random.choice([fake_us, fake_uk])

    gender = random.choice(["male", "female"])
    age = random.randint(18, 85)

    num_symptoms = random.randint(3, min(6, len(disease["symptoms"])))
    symptoms = random.sample(disease["symptoms"], num_symptoms)
    if random.random() < 0.2:
        extra = random.sample([s for s in ALL_SYMPTOMS if s not in symptoms], min(2, len(ALL_SYMPTOMS)))
        symptoms.extend(extra)

    severity = weighted_choice(disease["severity_weights"])
    smoking = random.random() < (0.25 if gender == "male" else 0.08)
    alcohol = random.random() < (0.3 if gender == "male" else 0.1)

    weight = round(random.gauss(72, 15), 1) if gender == "male" else round(random.gauss(62, 12), 1)
    weight = max(40, min(150, weight))
    height = round(random.gauss(170, 8), 1) if gender == "male" else round(random.gauss(158, 7), 1)
    height = max(140, min(200, height))
    bmi = round(weight / ((height / 100) ** 2), 1)

    bp_sys = round(random.gauss(125, 20), 0)
    bp_dia = round(random.gauss(80, 12), 0)
    if "vital_markers" in disease:
        vm = disease["vital_markers"]
        if "blood_pressure_systolic" in vm:
            bp_sys = round(random.uniform(*vm["blood_pressure_systolic"]), 0)
            bp_dia = round(random.uniform(*vm["blood_pressure_diastolic"]), 0)

    vital_signs = {
        "blood_pressure_systolic": bp_sys,
        "blood_pressure_diastolic": bp_dia,
        "heart_rate": round(random.gauss(78, 12), 0),
        "temperature": round(random.gauss(98.6, 0.8), 1),
        "respiratory_rate": round(random.gauss(16, 3), 0),
        "oxygen_saturation": round(random.gauss(97, 2), 1),
        "bmi": bmi,
    }

    if disease_name in ["Pneumonia", "Dengue Fever", "Malaria", "Tuberculosis"]:
        vital_signs["temperature"] = round(random.uniform(100.0, 104.0), 1)

    lab = {
        "hemoglobin": round(random.gauss(14.0 if gender == "male" else 12.5, 1.5), 1),
        "wbc_count": round(random.gauss(7500, 2000), 0),
        "rbc_count": round(random.gauss(5.0 if gender == "male" else 4.5, 0.5), 2),
        "platelet_count": round(random.gauss(250000, 60000), 0),
        "blood_sugar_fasting": round(random.gauss(95, 15), 1),
        "blood_sugar_pp": round(random.gauss(130, 25), 1),
        "hba1c": round(random.gauss(5.5, 0.6), 1),
        "cholesterol_total": round(random.gauss(195, 30), 1),
        "cholesterol_hdl": round(random.gauss(50, 10), 1),
        "cholesterol_ldl": round(random.gauss(120, 25), 1),
        "triglycerides": round(random.gauss(140, 40), 1),
        "creatinine": round(random.gauss(1.0, 0.3), 2),
        "urea": round(random.gauss(30, 10), 1),
        "uric_acid": round(random.gauss(5.5, 1.5), 1),
        "sgot": round(random.gauss(28, 10), 1),
        "sgpt": round(random.gauss(30, 12), 1),
        "alkaline_phosphatase": round(random.gauss(80, 25), 1),
        "bilirubin_total": round(random.gauss(0.8, 0.3), 2),
        "albumin": round(random.gauss(4.0, 0.5), 1),
        "tsh": round(random.gauss(2.5, 1.0), 2),
        "t3": round(random.gauss(1.2, 0.3), 2),
        "t4": round(random.gauss(1.0, 0.2), 2),
        "vitamin_d": round(random.gauss(35, 15), 1),
        "vitamin_b12": round(random.gauss(500, 150), 1),
        "iron": round(random.gauss(90, 30), 1),
        "calcium": round(random.gauss(9.5, 0.8), 1),
        "sodium": round(random.gauss(140, 3), 1),
        "potassium": round(random.gauss(4.2, 0.5), 1),
    }

    if "lab_markers" in disease:
        for marker, (low, high) in disease["lab_markers"].items():
            if marker in lab:
                lab[marker] = gen_normal_lab(low, high)

    existing_conditions = []
    if random.random() < 0.3:
        possible = [d for d in DISEASES.keys() if d != disease_name]
        existing_conditions = random.sample(possible, min(random.randint(1, 2), len(possible)))

    family_history = []
    if random.random() < 0.4:
        family_diseases = list(DISEASES.keys())
        family_history = random.sample(family_diseases, min(random.randint(1, 3), len(family_diseases)))

    current_medications = []
    if existing_conditions or random.random() < 0.2:
        current_medications = random.sample(MEDICATIONS, random.randint(1, 3))

    allergies = random.sample(ALLERGIES, random.randint(0, 2))
    allergies = [a for a in allergies if a != "None"] if "None" not in allergies else []

    days_ago = random.randint(0, 365)
    created = datetime.now() - timedelta(days=days_ago)

    record = {
        "patient_id": f"EP{idx:05d}",
        "first_name": fake.first_name_male() if gender == "male" else fake.first_name_female(),
        "last_name": fake.last_name(),
        "age": age,
        "gender": gender,
        "blood_group": random.choice(BLOOD_GROUPS),
        "country": country,
        "state": state,
        "city": city,
        "contact": fake.phone_number(),
        "email": fake.email(),
        "weight_kg": weight,
        "height_cm": height,
        "smoking": smoking,
        "alcohol": alcohol,
        "existing_conditions": existing_conditions,
        "family_history": family_history,
        "current_medications": current_medications,
        "allergies": allergies,
        "symptoms": symptoms,
        "symptom_duration_days": random.randint(1, 60),
        "vital_signs": vital_signs,
        "lab_results": lab,
        "diagnosis": disease_name,
        "severity": severity,
        "treatment": random.choice(disease["treatments"]),
        "root_cause": disease["root_cause"],
        "created_at": created.isoformat(),
        "updated_at": created.isoformat(),
    }
    return record


def generate_all(n: int = 1000) -> list[dict]:
    random.seed(42)
    records = [generate_record(i) for i in range(n)]
    random.shuffle(records)
    return records


def save_to_json(records: list[dict], filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(records, f, indent=2, default=str)
    print(f"Saved {len(records)} records to {filepath}")


if __name__ == "__main__":
    data = generate_all(1000)
    save_to_json(data, os.path.join(os.path.dirname(__file__), "../../data/synthetic_patients.json"))

    import pandas as pd
    flat = []
    for r in data:
        row = {k: v for k, v in r.items() if k not in ("vital_signs", "lab_results")}
        row["symptoms"] = "|".join(r["symptoms"])
        row["existing_conditions"] = "|".join(r["existing_conditions"])
        row["family_history"] = "|".join(r["family_history"])
        row["current_medications"] = "|".join(r["current_medications"])
        row["allergies"] = "|".join(r["allergies"])
        if r["vital_signs"]:
            for k2, v2 in r["vital_signs"].items():
                row[f"vs_{k2}"] = v2
        if r["lab_results"]:
            for k2, v2 in r["lab_results"].items():
                row[f"lab_{k2}"] = v2
        flat.append(row)
    df = pd.DataFrame(flat)
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/synthetic_patients.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV to {csv_path}")
