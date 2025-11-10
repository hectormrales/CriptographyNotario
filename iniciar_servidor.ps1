# Script PowerShell para iniciar el servidor del Notario Digital

Write-Host "========================================"
Write-Host "   NOTARIO DIGITAL - Servidor API"
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

$fastapi = pip show fastapi 2>&1
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
Write-Host "Iniciando servidor..." -ForegroundColor Cyan
Write-Host ""
Write-Host "El servidor estará disponible en: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Para detener el servidor, presiona Ctrl+C"
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Iniciar servidor
python server\api_server.py
