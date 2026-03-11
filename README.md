# Euron Healthcare Diagnosis Support System

AI-powered assistant that helps doctors analyze patient reports, scans, and medical history to suggest possible diagnoses and treatments.

## Architecture

```
eurondoctorshelp/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Environment configuration
│   │   ├── database.py      # MongoDB async connection
│   │   ├── models/          # Pydantic data models
│   │   ├── routes/          # API route handlers
│   │   │   ├── patients.py  # Patient CRUD + stats
│   │   │   ├── diagnosis.py # ML prediction + AI suggestions
│   │   │   └── data.py      # Seed, train, export
│   │   ├── services/        # Business logic
│   │   │   ├── ml_service.py      # XGBoost inference
│   │   │   ├── openai_service.py  # GPT-4o suggestions
│   │   │   └── image_service.py   # Medical image analysis
│   │   ├── ml/              # ML model training
│   │   │   └── train_model.py
│   │   └── utils/           # Data generation
│   │       └── generate_synthetic_data.py
│   └── data/                # Generated datasets
├── frontend/                # Next.js TypeScript frontend
│   └── src/
│       ├── app/             # App router pages
│       ├── components/      # Reusable UI components
│       └── lib/api.ts       # API client
├── docker-compose.yml       # Full-stack Docker setup
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python 3.11) |
| Frontend | Next.js 15 + TypeScript + Tailwind CSS v4 |
| Database | MongoDB (Motor async driver) |
| ML Model | XGBoost (20-class disease classifier, 99% accuracy) |
| AI Suggestions | OpenAI GPT-4o |
| Image Analysis | GPT-4o Vision + Hugging Face Swin Transformer |
| Deployment | Docker + Docker Compose |

## Features

- **Disease Classification**: XGBoost model trained on 1000 synthetic records across 20 diseases
- **AI Clinical Assessment**: GPT-4o provides root cause analysis, treatment plans, and red flags
- **Medical Image Analysis**: Upload X-ray/MRI/CT scans for AI-powered findings
- **Batch Processing**: Upload CSV/Excel patient files for bulk predictions
- **Patient Management**: Full CRUD with search, filter, and pagination
- **Dashboard Analytics**: Interactive charts for disease, severity, age, and country distributions
- **Diagnosis History**: Track all past predictions with expandable details

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Set your MongoDB URI and OpenAI key
cp .env.example .env
# Edit .env with your credentials

docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Generate synthetic data + train model
python -m app.utils.generate_synthetic_data
python -m app.ml.train_model

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### After Starting

1. Visit http://localhost:8000/docs for API documentation
2. Seed the database: `POST /api/data/seed`
3. Visit http://localhost:3000 for the dashboard

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/patients` | List patients (paginated, searchable) |
| POST | `/api/patients/` | Create patient |
| GET | `/api/patients/stats` | Dashboard statistics |
| GET | `/api/patients/{id}` | Get patient details |
| POST | `/api/diagnosis/predict` | ML disease prediction + AI suggestion |
| POST | `/api/diagnosis/upload-csv` | Batch CSV/Excel prediction |
| POST | `/api/diagnosis/analyze-image` | Medical image analysis |
| GET | `/api/diagnosis/symptoms` | Available symptom list |
| GET | `/api/diagnosis/diseases` | Disease class list |
| GET | `/api/diagnosis/history` | Past diagnoses |
| POST | `/api/data/seed` | Seed 1000 synthetic records |
| POST | `/api/data/train` | Train/retrain ML model |

## Disease Classes (20)

Anemia, Asthma, COPD, Chronic Kidney Disease, Coronary Artery Disease, Dengue Fever, Depression, GERD, Hypertension, Hyperthyroidism, Hypothyroidism, Liver Disease (NAFLD), Malaria, Migraine, Pneumonia, Rheumatoid Arthritis, Tuberculosis, Type 2 Diabetes, UTI, Vitamin D Deficiency

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o | No (graceful fallback) |
| `JWT_SECRET` | JWT signing secret | Yes |
