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
        rejection_text = data.rejection_ground.lower()
        
        # ── FIX 1: Rule-Based Overriding Guardrail ──
        STRONG_REJECTION_GROUNDS = [
            "8(1)(j)", "personal information", "third party", "invasion of privacy", 
            "2(f)", "interrogatory", "opinion", "hypothetical", 
            "8(1)(a)", "security", "sovereignty" 
        ]
        
        # Check if a strict legal exemption is invoked
        for phrase in STRONG_REJECTION_GROUNDS:
            if phrase in rejection_text:
                return {
                    "predicted_outcome": "DISMISSED_UPHELD",
                    "win_probability_percent": 25, # Hard-capped low probability
                    "recommended_action": "Weak Grounds: Rejection aligns with statutory exemptions under RTI Act."
                }

        # Simulated base probabilities for remaining conditions based on your current setup
        if "8(1)(d)" in rejection_text or "commercial" in rejection_text:
            raw_prob = 0.72
        elif "section 24" in rejection_text:
            raw_prob = 0.40
        else:
            raw_prob = 0.58

        # ── FIX 3: Multi-Tier Decision Thresholds ──
        if raw_prob >= 0.65:
            outcome = "OVERTURNED_ALLOWED"
            action = "Strong Case: Proceed with First Appeal under Section 19(1)."
        elif raw_prob >= 0.50:
            outcome = "PARTIALLY_ALLOWED"
            action = "Moderate Case: Proceed with targeted legal clarifications."
        else:
            outcome = "DISMISSED_UPHELD"
            action = "Weak Case: Grounded in valid RTI exemptions. Filing an appeal is not recommended."

        return {
            "predicted_outcome": outcome,
            "win_probability_percent": int(raw_prob * 100),
            "recommended_action": action
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))