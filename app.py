from flask import Flask, request, render_template, redirect, url_for, session, flash
import pickle
import pandas as pd
import os
import csv
import sqlite3
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_heart_key'

def init_db():
    conn = sqlite3.connect('cardioguard.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            prediction_text TEXT,
            confidence REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('cardioguard.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------
# Load Model & Scaler
# ----------------------------
try:
    model = pickle.load(open("Models/xgb_classifier.pkl", "rb"))
    scaler = pickle.load(open("Models/scaler.pkl", "rb"))
    print("Model & Scaler loaded successfully.")
except Exception as e:
    print("Error loading model or scaler:", e)
    model = None
    scaler = None


# ----------------------------
# Prediction Function
# ----------------------------
def predict_heart_risk(form_data):
    try:
        data = {
            "male": 1 if form_data.get("male", "").lower() == "male" else 0,
            "age": int(form_data.get("age", 0)),
            "currentSmoker": 1 if form_data.get("currentSmoker", "").lower() == "yes" else 0,
            "cigsPerDay": float(form_data.get("cigsPerDay", 0)),
            "BPMeds": 1 if form_data.get("BPMeds", "").lower() == "yes" else 0,
            "prevalentStroke": 1 if form_data.get("prevalentStroke", "").lower() == "yes" else 0,
            "prevalentHyp": 1 if form_data.get("prevalentHyp", "").lower() == "yes" else 0,
            "diabetes": 1 if form_data.get("diabetes", "").lower() == "yes" else 0,
            "totChol": float(form_data.get("totChol", 0)),
            "sysBP": float(form_data.get("sysBP", 0)),
            "diaBP": float(form_data.get("diaBP", 0)),
            "BMI": float(form_data.get("BMI", 0)),
            "heartRate": float(form_data.get("heartRate", 0)),
            "glucose": float(form_data.get("glucose", 0))
        }

        columns_order = [
            "male","age","currentSmoker","cigsPerDay",
            "BPMeds","prevalentStroke","prevalentHyp",
            "diabetes","totChol","sysBP","diaBP",
            "BMI","heartRate","glucose"
        ]

        input_df = pd.DataFrame([data])[columns_order]

        # Apply scaling
        input_scaled = scaler.transform(input_df)

        prediction = int(model.predict(input_scaled)[0])
        probability = float(model.predict_proba(input_scaled)[0][1])

        return prediction, round(probability * 100, 2)

    except ValueError:
        return None, "Please enter valid numeric values."
    except Exception as e:
        print("Prediction error:", e)
        return None, "Unexpected error occurred."


# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def home():
    return render_template('Home1.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    raw_predictions = conn.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY timestamp DESC', (session['user_id'],)).fetchall()
    conn.close()
    
    # Process rows to handle any legacy corrupted binary data
    predictions = []
    for row in raw_predictions:
        p = dict(row)
        # If 'confidence' is bytes/blob from a previous bug, try to recover or default
        if isinstance(p['confidence'], bytes):
            # This is a safety fallback for the user's observed 'garbage' data
            p['confidence'] = "Legacy Data"
        predictions.append(p)
        
    return render_template('Dashboard.html', username=session['username'], predictions=predictions)

@app.route('/prediction')
@login_required
def prediction_page():
    return render_template('Index1.html')

@app.route('/symptoms')
@login_required
def symptoms():
    return render_template('Symptoms.html')

@app.route('/contacts')
@login_required
def contacts():
    return render_template('Contacts.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('Login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, generate_password_hash(password)))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
        finally:
            conn.close()
            
    return render_template('Register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/predict', methods=['POST'])
@login_required
def predict_route():

    if model is None or scaler is None:
        return render_template(
            'predict.html',
            prediction="Model not loaded properly.",
            confidence="N/A"
        )

    prediction, confidence = predict_heart_risk(request.form)

    if prediction is None:
        return render_template(
            'predict.html',
            prediction=confidence,
            confidence="N/A"
        )

    prediction_text = (
        "High Risk of Heart Disease"
        if prediction == 1
        else "Low Risk of Heart Disease"
    )
    
    # Save to DB
    conn = get_db()
    conn.execute('INSERT INTO predictions (user_id, prediction_text, confidence) VALUES (?, ?, ?)',
                 (session['user_id'], prediction_text, confidence))
    conn.commit()
    conn.close()

    return render_template(
        'predict.html',
        prediction=prediction_text,
        confidence=confidence
    )


# ----------------------------
# Run App
# ----------------------------
if __name__ == '__main__':
    print("Starting Flask Server...")
    app.run(debug=True)