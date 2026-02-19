@echo off
title DAY CODE LEN GITHUB - FIX PATH
cls
color 0A

:: Kiem tra duong dan Git mac dinh
set GIT_PATH="C:\Program Files\Git\bin\git.exe"

if not exist %GIT_PATH% (
    echo [LOI] Khong tim thay Git tai %GIT_PATH%
    echo Vui long cai dat Git tai: https://git-scm.com/download/win
    pause
    exit
)

cd /d "C:\Users\Admin\OneDrive\Desktop\Lv09022026"

echo ======================================================
echo   DANG SU DUNG GIT TU: %GIT_PATH%
echo ======================================================

%GIT_PATH% init
%GIT_PATH% remote remove origin >nul 2>&1
%GIT_PATH% remote add origin https://github.com/Hethonggoiy/LuanVan_MLP.git
%GIT_PATH% add .
%GIT_PATH% commit -m "Fn223g0019022026 - Cap nhat luan van"
%GIT_PATH% branch -M main
%GIT_PATH% push -u origin main --force

echo.
echo ======================================================
echo   DA DAY CODE THANH CONG!
echo ======================================================
pause