"""
Módulo para leer y procesar archivos Excel
Extrae la información de los clientes y la cédula
"""

import pandas as pd
from typing import List, Dict


def leer_clientes_excel(ruta_archivo: str) -> List[Dict]:
    """
    Lee el archivo Excel con la información de los clientes
    
    Args:
        ruta_archivo: Ruta al archivo Excel de entrada
        
    Returns:
        Lista de diccionarios con la información de cada cliente
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo)
        
        # Convertir a lista de diccionarios
        clientes = df.to_dict('records')
        
        print(f"[OK] Se cargaron {len(clientes)} cliente(s) del Excel")
        return clientes
        
    except FileNotFoundError:
        print(f"[ERROR] Error: No se encontró el archivo {ruta_archivo}")
        return []
    except Exception as e:
        print(f"[ERROR] Error al leer Excel: {str(e)}")
        return []


def extraer_cedula(cliente: Dict) -> str:
    """
    Extrae la cédula del diccionario del cliente
    
    Args:
        cliente: Diccionario con información del cliente
        
    Returns:
        La cédula del cliente como string
    """
    # Busca la columna que contenga 'cedula' o 'cédula' (con o sin tilde)
    for columna, valor in cliente.items():
        col_lower = columna.lower()
        if 'cedula' in col_lower or 'cedula' in col_lower.replace('e', 'e').replace('\u00e9', 'e'):
            # Convertir a entero primero para quitar el .0 que agrega pandas
            try:
                return str(int(float(valor)))
            except (ValueError, TypeError):
                return str(valor).strip()
    
    return None


def extraer_telefono(cliente: Dict) -> str:
    """
    Extrae el teléfono del diccionario del cliente
    
    Args:
        cliente: Diccionario con información del cliente
        
    Returns:
        El teléfono del cliente como string
    """
    # DEBUG: Mostrar todas las columnas disponibles
    print(f"  [DEBUG] Columnas disponibles: {list(cliente.keys())}")
    
    # Busca la columna que contenga 'telefono', 'teléfono', 'celular', 'phone'
    for columna, valor in cliente.items():
        col_lower = columna.lower()
        print(f"  [DEBUG] Revisando columna: '{columna}' (lower: '{col_lower}'), valor: '{valor}'")
        if any(palabra in col_lower for palabra in ['telefono', 'teléfono', 'celular', 'phone', 'movil', 'móvil']):
            # Convertir a entero primero para quitar el .0 que agrega pandas
            try:
                telefono_str = str(int(float(valor)))
                print(f"  [DEBUG] Teléfono encontrado: '{telefono_str}'")
                return telefono_str
            except (ValueError, TypeError):
                telefono_str = str(valor).strip()
                print(f"  [DEBUG] Teléfono encontrado (string): '{telefono_str}'")
                return telefono_str
    
    print(f"  [DEBUG] No se encontró columna de teléfono")
    return None


def extraer_ciudad(cliente: Dict) -> str:
    """
    Extrae la ciudad del diccionario del cliente
    
    Args:
        cliente: Diccionario con información del cliente
        
    Returns:
        La ciudad del cliente como string
    """
    # Busca la columna que contenga 'ciudad', 'población', 'poblacion', 'municipio'
    for columna, valor in cliente.items():
        col_lower = columna.lower()
        if any(palabra in col_lower for palabra in ['ciudad', 'población', 'poblacion', 'municipio']):
            return str(valor).strip()
    
    return None


def obtener_marca(cliente: Dict) -> str:
    """
    Extrae la marca del cliente (SAS o Mobility)
    
    Args:
        cliente: Diccionario con información del cliente
        
    Returns:
        La marca del cliente
    """
    for columna, valor in cliente.items():
        if 'marca' in columna.lower():
            valor_str = str(valor).strip().upper()
            if valor_str == 'TVS':
                return 'SAS'
            else:
                return 'Mobility'
    
    return None


def obtener_datos_organizativos(marca: str) -> Dict[str, str]:
    """
    Determina los datos organizativos según la marca
    
    Args:
        marca: Marca del producto (Mobility, SAS, etc.)
        
    Returns:
        Diccionario con los datos organizativos:
        - clase_pedido: Clase de pedido
        - org_ventas: Organización de ventas
        - canal_dist: Canal de distribución
        - sector: Sector
    """
    # Normalizar la marca (convertir a mayúsculas y quitar espacios)
    marca_normalizada = marca.upper().strip() if marca else ""
    
    # Mobility (TVS)
    if "MOBILITY" in marca_normalizada:
        return {
            "clase_pedido": "zpec",
            "org_ventas": "2100",
            "canal_dist": "10",
            "sector": "43"
        }
    
    # SAS y otras marcas
    else:
        return {
            "clase_pedido": "zpec",
            "org_ventas": "2000",
            "canal_dist": "10",
            "sector": "40"
        }


def procesar_referencia(cliente: Dict) -> Dict:
    """
    Procesa la columna Referencia del cliente y extrae material y cantidad
    
    Reglas:
    - Si tiene guion (-): descartar cliente
    - Si tiene formato "12345 X2" o "12345 X3": material=12345, cantidad=2 o 3
    - Si tiene formato "12447(4)" o "12447 (4)": material=12447, cantidad=4 (con espacios opcionales)
    - Si empieza con letra: descartar cliente
    - Caso normal: material=valor, cantidad=1
    
    Args:
        cliente: Diccionario con información del cliente
        
    Returns:
        Diccionario con:
        - materiales: Lista de tuplas (material, cantidad)
        - descartar: True si el cliente debe ser descartado
    """
    import re
    
    # Buscar columna Referencia o repuesto
    referencia_str = None
    for columna, valor in cliente.items():
        col_lower = columna.lower()
        if 'referencia' in col_lower or 'repuesto' in col_lower:
            referencia_str = str(valor).strip()
            break
    
    if not referencia_str or referencia_str == 'nan':
        return {"materiales": [], "descartar": True}
    
    # Dividir por comas para detectar múltiples repuestos
    referencias = [ref.strip() for ref in referencia_str.split(',')]
    
    materiales_lista = []
    
    for referencia in referencias:
        if not referencia:
            continue
            
        # Verificar si empieza con letra (descartar)
        if referencia[0].upper().isalpha():
            print(f"  [INFO] Referencia '{referencia}' descartada (empieza con letra)")
            continue
        
        # Verificar si tiene guion (descartar)
        if '-' in referencia:
            print(f"  [INFO] Referencia '{referencia}' descartada (contiene guion)")
            continue
        
        # Buscar formato "12345 X2" o "12345 X3"
        match_x = re.search(r'^(\d+)\s*X(\d+)$', referencia, re.IGNORECASE)
        if match_x:
            material = match_x.group(1)
            cantidad = match_x.group(2)
            print(f"  [INFO] Referencia '{referencia}' -> Material: {material}, Cantidad: {cantidad}")
            materiales_lista.append((material, cantidad))
            continue
        
        # Buscar formato "12447(4)" o "12447 (4)" con espacios opcionales
        match_parentesis = re.search(r'^(\d+)\s*\((\d+)\)$', referencia)
        if match_parentesis:
            material = match_parentesis.group(1)
            cantidad = match_parentesis.group(2)
            print(f"  [INFO] Referencia '{referencia}' -> Material: {material}, Cantidad: {cantidad}")
            materiales_lista.append((material, cantidad))
            continue
        
        # Caso normal: solo el número
        if re.match(r'^\d+$', referencia):
            print(f"  [INFO] Referencia '{referencia}' -> Material: {referencia}, Cantidad: 1")
            materiales_lista.append((referencia, "1"))
            continue
        
        # Si no cumple ningún formato, descartar este item
        print(f"  [WARN] Referencia '{referencia}' no cumple formato esperado (descartado)")
    
    # Si no se procesó ningún material válido, descartar el cliente
    if not materiales_lista:
        print(f"  [WARN] Cliente sin materiales validos (descartado)")
        return {"materiales": [], "descartar": True}
    
    return {"materiales": materiales_lista, "descartar": False}


class GestorExcelEstados:
    """
    Clase para gestionar la actualización de estados en el Excel de clientes
    """
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el gestor con la ruta del archivo Excel
        
        Args:
            ruta_archivo: Ruta al archivo Excel
        """
        self.ruta_archivo = ruta_archivo
        self.df = None
        self.cargar()
    
    def cargar(self):
        """Carga el DataFrame desde el archivo Excel"""
        try:
            self.df = pd.read_excel(self.ruta_archivo)
            
            # Agregar columnas de estado si no existen
            if 'Estado' not in self.df.columns:
                self.df['Estado'] = 'Pendiente'
            if 'Detalle Error' not in self.df.columns:
                self.df['Detalle Error'] = ''
            if 'Numero Pedido' not in self.df.columns:
                self.df['Numero Pedido'] = ''
            
            print(f"[OK] Excel cargado con {len(self.df)} filas")
            return True
        except Exception as e:
            print(f"[ERROR] Error al cargar Excel: {str(e)}")
            return False
    
    def actualizar_estado(self, indice: int, estado: str, detalle: str = ""):
        """
        Actualiza el estado de un cliente en el DataFrame
        
        Args:
            indice: Índice del cliente (0-based, corresponde a la fila del DataFrame)
            estado: Estado del pedido ('Pedido creado', 'Error al crear pedido', 'Omitido - Material bloqueado')
            detalle: Detalle del error (opcional)
        """
        try:
            if self.df is None:
                print("[ERROR] DataFrame no cargado")
                return False
            
            if indice >= len(self.df):
                print(f"[ERROR] Índice {indice} fuera de rango")
                return False
            
            self.df.at[indice, 'Estado'] = estado
            self.df.at[indice, 'Detalle Error'] = detalle
            
            print(f"  [OK] Estado actualizado: {estado}")
            if detalle:
                print(f"       Detalle: {detalle}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al actualizar estado: {str(e)}")
            return False
    
    def actualizar_numero_pedido(self, indice: int, numero_pedido: str):
        """
        Actualiza el número de pedido de un cliente en el DataFrame
        
        Args:
            indice: Índice del cliente (0-based)
            numero_pedido: Número de pedido SAP
        """
        try:
            if self.df is None:
                print("[ERROR] DataFrame no cargado")
                return False
            
            if indice >= len(self.df):
                print(f"[ERROR] Índice {indice} fuera de rango")
                return False
            
            self.df.at[indice, 'Numero Pedido'] = numero_pedido
            print(f"  [OK] Numero de pedido actualizado: {numero_pedido}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al actualizar numero de pedido: {str(e)}")
            return False
    
    def guardar(self):
        """Guarda el DataFrame actualizado en el archivo Excel"""
        try:
            if self.df is None:
                print("[ERROR] No hay DataFrame para guardar")
                return False
            
            self.df.to_excel(self.ruta_archivo, index=False)
            print(f"[OK] Excel guardado con estados actualizados: {self.ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al guardar Excel: {str(e)}")
            return False
    
    def obtener_resumen(self) -> Dict[str, int]:
        """
        Retorna un resumen de los estados de todos los clientes
        
        Returns:
            Diccionario con el conteo de cada estado
        """
        if self.df is None:
            return {}
        
        resumen = self.df['Estado'].value_counts().to_dict()
        return resumen
