# RPA AUTECO - Guía de Uso

## Descripción
Este proyecto es un Robotic Process Automation (RPA) que automatiza el login en el sistema SAP de Auteco y realiza consultas de clientes.

## Características
- ✓ Usa `undetected-chromedriver` para evitar detección
- ✓ Lee datos de clientes desde Excel
- ✓ Automatiza login en SAP
- ✓ Extrae información de cédula
- ✓ Código limpio y comentado en español
- ✓ Estructura modular y mantenible

## Estructura del Proyecto

```
RPA_auteco/
├── config/
│   └── credenciales.py          # Configuración de credenciales y URLs
├── modulos/
│   ├── driver_selenium.py       # Manejo del driver de Selenium
│   ├── leer_excel.py            # Lectura de archivos Excel
│   └── login_sap.py             # Lógica de login en SAP
├── datos/
│   └── clientes.xlsx            # Archivo de entrada (debes crearlo)
├── main.py                       # Script principal
├── instalar_dependencias.py      # Script para instalar librerías
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Este archivo
```

## Requisitos
- Python 3.8 o superior
- Windows (el RPA está configurado para Windows)
- Google Chrome instalado

## Instalación

### Paso 1: Instalar dependencias
Abre la terminal en la carpeta del proyecto y ejecuta una de estas opciones:

**Opción A (Recomendado):**
```bash
pip install -r requirements.txt
```

**Opción B (Automático):**
```bash
python instalar_dependencias.py
```

Esto instalará automáticamente todas las librerías necesarias listadas en `requirements.txt`:
- `selenium` - Automatización web
- `undetected-chromedriver` - Chrome sin detectar
- `pandas` - Lectura de Excel
- `openpyxl` - Manejo de archivos Excel

### Paso 2: Preparar archivo Excel
Crea un archivo Excel llamado `clientes.xlsx` en la carpeta `datos/`

**Columnas requeridas:**
- `cedula` - Número de cédula del cliente
- `nombre` - Nombre completo
- `direccion` - Dirección del cliente
- `referencia` - Referencia del cliente
- `marca` - SAS o Movilty

**Ejemplo:**
```
cedula   | nombre              | direccion           | referencia | marca
---------|---------------------|---------------------|------------|-------
1234567  | Juan Pérez García   | Calle 1 # 2-3      | Ref 001    | SAS
2345678  | María López Martín  | Carrera 2 # 3-4    | Ref 002    | Movilty
```

### Paso 3: Ejecutar el RPA
```bash
python main.py
```

## Flujo del RPA

1. **Inicialización:**
   - Crea driver de Chrome sin detectar
   - Lee clientes del Excel

2. **Conexión:**
   - Navega a SAP
   - Realiza login automático

3. **Procesamiento:**
   - Extrae cédula de cada cliente
   - Prepara los datos para consultas

4. **Cierre:**
   - Cierra el navegador

## Próximos Pasos
Una vez que esto esté funcionando, agregaremos:
- Ingreso de cédula en los campos de búsqueda
- Realización de consultas en SAP
- Extracción de resultados
- Guardado en Excel de salida

## Credenciales Actuales
- **Usuario:** CANALESAUM36
- **Contraseña:** Andes2026++
- **URL SAP:** https://erp.sap.auteco.com.co/sap/bc/gui/sap/its/webgui?sap-client=300&sap-language=ES

## Notas Importantes
- ⚠️ No compartas las credenciales en público
- ⚠️ El Chrome se abrirá en modo visible (no headless) para ver el progreso
- ⚠️ Asegúrate de tener permisos para descargar ChromeDriver automáticamente
- ⚠️ Si SAP realiza cambios en los elementos HTML, habrá que actualizar los selectores

## Solución de Problemas

### Error: "ChromeDriver no encontrado"
```
Solución: undetected-chromedriver lo descarga automáticamente
Revisa que no haya restricciones de firewall
```

### Error: "Archivo Excel no encontrado"
```
Solución: Asegúrate de que clientes.xlsx esté en la carpeta datos/
```

### Error: "No se puede iniciar sesión"
```
Solución: 
- Verifica que las credenciales sean correctas
- Revisa que SAP esté disponible
- Comprueba tu conexión a internet
```

## Contacto
Para más información o problemas, contacta al equipo de desarrollo.

Última actualización: 2026-02-26
