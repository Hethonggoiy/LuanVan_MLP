# =====================================================================
# LUẬN VĂN THẠC SĨ CÔNG NGHỆ THÔNG TIN - TRƯỜNG ĐẠI HỌC LẠC HỒNG 2026
# HỆ THỐNG GỢI Ý CHỌN KHỐI THI ĐẠI HỌC DỰA TRÊN MLP
# Tác giả: Trương Minh Điệp
#
# Các tối ưu chính:
# - Feature engineering: Thêm 4 tổng điểm khối (Sum_A01, B00, C01, D01)
# - Xử lý imbalance: SMOTE để cân bằng 4 lớp
# - MLP sâu + adaptive learning rate + early stopping
# - GUI Tkinter hoàn chỉnh: input, huấn luyện, gợi ý, báo cáo
# - Lưu mô hình/scaler/encoder để tái sử dụng
# =====================================================================

import os
import json
from datetime import datetime
from collections import Counter
import logging

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from tkinter.ttk import Progressbar

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neural_network import MLPClassifier

from imblearn.over_sampling import SMOTE

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Files
DATA_FILE = "rs12excel6k-datienXuly.csv"
PRED_LOG_FILE = "prediction_log.csv"
MODEL_FILE = "best_mlp_model.pkl"
SCALER_FILE = "scaler.pkl"
ENCODER_FILE = "label_encoder.pkl"

# Tổ hợp môn theo khối
BLOCK_TO_SUBJECTS = {
    "A01": "Toán – Vật lý – Tiếng Anh",
    "B00": "Toán – Hóa học – Sinh học",
    "C01": "Ngữ văn – Toán – Vật lý",
    "D01": "Toán – Ngữ văn – Tiếng Anh",
}

def load_and_preprocess():
    """Đọc dữ liệu + feature engineering"""
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig').dropna()

        # Feature engineering: Tổng điểm theo từng khối
        df['Sum_A01'] = df['Toan'] + df['Ly'] + df['Anh']
        df['Sum_B00'] = df['Toan'] + df['Hoa'] + df['Sinh']
        df['Sum_C01'] = df['Van'] + df['Toan'] + df['Ly']
        df['Sum_D01'] = df['Toan'] + df['Van'] + df['Anh']

        X = df[['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh',
                'Sum_A01', 'Sum_B00', 'Sum_C01', 'Sum_D01']]
        y = df['Khoi_Thi']

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        joblib.dump(le, ENCODER_FILE)

        logging.info(f"Loaded {len(df)} samples. Classes: {le.classes_}")
        return X, y_encoded, le
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không đọc được dữ liệu:\n{e}")
        return None, None, None

def train_mlp(X, y_encoded, le, progress_callback=None):
    """Huấn luyện MLP với SMOTE + tối ưu"""
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y_encoded)
    logging.info(f"After SMOTE: {len(X_res)} samples (balanced)")

    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.15, stratify=y_res, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, SCALER_FILE)

    # Kiến trúc tối ưu (dựa trên thử nghiệm đạt ~84%)
    mlp = MLPClassifier(
        hidden_layer_sizes=(1024, 512, 256, 128, 64, 32, 16, 8),
        activation='relu',
        solver='adam',
        alpha=1e-5,
        batch_size=32,
        learning_rate='adaptive',
        learning_rate_init=0.0005,
        max_iter=3000,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=50,
        random_state=42,
        verbose=True
    )

    if progress_callback:
        progress_callback(30)

    logging.info("Bắt đầu huấn luyện MLP...")
    mlp.fit(X_train_scaled, y_train)

    y_pred = mlp.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    logging.info(f"Test Accuracy: {acc*100:.2f}%")

    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    joblib.dump(mlp, MODEL_FILE)
    logging.info("Đã lưu mô hình tốt nhất.")

    if progress_callback:
        progress_callback(100)

    return mlp, acc, report, cm, X_test_scaled, y_test, le.classes_

