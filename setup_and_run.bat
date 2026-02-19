@echo off
title HE THONG GOI Y KHOI THI - MLP LHU 2026
cls

echo ======================================================================
echo   LUAN VAN THAC SI CNTT - TRUONG DAI HOC LAC HONG
echo   HE THONG GOI Y KHOI THI DAI HOC DUA TREN MLP
echo   Tac gia: Truong Minh Diep
echo ======================================================================
echo.

:: 1. Kiem tra Python da duoc cai dat chua
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Python chua duoc cai dat. Vui long cai dat Python truoc khi chay.
    pause
    exit /b
)

:: 2. Tao moi truong ao (Virtual Environment)
if not exist "venv" (
    echo [1/3] Dang tao moi truong ao (venv)...
    python -m venv venv
) else (
    echo [1/3] Moi truong ao venv da ton tai.
)

:: 3. Kich hoat venv va cai dat thu vien
echo [2/3] Dang kich hoat venv va cai dat thu vien (co the mat vai phut)...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. Kiem tra file du lieu va file app.py
if not exist "app.py" (
    echo [LOI] Khong tim thay file app.py trong thu muc nay.
    pause
    exit /b
)
if not exist "rs12excel6k-datienXuly.csv" (
    echo [CANH BAO] Khong tim thay file du lieu rs12excel6k-datienXuly.csv.
    echo Vui long dam bao file du lieu nam cung thu muc voi app.py.
)

:: 5. Khoi chay ung dung Web
echo [3/3] Dang khoi chay Web Server...
echo ----------------------------------------------------------------------
echo Ung dung se chay tai dia chi: http://127.0.0.1:5000
echo Nhan Ctrl+C de dung server.
echo ----------------------------------------------------------------------
echo.

python app.py

pause