@echo off
REM Script para iniciar el cliente GUI del Notario Digital

echo ========================================
echo  NOTARIO DIGITAL - Cliente GUI
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
pip show cryptography >nul 2>&1
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
echo Iniciando aplicación...
echo.
echo IMPORTANTE: Asegúrate de que el servidor esté ejecutándose
echo            (ejecuta iniciar_servidor.bat en otra ventana)
echo.

cd /d "%~dp0"

REM Verificar si existe entorno virtual
if exist .venv\Scripts\python.exe (
    echo Usando entorno virtual...
    .venv\Scripts\python.exe client\notario_gui.py
) else (
    python client\notario_gui.py
)

if errorlevel 1 (
    echo.
    echo ERROR: La aplicación finalizó con errores
    pause
)
