import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import joblib
import random

np.random.seed(42)
random.seed(42)

print("==================================================")
print(" 🚀 GENERATING DATASETS & TRAINING ML MODELS")
print("==================================================")

# ----------------------------------------------------
# 1. DEPARTMENT RESPONSE PREDICTOR DATASET & MODEL
# ----------------------------------------------------
departments = [
    'Chennai Metropolitan Development Authority (CMDA)',
    'Greater Chennai Corporation',
    'Chennai Metro Water (CMWSSB)',
    'TANGEDCO (Electricity Board)',
    'Tamil Nadu Police Headquarters',
    'Southern Railway Headquarters',
    'Reserve Bank of India (RBI)',
    'Employees Provident Fund Organisation (EPFO)'
]

states = ['Tamil Nadu', 'Maharashtra', 'Delhi', 'Karnataka', 'Telangana']
sections = ['Sec 6(1) General', 'Sec 8(1)(j) Privacy', 'Sec 8(1)(d) Commercial', 'Sec 7(1) Life & Liberty']

n_samples = 1200
dept_samples = np.random.choice(departments, n_samples)
state_samples = np.random.choice(states, n_samples)
sec_samples = np.random.choice(sections, n_samples)

base_days = []
for dept, sec in zip(dept_samples, sec_samples):
    days = 30
    if 'Railway' in dept: days += np.random.randint(5, 18)
    elif 'Corporation' in dept: days += np.random.randint(10, 25)
    elif 'RBI' in dept: days -= np.random.randint(5, 12)
    elif 'EPFO' in dept: days += np.random.randint(15, 35)
    
    if 'Life & Liberty' in sec: days = np.random.randint(2, 5)
    elif 'Privacy' in sec or 'Commercial' in sec: days += np.random.randint(15, 30)
    
    base_days.append(max(2, days + np.random.normal(0, 4)))

df_response = pd.DataFrame({
    'department': dept_samples,
    'state': state_samples,
    'rti_section': sec_samples,
    'response_days': np.round(base_days, 1)
})

df_response.to_csv('rti_department_response_dataset.csv', index=False)
print("\n[1/2] Saved 'rti_department_response_dataset.csv' (1,200 rows)")

X_resp = pd.get_dummies(df_response[['department', 'state', 'rti_section']], drop_first=True)
y_resp = df_response['response_days']

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_resp, y_resp, test_size=0.2, random_state=42)

reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
reg_model.fit(X_train_r, y_train_r)

joblib.dump(reg_model, 'department_response_model.joblib')
print(f"      Model Metrics -> R² Score: {r2_score(y_test_r, reg_model.predict(X_test_r)):.4f}")
print("      Saved Trained Model -> 'department_response_model.joblib'")

# ----------------------------------------------------
# 2. TRUE ML CIC ADJUDICATION PREDICTOR (NOISE-RESILIENT)
# ----------------------------------------------------
headers = [
    "Reference is invited to your RTI application dated 12/05/2026. ",
    "This order disposes of the First Appeal filed by the appellant. ",
    "Subject: Information sought under RTI Act, 2005. ",
    "With reference to the subject cited above, it is to inform that "
]
footers = [
    " Hence your application is rejected. (Signature) Public Information Officer",
    " The application is disposed of accordingly. CPIO",
    " No further intervention is required. Information Commissioner"
]

win_triggers = [
    ("The requested information runs into 150 pages. You are directed to pay Rs. 1500 towards compilation and search charges.", "OVERTURNED_ALLOWED"),
    ("The PIO failed to furnish the requested information within the mandatory 30-day period stipulated under Section 7(1).", "OVERTURNED_ALLOWED"),
    ("Please be informed that this office does not maintain this. You are advised to separately file fresh RTI applications to other offices instead of a Section 6(3) transfer.", "OVERTURNED_ALLOWED"),
    ("The information submitted is in Marathi language and it is not understood. Submit in Hindi or English.", "OVERTURNED_ALLOWED"),
    ("Information denied under commercial confidence Section 8(1)(d).", "PARTIALLY_ALLOWED"),
]

loss_triggers = [
    ("The information sought qualifies as personal information of a third party, causing an unwarranted invasion of privacy under Section 8(1)(j).", "REJECTED_DISMISSED"),
    ("The information is held by the bank in a fiduciary capacity and is exempt under Section 8(1)(e).", "REJECTED_DISMISSED"),
    ("You have asked us to investigate and take strict disciplinary action. This does not fall under the definition of information as per Section 2(f).", "REJECTED_DISMISSED"),
    ("The organization is exempt under Section 24 of the RTI Act.", "REJECTED_DISMISSED"),
    ("Disclosure of this information would prejudicially affect the sovereignty and security of the state under Section 8(1)(a).", "REJECTED_DISMISSED"),
]

all_triggers = win_triggers + loss_triggers

dataset = []
for _ in range(2000):
    header = random.choice(headers)
    footer = random.choice(footers)
    trigger, outcome = random.choice(all_triggers)
    noise = " ".join(random.choices(["regarding", "department", "appeals", "stipulated", "records", "perusal", "applicant", "officials", "forwarded"], k=4))
    full_text = f"{header} {noise}. {trigger} {footer}"
    dataset.append({"rejection_ground": full_text, "outcome": outcome})

df_cic = pd.DataFrame(dataset)

df_cic.to_csv('cic_adjudication_dataset.csv', index=False)
print("\n[2/2] Saved 'cic_adjudication_dataset.csv' (2,000 rows)")

# NLP Vectorization (Strictly Text-Based to avoid dimensionality errors)
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=5000, stop_words='english')
X_cic = vectorizer.fit_transform(df_cic['rejection_ground']).toarray()
y_cic = df_cic['outcome']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cic, y_cic, test_size=0.2, random_state=42)

clf_model = RandomForestClassifier(n_estimators=300, max_depth=20, random_state=42)
clf_model.fit(X_train_c, y_train_c)

joblib.dump(vectorizer, 'tfidf_vectorizer.joblib')
joblib.dump(clf_model, 'cic_adjudication_model.joblib')

acc = accuracy_score(y_test_c, clf_model.predict(X_test_c))
print(f"      Model Metrics -> Accuracy: {acc * 100:.2f}%")
print("      Saved Trained Models -> 'cic_adjudication_model.joblib' & 'tfidf_vectorizer.joblib'")

print("\n==================================================")
print(" SUCCESS! All CSVs & Trained Models generated.")
print("==================================================")