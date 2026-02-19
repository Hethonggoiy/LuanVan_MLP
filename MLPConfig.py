import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ============================================================
# CẤU HÌNH MÔ HÌNH MLP 8 LỚP ẨN
# ============================================================
def train_deep_mlp():
    # 1. Đọc dữ liệu
    try:
        df = pd.read_csv("rs12excel6k-datienXuly.csv")
    except FileNotFoundError:
        return None, None, None, "Không tìm thấy file dữ liệu!"

    # 2. Feature Engineering (Tạo thêm biến phụ trợ để hỗ trợ mạng sâu)
    df['Sum_All'] = df[['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh']].sum(axis=1)
    
    X = df.drop('Khoi_Thi', axis=1)
    y = df['Khoi_Thi']

    # 3. Tiền xử lý
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.15, random_state=42, stratify=y_encoded
    )

    # 4. Cấu hình MLP 8 lớp ẩn (Theo yêu cầu)
    mlp = MLPClassifier(
        hidden_layer_sizes=(512, 384, 256, 192, 128, 64, 32, 16), # 8 lớp
        activation='relu',
        solver='adam',
        alpha=0.01,                # Tăng mạnh Regularization để kiểm soát mạng sâu
        learning_rate_init=0.0005,  # Tốc độ học thấp để hội tụ sâu
        max_iter=5000,             # Tăng số vòng lặp cho mạng sâu
        early_stopping=True,       # Ngăn chặn overfitting
        validation_fraction=0.1,
        n_iter_no_change=50,       # Kiên nhẫn hơn khi tìm điểm tối ưu
        random_state=42
    )

    mlp.fit(X_train, y_train)
    return mlp, scaler, le, X_test, y_test

# ============================================================
# GIAO DIỆN ỨNG DỤNG (Times New Roman, 13pt)
# ============================================================
class DeepMLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deep Learning MLP - Hệ thống gợi ý khối thi")
        self.root.geometry("1100x750")
        
        # Font chuẩn in ấn
        self.font_standard = ("Times New Roman", 13)
        self.font_bold = ("Times New Roman", 13, "bold")

        # Huấn luyện
        self.model, self.scaler, self.le, self.X_test, self.y_test = train_deep_mlp()
        
        if self.model is None:
            messagebox.showerror("Lỗi", "Vui lòng kiểm tra file CSV!")
            return

        self.setup_ui()

    def setup_ui(self):
        # Frame chính
        main_frame = tk.Frame(self.root, bg="#fdfdfd")
        main_frame.pack(fill="both", expand=True)

        # Tiêu đề
        title = tk.Label(main_frame, text="PHÂN TÍCH ĐIỂM HỌC TẬP VỚI MẠNG NEURAL 8 LỚP", 
                         font=("Times New Roman", 16, "bold"), fg="#0d47a1", bg="#fdfdfd")
        title.pack(pady=20)

        content_frame = tk.Frame(main_frame, bg="#fdfdfd")
        content_frame.pack(padx=30, fill="both", expand=True)

        # Trái: Nhập liệu
        input_frame = tk.LabelFrame(content_frame, text=" Dữ liệu đầu vào ", font=self.font_bold, bg="#ffffff")
        input_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.entries = {}
        fields = [('Toán', 'Toan'), ('Văn', 'Van'), ('Lý', 'Ly'), 
                  ('Hóa', 'Hoa'), ('Sinh', 'Sinh'), ('Anh', 'Anh')]

        for label, key in fields:
            row = tk.Frame(input_frame, bg="#ffffff")
            row.pack(fill="x", padx=15, pady=8)
            tk.Label(row, text=f"{label}:", font=self.font_standard, bg="#ffffff", width=10, anchor="w").pack(side="left")
            ent = tk.Entry(row, font=self.font_standard, width=12, relief="solid")
            ent.pack(side="right")
            self.entries[key] = ent

        btn_predict = tk.Button(input_frame, text="DỰ BÁO NGAY", font=self.font_bold, 
                                bg="#1565c0", fg="white", height=2, command=self.predict)
        btn_predict.pack(fill="x", padx=15, pady=30)

        # Phải: Hiển thị kết quả & Accuracy
        self.result_frame = tk.LabelFrame(content_frame, text=" Kết quả phân tích sâu ", font=self.font_bold, bg="#ffffff")
        self.result_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.lbl_acc = tk.Label(self.result_frame, text=f"Model Accuracy: {accuracy_score(self.y_test, self.model.predict(self.X_test))*100:.2f}%", 
                                font=("Times New Roman", 11, "italic"), bg="#ffffff")
        self.lbl_acc.pack(anchor="ne", padx=10)

        self.lbl_main_res = tk.Label(self.result_frame, text="Chưa có dữ liệu", font=("Times New Roman", 24, "bold"), 
                                     fg="#388e3c", bg="#ffffff", pady=50)
        self.lbl_main_res.pack()

    def predict(self):
        try:
            # Lấy điểm và tạo feature mới
            scores = [float(self.entries[k].get()) for k in ['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh']]
            sum_score = sum(scores)
            full_data = scores + [sum_score]
            
            # Dự báo
            data_scaled = self.scaler.transform([full_data])
            pred_idx = self.model.predict(data_scaled)[0]
            khoi_thi = self.le.inverse_transform([pred_idx])[0]
            
            # Hiển thị
            self.lbl_main_res.config(text=f"KHỐI THI: {khoi_thi}")
            
        except Exception:
            messagebox.showwarning("Lỗi", "Vui lòng nhập điểm số từ 0 đến 10")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeepMLPApp(root)
    root.mainloop()