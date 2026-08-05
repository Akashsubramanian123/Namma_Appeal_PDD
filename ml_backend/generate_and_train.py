import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import joblib

np.random.seed(42)

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

y_pred_r = reg_model.predict(X_test_r)
r2 = r2_score(y_test_r, y_pred_r)
mae = mean_absolute_error(y_test_r, y_pred_r)

joblib.dump(reg_model, 'department_response_model.joblib')
print(f"      Model Metrics -> R² Score: {r2:.4f} | MAE: {mae:.2f} days")
print("      Saved Trained Model -> 'department_response_model.joblib'")

# ----------------------------------------------------
# 2. CIC ADJUDICATION PREDICTOR DATASET & MODEL
# ----------------------------------------------------
rejection_reasons = [
    "Information denied under Section 8(1)(j) citing personal privacy of third party.",
    "Application rejected as information requested is commercial confidence under Section 8(1)(d).",
    "PIO stated information is not available in official records and cannot be created.",
    "Rejected citing exempt organization status under Section 24 of the RTI Act.",
    "Denied claiming disclosure would prejudicially affect sovereignty and security of India.",
    "Application returned stating fee payment mode was incorrect or invalid.",
    "Rejected on grounds of seeking opinions, hypothetical questions rather than records.",
    "Information held in fiduciary relationship under Section 8(1)(e).",
    "Demanding exorbitant fees for compilation.",
    "Improper transfer under Section 6(3) asking applicant to file multiple RTIs."
]

df_cic = pd.DataFrame({'rejection_ground': np.random.choice(rejection_reasons, 1500)})

def assign_outcome(row):
    g = row['rejection_ground']
    if any(x in g for x in ["8(1)(j)", "24", "sovereignty", "opinions", "8(1)(e)"]):
        return "DISMISSED_UPHELD"
    elif any(x in g for x in ["fee payment", "exorbitant", "6(3)", "incorrect"]):
        return "OVERTURNED_ALLOWED"
    else:
        return "PARTIALLY_ALLOWED"

df_cic['outcome'] = df_cic.apply(assign_outcome, axis=1)

df_cic.to_csv('cic_adjudication_dataset.csv', index=False)
print("\n[2/2] Saved 'cic_adjudication_dataset.csv' (1,500 rows)")

# Train Classifier Model (Text NLP Only)
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=5000, stop_words='english')
X_cic = vectorizer.fit_transform(df_cic['rejection_ground']).toarray()
y_cic = df_cic['outcome']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cic, y_cic, test_size=0.2, random_state=42)

clf_model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
clf_model.fit(X_train_c, y_train_c)

# Save both model and vectorizer
joblib.dump(vectorizer, 'tfidf_vectorizer.joblib')
joblib.dump(clf_model, 'cic_adjudication_model.joblib')

acc = accuracy_score(y_test_c, clf_model.predict(X_test_c))
print(f"      Model Metrics -> Accuracy: {acc * 100:.2f}%")
print("      Saved Trained Models -> 'cic_adjudication_model.joblib' & 'tfidf_vectorizer.joblib'")

print("\n==================================================")
print(" SUCCESS! All CSVs & Trained Models generated.")
print("==================================================")