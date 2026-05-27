@echo off
echo ============================================
echo   Configurando actualizacion automatica
echo   Hedgeye - CRM ExpressLine
echo ============================================
echo.

set PYTHON=C:\Users\usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe
set BASE=%~dp0
set SCRAPER="%BASE%run_diario.py"
set SERVER="%BASE%hedgeye_server.py"
set LISTENER="%BASE%iniciar_listener.bat"

echo [1/3] Tarea: Servidor Hedgeye al iniciar Windows...
schtasks /delete /tn "Hedgeye - Servidor" /f >nul 2>&1
schtasks /create /tn "Hedgeye - Servidor" ^
  /tr "\"%PYTHON%\" %SERVER%" ^
  /sc onlogon ^
  /ru "%USERNAME%" ^
  /delay 0001:00 ^
  /f
if %errorlevel%==0 (echo     OK - arranca 1 minuto despues de iniciar sesion) else (echo     ERROR al crear tarea)

echo.
echo [2/3] Tarea: Listener ntfy + HTTP :5055 al iniciar Windows (consola visible)...
schtasks /delete /tn "Hedgeye - Listener" /f >nul 2>&1
schtasks /create /tn "Hedgeye - Listener" ^
  /tr "cmd.exe /c %LISTENER%" ^
  /sc onlogon ^
  /ru "%USERNAME%" ^
  /delay 0001:30 ^
  /f
if %errorlevel%==0 (echo     OK - arranca con consola visible 90s despues de iniciar sesion) else (echo     ERROR al crear tarea)

echo.
echo [3/3] Tarea: Scraper diario a las 13:00...
schtasks /delete /tn "Hedgeye - Scraper 13hs" /f >nul 2>&1
schtasks /create /tn "Hedgeye - Scraper 13hs" ^
  /tr "\"%PYTHON%\" %SCRAPER%" ^
  /sc daily ^
  /st 13:00 ^
  /ru "%USERNAME%" ^
  /f
if %errorlevel%==0 (echo     OK - corre todos los dias a las 13:00) else (echo     ERROR al crear tarea)

echo.
echo ============================================
echo   Listo. Tareas instaladas:
echo   - Servidor arranca solo al prender la PC (1 min)
echo   - Listener arranca con consola visible (90s)
echo   - Scraper actualiza datos cada dia 13:00
echo ============================================
echo.
pause
