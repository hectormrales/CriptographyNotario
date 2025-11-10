@echo off
REM Script para iniciar el servidor del Notario Digital

echo ========================================
echo    NOTARIO DIGITAL - Servidor API
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Verificando dependencias...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo.
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo.
echo Iniciando servidor...
echo.
echo El servidor estará disponible en: http://127.0.0.1:8000
echo Para detener el servidor, presiona Ctrl+C
echo.

cd /d "%~dp0"

REM Verificar si existe entorno virtual
if exist .venv\Scripts\python.exe (
    echo Usando entorno virtual...
    .venv\Scripts\python.exe server\api_server.py
) else (
    python server\api_server.py
)

pause
