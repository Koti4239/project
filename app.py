
# =====================================================
# CONFIG
# =====================================================
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import base64
import os
import requests
# =====================================================
# CONFIG
# =====================================================
API_URL = "http://127.0.0.1:8000"
SHEET_ID = "17eCJJOuAGzJ6J8ozx-8ipyCp-rhN1oIqqi3DH0sH1OE"

st.set_page_config(page_title="AI Placement Assistant", layout="wide")

# =====================================================
# BACKGROUND IMAGE (FIXED)
# =====================================================
def set_bg(image_file):

    if not os.path.exists(image_file):
        return

    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background:
            linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
            url("data:image/png;base64,{encoded}");
        background-size: cover;
        color: white;
    }}

    h1,h2,h3,h4,h5,h6,p,label {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("background.jpg")

# =====================================================
# GOOGLE SHEETS
# =====================================================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "role" not in st.session_state:
    st.session_state.role = "user"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "question" not in st.session_state:
    st.session_state.question = None
# =====================================================
# REGISTER
# =====================================================
def registration_page():

    st.title("🎓 Registration")

    with st.form("register_form"):

        name = st.text_input("Full Name")
        roll = st.text_input("Roll Number")
        dept = st.text_input("Department")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")

        role = st.selectbox("Role", ["user", "admin"])

        submit = st.form_submit_button("Register")

    if submit:

        if not name or not email:
            st.warning("Fill required fields")
            return

        sheet.append_row([name, roll, dept, email, phone, role])

        st.success("Registered Successfully ✅")

# =====================================================
# LOGIN (FIXED)
# =====================================================
def login_page():

    st.title("🔐 Login")

    with st.form("login_form"):

        login_name = st.text_input("Enter Name")
        login_email = st.text_input("Enter Email")

        submit = st.form_submit_button("Login")

    if submit:

        # DEBUG
        st.write("Name:", login_name)
        st.write("Email:", login_email)

        if not login_name or not login_email:
            st.warning("Please enter all fields")
            return

        records = sheet.get_all_records()

        for row in records:

            name = str(row.get("Name", "")).strip().lower()
            email = str(row.get("Email", "")).strip().lower()
            role = str(row.get("Role", "user")).strip().lower()

            if name == login_name.strip().lower() and email == login_email.strip().lower():

                st.success(f"Welcome {login_name} 🎉")

                st.session_state.logged_in = True
                st.session_state.user_name = login_name
                st.session_state.role = role

                st.rerun()
                return

        st.error("User not found ❌")


# MODULE PAGE
# =====================================================
def modules_page():

    st.sidebar.success(f"Welcome {st.session_state.user_name} ✅")


    menu = [
        "Home",
        "Company Resources",
        "Resume Screening",
        "Aptitude Practice",
        "Coding Practice",
        "HR Interview",
        "Communication",
        "Leaderboard",
        "ML Predictor"
    ]

    choice = st.sidebar.selectbox("Select Module", menu)

    # HOME
    if choice == "Home":
        st.title("👋 Virtual AI Mentor")
        st.info(f"Welcome {st.session_state.user_name}")

    # RESUME
    elif choice == "Resume Screening":
        st.title("📄 AI Resume Screening")

        # ✅ ADD COMPANY SELECTION
        company = st.selectbox(
            "Select Company",
            ["tcs", "infosys", "google", "amazon"]
        )

        uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

        if uploaded_file and st.button("Analyze Resume"):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            # ✅ PASS COMPANY PARAMETER
            response = requests.post(
                f"{API_URL}/resume/screen",
                params={"company": company},
                files=files
            )

            if response.status_code == 200:
                result = response.json()

                st.success("✅ Analysis Completed")

                st.metric("📊 Prediction", result["prediction"])

                # Optional fields
                if "score" in result:
                    st.metric("Score", f"{result['score']}%")

                if "features_used" in result:
                    st.subheader("🔍 Extracted Features")
                    st.json(result["features_used"])

            else:
                st.error("❌ Resume analysis failed")
    # APTITUDE
    elif choice == "Aptitude Practice":
        st.title("🧠 Aptitude Test")

        count = st.slider("Number of Questions", 1, 10, 5)

        if st.button("Start Test"):
            res = requests.get(f"{API_URL}/aptitude/random?count={count}")

            if res.status_code == 200:
                st.session_state.questions = res.json()["questions"]
                st.session_state.answers = {}

        if st.session_state.questions:

            for q in st.session_state.questions:
                st.write("###", q["question"])

                ans = st.radio(
                    "Choose answer",
                    q["options"],
                    key=f"q_{q['id']}"
                )

                st.session_state.answers[str(q["id"])] = ans

            if st.button("Submit Test"):

                submission = {
                    "answers": st.session_state.answers,
                    "user_name": st.session_state.user_name
                }

                result = requests.post(
                    f"{API_URL}/aptitude/submit",
                    json=submission
                ).json()

                score = result.get("score", 0)
                total_questions = result.get("total_questions", len(st.session_state.questions))
                percentage = result.get("percentage", 0)
                level = result.get("level", "Beginner")

                st.metric("Score", f"{score} / {total_questions}")
                st.metric("Percentage", f"{percentage:.2f}%")
                st.metric("Level", level)

    # CODING
    elif choice == "Coding Practice":
     st.title("💻 Coding Practice")

    # ----------------------------
    # Session Init
    # ----------------------------
     if "question" not in st.session_state:
        st.session_state.question = None

    # ----------------------------
    # Buttons Row (ONLY ONE BUTTON NOW)
    # ----------------------------
     if st.button("🎯 Get Coding Question"):
        response = requests.get(f"{API_URL}/coding/question")

        if response.status_code == 200:
            st.session_state.question = response.json()
        else:
            st.error("❌ Unable to fetch question")

    # ----------------------------
    # Show Question
    # ----------------------------
     if st.session_state.question:

        q = st.session_state.question

        st.divider()

        st.subheader(f"📌 {q['title']}")
        st.write(q["description"])
        st.info(f"Difficulty: {q.get('difficulty', 'Easy')}")

        # ----------------------------
        # Code Editor
        # ----------------------------
        code = st.text_area(
            "✍️ Write your Python code here:",
            height=300,
            placeholder="Example:\n\nn = int(input())\nprint(n)"
        )

        # ----------------------------
        # Submit Code
        # ----------------------------
        if st.button("🚀 Submit Code"):

            if not code.strip():
                st.warning("⚠️ Please write some code first!")
            else:
                payload = {
                    "code": code,
                    "question_id": q["id"]
                }

                with st.spinner("Running your code... ⏳"):
                    response = requests.post(
                        f"{API_URL}/coding/submit",
                        json=payload
                    )

                if response.status_code == 200:

                    result = response.json()

                    # ----------------------------
                    # Test Case Results
                    # ----------------------------
                    st.divider()
                    st.subheader("🧪 Test Case Results")

                    for i, r in enumerate(result.get("results", []), start=1):

                        st.write(f"### Test Case {i}")

                        if r["status"] == "Passed":
                            st.success("✅ Passed")

                        elif r["status"] == "Failed":
                            st.error("❌ Failed")
                            st.write("**Expected:**", r["expected"])
                            st.write("**Got:**", r["got"])

                        else:
                            st.warning("⚠️ Error")
                            st.code(r.get("error", ""))

                    # ----------------------------
                    # Score Section
                    # ----------------------------
                    st.divider()
                    st.subheader("📊 Result Summary")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Score", f"{result.get('score', 0)}%")

                    with col2:
                        st.metric(
                            "Passed",
                            f"{result.get('total_passed', 0)} / {result.get('total_cases', 0)}"
                        )

                    # ----------------------------
                    # Verdict
                    # ----------------------------
                    verdict = result.get("verdict", "")

                    if verdict == "All Test Cases Passed":
                        st.success("🎉 Excellent! All test cases passed")

                    elif verdict == "Partial Correct":
                        st.warning("⚠️ Some test cases failed")

                    else:
                        st.error("❌ Wrong Answer")

                    # ----------------------------
                    # AI Feedback
                    # ----------------------------
                    if result.get("feedback"):
                        st.divider()
                        st.subheader("🤖 AI Feedback")
                        st.write(result["feedback"])

                else:
                    st.error("❌ Submission failed")

    # HR
    elif choice == "HR Interview":
        st.title("🧑‍💼 AI HR Interview Evaluator")

        questions = [
            "Tell me about yourself",
            "Why should we hire you?",
            "What are your strengths?",
            "Where do you see yourself in 5 years?",
            "Explain one project you worked on"
        ]

        q = st.selectbox("Select Interview Question", questions)
        st.info(q)

        answer = st.text_area("Write your answer")

        if st.button("Evaluate Answer"):

            if answer.strip() == "":
                st.warning("Please write your answer first")
            else:

                payload = {"question": q, "answer": answer}

                response = requests.post(
                    f"{API_URL}/hr/evaluate",
                    json=payload
                )

                if response.status_code == 200:

                    result = response.json()

                    st.subheader("📊 Evaluation Result")
                    st.metric("Score", f"{result.get('score',0)}/10")

                    st.write("### Feedback")
                    st.write(result.get("feedback","No feedback"))

                    st.write("### Strengths")
                    for s in result.get("strengths", []):
                        st.success(s)

                    st.write("### Weaknesses")
                    for w in result.get("weaknesses", []):
                        st.error(w)

                    st.write("### Recommendations")
                    for r in result.get("recommendations", []):
                        st.info(r)

                    if result.get("result") == "Selected":
                        st.success("✅ Likely Selected")
                    else:
                        st.error("❌ Needs Improvement")

                else:
                    st.error("HR evaluation failed")

    # COMMUNICATION ✅ FIXED ONLY INDENTATION
    elif choice == "Communication":
        st.title("🗣 AI Communication Practice")

        if st.button("Get Question"):

            response = requests.get(f"{API_URL}/communication/question")

            if response.status_code == 200:
                st.session_state.communication_question = response.json()["question"]
            else:
                st.error("Unable to fetch question")

        if "communication_question" in st.session_state:

            st.subheader("Question")
            st.info(st.session_state.communication_question)

            answer = st.text_area("Write your answer in English", height=150)

            if st.button("Evaluate Answer"):

                payload = {"answer": answer}

                response = requests.post(
                    f"{API_URL}/communication/evaluate",
                    json=payload
                )

                if response.status_code == 200:

                    result = response.json()

                    st.metric("Score", f"{result.get('score',0)} / 10")
                    st.write(result.get("result",""))

                    for f in result.get("feedback", []):
                        st.success(f)

                    for r in result.get("recommendations", []):
                        st.warning(r)

                    st.info(result.get("ai_feedback",""))

                else:
                    st.error("Evaluation failed")

    # COMPANY ✅ FIXED ONLY INDENTATION
    elif choice == "Company Resources":
        st.title("🏢 Company Eligibility Checker")

        response = requests.get(f"{API_URL}/company/list")

        if response.status_code == 200:

            companies = response.json()["companies"]

            company = st.selectbox("Select Company", companies)

            cgpa = st.number_input(
                "Enter Your CGPA",
                min_value=0.0,
                max_value=10.0,
                step=0.1
            )

            if st.button("Check Eligibility"):

                payload = {"company": company, "cgpa": cgpa}

                res = requests.post(
                    f"{API_URL}/company/eligibility",
                    json=payload
                )

                if res.status_code == 200:

                    result = res.json()

                    st.metric("Your CGPA", result["your_cgpa"])
                    st.metric("Required CGPA", result["required_cgpa"])

                    if "Eligible" in result["status"]:
                        st.success(result["status"])
                    else:
                        st.error(result["status"])

                    for skill in result["recommended_skills"]:
                        st.info(skill)

                    st.write(result["hr_process"])

                    for r in result["resources"]:
                        st.write(f"[{r['title']}]({r['url']})")

                    st.warning(result["general_recommendation"])

                else:
                    st.error("Failed to check eligibility")

        else:
            st.error("Unable to load company list")

    # LEADERBOARD ✅ EXACTLY YOUR ORIGINAL
    elif choice == "Leaderboard":

        st.title("🏆 Placement Leaderboard")

        response = requests.get(f"{API_URL}/leaderboard/top")

        if response.status_code == 200:

            data = response.json()

            if data:

                df = pd.DataFrame(data)

                df = df.rename(columns={
                    "user_name": "Name",
                    "aptitude_score": "Aptitude",
                    "coding_score": "Coding",
                    "communication_score": "Communication",
                    "hr_score": "HR",
                    "resume_score": "Resume",
                    "total_score": "Total"
                })

                df = df.sort_values(by="Total", ascending=False)

                df.insert(0, "Rank", range(1, len(df) + 1))

                st.dataframe(df)

                st.bar_chart(df.set_index("Name")["Total"])

            else:
                st.warning("No data in leaderboard")

        else:
            st.error("Failed to load leaderboard")

    # ML PREDICTOR ✅ FIXED ONLY INDENTATION
    elif choice == "ML Predictor":
        st.title("🎯 Placement Readiness Predictor")

        st.write("Enter your details:")

        cgpa = st.number_input("CGPA", 0.0, 10.0, 7.0)
        aptitude = st.number_input("Aptitude Score", 0, 100, 50)
        coding = st.number_input("Coding Score", 0, 100, 50)
        communication = st.number_input("Communication Score", 0, 100, 50)
        resume = st.number_input("Resume Score", 0, 100, 50)
        hr = st.number_input("HR Score", 0, 100, 50)

        if st.button("Predict"):

            payload = {
                "cgpa": cgpa,
                "aptitude_score": aptitude,
                "coding_score": coding,
                "communication_score": communication,
                "resume_score": resume,
                "hr_score": hr
            }

            response = requests.post(f"{API_URL}/predict", json=payload)

            if response.status_code == 200:

                result = response.json()

                st.success(result["status"])
                st.metric("Confidence", f"{result['confidence']*100:.2f}%")

                if result["prediction"] == 1:
                    st.balloons()

            else:
                st.error("Prediction API failed")
# =====================================================
def admin_page():

    st.title("👨‍💼 Admin Dashboard")

    st.success(f"Welcome Admin {st.session_state.user_name}")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.subheader("📊 All Students Data")
    st.dataframe(df)

    st.download_button("Download CSV", df.to_csv(), "students.csv")

# =====================================================
# NAVIGATION
# =====================================================
st.sidebar.title("📌 Navigation")

if not st.session_state.logged_in:

    page = st.sidebar.radio("Go to", ["Register", "Login"])

    if page == "Register":
        registration_page()

    else:
        login_page()

else:

    if st.session_state.role == "admin":
        admin_page()
    else:
        modules_page()