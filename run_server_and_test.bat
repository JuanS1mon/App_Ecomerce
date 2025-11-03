@echo off
cd "c:\Users\PCJuan\Desktop\sql_app_Ecomerce"
start /B python -c "
import os
os.environ['PYTHONPATH'] = '.'
import uvicorn
from main import app
print('Iniciando servidor...')
uvicorn.run(app, host='0.0.0.0', port=8001, log_level='info', access_log=False)
"
timeout /t 3 /nobreak > nul
python final_test.py