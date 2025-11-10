# Script PowerShell para iniciar el cliente GUI del Notario Digital

Write-Host "========================================"
Write-Host "  NOTARIO DIGITAL - Cliente GUI"
Write-Host "========================================"
Write-Host ""

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detectado: $pythonVersion"
}
catch {
    Write-Host "✗ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Python 3.8 o superior desde:"
    Write-Host "https://www.python.org/downloads/"
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar dependencias
Write-Host ""
Write-Host "Verificando dependencias..."

$cryptography = pip show cryptography 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

Write-Host "✓ Dependencias verificadas" -ForegroundColor Green
Write-Host ""
Write-Host "Iniciando aplicación..." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Asegúrate de que el servidor esté ejecutándose" -ForegroundColor Yellow
Write-Host "            (ejecuta iniciar_servidor.ps1 en otra ventana PowerShell)"
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Iniciar cliente
python client\notario_gui.py
