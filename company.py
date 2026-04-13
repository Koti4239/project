# =====================================================
# COMPANY ELIGIBILITY + RESOURCES + HR PROCESS
# =====================================================

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/company", tags=["Company Resources"])


# =====================================================
# COMPANY DATABASE
# =====================================================

COMPANIES = {

    "TCS": {
        "min_cgpa": 6.0,
        "skills": ["DBMS", "Aptitude", "Coding Basics"],
        "hr_process": "Usually 1 HR round with behavioral and situational questions.",
        "resources": [
            {"title": "TCS Careers", "url": "https://www.tcs.com/careers"},
            {"title": "TCS Interview Experience", "url": "https://www.geeksforgeeks.org/tcs-interview-experience/"},
            {"title": "TCS Ninja Prep", "url": "https://prepinsta.com/tcs-ninja/"}
        ]
    },

    "Infosys": {
        "min_cgpa": 6.5,
        "skills": ["DSA", "SQL", "English Communication"],
        "hr_process": "Technical + Managerial + HR rounds.",
        "resources": [
            {"title": "Infosys Careers", "url": "https://www.infosys.com/careers"},
            {"title": "Interview Experience", "url": "https://www.geeksforgeeks.org/infosys-interview-experience/"},
            {"title": "Prep Guide", "url": "https://prepinsta.com/infosys/"}
        ]
    },

    "Cognizant": {
        "min_cgpa": 7.0,
        "skills": ["Python", "Cloud Basics", "Projects"],
        "hr_process": "Coding test + Technical + HR.",
        "resources": [
            {"title": "Cognizant Careers", "url": "https://careers.cognizant.com"},
            {"title": "CTS Prep", "url": "https://prepinsta.com/cognizant/"}
        ]
    }
}


# =====================================================
# REQUEST MODEL
# =====================================================

class EligibilityRequest(BaseModel):
    company: str
    cgpa: float


# =====================================================
# LIST COMPANIES
# =====================================================

@router.get("/list")
def list_companies():
    return {"companies": list(COMPANIES.keys())}


# =====================================================
# CHECK ELIGIBILITY
# =====================================================

@router.post("/eligibility")
def check_eligibility(data: EligibilityRequest):

    company = data.company
    cgpa = data.cgpa

    if company not in COMPANIES:
        return {"error": "Company not found"}

    info = COMPANIES[company]

    min_cgpa = info["min_cgpa"]

    if cgpa >= min_cgpa:
        status = "Eligible ✅"
        recommendation = "Focus on interview preparation and coding practice."
    else:
        status = "Not Eligible ❌"
        recommendation = "Improve CGPA or strengthen skills with certifications and projects."

    return {
        "company": company,
        "your_cgpa": cgpa,
        "required_cgpa": min_cgpa,
        "status": status,
        "recommended_skills": info["skills"],
        "hr_process": info["hr_process"],
        "resources": info["resources"],
        "general_recommendation": recommendation
    }
