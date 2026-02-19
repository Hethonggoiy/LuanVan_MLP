# ============================================================
# ỨNG DỤNG GỢI Ý KHỐI THI ĐẠI HỌC (DT | SVM | MLP)
# - Giữ nguyên mô hình + pipeline train/evaluate
# - Nâng cấp giao diện chuyên nghiệp
# - Bổ sung nhập thông tin học sinh (Họ tên, Giới tính, Năm sinh)
# - Tự động lưu cấu hình (app_config.json)
# - Lưu kết quả mỗi lần gợi ý (prediction_log.csv)
# - Chỉ hiển thị 1 khối thi (theo đa số phiếu) + tổ hợp môn tương ứng
# - Nút "Đánh giá mô hình" (hiển thị report + confusion matrix + ROC micro-AUC)
# ============================================================

import os
import json
from datetime import datetime
from collections import Counter

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import pandas as pd
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================
# FILES
# =========================
APP_CONFIG_FILE = "app_config.json"
PRED_LOG_FILE = "prediction_log.csv"
DATA_FILE = "rs12excel6k-datienXuly.csv"

# =========================
# KHỐI THI -> TỔ HỢP MÔN
# =========================
BLOCK_TO_SUBJECTS = {
    "A01": "Toán – Vật lý – Tiếng Anh",
    "B00": "Toán – Hóa học – Sinh học",
    "C01": "Ngữ văn – Toán – Vật lý",
    "D01": "Toán – Ngữ văn – Tiếng Anh",
}


# ────────────────────────────────────────────────
#                LOAD & TRAIN
# ────────────────────────────────────────────────
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        X = df[['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh']]
        y = df['Khoi_Thi']
        return X, y
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc file CSV:\n{e}")
        return None, None


def compute_roc(y_true_bin, y_score, classes):
    fpr_dict, tpr_dict, auc_dict = {}, {}, {}
    for i, cls in enumerate(classes):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        fpr_dict[cls] = fpr
        tpr_dict[cls] = tpr
        auc_dict[cls] = auc(fpr, tpr)

    fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    auc_micro = auc(fpr_micro, tpr_micro)

    return {
        'fpr_per_class': fpr_dict, 'tpr_per_class': tpr_dict, 'auc_per_class': auc_dict,
        'fpr_micro': fpr_micro, 'tpr_micro': tpr_micro, 'auc_micro': auc_micro
    }


def train_and_evaluate(X, y):
    # Split 80/20, stratified
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    lb = LabelBinarizer()
    y_test_bin = lb.fit_transform(y_test)
    classes = lb.classes_

    results = {'models': {}, 'accs': {}, 'reports': {}, 'cms': {}, 'roc': {}}

    # ─── Decision Tree ───
    dt = DecisionTreeClassifier(
        max_depth=28, min_samples_split=12, min_samples_leaf=4, random_state=42
    )
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    results['models']['DT'] = dt
    results['accs']['DT'] = accuracy_score(y_test, y_pred)
    results['reports']['DT'] = classification_report(y_test, y_pred)
    results['cms']['DT'] = confusion_matrix(y_test, y_pred)
    results['roc']['DT'] = compute_roc(y_test_bin, dt.predict_proba(X_test), classes)

    # ─── SVM ───
    svm = SVC(kernel='rbf', C=80, gamma='scale', probability=True, random_state=42)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    results['models']['SVM'] = svm
    results['accs']['SVM'] = accuracy_score(y_test, y_pred)
    results['reports']['SVM'] = classification_report(y_test, y_pred)
    results['cms']['SVM'] = confusion_matrix(y_test, y_pred)
    results['roc']['SVM'] = compute_roc(y_test_bin, svm.predict_proba(X_test), classes)

    # ─── MLP (8 lớp ẩn - tối ưu) ───
    mlp = MLPClassifier(
        hidden_layer_sizes=(512, 384, 256, 192, 128, 64, 32, 16),
        activation='relu',
        solver='adam',
        learning_rate='adaptive',
        learning_rate_init=0.0008,
        max_iter=4000,
        early_stopping=True,
        validation_fraction=0.12,
        n_iter_no_change=100,
        tol=1e-4,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-8,
        random_state=42,
        verbose=False
    )
    mlp.fit(X_train, y_train)
    y_pred = mlp.predict(X_test)
    results['models']['MLP'] = mlp
    results['accs']['MLP'] = accuracy_score(y_test, y_pred)
    results['reports']['MLP'] = classification_report(y_test, y_pred)
    results['cms']['MLP'] = confusion_matrix(y_test, y_pred)
    results['roc']['MLP'] = compute_roc(y_test_bin, mlp.predict_proba(X_test), classes)

    return results, classes


