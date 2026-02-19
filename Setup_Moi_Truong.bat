@echo off
title THIET LAP MOI TRUONG LUAN VAN - MLP 2026
cls

:: 1. Thiet lap duong dan du an
set PROJECT_PATH=C:\Users\Admin\OneDrive\Desktop\Lv09022026

echo ======================================================================
echo   DANG THIET LAP MOI TRUONG TAI: 
echo   %PROJECT_PATH%
echo ======================================================================
echo.

:: Di chuyen vao thu muc du an
cd /d "%PROJECT_PATH%"

:: 2. Tao moi truong ao (Virtual Environment)
if not exist "venv" (
    echo [*] Dang tao moi truong ao (venv) moi...
    python -m venv venv
) else (
    echo [*] Moi truong ao (venv) da ton tai.
)

:: 3. Kich hoat venv va cai dat thu vien
echo [*] Dang kich hoat moi truong va tai cac thu vien quan trong...
call venv\Scripts\activate

:: Cap nhat pip
python -m pip install --upgrade pip

:: Cai dat cac thu vien MLP chuyen sau cho Luan van
echo [*] Dang cai dat: Flask, Scikit-learn, Imbalanced-learn, Pandas, Joblib...
pip install flask gunicorn pandas numpy==1.26.0 scikit-learn==1.3.1 imbalanced-learn==0.11.0 joblib matplotlib seaborn

:: 4. Kiem tra file cau truc
echo.
echo ======================================================================
echo   KIEM TRA CAU TRUC THU MUC:
if exist "app.py" (echo [OK] Da tim thay file app.py) else (echo [!] Thieu file app.py)
if exist "rs12excel6k-datienXuly.csv" (echo [OK] Da tim thay du lieu CSV) else (echo [!] Thieu file du lieu CSV)
echo ======================================================================

echo.
echo [HOAN THANH] Moi truong da san sang!
echo Nhan phim bat ky de KHOI CHAY Ung dung Web...
pause

python app.py