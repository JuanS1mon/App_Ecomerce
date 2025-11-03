@echo off
cd /d c:\Users\PCJuan\Desktop\sql_app_Ecomerce
start /B python main.py
timeout /t 5 /nobreak > nul
python test_json_parsing.py
taskkill /f /im python.exe > nul 2>&1