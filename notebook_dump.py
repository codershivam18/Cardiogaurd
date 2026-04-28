# Cell 0
import pandas as pd
import numpy as np
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from xgboost import XGBClassifier

# Cell 1
df = pd.read_csv("Patientdataset.csv")

print("Shape:", df.shape)
print(df.head())
print(df.info())

# Cell 2
print(df.isnull().sum())

# Cell 3
df = df.drop("education", axis=1)

# Cell 4
print(df.isnull().sum())

# Cell 5
df["BPMeds"] = df["BPMeds"].fillna(0).astype(int)

# Cell 6
small_missing_cols = ["cigsPerDay", "totChol", "BMI", "heartRate"]

for col in small_missing_cols:
    df[col] = df[col].fillna(df[col].median())

# Cell 7
print((388 / len(df)) * 100)

# Cell 8
df["glucose"] = df["glucose"].fillna(df["glucose"].median())

# Cell 9
print(df.isnull().sum())

# Cell 10
X = df.drop("TenYearCHD", axis=1)
y = df["TenYearCHD"]

# Cell 11
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# Cell 12
scale_pos_weight = y.value_counts()[0] / y.value_counts()[1]

# Cell 13
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=4,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

model.fit(X_train, y_train)

# Cell 14
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC AUC:", roc_auc_score(y_test, y_prob))
print(classification_report(y_test, y_pred))

# Cell 15
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt="d")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# Cell 16
model = XGBClassifier(
    n_estimators=600,
    learning_rate=0.03,
    max_depth=3,
    scale_pos_weight=scale_pos_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# Cell 17
import matplotlib.pyplot as plt

# Cell 18
from xgboost import XGBClassifier

# Create model
model = XGBClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=4,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Cell 19
import matplotlib.pyplot as plt
import numpy as np

# Get importance
importance = model.feature_importances_

# Sort features
indices = np.argsort(importance)

# Plot
plt.figure(figsize=(8,6))
plt.barh(range(len(indices)), importance[indices])
plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
plt.title("Feature Importance (XGBoost)")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.show()

# Cell 20
print(model)

# Cell 21
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt

# Predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

# Metrics
print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)

plt.figure()
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# Cell 22


# Cell 23
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# Cell 24
model = XGBClassifier(
    n_estimators=800,
    learning_rate=0.02,
    max_depth=3,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0.1,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

model.fit(X_train, y_train)

# Cell 25
from sklearn.metrics import classification_report, roc_auc_score

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print(classification_report(y_test, y_pred))

# Cell 26
from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(class_weight='balanced', max_iter=1000)
lr.fit(X_train, y_train)

y_prob_lr = lr.predict_proba(X_test)[:,1]
print("ROC-AUC:", roc_auc_score(y_test, y_prob_lr))

# Cell 27
!pip install imbalanced-learn

# Cell 28
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)

X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

print("Before SMOTE:", y_train.value_counts())
print("After SMOTE:", pd.Series(y_resampled).value_counts())

# Cell 29
model = XGBClassifier(
    n_estimators=600,
    learning_rate=0.03,
    max_depth=3,
    random_state=42
)

model.fit(X_resampled, y_resampled)

# Cell 30
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print(classification_report(y_test, y_pred))

# Cell 31
import pickle

model = pickle.load(open("Models/xgb_classifier.pkl", "rb"))

# Cell 32
import pandas as pd

input_data = {
    "male": 1,
    "age": 55,
    "currentSmoker": 1,
    "cigsPerDay": 10,
    "BPMeds": 0,
    "prevalentStroke": 0,
    "prevalentHyp": 1,
    "diabetes": 0,
    "totChol": 240,
    "sysBP": 150,
    "diaBP": 95,
    "BMI": 28,
    "heartRate": 80,
    "glucose": 110
}

input_df = pd.DataFrame([input_data])

prediction = model.predict(input_df)[0]
probability = model.predict_proba(input_df)[0][1]

print("Prediction:", "High Risk" if prediction == 1 else "Low Risk")
print("Risk Probability:", round(probability * 100, 2), "%")

# Cell 33
male = int(input("Male (1=yes, 0=no): "))
age = int(input("Age: "))
currentSmoker = int(input("Current Smoker (1/0): "))
cigsPerDay = float(input("Cigarettes per day: "))
BPMeds = int(input("BP Meds (1/0): "))
prevalentStroke = int(input("Stroke history (1/0): "))
prevalentHyp = int(input("Hypertension (1/0): "))
diabetes = int(input("Diabetes (1/0): "))
totChol = float(input("Total Cholesterol: "))
sysBP = float(input("Systolic BP: "))
diaBP = float(input("Diastolic BP: "))
BMI = float(input("BMI: "))
heartRate = float(input("Heart Rate: "))
glucose = float(input("Glucose: "))

input_data = pd.DataFrame([[
    male, age, currentSmoker, cigsPerDay,
    BPMeds, prevalentStroke, prevalentHyp,
    diabetes, totChol, sysBP, diaBP,
    BMI, heartRate, glucose
]], columns=[
    "male","age","currentSmoker","cigsPerDay",
    "BPMeds","prevalentStroke","prevalentHyp",
    "diabetes","totChol","sysBP","diaBP",
    "BMI","heartRate","glucose"
])

prediction = model.predict(input_data)[0]
probability = model.predict_proba(input_data)[0][1]

print("\nPrediction:", "High Risk" if prediction == 1 else "Low Risk")
print("Risk Probability:", round(probability * 100, 2), "%")