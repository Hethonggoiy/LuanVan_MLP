# HỆ THỐNG GỢI Ý CHỌN KHỐI THI ĐẠI HỌC DỰA TRÊN KỸ THUẬT PHÂN LỚP 
### LUẬN VĂN THẠC SĨ CÔNG NGHỆ THÔNG TIN - TRƯỜNG ĐẠI HỌC LẠC HỒNG (2026)

---

## 📝 Giới thiệu đề tài
Đề tài nghiên cứu xây dựng mô hình dự báo và gợi ý khối thi đại học phù hợp cho học sinh THPT dựa trên năng lực học tập các môn văn hóa. Hệ thống sử dụng thuật toán **Multi-Layer Perceptron (MLP)** - một dạng mạng nơ-ron nhân tạo tiên tiến để trích xuất đặc trưng và phân loại dữ liệu.

**Tác giả:** Trương Minh Điệp  
**Hướng dẫn khoa học:** [ts. TRẦN BÌNH LONG]  
**Đơn vị:** Khoa Sau Đại học - Trường Đại học Lạc Hồng (LHU)

---

## Các tính năng chính
* Xử lý dữ liệu:** Sử dụng kỹ thuật **SMOTE** để giải quyết vấn đề mất cân bằng giữa các khối thi (A01, B00, C01, D01).
* Tối ưu hóa đầu vào bằng cách tính toán điểm số.
* Mô hình MLP:Mạng MLP với cấu trúc 8 lớp ẩn được tối ưu hóa bằng thuật toán Adam và Adaptive Learning Rate.
* Giao diện đồ họa hiện đại: Phát triển trên nền tảng Python và Đồ họa, hỗ trợ trực quan hóa năng lực.

---

## 🛠 Kiến trúc hệ thống
Hệ thống được triển khai theo mô hình MLP:
---

## 📂 Cấu trúc thư mục
```text
├── app.py              # File chạy chính ()
├── rs12excel6k-datienXuly.csv # Tập dữ liệu huấn luyện
├── saved_models/       # Thư mục lưu trữ mô hình đã huấn luyện (.pkl)
│   ├── mlp_model.pkl
│   ├── scaler.pkl
│   └── encoder.pkl
├── static/             # Tài nguyên tĩnh (Images)
├── templates/          # Giao diện đồ họa
├── requirements.txt    # Danh sách thư viện cần thiết
└── README.md           # Hướng dẫn này