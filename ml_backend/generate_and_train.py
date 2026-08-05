import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
import joblib
import random

np.random.seed(42)
random.seed(42)

print("🚀 GENERATING REALISTIC FULL-LENGTH DATASET & TRAINING ML MODEL...")

# 1. Boilerplate Administrative Noise (to simulate real letters)
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

# 2. Core Legal Triggers
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

# 3. Generate 2,000 synthetic full-length letters
dataset = []
for _ in range(2000):
    header = random.choice(headers)
    footer = random.choice(footers)
    trigger, outcome = random.choice(all_triggers)
    
    # Add random noise words to simulate OCR inconsistencies 
    noise = " ".join(random.choices(["regarding", "department", "appeals", "stipulated", "records", "perusal"], k=3))
    
    full_text = f"{header} {noise}. {trigger} {footer}"
    dataset.append({"rejection_ground": full_text, "outcome": outcome})

df_cic = pd.DataFrame(dataset)

# 4. Train True NLP Classifier
# Using a broader n-gram range and stripping english stop words to isolate legal phrases
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=5000, stop_words='english')
X_cic = vectorizer.fit_transform(df_cic['rejection_ground']).toarray()
y_cic = df_cic['outcome']

X_train, X_test, y_train, y_test = train_test_split(X_cic, y_cic, test_size=0.2, random_state=42)

# Random Forest with more trees for smoother probability variance
clf_model = RandomForestClassifier(n_estimators=300, max_depth=20, random_state=42)
clf_model.fit(X_train, y_train)

# 5. Save Models
joblib.dump(vectorizer, 'tfidf_vectorizer.joblib')
joblib.dump(clf_model, 'cic_adjudication_model.joblib')

acc = accuracy_score(y_test, clf_model.predict(X_test))
print(f"✅ True ML Training Complete! Accuracy: {acc * 100:.2f}%")
print("✅ Saved 'cic_adjudication_model.joblib' & 'tfidf_vectorizer.joblib'")