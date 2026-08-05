from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI(title="Namma-Appeal ML Engine")

# ── 1. Enable CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. Request Data Schemes ──
class DepartmentRequest(BaseModel):
    department: str
    state: str
    section: str

class RejectionRequest(BaseModel):
    rejection_ground: str
    appeal_stage: str = "First Appeal"
    department: str = "General"

# ── 3. API Endpoints ──
@app.get("/")
def health_check():
    return {"status": "online", "engine": "Namma-Appeal Sovereign ML Server"}

@app.post("/predict-appeal-outcome")
def predict_appeal_outcome(data: RejectionRequest):
    try:
        text = data.rejection_ground.lower()
        
        # ----------------------------------------------------
        # CATEGORY 1: STRONG STATUTORY LOSS (20% - 30% Win Chance)
        # ----------------------------------------------------
        # Valid Exemptions: Privacy 8(1)(j), Fiduciary 8(1)(e), Security 8(1)(a), Exempt Org Sec 24, Non-Information 2(f)
        loss_keywords = [
            "8(1)(j)", "personal information", "third party", "privacy",
            "8(1)(e)", "fiduciary", "trust",
            "8(1)(a)", "security", "sovereignty",
            "section 24", "exempt organization",
            "2(f)", "opinion", "hypothetical", "investigate", "disciplinary action", "grievance"
        ]
        
        for kw in loss_keywords:
            if kw in text:
                return {
                    "predicted_outcome": "REJECTED_DISMISSED",
                    "win_probability_percent": 25,
                    "recommended_action": "Weak Grounds: Rejection aligns with statutory exemptions under the RTI Act."
                }

        # ----------------------------------------------------
        # CATEGORY 2: STRONG APPELLATE WIN (70% - 90% Win Chance)
        # ----------------------------------------------------
        # Invalid Rejections: Language issues, Fee demands, Improper Sec 6(3) transfers, Delay
        win_high_keywords = [
            "language", "marathi", "hindi", "official language", "english", # Language rejection (Central Govt must accept/translate)
            "fee", "exorbitant", "compilation", "postal order", "search charges", # Fee stalling
            "6(3)", "transfer", "separate application", "fresh application", # Improper transfer
            "delay", "30 days", "deemed refusal", "expired" # Timeline breach
        ]
        
        for kw in win_high_keywords:
            if kw in text:
                return {
                    "predicted_outcome": "OVERTURNED_ALLOWED",
                    "win_probability_percent": 82,
                    "recommended_action": "Strong Case: Procedural rejection violates RTI Act. Proceed with First Appeal under Section 19(1)."
                }

        # ----------------------------------------------------
        # CATEGORY 3: MODERATE WIN / COMMERCIAL CONFIDENCE (55% - 70%)
        # ----------------------------------------------------
        if "8(1)(d)" in text or "commercial" in text or "trade secret" in text:
            return {
                "predicted_outcome": "PARTIALLY_ALLOWED",
                "win_probability_percent": 68,
                "recommended_action": "Moderate Case: Commercial confidence can be overridden by Public Interest under Section 8(2)."
            }

        # ----------------------------------------------------
        # DEFAULT FALLBACK (GENERAL REJECTION APPEAL)
        # ----------------------------------------------------
        return {
            "predicted_outcome": "PARTIALLY_ALLOWED",
            "win_probability_percent": 60,
            "recommended_action": "Moderate Case: Grounds for appeal exist. File First Appeal under Section 19(1)."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))