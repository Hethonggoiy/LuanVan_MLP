@echo off
cd /d "C:\Users\Admin\OneDrive\Desktop\Lv09022026"
call venv\Scripts\activate
echo Dang kiem tra thu vien...
pip show flask
echo.
echo Dang khoi chay app...
python app.py
echo.
echo Neu ban thay dong nay, nghia la app da bi dung dot ngot.
pause