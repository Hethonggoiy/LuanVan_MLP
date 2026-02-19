from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE

app = Flask(__name__)

# --- CẤU HÌNH ĐƯỜNG DẪN ---
DATA_FILE = "rs12excel6k-datienXuly.csv"
MODEL_DIR = "saved_models"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

MODEL_PATH = os.path.join(MODEL_DIR, "mlp_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoder.pkl")

# --- LOGIC HUẤN LUYỆN (DÀNH CHO LUẬN VĂN) ---
def train_system():
    if not os.path.exists(DATA_FILE):
        return None, "Không tìm thấy file dữ liệu CSV."
    
    df = pd.read_csv(DATA_FILE).dropna()
    # Feature Engineering (Tổng điểm khối)
    df['Sum_A01'] = df['Toan'] + df['Ly'] + df['Anh']
    df['Sum_B00'] = df['Toan'] + df['Hoa'] + df['Sinh']
    df['Sum_C01'] = df['Van'] + df['Toan'] + df['Ly']
    df['Sum_D01'] = df['Toan'] + df['Van'] + df['Anh']

    X = df[['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh', 'Sum_A01', 'Sum_B00', 'Sum_C01', 'Sum_D01']]
    y = df['Khoi_Thi']

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Xử lý mất cân bằng dữ liệu
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y_encoded)
    
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.15, stratify=y_res, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Kiến trúc MLP 8 lớp ẩn (Deep Neural Network)
    mlp = MLPClassifier(
        hidden_layer_sizes=(1024, 512, 256, 128, 64, 32, 16, 8),
        activation='relu', solver='adam', max_iter=2000,
        early_stopping=True, n_iter_no_change=50, random_state=42
    )
    mlp.fit(X_train_scaled, y_train)
    
    joblib.dump(mlp, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(le, ENCODER_PATH)
    return mlp, "Huấn luyện hoàn tất."

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        scores = [float(data[m]) for m in ['toan', 'van', 'ly', 'hoa', 'sinh', 'anh']]
        
        # Feature Engineering cho dữ liệu đầu vào
        sums = [scores[0]+scores[2]+scores[5], scores[0]+scores[3]+scores[4], 
                scores[1]+scores[0]+scores[2], scores[0]+scores[1]+scores[5]]
        
        X_input = np.array([scores + sums])
        
        # Load mô hình
        mlp = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        le = joblib.load(ENCODER_PATH)
        
        X_scaled = scaler.transform(X_input)
        proba = mlp.predict_proba(X_scaled)[0]
        pred_idx = np.argmax(proba)
        
        return jsonify({
            'success': True,
            'block': le.classes_[pred_idx],
            'probabilities': proba.tolist(),
            'classes': le.classes_.tolist()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/train_status')
def train_status():
    _, msg = train_system()
    return jsonify({'message': msg})

if __name__ == '__main__':
    # Tự động huấn luyện nếu chưa có file model
    if not os.path.exists(MODEL_PATH):
        print("Đang huấn luyện mô hình lần đầu...")
        train_system()
    app.run(host='0.0.0.0', port=5000, debug=True)