# ────────────────────────────────────────────────
#                 APP CONFIG I/O
# ────────────────────────────────────────────────
def load_app_config():
    if not os.path.exists(APP_CONFIG_FILE):
        return {}
    try:
        with open(APP_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_app_config(cfg: dict):
    try:
        with open(APP_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def append_prediction_log(row: dict):
    df = pd.DataFrame([row])
    file_exists = os.path.exists(PRED_LOG_FILE)
    df.to_csv(PRED_LOG_FILE, mode="a", header=not file_exists, index=False, encoding="utf-8-sig")


# ────────────────────────────────────────────────
#                   UI APP
# ────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Gợi Ý Khối Thi Đại Học (DT | SVM | MLP)")
        self.root.geometry("1280x880")
        self.root.configure(bg="#f3f6fb")

        self.results = None
        self.classes = None

        self._setup_style()
        self._build_layout()
        self._load_last_config_to_form()

        # auto-save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # =========================
    # STYLE
    # =========================
    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#f3f6fb")
        style.configure("Card.TLabelframe", background="#ffffff", padding=12)
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#1f2937")
        style.configure("TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f3f6fb", foreground="#0f172a",
                        font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background="#f3f6fb", foreground="#334155",
                        font=("Segoe UI", 11))

        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.map("Primary.TButton",
                  background=[("active", "#2563eb")],
                  foreground=[("active", "white")])

        style.configure("Ghost.TButton", font=("Segoe UI", 11), padding=10)

        style.configure("TEntry", font=("Segoe UI", 11), padding=6)
        style.configure("TCombobox", font=("Segoe UI", 11), padding=6)

    # =========================
    # LAYOUT
    # =========================
    def _build_layout(self):
        # Top title
        header = ttk.Frame(self.root, style="App.TFrame")
        header.pack(fill=tk.X, padx=20, pady=(16, 10))

        ttk.Label(header, text="Hệ Thống Gợi Ý Khối Thi Đại Học", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Mô hình so sánh: Decision Tree – SVM – MLP (tối ưu)",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(4, 0))

        # Main container (2 columns)
        main = ttk.Frame(self.root, style="App.TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left = ttk.Frame(main, style="App.TFrame")
        right = ttk.Frame(main, style="App.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ----- LEFT: Student card + Score card + Buttons -----
        self.student_card = ttk.LabelFrame(left, text=" Thông tin học sinh ", style="Card.TLabelframe")
        self.student_card.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(self.student_card, text="Họ tên").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 4))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.student_card, width=30, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=0, sticky="we", padx=8, pady=(0, 10))

        ttk.Label(self.student_card, text="Giới tính").grid(row=0, column=1, sticky="w", padx=8, pady=(6, 4))
        self.gender_var = tk.StringVar()
        self.gender_cb = ttk.Combobox(self.student_card, values=["Nam", "Nữ", "Khác"], width=10,
                                      state="readonly", textvariable=self.gender_var)
        self.gender_cb.grid(row=1, column=1, sticky="we", padx=8, pady=(0, 10))

        ttk.Label(self.student_card, text="Năm sinh").grid(row=0, column=2, sticky="w", padx=8, pady=(6, 4))
        self.birth_var = tk.StringVar()
        self.birth_entry = ttk.Entry(self.student_card, width=10, textvariable=self.birth_var)
        self.birth_entry.grid(row=1, column=2, sticky="we", padx=8, pady=(0, 10))

        for c in range(3):
            self.student_card.columnconfigure(c, weight=1)

        # Scores
        self.score_card = ttk.LabelFrame(left, text=" Nhập điểm 6 môn ", style="Card.TLabelframe")
        self.score_card.pack(fill=tk.X, pady=(0, 12))

        self.score_vars = {}
        subjects = [("Toán", "Toan"), ("Văn", "Van"), ("Lý", "Ly"),
                    ("Hóa", "Hoa"), ("Sinh", "Sinh"), ("Anh", "Anh")]

        for i, (label, key) in enumerate(subjects):
            r = (i // 2) * 2
            c = (i % 2) * 2

            ttk.Label(self.score_card, text=label).grid(row=r, column=c, sticky="w", padx=8, pady=(8, 2))
            v = tk.StringVar()
            e = ttk.Entry(self.score_card, width=14, textvariable=v)
            e.grid(row=r + 1, column=c, sticky="we", padx=8, pady=(0, 10))
            self.score_vars[key] = v

            self.score_card.columnconfigure(c, weight=1)

        # Buttons
        btns = ttk.Frame(left, style="App.TFrame")
        btns.pack(fill=tk.X)

        self.train_btn = ttk.Button(btns, text="Huấn luyện & đánh giá", style="Primary.TButton", command=self.train)
        self.train_btn.pack(fill=tk.X, pady=(0, 10))

        self.predict_btn = ttk.Button(btns, text="Gợi ý khối thi", style="Primary.TButton", command=self.predict)
        self.predict_btn.pack(fill=tk.X, pady=(0, 10))

        self.eval_btn = ttk.Button(btns, text="Đánh giá mô hình", style="Ghost.TButton", command=self.show_evaluation)
        self.eval_btn.pack(fill=tk.X)

        # Status hint
        self.status_var = tk.StringVar(value="Trạng thái: Chưa huấn luyện mô hình.")
        status_lbl = ttk.Label(left, textvariable=self.status_var, background="#f3f6fb",
                               foreground="#475569", font=("Segoe UI", 10))
        status_lbl.pack(anchor="w", pady=(12, 0), padx=2)

        # ----- RIGHT: Result + Notebook (Report, ROC) -----
        result_card = ttk.LabelFrame(right, text=" Kết quả gợi ý ", style="Card.TLabelframe")
        result_card.pack(fill=tk.X, pady=(0, 12))

        self.result_var = tk.StringVar(value="Chưa có kết quả. Vui lòng huấn luyện và nhập điểm.")
        self.result_big = ttk.Label(result_card, textvariable=self.result_var,
                                    font=("Segoe UI", 16, "bold"), foreground="#1d4ed8")
        self.result_big.pack(anchor="w", padx=8, pady=(8, 0))

        self.combo_var = tk.StringVar(value="")
        self.combo_lbl = ttk.Label(result_card, textvariable=self.combo_var,
                                   font=("Segoe UI", 12), foreground="#0f172a")
        self.combo_lbl.pack(anchor="w", padx=8, pady=(6, 10))

        # Notebook tabs
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.report_tab = ttk.Frame(self.notebook)
        self.roc_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.report_tab, text=" Báo cáo & Confusion Matrix ")
        self.notebook.add(self.roc_tab, text=" ROC Curves ")

        # Report text
        self.report_text = scrolledtext.ScrolledText(
            self.report_tab, font=("Consolas", 10), wrap=tk.WORD,
            bg="#ffffff", fg="#111827"
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.report_text.config(state=tk.DISABLED)

        # ROC notebook inside
        self.roc_notebook = ttk.Notebook(self.roc_tab)
        self.roc_notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # =========================
    # CONFIG LOAD/SAVE
    # =========================
    def _load_last_config_to_form(self):
        cfg = load_app_config()

        self.name_var.set(cfg.get("student_name", ""))
        self.gender_var.set(cfg.get("student_gender", "Nam"))
        self.birth_var.set(cfg.get("student_birth_year", ""))

        last_scores = cfg.get("last_scores", {})
        for key, var in self.score_vars.items():
            if key in last_scores:
                var.set(str(last_scores[key]))

    def _save_current_form_to_config(self):
        cfg = load_app_config()
        cfg["student_name"] = self.name_var.get().strip()
        cfg["student_gender"] = self.gender_var.get().strip()
        cfg["student_birth_year"] = self.birth_var.get().strip()

        scores = {}
        for k, v in self.score_vars.items():
            scores[k] = v.get().strip()
        cfg["last_scores"] = scores

        # also save final model config snapshot (as per code)
        cfg["mlp_config"] = {
            "hidden_layer_sizes": [512, 384, 256, 192, 128, 64, 32, 16],
            "activation": "relu",
            "solver": "adam",
            "learning_rate": "adaptive",
            "learning_rate_init": 0.0008,
            "max_iter": 4000,
            "early_stopping": True,
            "validation_fraction": 0.12,
            "n_iter_no_change": 100,
            "tol": 1e-4,
            "beta_1": 0.9,
            "beta_2": 0.999,
            "epsilon": 1e-8,
            "random_state": 42
        }
        save_app_config(cfg)

    def on_close(self):
        self._save_current_form_to_config()
        self.root.destroy()

    # =========================
    # VALIDATION
    # =========================
    def _validate_student_info(self):
        name = self.name_var.get().strip()
        gender = self.gender_var.get().strip()
        birth = self.birth_var.get().strip()

        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Họ tên học sinh.")
            return False
        if gender not in ["Nam", "Nữ", "Khác"]:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Giới tính.")
            return False

        if birth:
            if not birth.isdigit():
                messagebox.showwarning("Sai định dạng", "Năm sinh phải là số (ví dụ: 2007).")
                return False
            y = int(birth)
            if y < 1900 or y > datetime.now().year:
                messagebox.showwarning("Sai dữ liệu", "Năm sinh không hợp lệ.")
                return False
        return True

    def _read_scores(self):
        keys = ["Toan", "Van", "Ly", "Hoa", "Sinh", "Anh"]
        scores = []
        for k in keys:
            s = self.score_vars[k].get().strip()
            if s == "":
                raise ValueError("Thiếu điểm")
            val = float(s)
            if val < 0 or val > 10:
                raise ValueError("Điểm phải trong [0,10]")
            scores.append(val)
        return scores

    # =========================
    # ACTIONS
    # =========================
    def train(self):
        self._save_current_form_to_config()

        X, y = load_data()
        if X is None:
            return

        self.status_var.set("Trạng thái: Đang huấn luyện và đánh giá mô hình...")
        self.root.update_idletasks()

        self.results, self.classes = train_and_evaluate(X, y)

        acc_dt = self.results['accs']['DT'] * 100
        acc_svm = self.results['accs']['SVM'] * 100
        acc_mlp = self.results['accs']['MLP'] * 100

        self.status_var.set("Trạng thái: Đã huấn luyện xong. Bạn có thể gợi ý khối thi.")
        messagebox.showinfo(
            "Kết quả huấn luyện",
            f"Hoàn tất huấn luyện!\n\n"
            f"• Decision Tree : {acc_dt:5.2f}%\n"
            f"• SVM           : {acc_svm:5.2f}%\n"
            f"• MLP (8 Layers): {acc_mlp:5.2f}%"
        )
        self._render_report()
        self._render_roc_tabs()

    def predict(self):
        self._save_current_form_to_config()

        if not self.results:
            messagebox.showwarning("Chưa huấn luyện", "Vui lòng bấm 'Huấn luyện & đánh giá' trước.")
            return

        if not self._validate_student_info():
            return

        try:
            scores = self._read_scores()
        except Exception as e:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập đầy đủ 6 điểm hợp lệ (0–10).")
            return

        input_df = pd.DataFrame([scores], columns=['Toan', 'Van', 'Ly', 'Hoa', 'Sinh', 'Anh'])

        pred_dt = self.results['models']['DT'].predict(input_df)[0]
        pred_svm = self.results['models']['SVM'].predict(input_df)[0]
        pred_mlp = self.results['models']['MLP'].predict(input_df)[0]

        # Majority vote => chỉ hiển thị 1 khối thi
        preds = [pred_dt, pred_svm, pred_mlp]
        final_block = Counter(preds).most_common(1)[0][0]
        combo = BLOCK_TO_SUBJECTS.get(final_block, "Chưa có mô tả tổ hợp môn.")

        self.result_var.set(f"Khối thi phù hợp: {final_block}")
        self.combo_var.set(f"Tổ hợp môn tương ứng: {combo}")

        # Save prediction log
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": self.name_var.get().strip(),
            "gender": self.gender_var.get().strip(),
            "birth_year": self.birth_var.get().strip(),
            "Toan": scores[0],
            "Van": scores[1],
            "Ly": scores[2],
            "Hoa": scores[3],
            "Sinh": scores[4],
            "Anh": scores[5],
            "pred_DT": pred_dt,
            "pred_SVM": pred_svm,
            "pred_MLP": pred_mlp,
            "final_recommendation": final_block,
            "subject_combo": combo
        }
        append_prediction_log(row)

        self.status_var.set(f"Trạng thái: Đã lưu kết quả gợi ý vào '{PRED_LOG_FILE}'.")

    def show_evaluation(self):
        if not self.results:
            messagebox.showwarning("Chưa huấn luyện", "Vui lòng bấm 'Huấn luyện & đánh giá' trước.")
            return

        # Jump to report tab and show a concise summary popup
        self.notebook.select(self.report_tab)

        acc_dt = self.results['accs']['DT'] * 100
        acc_svm = self.results['accs']['SVM'] * 100
        acc_mlp = self.results['accs']['MLP'] * 100

        auc_dt = self.results['roc']['DT']['auc_micro']
        auc_svm = self.results['roc']['SVM']['auc_micro']
        auc_mlp = self.results['roc']['MLP']['auc_micro']

        messagebox.showinfo(
            "Đánh giá mô hình",
            f"Accuracy:\n"
            f"• DT  : {acc_dt:.2f}%\n"
            f"• SVM : {acc_svm:.2f}%\n"
            f"• MLP : {acc_mlp:.2f}%\n\n"
            f"Micro-AUC (ROC):\n"
            f"• DT  : {auc_dt:.4f}\n"
            f"• SVM : {auc_svm:.4f}\n"
            f"• MLP : {auc_mlp:.4f}\n"
        )

    # =========================
    # RENDER REPORT / ROC
    # =========================
    def _render_report(self):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)

        for name in ['DT', 'SVM', 'MLP']:
            acc = self.results['accs'][name] * 100
            roc_micro = self.results['roc'][name]['auc_micro']
            self.report_text.insert(tk.END, f"{'='*70}\n")
            self.report_text.insert(tk.END, f"{name} — Accuracy: {acc:.2f}% | Micro-AUC(ROC): {roc_micro:.4f}\n")
            self.report_text.insert(tk.END, f"{'='*70}\n\n")

            self.report_text.insert(tk.END, self.results['reports'][name] + "\n\n")
            self.report_text.insert(tk.END, "Confusion Matrix:\n")

            cm = self.results['cms'][name]
            header = " " * 10 + " ".join([f"{c:>8}" for c in self.classes]) + "\n"
            self.report_text.insert(tk.END, header)

            for i, row in enumerate(cm):
                line = f"{self.classes[i]:>8} " + " ".join([f"{v:>8}" for v in row]) + "\n"
                self.report_text.insert(tk.END, line)

            self.report_text.insert(tk.END, "\n\n")

        self.report_text.config(state=tk.DISABLED)

    def _render_roc_tabs(self):
        # clear
        for tab in self.roc_notebook.tabs():
            self.roc_notebook.forget(tab)

        for name in ['DT', 'SVM', 'MLP']:
            tab = ttk.Frame(self.roc_notebook)
            self.roc_notebook.add(tab, text=name)
            self._plot_roc(tab, self.results['roc'][name], name)

    def _plot_roc(self, master, roc_data, title):
        fig, ax = plt.subplots(figsize=(6.8, 5.6), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")

        # Micro-average
        ax.plot(
            roc_data['fpr_micro'], roc_data['tpr_micro'],
            label=f"Micro-AUC = {roc_data['auc_micro']:.3f}",
            lw=2.5, linestyle="--"
        )

        for cls in roc_data['fpr_per_class']:
            ax.plot(
                roc_data['fpr_per_class'][cls],
                roc_data['tpr_per_class'][cls],
                lw=1.8,
                label=f"{cls} (AUC={roc_data['auc_per_class'][cls]:.3f})"
            )

        ax.plot([0, 1], [0, 1], "k--", lw=1.2, alpha=0.5)
        ax.set_xlim([-0.01, 1.01])
        ax.set_ylim([-0.01, 1.01])
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title(f"ROC Curve — {title}", fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.legend(fontsize=9, loc="lower right")

        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# ────────────────────────────────────────────────
#                   MAIN
# ────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
