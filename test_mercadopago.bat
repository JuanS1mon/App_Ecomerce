@echo off
cd c:\Users\PCJuan\Desktop\sql_app_Ecomerce
start /B uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak > nul
curl -s http://localhost:8000/ecomerce/checkout/config/mercadopago
taskkill /f /im python.exe > nul 2>&1