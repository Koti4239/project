# =====================================================
# IMPORTS
# =====================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os

# =====================================================
# ROUTER INIT  ✅ IMPORTANT
# =====================================================
router = APIRouter()

# =====================================================
# LOAD MODEL
# =====================================================
MODEL_PATH = r"C:\Users\VICTUS\Downloads\placement_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model file not found! Check path.")

model = joblib.load(MODEL_PATH)

# =====================================================
# REQUEST SCHEMA
# =====================================================
class Student(BaseModel):
    cgpa: float = Field(..., ge=0, le=10)
    aptitude_score: int = Field(..., ge=0, le=100)
    coding_score: int = Field(..., ge=0, le=100)
    communication_score: int = Field(..., ge=0, le=100)
    resume_score: int = Field(..., ge=0, le=100)
    hr_score: int = Field(..., ge=0, le=100)

# =====================================================
# ROUTES
# =====================================================
@router.get("/")
def home():
    return {"message": "Predictor Module Running 🚀"}

@router.post("/predict")
def predict(student: Student):
    try:
        data = np.array([[
            student.cgpa,
            student.aptitude_score,
            student.coding_score,
            student.communication_score,
            student.resume_score,
            student.hr_score
        ]])

        prediction = model.predict(data)[0]

        probability = (
            model.predict_proba(data)[0][1]
            if hasattr(model, "predict_proba")
            else 0.0
        )

        status = "Ready ✅" if prediction == 1 else "Not Ready ❌"

        return {
            "prediction": int(prediction),
            "status": status,
            "confidence": round(float(probability), 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))