@echo off
title KHOI CHAY WEB GOI Y KHOI THI
cd /d "%~dp0"
call venv\Scripts\activate
echo Dang khoi chay giao dien Web...
streamlit run run_local.py
pause