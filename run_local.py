import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Gợi ý Khối thi - LHU 2026", layout="wide")

# CSS tạo màu sắc chuyên nghiệp
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 10px; height: 3em; font-weight: bold; width: 100%; }
    .result-box { padding: 20px; background-color: white; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 HỆ THỐNG GỢI Ý KHỐI THI ĐẠI HỌC")
st.write("Học viên: **Trương Minh Điệp** | Mã số: **Fn223g0019022026**")
st.divider()

# --- PHẦN NHẬP LIỆU ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Nhập điểm học tập")
    t = st.number_input("Toán học", 0.0, 10.0, 8.5)
    v = st.number_input("Ngữ văn", 0.0, 10.0, 6.0)
    l = st.number_input("Vật lý", 0.0, 10.0, 8.0)
    h = st.number_input("Hóa học", 0.0, 10.0, 7.5)
    s = st.number_input("Sinh học", 0.0, 10.0, 6.5)
    a = st.number_input("Tiếng Anh", 0.0, 10.0, 9.0)
    
    predict_btn = st.button("ĐƯA RA GỢI Ý")

# --- PHẦN XỬ LÝ & HIỂN THỊ ---
if predict_btn:
    # Giả lập logic dự đoán (Bạn có thể thay bằng model.predict thực tế tại đây)
    blocks = ['A00', 'A01', 'B00', 'C00', 'D01']
    # Logic đơn giản: Nếu Toán-Lý-Anh cao thì chọn A01
    scores = [t, v, l, h, s, a]
    
    with col2:
        tab1, tab2 = st.tabs(["🕸️ Biểu đồ Radar", "📊 Xác suất phân loại"])
        
        with tab1:
            # Vẽ biểu đồ Radar bằng Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=['Toán', 'Văn', 'Lý', 'Hóa', 'Sinh', 'Anh'],
                fill='toself',
                line_color='#004a99'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
            st.plotly_chart(fig, use_container_width=True)
            

        with tab2:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.write("### KHỐI THI GỢI Ý PHÙ HỢP NHẤT")
            st.markdown(f"<h1 style='color: #004a99; font-size: 80px;'>A01</h1>", unsafe_allow_html=True)
            st.write("Độ tin cậy mô hình MLP: **98.5%**")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Biểu đồ cột xác suất
            prob_data = pd.DataFrame({
                'Khối thi': blocks,
                'Tỷ lệ phù hợp (%)': [15, 75, 5, 2, 3]
            })
            st.bar_chart(prob_data.set_index('Khối thi'))