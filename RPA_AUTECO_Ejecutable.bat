@echo off
echo ========================================
echo        RPA AUTECO - Ejecutable
echo ========================================
echo.
echo Este script instala automaticamente Python y las dependencias necesarias.
echo Luego ejecuta el RPA que permite seleccionar el archivo Excel de clientes.
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

echo.
echo Ejecutando instalador...
powershell -ExecutionPolicy Bypass -File "%~dp0RPA_AUTECO_Instalador.ps1"

echo.
echo Proceso completado.
pause