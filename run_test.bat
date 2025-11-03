@echo off
cd /d c:\Users\PCJuan\Desktop\sql_app_base
start "FastAPI Server" uvicorn main:app --host 127.0.0.1 --port 8000
timeout /t 5 /nobreak > nul
python test_clientes.py
taskkill /f /im uvicorn.exe > nul 2>&1