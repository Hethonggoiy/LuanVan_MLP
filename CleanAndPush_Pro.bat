@echo off
title Git Ultimate Fix & Push - Master Thesis
cls

echo ======================================================
echo   1. DANG CAP NHAT FILE .GITIGNORE CHUAN...
echo ======================================================

(
echo # Microsoft Office Temporary Files
echo ~$*.doc*
echo ~$*.xls*
echo ~$*.ppt*
echo.
echo # OS generated files
echo Thumbs.db
echo Desktop.ini
echo .DS_Store
echo.
echo # LaTeX
echo *.aux
echo *.log
echo *.toc
echo *.pdfsync
echo *.synctex.gz
echo.
echo # Large files and backups (Chuyen sang luu Drive)
echo *.zip
echo *.7z
echo *.rar
echo *.mp4
echo *.iso
echo *.wav
echo /backup/
echo /data/
) > .gitignore

echo [OK] Da toi uu file .gitignore.

echo.
echo ======================================================
echo   2. DANG DON DEP VA DONG BO DU LIEU (PULL)...
echo ======================================================

:: Tăng buffer để tránh lỗi đường truyền
git config --global http.postBuffer 1048576000

:: Xóa cache các file nặng cũ
git rm -r --cached . >nul 2>&1
git add .

:: Lay du lieu tu server ve truoc de tranh loi "Rejected"
echo Dang kiem tra va gop du lieu tu GitHub...
git pull origin main --rebase

echo.
echo ======================================================
echo   3. DANG COMMIT VA DAY DU LIEU (PUSH)...
echo ======================================================

:: Tao tin nhan commit tu dong voi thoi gian
set current_date=%date% %time%
set /p commit_msg="Nhap noi dung commit (Bo trong de dung thoi gian thuc): "
if "%commit_msg%"=="" set commit_msg=Update Thesis at %current_date%

git commit -m "%commit_msg%"

:: Day code len
echo Dang day code len GitHub...
git push origin main

echo.
echo ======================================================
echo   HOAN THANH! MOI THU DA DUOC DONG BO.
echo ======================================================
pause