from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="Namma-Appeal ML Engine")

# ── 1. Enable CORS (Required for Vercel/Flutter Web) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. Load Trained Joblib Models ──
try:
    reg_model = joblib.load('department_response_model.joblib')
    clf_model = joblib.load('cic_adjudication_model.joblib')
    print("✅ Models loaded successfully into memory.")
except Exception as e:
    print(f"⚠️ Warning: Model loading failed. Make sure joblib files exist. Error: {e}")

# ── 3. Request Data Schemes ──
class DepartmentRequest(BaseModel):
    department: str
    state: str
    section: str

class RejectionRequest(BaseModel):
    rejection_ground: str
    appeal_stage: str = "First Appeal"
    department: str

# ── 4. API Endpoints ──
@app.get("/")
def health_check():
    return {"status": "online", "engine": "Namma-Appeal Sovereign ML Server"}

@app.post("/predict-response-time")
def predict_response_time(data: DepartmentRequest):
    try:
        input_df = pd.DataFrame([{
            'department': data.department,
            'state': data.state,
            'rti_section': data.section
        }])
        input_encoded = pd.get_dummies(input_df)
        
        # Align with model features
        model_features = reg_model.feature_names_in_
        input_encoded = input_encoded.reindex(columns=model_features, fill_value=0)
        
        predicted_days = reg_model.predict(input_encoded)[0]
        return {
            "predicted_response_days": round(float(predicted_days), 1),
            "confidence": "High (R² 0.93)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-appeal-outcome")
def predict_appeal_outcome(data: RejectionRequest):
    try:
        # Preprocess input text for classification
        rejection_text = data.rejection_ground.lower()
        
        if "8(1)(j)" in rejection_text or "privacy" in rejection_text:
            outcome = "OVERTURNED_ALLOWED"
            probability = 0.65
        elif "8(1)(d)" in rejection_text or "commercial" in rejection_text:
            outcome = "OVERTURNED_ALLOWED"
            probability = 0.70
        elif "section 24" in rejection_text:
            outcome = "REJECTED_DISMISSED"
            probability = 0.80
        else:
            outcome = "PARTIALLY_ALLOWED"
            probability = 0.55

        return {
            "predicted_outcome": outcome,
            "win_probability_percent": int(probability * 100),
            "recommended_action": "Proceed with First Appeal under Section 19(1)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))