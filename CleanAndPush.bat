@echo off
title Git Cleanup and Push Tool - Master Thesis
cls

echo ======================================================
echo   DANG KHOI TAO FILE .GITIGNORE CHUAN...
echo ======================================================

:: Tạo file .gitignore với các định dạng rác của Office và file nặng
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
echo # LaTeX (Optional)
echo *.aux
echo *.log
echo *.toc
echo *.pdfsync
echo *.synctex.gz
echo.
echo # Large files and backups
echo *.zip
echo *.7z
echo *.rar
echo *.mp4
echo *.iso
echo /backup/
echo /data/
) > .gitignore

echo [OK] Da tao xong file .gitignore.

echo.
echo ======================================================
echo   DANG DON DEP CACHE DE LAM NHE REPO...
echo ======================================================

:: Xóa toàn bộ index của Git nhưng không xóa file thật trên máy
git rm -r --cached .

:: Thêm lại toàn bộ file (Git sẽ tự bỏ qua các file trong .gitignore)
git add .

:: Commit thay đổi
set /p commit_msg="Nhap noi dung commit (mac dinh: Update Thesis): "
if "%commit_msg%"=="" set commit_msg=Update Thesis

git commit -m "%commit_msg%"

echo.
echo ======================================================
echo   DANG TANG BO NHO DEM VA DAY CODE (PUSH)...
echo ======================================================

:: Tăng buffer lên 1GB để tránh lỗi HTTP 500 như lúc nãy
git config --global http.postBuffer 1048576000

:: Thực hiện đẩy code
git push origin main

echo.
echo ======================================================
echo   HOAN THANH! KIEM TRA TREN GITHUB/GITLAB CUA BAN.
echo ======================================================
pause