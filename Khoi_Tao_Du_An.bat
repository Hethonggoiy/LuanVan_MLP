@echo off
title KHOI TAO THANH PHAN DU AN - LHU 2026
cls
color 0B

echo ======================================================================
echo   CHUONG TRINH TU DONG TAO FILE CAU CAU HINH LUAN VAN
echo   Hoc vien: Truong Minh Diep - Dai hoc Lac Hong
echo ======================================================================
echo.

:: 1. Tao file .gitignore
echo [*] Dang tao file .gitignore...
(
echo venv/
echo .env
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo .vscode/
echo .idea/
echo Thumbs.db
echo desktop.ini
echo saved_models/
) > .gitignore
echo [OK] Da tao .gitignore (Loai bo venv va file tam).

:: 2. Tao file requirements.txt (Phien ban toi uu cho Python 3.13)
echo [*] Dang tao file requirements.txt...
(
echo flask
echo gunicorn
echo pandas
echo numpy
echo scikit-learn
echo imbalanced-learn
echo joblib
echo matplotlib
echo seaborn
) > requirements.txt
echo [OK] Da tao requirements.txt (Danh sach thu vien).

:: 3. Tao file runtime.txt (Dinh nghia phien ban cho Render)
echo [*] Dang tao file runtime.txt...
echo python-3.13.1 > runtime.txt
echo [OK] Da tao runtime.txt (Xac dinh Python 3.13).

echo.
echo ======================================================================
echo   HOAN THANH! Tat ca file cau hinh da san sang de day len GitHub.
echo   Cac file da tao: .gitignore, requirements.txt, runtime.txt
echo ======================================================================
echo.
pause