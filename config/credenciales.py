"""
Configuración de credenciales y URLs del RPA
"""

import json
import os
import sys

# Credenciales por defecto (se usan solo si no existe aún el archivo JSON)
_USUARIO_DEFECTO = "CANALESAUM36"
_CONTRASEÑA_DEFECTO = "Tvrepuestos2026*"

# El JSON de credenciales se guarda junto al ejecutable (o junto al proyecto en modo desarrollo)
# para que persista entre ejecuciones y entre actualizaciones del .exe
if getattr(sys, "frozen", False):
    _DIR_BASE = os.path.dirname(sys.executable)
else:
    _DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RUTA_CREDENCIALES_JSON = os.path.join(_DIR_BASE, "credenciales.json")


def _guardar_credenciales(credenciales: dict):
    """Guarda el diccionario de credenciales en el archivo JSON."""
    with open(RUTA_CREDENCIALES_JSON, "w", encoding="utf-8") as f:
        json.dump(credenciales, f, ensure_ascii=False, indent=4)


def _cargar_credenciales() -> dict:
    """Carga las credenciales desde el JSON, creándolo con valores por defecto si no existe."""
    if not os.path.exists(RUTA_CREDENCIALES_JSON):
        credenciales_defecto = {"usuario": _USUARIO_DEFECTO, "contraseña": _CONTRASEÑA_DEFECTO}
        _guardar_credenciales(credenciales_defecto)
        return credenciales_defecto

    try:
        with open(RUTA_CREDENCIALES_JSON, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return {
            "usuario": datos.get("usuario", _USUARIO_DEFECTO),
            "contraseña": datos.get("contraseña", _CONTRASEÑA_DEFECTO),
        }
    except Exception:
        return {"usuario": _USUARIO_DEFECTO, "contraseña": _CONTRASEÑA_DEFECTO}


def actualizar_clave(nueva_clave: str):
    """Actualiza la contraseña en el JSON de credenciales y en memoria (variable CONTRASEÑA)."""
    global CONTRASEÑA
    credenciales = _cargar_credenciales()
    credenciales["contraseña"] = nueva_clave
    _guardar_credenciales(credenciales)
    CONTRASEÑA = nueva_clave


_credenciales = _cargar_credenciales()

# Credenciales de acceso al sistema SAP
USUARIO = _credenciales["usuario"]
CONTRASEÑA = _credenciales["contraseña"]


# URL del aplicativo
URL_SAP = "https://erp.sap.auteco.com.co/sap/bc/gui/sap/its/webgui?sap-client=300&sap-language=ES"

# Rutas de archivos
RUTA_EXCEL_ENTRADA = r"c:\Users\1040032741\Desktop\RPA_auteco\datos\clientes.xlsx"
RUTA_EXCEL_SALIDA = r"c:\Users\1040032741\Desktop\RPA_auteco\datos\resultados.xlsx"

# Tiempos de espera (segundos)
TIEMPO_ESPERA_GENERAL = 10
TIEMPO_ESPERA_ELEMENTO = 20
