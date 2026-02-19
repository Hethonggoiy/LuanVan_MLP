@echo off
title FIX TUONG THICH PYTHON 3.13 - LHU 2026
cls

cd /d "%~dp0"
echo Dang lam viec tai: %cd%

:: 1. Xoa moi truong cu bi loi
if exist "venv" (
    echo Dang xoa venv cu...
    rd /s /q venv
)

:: 2. Tao moi truong ao moi
echo Dang tao venv moi cho Python 3.13...
python -m venv venv

:: 3. Kich hoat va cai dat ban moi nhat
echo Dang kich hoat venv...
call venv\Scripts\activate

echo Dang nang cap pip va cai dat thu vien...
python -m pip install --upgrade pip

:: Cai dat cac thu vien (Bo cac so phien ban cu de tranh xung dot)
pip install flask pandas numpy scikit-learn imbalanced-learn joblib matplotlib seaborn gunicorn

:: 4. Chay thu app
echo ---------------------------------------
if exist "app.py" (
    echo [OK] Da tim thay app.py. Dang khoi chay...
    python app.py
) else (
    echo [LOI] Khong tim thay file app.py!
)
pause