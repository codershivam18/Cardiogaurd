import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from xgboost import XGBClassifier

# Load dataset
df = pd.read_csv("Patientdataset.csv")

# Features & Target
X = df.drop(["TenYearCHD", "education"], axis=1, errors='ignore')
y = df["TenYearCHD"]

# Ensure specific column order matching app.py
columns_order = [
    "male","age","currentSmoker","cigsPerDay",
    "BPMeds","prevalentStroke","prevalentHyp",
    "diabetes","totChol","sysBP","diaBP",
    "BMI","heartRate","glucose"
]
X = X[columns_order]

# Fill missing values
X.fillna(X.mean(), inplace=True)

# Stratified Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Handle imbalance
scale_pos_weight = y.value_counts()[0] / y.value_counts()[1]

model = XGBClassifier(
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

# Hyperparameter grid
param_grid = {
    'n_estimators': [200, 400],
    'learning_rate': [0.03, 0.05],
    'max_depth': [3, 4],
    'subsample': [0.8],
    'colsample_bytree': [0.8]
}

# Grid Search with ROC-AUC
grid_search = GridSearchCV(
    model,
    param_grid,
    cv=3,
    scoring='roc_auc',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train_scaled, y_train)

best_model = grid_search.best_estimator_

# Evaluate
y_pred = best_model.predict(X_test_scaled)
y_prob = best_model.predict_proba(X_test_scaled)[:,1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save model & scaler
pickle.dump(best_model, open("Models/xgb_classifier.pkl", "wb"))
pickle.dump(scaler, open("Models/scaler.pkl", "wb"))

print("Model and scaler saved successfully.")