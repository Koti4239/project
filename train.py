import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# -------------------
# Load dataset
# -------------------
df = pd.read_csv(r"C:\Users\VICTUS\Downloads\AI_Resume_Screening.csv")

# target
y = df["Recruiter Decision"]

# features
X = df[[
    "Skills",
    "Experience (Years)",
    "Education",
    "Certifications",
    "Job Role",
    "Salary Expectation ($)",
    "Projects Count"
]]

# -------------------
# Feature processing
# -------------------

text_features = ["Skills"]
cat_features = ["Education", "Certifications", "Job Role"]
num_features = ["Experience (Years)", "Salary Expectation ($)", "Projects Count"]

preprocessor = ColumnTransformer([
    ("skills", TfidfVectorizer(), "Skills"),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
    ("num", "passthrough", num_features)
])

# -------------------
# ML Model
# -------------------

model = Pipeline([
    ("prep", preprocessor),
    ("clf", LogisticRegression(max_iter=1000))
])

# -------------------
# Train test split
# -------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

# -------------------
# Evaluate
# -------------------

pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))

# -------------------
# Save model
# -------------------

joblib.dump(model, "resume_classifier.pkl")
print("Model saved as resume_classifier.pkl")
