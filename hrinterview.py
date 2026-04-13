# ======================================
# IMPORTS
# ======================================
from fastapi import APIRouter
from pydantic import BaseModel
import requests


# ======================================
# ROUTER
# ======================================
router = APIRouter(prefix="/hr", tags=["HR Interview"])


# ======================================
# REQUEST MODEL
# ======================================
class HRRequest(BaseModel):
    question: str
    answer: str


# ======================================
# HUGGINGFACE CONFIG
# ======================================
HF_TOKEN = "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"   # 🔴 put your key

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


# ======================================
# HELPER FUNCTION
# ======================================
def keyword_score(text: str):
    """
    Simple scoring logic if LLM fails
    """

    score = 5
    strengths = []
    weaknesses = []
    recommendations = []

    t = text.lower()

    # strengths
    if "project" in t:
        strengths.append("Explained projects")
        score += 2

    if "team" in t:
        strengths.append("Teamwork mentioned")
        score += 1

    if "experience" in t:
        strengths.append("Experience explained")
        score += 2

    # weaknesses
    if len(text.split()) < 15:
        weaknesses.append("Answer too short")
        score -= 2

    if "don't know" in t:
        weaknesses.append("Lack of confidence")
        score -= 3

    # recommendations
    if "project" not in t:
        recommendations.append("Add project examples")

    if "team" not in t:
        recommendations.append("Explain teamwork skills")

    if len(text.split()) < 30:
        recommendations.append("Give more detailed explanation")

    score = max(1, min(10, score))

    return score, strengths, weaknesses, recommendations


# ======================================
# MAIN API
# ======================================
@router.post("/evaluate")
def evaluate(req: HRRequest):

    try:

        prompt = f"""
        Evaluate the HR interview answer.

        Question: {req.question}
        Answer: {req.answer}

        Provide:
        1. Score out of 10
        2. Short feedback
        3. Strengths
        4. Weaknesses
        5. Improvement tips
        """

        payload = {"inputs": prompt}

        response = requests.post(API_URL, headers=headers, json=payload)

        data = response.json()

        # =============================
        # LLM feedback
        # =============================
        if isinstance(data, list):
            feedback = data[0].get("generated_text", "")
        else:
            feedback = ""

        # =============================
        # Rule-based scoring
        # =============================
        score, strengths, weaknesses, recommendations = keyword_score(req.answer)

        result = "Selected" if score >= 6 else "Rejected"

        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "result": result
        }

    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Error: {str(e)}",
            "strengths": [],
            "weaknesses": [],
            "recommendations": ["Try again"],
            "result": "Error"
        }
