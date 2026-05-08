# RPA AUTECO - Instalador y Ejecutable
# Este script instala Python y las dependencias necesarias, luego ejecuta el RPA

param(
    [switch]$SkipInstall,
    [string]$ExcelPath = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       RPA AUTECO - Ejecutable" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para verificar si Python está instalado
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Ignorar errores
    }
    return $false
}

# Función para instalar dependencias
function Install-Dependencies {
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow

    try {
        # Instalar dependencias
        pip install selenium pandas openpyxl

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencias instaladas correctamente" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "✗ Error instalando dependencias" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Verificar Python
if (-not (Test-Python)) {
    Write-Host "Python no está instalado." -ForegroundColor Yellow
    Write-Host "Por favor instala Python desde https://python.org" -ForegroundColor Red
    Write-Host "Asegúrate de marcar 'Add Python to PATH' durante la instalación." -ForegroundColor Yellow
    Read-Host "Presiona Enter cuando hayas instalado Python"
}

# Instalar dependencias
if (-not $SkipInstall) {
    if (-not (Install-Dependencies)) {
        Write-Host "Error instalando dependencias. Intentando continuar..." -ForegroundColor Yellow
    }
}

# Ejecutar RPA
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         Ejecutando RPA AUTECO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Ejecutar el RPA
try {
    if ($ExcelPath) {
        Write-Host "Usando archivo Excel especificado: $ExcelPath" -ForegroundColor Green
        python main.py
    }
    else {
        python main.py
    }

    Write-Host ""
    Write-Host "RPA completado." -ForegroundColor Green
}
catch {
    Write-Host "Error ejecutando RPA: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Presiona Enter para salir"