@echo off
title Hedgeye Listener — CRM ExpressLine
cd /d "%~dp0"
set PYTHON=C:\Users\usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe

:inicio
echo.
echo ============================================
echo   Hedgeye Listener — CRM ExpressLine
echo   Puerto HTTP : 5055  (snapshots CRM)
echo   ntfy topic  : crm-hg-dsalem123-offshore
echo   %date% %time%
echo ============================================
echo.
"%PYTHON%" hedgeye_listener.py
echo.
echo [!] El listener se cerro. Reiniciando en 10 segundos...
echo     (Cerrá esta ventana para detenerlo definitivamente)
echo.
timeout /t 10 /nobreak
goto inicio
