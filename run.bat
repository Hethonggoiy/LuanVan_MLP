if __name__ == '__main__':
    # Đảm bảo server chạy trên 0.0.0.0 để dễ kết nối
    app.run(host='0.0.0.0', port=5000, debug=False)