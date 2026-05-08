# RPA AUTECO - Ejecutable

Este paquete contiene el RPA (Robotic Process Automation) para procesar pedidos de clientes en SAP.

## Archivos incluidos:
- `RPA_AUTECO_Ejecutable.bat` - Ejecutable principal (recomendado)
- `RPA_AUTECO_Instalador.ps1` - Script de instalación (avanzado)
- `main.py` - Código fuente del RPA
- `requirements.txt` - Dependencias necesarias
- `config/` - Configuración (credenciales, etc.)
- `modulos/` - Módulos del RPA

## Cómo usar:

### Opción 1: Ejecutable automático (Recomendado)
1. Doble clic en `RPA_AUTECO_Ejecutable.bat`
2. El script verificará e instalará Python automáticamente si es necesario
3. Se instalarán las dependencias (Selenium, Pandas, OpenPyXL)
4. Se abrirá un diálogo para seleccionar el archivo Excel de clientes
5. El RPA procesará los clientes automáticamente

### Opción 2: Instalación manual
Si prefieres instalar manualmente:
1. Instala Python 3.8+ desde https://python.org
2. Marca "Add Python to PATH" durante la instalación
3. Ejecuta: `pip install -r requirements.txt`
4. Ejecuta: `python main.py`

## Requisitos:
- Windows 10/11
- Conexión a internet (para instalación automática)
- Acceso a SAP (credenciales configuradas en config/credenciales.py)

## Funcionalidades:
- ✅ Selección interactiva del archivo Excel de clientes
- ✅ Procesamiento automático de pedidos en SAP
- ✅ Actualización del Excel con estados de procesamiento
- ✅ Manejo de errores y reintentos
- ✅ Soporte para múltiples materiales por cliente

## Notas importantes:
- Los archivos de precios por ciudad deben estar en la ubicación esperada por el código
- Las credenciales de SAP deben estar configuradas en `config/credenciales.py`
- El RPA actualiza el Excel original con los resultados

## Soporte:
Si tienes problemas, verifica:
1. Que Python esté instalado correctamente
2. Que las dependencias se instalaron sin errores
3. Que tengas acceso a SAP
4. Que el archivo Excel tenga el formato correcto