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

# Save Dataset 1 CSV
df_response.to_csv('rti_department_response_dataset.csv', index=False)
print("\n[1/2] Saved 'rti_department_response_dataset.csv' (1,200 rows)")

# Train Regression Model
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
    "Rejected on grounds of seeking opinions, hypothetical questions rather than records."
]

df_cic = pd.DataFrame({
    'rejection_ground': np.random.choice(rejection_reasons, 1000),
    'appeal_stage': np.random.choice(['First Appeal', 'Second Appeal (CIC)'], 1000),
    'department': np.random.choice(departments, 1000)
})

def assign_outcome(row):
    g = row['rejection_ground']
    if "8(1)(j)" in g:
        return np.random.choice(["OVERTURNED_ALLOWED", "REJECTED_DISMISSED"], p=[0.65, 0.35])
    elif "8(1)(d)" in g:
        return np.random.choice(["OVERTURNED_ALLOWED", "PARTIALLY_ALLOWED"], p=[0.70, 0.30])
    elif "Section 24" in g:
        return np.random.choice(["REJECTED_DISMISSED", "PARTIALLY_ALLOWED"], p=[0.80, 0.20])
    else:
        return np.random.choice(["OVERTURNED_ALLOWED", "REJECTED_DISMISSED", "PARTIALLY_ALLOWED"], p=[0.50, 0.30, 0.20])

df_cic['outcome'] = df_cic.apply(assign_outcome, axis=1)

# Save Dataset 2 CSV
df_cic.to_csv('cic_adjudication_dataset.csv', index=False)
print("\n[2/2] Saved 'cic_adjudication_dataset.csv' (1,000 rows)")

# Train Classifier Model
vectorizer = TfidfVectorizer(max_features=100)
X_text = vectorizer.fit_transform(df_cic['rejection_ground']).toarray()
X_meta = pd.get_dummies(df_cic[['appeal_stage', 'department']], drop_first=True).values

X_cic = np.hstack((X_text, X_meta))
y_cic = df_cic['outcome']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cic, y_cic, test_size=0.2, random_state=42)

clf_model = RandomForestClassifier(n_estimators=100, random_state=42)
clf_model.fit(X_train_c, y_train_c)

y_pred_c = clf_model.predict(X_test_c)
acc = accuracy_score(y_test_c, y_pred_c)

joblib.dump(clf_model, 'cic_adjudication_model.joblib')
print(f"      Model Metrics -> Accuracy: {acc * 100:.2f}%")
print("      Saved Trained Model -> 'cic_adjudication_model.joblib'")

print("\n==================================================")
print(" SUCCESS! All 2 CSVs & 2 Trained Models generated.")
print("==================================================")