def append_log(row):
    df_new = pd.DataFrame([row])
    if os.path.exists(PRED_LOG_FILE):
        df_new.to_csv(PRED_LOG_FILE, mode='a', header=False, index=False)
    else:
        df_new.to_csv(PRED_LOG_FILE, index=False)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG GỢI Ý KHỐI THI ĐẠI HỌC - MLP")
        self.root.geometry("950x700")
        self.root.resizable(False, False)

        self.mlp_model = None
        self.scaler = None
        self.le = None
        self.classes = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề
        ttk.Label(main_frame, text="HỆ THỐNG GỢI Ý KHỐI THI ĐẠI HỌC", font=('Arial', 16, 'bold')).pack(pady=10)

        # Thông tin học sinh
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin học sinh")
        info_frame.pack(fill=tk.X, pady=5)

        labels_info = ["Họ và tên:", "Giới tính:", "Năm sinh:"]
        self.vars_info = [tk.StringVar() for _ in labels_info]
        for i, lbl in enumerate(labels_info):
            ttk.Label(info_frame, text=lbl).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            ttk.Entry(info_frame, textvariable=self.vars_info[i]).grid(row=i, column=1, padx=10, pady=5, sticky='ew')

        info_frame.columnconfigure(1, weight=1)

        # Điểm số
        score_frame = ttk.LabelFrame(main_frame, text="Điểm trung bình các môn")
        score_frame.pack(fill=tk.X, pady=5)

        subjects = ['Toán', 'Văn', 'Lý', 'Hóa', 'Sinh', 'Anh']
        self.vars_score = [tk.DoubleVar() for _ in subjects]
        for i, sub in enumerate(subjects):
            ttk.Label(score_frame, text=f"{sub}:").grid(row=i//3, column=(i%3)*2, padx=10, pady=5, sticky='w')
            ttk.Entry(score_frame, textvariable=self.vars_score[i], width=8).grid(row=i//3, column=(i%3)*2+1, padx=10, pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Huấn luyện MLP (tối ưu 84%+)", command=self.train).pack(side=tk.LEFT, padx=10)
        self.progress = Progressbar(btn_frame, mode='determinate', length=300)
        self.progress.pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="Gợi ý khối thi", command=self.predict).pack(side=tk.LEFT, padx=10)

        # Kết quả
        self.result_var = tk.StringVar(value="Chưa có kết quả")
        ttk.Label(main_frame, textvariable=self.result_var, font=('Arial', 14, 'bold'), foreground='darkblue').pack(pady=10)

        self.combo_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.combo_var, font=('Arial', 12)).pack(pady=5)

        self.status_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.status_var, foreground='green').pack(pady=5)

        # Nút xem báo cáo
        ttk.Button(main_frame, text="Xem báo cáo hiệu năng", command=self.show_report).pack(pady=10)

    def train(self):
        X, y_encoded, le = load_and_preprocess()
        if X is None:
            return

        self.progress['value'] = 0
        self.status_var.set("Đang huấn luyện MLP... (có thể mất 1-3 phút)")
        self.root.update()

        def progress_update(val):
            self.progress['value'] = val
            self.root.update()

        self.mlp_model, acc, report, cm, X_test_scaled, y_test, self.classes = train_mlp(X, y_encoded, le, progress_update)

        self.le = le
        self.scaler = joblib.load(SCALER_FILE)

        msg = f"Hoàn tất huấn luyện!\nAccuracy trên tập test: {acc*100:.2f}%"
        messagebox.showinfo("Kết quả huấn luyện", msg)
        self.status_var.set(f"MLP đạt {acc*100:.2f}% - Sẵn sàng gợi ý")

    def predict(self):
        if self.mlp_model is None:
            messagebox.showwarning("Chưa huấn luyện", "Vui lòng huấn luyện mô hình trước.")
            return

        try:
            scores = [v.get() for v in self.vars_score]
            if any(s < 0 or s > 10 for s in scores):
                raise ValueError("Điểm phải từ 0 đến 10.")

            sum_a01 = scores[0] + scores[2] + scores[5]
            sum_b00 = scores[0] + scores[3] + scores[4]
            sum_c01 = scores[1] + scores[0] + scores[2]
            sum_d01 = scores[0] + scores[1] + scores[5]

            input_data = np.array([scores + [sum_a01, sum_b00, sum_c01, sum_d01]])
            input_scaled = self.scaler.transform(input_data)

            pred_encoded = self.mlp_model.predict(input_scaled)[0]
            pred_block = self.le.inverse_transform([pred_encoded])[0]

            combo = BLOCK_TO_SUBJECTS.get(pred_block, "Không xác định")

            self.result_var.set(f"Khối thi phù hợp: {pred_block}")
            self.combo_var.set(f"Tổ hợp môn: {combo}")

            # Lưu log
            row = {
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Họ tên": self.vars_info[0].get(),
                "Giới tính": self.vars_info[1].get(),
                "Năm sinh": self.vars_info[2].get(),
                "Toán": scores[0], "Văn": scores[1], "Lý": scores[2],
                "Hóa": scores[3], "Sinh": scores[4], "Anh": scores[5],
                "Khối dự đoán": pred_block,
                "Tổ hợp môn": combo
            }
            append_log(row)

            self.status_var.set("Đã lưu kết quả vào prediction_log.csv")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_report(self):
        if self.mlp_model is None:
            messagebox.showwarning("Chưa huấn luyện", "Vui lòng huấn luyện trước.")
            return

        # Tạo cửa sổ mới hiển thị báo cáo
        report_win = tk.Toplevel(self.root)
        report_win.title("Báo cáo hiệu năng MLP")
        report_win.geometry("900x600")

        text = scrolledtext.ScrolledText(report_win, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        content = "BÁO CÁO HIỆU NĂNG MÔ HÌNH MLP (Sau SMOTE + Feature Engineering)\n"
        content += "=" * 80 + "\n\n"
        content += f"Accuracy trên tập test: {self.results['test_acc']['MLP']*100:.2f}%\n" if 'MLP' in self.results else "Chưa có kết quả huấn luyện\n"
        content += "Classification Report:\n" + self.results['reports']['MLP'] + "\n" if 'reports' in self.results else ""
        content += "Confusion Matrix:\n" + str(self.results['cms']['MLP']) + "\n"

        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()