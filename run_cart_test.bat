@echo off
cd /d c:\Users\PCJuan\Desktop\sql_app_Ecomerce
start "FastAPI Server" python main.py
timeout /t 5 /nobreak > nul
python test_cart_simple.py
taskkill /f /im python.exe > nul 2>&1