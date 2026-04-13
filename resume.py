# =====================================================
# IMPORTS
# =====================================================
from fastapi import APIRouter, UploadFile, File, HTTPException
import joblib
import pdfplumber
from io import BytesIO
import pandas as pd

router = APIRouter()

# =====================================================
# LOAD MODELS
# =====================================================
MODELS = {
    "tcs": joblib.load(r"C:\Users\VICTUS\Downloads\tcs_model.pkl"),
    "infosys": joblib.load(r"C:\Users\VICTUS\Downloads\infosys_model.pkl"),
    "google": joblib.load(r"C:\Users\VICTUS\Downloads\google_model.pkl"),
    "amazon": joblib.load(r"C:\Users\VICTUS\Downloads\amazon_model.pkl"),
}

# =====================================================
# EXTRACT TEXT FROM PDF
# =====================================================
def extract_text(file_bytes):
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t
    return text.lower()


# =====================================================
# FEATURE EXTRACTION
# =====================================================
def extract_features(text):

    skills = ""
    if "python" in text:
        skills += "Python "
    if "sql" in text:
        skills += "SQL "
    if "java" in text:
        skills += "Java "

    experience = 0
    if "3 year" in text:
        experience = 3
    elif "2 year" in text:
        experience = 2
    elif "1 year" in text:
        experience = 1

    education = "B.Tech" if "b.tech" in text else "B.Sc" if "b.sc" in text else "Unknown"

    certifications = "AWS" if "aws" in text else "None"

    job_role = "Data Analyst" if "data" in text else "Software Engineer"

    salary = 50000
    projects = text.count("project")

    return {
        "Skills": skills.strip() if skills else "None",
        "Experience (Years)": int(experience),
        "Education": education,
        "Certifications": certifications,
        "Job Role": job_role,
        "Salary Expectation ($)": int(salary),
        "Projects Count": int(projects)
    }


# =====================================================
# SAFE TRANSFORM
# =====================================================
def safe_transform(le, value):
    try:
        if value in le.classes_:
            return int(le.transform([value])[0])
        else:
            return 0
    except:
        return 0


# =====================================================
# PREPROCESS
# =====================================================
def preprocess(features, model_bundle):

    # If model has encoders
    if isinstance(model_bundle, dict):

        le_skills = model_bundle.get("le_skills")
        le_edu = model_bundle.get("le_edu")
        le_cert = model_bundle.get("le_cert")
        le_role = model_bundle.get("le_role")

        if le_skills:
            features["Skills"] = safe_transform(le_skills, features["Skills"])
        if le_edu:
            features["Education"] = safe_transform(le_edu, features["Education"])
        if le_cert:
            features["Certifications"] = safe_transform(le_cert, features["Certifications"])
        if le_role:
            features["Job Role"] = safe_transform(le_role, features["Job Role"])

        return pd.DataFrame([features])

    else:
        # If plain model
        return pd.DataFrame([features])


# =====================================================
# API ENDPOINT
# =====================================================
@router.post("/screen")
async def screen_resume(company: str, file: UploadFile = File(...)):
    try:
        company = company.lower()

        if company not in MODELS:
            raise HTTPException(status_code=400, detail="Invalid company")

        # Read file
        contents = await file.read()

        # Extract text
        text = extract_text(contents)

        # Extract features
        features = extract_features(text)

        # Load model
        model_bundle = MODELS[company]

        # Preprocess
        X_new = preprocess(features, model_bundle)

        # Predict
        if isinstance(model_bundle, dict):
            model = model_bundle["model"]
        else:
            model = model_bundle

        prediction = int(model.predict(X_new)[0])

        result = "Selected ✅" if prediction == 1 else "Rejected ❌"

        return {
            "company": company,
            "filename": file.filename,
            "prediction": result,
            "features_used": features
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))