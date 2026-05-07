@echo off
echo ============================================
echo   Hedgeye Server - CRM ExpressLine
echo ============================================
echo.

cd /d "%~dp0"

echo Instalando dependencias...
pip install -q flask flask-cors apscheduler selenium webdriver-manager

echo.
echo Iniciando servidor en http://localhost:5050
echo Auto-actualizacion: todos los dias a las 17:00 hs
echo.
echo Para detener el servidor presiona CTRL+C
echo.

python hedgeye_server.py

pause
