# -*- coding: utf-8 -*-
"""
Script principal del RPA AUTECO
Flujo completo: Login -> Buscar VA01 -> Llenar datos organizativos
Procesa múltiples clientes desde un archivo Excel
"""

import sys
import os
import time
import tkinter as tk
from tkinter import filedialog

# Agregar rutas para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modulos.driver_selenium import DriverSAP
from modulos.login_sap import LoginSAP
from modulos.consultas_sap import ConsultasSAP
from modulos.leer_excel import leer_clientes_excel, obtener_marca, obtener_datos_organizativos, extraer_cedula, extraer_telefono, procesar_referencia, extraer_ciudad, GestorExcelEstados
from config.credenciales import USUARIO, CONTRASEÑA, URL_SAP

# Ruta al archivo Excel con los clientes (ahora seleccionable por el usuario)
# RUTA_EXCEL = r"C:\Users\1018232653\Downloads\base pedidos.xlsx"


class RPA_AUTECO:
    """
    Clase principal que coordina el RPA
    Ejecuta: Login -> VA01 -> Llenar datos organizativos
    Procesa múltiples clientes desde Excel
    """
    
    def __init__(self, ruta_excel: str, solo_filas=None, solo_cedulas=None, limite=None):
        """
        Inicializa el RPA
        
        Args:
            ruta_excel: Ruta al archivo Excel con los clientes
            solo_filas: Lista de índices de filas a procesar (ej: [0, 2, 5] para filas 1, 3, 6)
            solo_cedulas: Lista de cédulas específicas a procesar (ej: ['123456789', '987654321'])
            limite: Número máximo de clientes a procesar (ej: 3 para solo los primeros 3)
        """
        self.driver_sap = None
        self.ruta_excel = ruta_excel
        self.clientes = []
        self.gestor_excel = None  # Gestor para actualizar estados en Excel
        self.solo_filas = solo_filas
        self.solo_cedulas = solo_cedulas
        self.limite = limite
    
    def cargar_clientes(self):
        """
        Carga los clientes desde el archivo Excel
        Aplica filtros si se especificaron (solo_filas, solo_cedulas, limite)
        """
        print("\n" + "="*60)
        print("CARGANDO DATOS DEL EXCEL")
        print("="*60)
        
        # Inicializar gestor de Excel
        self.gestor_excel = GestorExcelEstados(self.ruta_excel)
        
        # Cargar todos los clientes
        todos_clientes = leer_clientes_excel(self.ruta_excel)
        
        if not todos_clientes:
            print("[ERROR] No se pudieron cargar los clientes del Excel")
            return False
        
        print(f"[INFO] Total en Excel: {len(todos_clientes)} cliente(s)")
        
        # Aplicar filtros y mantener índice original
        clientes_con_indice = []
        
        if self.solo_filas is not None:
            print(f"[FILTRO] Procesando solo filas: {[f+1 for f in self.solo_filas]}")  # +1 para mostrar número de fila humano
            for i in self.solo_filas:
                if i < len(todos_clientes):
                    cliente = todos_clientes[i].copy()
                    cliente['_indice_original'] = i  # Guardar índice original
                    clientes_con_indice.append(cliente)
        elif self.solo_cedulas is not None:
            print(f"[FILTRO] Procesando solo cédulas: {self.solo_cedulas}")
            # Filtrar por cédulas
            cedulas_str = [str(c) for c in self.solo_cedulas]
            for i, cliente in enumerate(todos_clientes):
                cedula = extraer_cedula(cliente)
                if cedula in cedulas_str:
                    cliente_copia = cliente.copy()
                    cliente_copia['_indice_original'] = i  # Guardar índice original
                    clientes_con_indice.append(cliente_copia)
        elif self.limite is not None:
            print(f"[FILTRO] Procesando solo los primeros {self.limite} cliente(s)")
            for i, cliente in enumerate(todos_clientes[:self.limite]):
                cliente_copia = cliente.copy()
                cliente_copia['_indice_original'] = i  # Guardar índice original
                clientes_con_indice.append(cliente_copia)
        else:
            # Sin filtros, procesar todos
            for i, cliente in enumerate(todos_clientes):
                cliente_copia = cliente.copy()
                cliente_copia['_indice_original'] = i  # Guardar índice original
                clientes_con_indice.append(cliente_copia)
        
        # Filtrar clientes que ya tienen Numero Pedido asignado o estado "Error al crear pedido" o "Bloqueado"
        import pandas as pd
        clientes_filtrados = []
        omitidos_pedido = 0
        omitidos_error = 0
        omitidos_bloqueado = 0
        for cliente in clientes_con_indice:
            numero_pedido = cliente.get('Numero Pedido', '')
            estado = str(cliente.get('Estado', '')).strip()
            if pd.notna(numero_pedido) and str(numero_pedido).strip() not in ('', 'nan'):
                omitidos_pedido += 1
            elif estado == 'Error al crear pedido':
                omitidos_error += 1
            elif estado == 'Bloqueado':
                omitidos_bloqueado += 1
            else:
                clientes_filtrados.append(cliente)
        
        if omitidos_pedido > 0:
            print(f"[FILTRO] {omitidos_pedido} cliente(s) omitido(s) por ya tener Numero Pedido")
        if omitidos_error > 0:
            print(f"[FILTRO] {omitidos_error} cliente(s) omitido(s) por estado 'Error al crear pedido'")
        if omitidos_bloqueado > 0:
            print(f"[FILTRO] {omitidos_bloqueado} cliente(s) omitido(s) por estado 'Bloqueado'")
        
        self.clientes = clientes_filtrados
        
        print(f"[OK] {len(self.clientes)} cliente(s) a procesar")
        
        if len(self.clientes) == 0:
            print("[WARN] No hay clientes que procesar después de aplicar filtros")
            return False
        return True
    
    def procesar_cliente(self, cliente: dict, numero: int, total: int):
        """
        Procesa un cliente individual
        
        Args:
            cliente: Diccionario con la información del cliente
            numero: Número del cliente actual
            total: Total de clientes a procesar
            
        Returns:
            True si el procesamiento fue exitoso
        """
        try:
            print("\n" + "="*60)
            print(f"PROCESANDO CLIENTE {numero}/{total}")
            print("="*60)
            
            # Obtener índice original del Excel (para actualizar estado correctamente)
            indice_excel = cliente.get('_indice_original', numero - 1)
            
            # Obtener datos del cliente
            nombre = cliente.get('Nombre completo', 'N/A')
            cedula = extraer_cedula(cliente)
            telefono = extraer_telefono(cliente)
            marca = obtener_marca(cliente)
            ciudad = extraer_ciudad(cliente)
            
            print(f"Nombre: {nombre}")
            print(f"Cedula: {cedula}")
            print(f"Telefono: {telefono}")
            print(f"Marca: {marca}")
            print(f"Ciudad: {ciudad if ciudad else 'No especificada'}")
            print(f"[DEBUG] Fila en Excel: {indice_excel + 1}")
            
            # Procesar referencia para obtener material y cantidad
            print("\n>> Procesando Referencia...")
            ref_data = procesar_referencia(cliente)
            
            if ref_data['descartar']:
                print(f"[SKIP] Cliente {numero} descartado por referencia invalida")
                # Actualizar estado en Excel
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Omitido", "Referencia inválida")
                print("="*60)
                return True  # Continuar con el siguiente
            
            materiales_lista = ref_data['materiales']
            print(f"[INFO] Se procesaran {len(materiales_lista)} material(es) para este cliente")
            
            # Determinar valores organizativos según la marca
            datos_org = obtener_datos_organizativos(marca)
            
            print("\nDatos organizativos a usar:")
            print(f"   - Clase de pedido: {datos_org['clase_pedido']}")
            print(f"   - Organizacion ventas: {datos_org['org_ventas']}")
            print(f"   - Canal distribucion: {datos_org['canal_dist']}")
            print(f"   - Sector: {datos_org['sector']}")
            
            # Buscar transacción VA01
            print("\n>> Buscando transaccion VA01...")
            consultas = ConsultasSAP(self.driver_sap)
            if not consultas.buscar_va01():
                motivo = "No se pudo navegar a la transaccion VA01"
                print(f"[ERROR] {motivo}")
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error - Fallo VA01", motivo)
                return False
            
            print("[OK] Navegacion a VA01 completada")
            time.sleep(2)
            
            # Llenar datos organizativos
            print("\n>> Llenando datos organizativos...")
            if not consultas.llenar_datos_organizativos(
                datos_org['clase_pedido'],
                datos_org['org_ventas'],
                datos_org['canal_dist'],
                datos_org['sector']
            ):
                motivo = f"No se pudo llenar datos organizativos (marca: {marca})"
                print(f"[ERROR] {motivo}")
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error - Datos organizativos", motivo)
                return False
            
            print("[OK] Datos organizativos llenados correctamente")
            time.sleep(2)
            
            # Ingresar cédula del solicitante
            print("\n>> Ingresando cedula del solicitante...")
            if not consultas.ingresar_cedula_solicitante(cedula):
                print("[WARN] No se pudo ingresar la cedula del solicitante, continuando...")
            
            time.sleep(3)
            
            # Ingresar cédula del destinatario de mercancía
            print("\n>> Ingresando cedula del destinatario...")
            if not consultas.ingresar_cedula_destinatario(cedula):
                print("[WARN] No se pudo ingresar la cedula del destinatario, continuando...")
            
            time.sleep(3)
            
            # Ingresar cédula en N° ped.cliente
            print("\n>> Ingresando cedula en N ped.cliente...")
            if not consultas.ingresar_numero_pedido_cliente(cedula):
                print("[WARN] No se pudo ingresar N ped.cliente, continuando...")
            
            time.sleep(3)
            
            # Seleccionar Modific.cantidad
            print("\n>> Seleccionando Modific.cantidad...")
            if not consultas.seleccionar_modific_cantidad():
                print("[WARN] No se pudo seleccionar Modific.cantidad, continuando...")
            
            time.sleep(1)
            
            # Seleccionar Pedido Ecommerce Cliente Final
            print("\n>> Seleccionando Pedido Ecommerce Cliente Final...")
            if not consultas.seleccionar_pedido_ecommerce():
                print("[WARN] No se pudo seleccionar Pedido Ecommerce, continuando...")
            
            # Verificar si hay error de pedido duplicado y corregirlo
            print("\n>> Verificando pedido duplicado...")
            if not consultas.verificar_y_corregir_pedido_duplicado(telefono):
                print("[WARN] Hubo problema al verificar/corregir pedido duplicado, continuando...")
            
            time.sleep(2)
            
            # Confirmar N° ped.cliente con Enter para habilitar Material/Cantidad
            print("\n>> Confirmando N ped.cliente con Enter...")
            if not consultas.confirmar_numero_pedido_cliente(telefono=telefono):
                print("[WARN] No se pudo confirmar N ped.cliente, continuando...")
            
            time.sleep(5)
            
            # Ingresar Material y Cantidad para cada repuesto
            print(f"\n>> Ingresando {len(materiales_lista)} Material(es) y Cantidad(es)...")
            materiales_exitosos = 0
            primer_material_exitoso = None
            materiales_omitidos = []
            
            for idx, (material, cantidad) in enumerate(materiales_lista, 1):
                print(f"\n   ========================================")
                print(f"   [{idx}/{len(materiales_lista)}] Material: {material}, Cantidad: {cantidad}")
                print(f"   ========================================")
                
                if consultas.ingresar_material_cantidad(material, cantidad):
                    materiales_exitosos += 1
                    if primer_material_exitoso is None:
                        primer_material_exitoso = material
                    print(f"   [OK] Material {material} ingresado correctamente")
                else:
                    print(f"   [SKIP] Material {material} bloqueado o con error, intentando siguiente...")
                    materiales_omitidos.append(material)
                
                # Pausa entre materiales para dar tiempo a SAP
                if idx < len(materiales_lista):  # No esperar después del último
                    print(f"   [INFO] Esperando 2 segundos antes del siguiente material...")
                    time.sleep(2)
            
            # Verificar si se procesó al menos un material
            if materiales_exitosos == 0:
                print(f"\n[SKIP] Todos los materiales del cliente {numero} estan bloqueados")
                print("       Recargando pagina y pasando al siguiente cliente...")
                motivo = f"Todos los materiales bloqueados: {', '.join(str(m) for m in materiales_lista)}"
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Omitido - Material bloqueado", motivo)
                consultas.recargar_pagina()
                time.sleep(2)
                return True  # Continuar con el siguiente cliente
            
            # Si hay materiales exitosos, hacer click en Condiciones
            print(f"\n[OK] {materiales_exitosos}/{len(materiales_lista)} material(es) procesado(s) exitosamente")
            
            # Si hay MÁS de 1 material, volver al primer material antes de continuar
            if materiales_exitosos > 1:
                print(f"\n>> Volviendo al primer material (hay {materiales_exitosos} materiales)...")
                num_flechas = materiales_exitosos
                print(f"   [INFO] Buscando el primer material ingresado y usando flechas como respaldo...")
                
                if consultas.volver_al_primer_material(num_flechas, primer_material_exitoso):
                    print(f"   [OK] Posicionado en el primer material")
                else:
                    raise Exception("No se pudo volver al primer material - reintentando cliente")
                
                time.sleep(1)
            else:
                # Con 1 solo material, hacer doble click en él para seleccionarlo
                print(f"\n>> Haciendo doble click en el material para seleccionarlo...")
                if consultas.volver_al_primer_material(1, primer_material_exitoso):
                    print(f"   [OK] Material seleccionado")
                else:
                    raise Exception("No se pudo seleccionar el material - reintentando cliente")
            
            print("\n>> Haciendo click en pestaña Condiciones...")
            if not consultas.hacer_click_condiciones():
                motivo = "No se pudo abrir la pestana Condiciones en SAP"
                print(f"[ERROR] {motivo}")
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error - Pestana Condiciones", motivo)
                raise Exception(motivo)
            
            time.sleep(1)
            
            # Hacer click en el campo de condiciones
            print("\n>> Haciendo click en campo de condiciones...")
            if not consultas.hacer_click_campo_condiciones():
                print("[WARN] No se pudo hacer click en campo de condiciones, continuando...")
            
            time.sleep(1)
            
            # ============================================================
            # FASE 1: OBTENER PRECIOS DE TODOS LOS MATERIALES DEL PORTAL
            # ============================================================
            print(f"\n{'='*60}")
            print(f"[FASE 1] Obteniendo precios de {len(materiales_lista)} material(es) del portal...")
            print(f"{'='*60}")
            
            # Lista para almacenar información de todos los materiales
            materiales_con_precios = []
            suma_total_con_iva = 0
            
            for indice, material_item in enumerate(materiales_lista):
                material_codigo = material_item[0]
                print(f"\n>> Buscando material {indice + 1}/{len(materiales_lista)}: {material_codigo} en portal...")
                
                # Abrir portal de socios para obtener el valor de este material
                resultado_portal = consultas.abrir_portal_socios(cedula, material_codigo)
                
                # Verificar si obtuvimos resultado
                if not resultado_portal:
                    motivo = f"No se obtuvo precio del portal para material {material_codigo}"
                    print(f"  [ERROR] {motivo}")
                    if self.gestor_excel:
                        self.gestor_excel.actualizar_estado(indice_excel, "Error - Precio no disponible", motivo)
                    consultas.recargar_pagina()
                    raise Exception(motivo)
                
                # Extraer información del resultado
                precio_sin_iva = resultado_portal.get('precio_sin_iva')
                precio_con_iva = resultado_portal.get('precio_con_iva')
                
                # Validar que los precios no sean 0 ni None
                if not precio_sin_iva or not precio_con_iva or precio_sin_iva == 0 or precio_con_iva == 0:
                    motivo = f"Precio en 0 para material {material_codigo} (sin IVA: {precio_sin_iva}, con IVA: {precio_con_iva})"
                    print(f"  [ERROR] {motivo}")
                    if self.gestor_excel:
                        self.gestor_excel.actualizar_estado(indice_excel, "Error - Precio en 0", motivo)
                    consultas.recargar_pagina()
                    raise Exception(motivo)
                
                print(f"  [OK] Material {material_codigo}:")
                print(f"       Precio sin IVA: {precio_sin_iva} COP")
                print(f"       Precio con IVA: {precio_con_iva} COP")
                
                # Guardar info del material
                materiales_con_precios.append({
                    'codigo': material_codigo,
                    'cantidad': material_item[1],
                    'precio_sin_iva': precio_sin_iva,
                    'precio_con_iva': precio_con_iva
                })
                
                # Sumar al total con IVA (multiplicar por cantidad)
                cantidad_material = int(material_item[1])
                suma_total_con_iva += precio_con_iva * cantidad_material
                print(f"       Suma parcial (x{cantidad_material}): {precio_con_iva * cantidad_material:,} COP")
            
            # Verificar que obtuvimos precios
            if not materiales_con_precios:
                raise Exception("No se pudo obtener precios del portal para ningún material")
            
            print(f"\n{'='*60}")
            print(f"[RESULTADO FASE 1]")
            print(f"  Total materiales con precio: {len(materiales_con_precios)}")
            print(f"  Suma total CON IVA: {suma_total_con_iva:,} COP")
            print(f"{'='*60}")
            
            # ============================================================
            # FASE 2: DECIDIR ESTRATEGIA (CON O SIN FLETE)
            # ============================================================
            LIMITE_FLETE = 150000
            aplicar_flete = suma_total_con_iva < LIMITE_FLETE
            tarifa_flete = None
            valor_flete_por_material = 0
            
            print(f"\n{'='*60}")
            print(f"[FASE 2] Determinando estrategia de flete...")
            print(f"{'='*60}")
            print(f"  Suma total con IVA: {suma_total_con_iva:,} COP")
            print(f"  Límite para flete: {LIMITE_FLETE:,} COP")
            
            if aplicar_flete:
                print(f"  [DECISIÓN] Suma < {LIMITE_FLETE:,} => SE APLICA FLETE MANUAL")
                
                # Obtener tarifa de flete
                if ciudad:
                    tarifa_flete = consultas.obtener_tarifa_flete(ciudad)
                    if tarifa_flete:
                        # Dividir entre número de materiales
                        num_materiales = len(materiales_con_precios)
                        valor_flete_por_material = int(tarifa_flete / num_materiales)
                        print(f"  [OK] Tarifa de flete: {tarifa_flete:,} COP sin IVA")
                        print(f"  [OK] Flete por material ({tarifa_flete} / {num_materiales}): {valor_flete_por_material:,} COP")
                    else:
                        print(f"  [WARN] No se pudo obtener tarifa de flete para ciudad {ciudad}")
                        aplicar_flete = False
                else:
                    print(f"  [WARN] No hay ciudad, no se puede aplicar flete")
                    aplicar_flete = False
            else:
                print(f"  [DECISIÓN] Suma >= {LIMITE_FLETE:,} => NO SE APLICA FLETE MANUAL")
            
            print(f"{'='*60}")
            
            # ============================================================
            # FASE 3: INGRESAR CONDICIONES PARA TODOS LOS MATERIALES
            # ============================================================
            print(f"\n{'='*60}")
            print(f"[FASE 3] Ingresando condiciones en SAP...")
            print(f"{'='*60}")
            
            for indice, material_info in enumerate(materiales_con_precios):
                material_codigo = material_info['codigo']
                precio_sin_iva = material_info['precio_sin_iva']
                
                print(f"\n>> Material {indice + 1}/{len(materiales_con_precios)}: {material_codigo}")
                
                # Si NO es el primer material, hacer click en "Posición siguiente"
                if indice > 0:
                    print(f"  [INFO] Navegando a la posición #{indice + 1}...")
                    if not consultas.hacer_click_posicion_siguiente():
                        motivo = f"No se pudo navegar a posicion siguiente (material #{indice + 1}: {material_codigo})"
                        print(f"  [ERROR] {motivo}")
                        if self.gestor_excel:
                            self.gestor_excel.actualizar_estado(indice_excel, "Error - Posicion siguiente", motivo)
                        raise Exception(motivo)
                    time.sleep(1)
                
                # Ingresar precio sin IVA
                print(f"  [INFO] Ingresando precio sin IVA: {precio_sin_iva} COP")
                if consultas.ingresar_valor_condiciones(precio_sin_iva):
                    print(f"  [OK] Precio sin IVA ingresado")
                else:
                    motivo = f"No se pudo ingresar precio sin IVA para material {material_codigo} ({precio_sin_iva} COP)"
                    print(f"  [ERROR] {motivo}")
                    if self.gestor_excel:
                        self.gestor_excel.actualizar_estado(indice_excel, "Error - Precio no ingresado", motivo)
                    raise Exception(motivo)
                
                time.sleep(1)
                
                # Si aplica flete, ingresar flete manual
                if aplicar_flete and valor_flete_por_material > 0:
                    print(f"  [INFO] Ingresando flete manual: {valor_flete_por_material} COP")
                    
                    if consultas.scroll_click_y_escribir_flete(valor_flete_por_material):
                        print(f"  [OK] Flete manual ingresado")
                    else:
                        aviso_flete = f"Flete no ingresado en material {material_codigo} ({valor_flete_por_material} COP)"
                        print(f"  [WARN] {aviso_flete}")
                        if self.gestor_excel:
                            self.gestor_excel.actualizar_estado(indice_excel, "Incompleto - Flete no ingresado", aviso_flete)
                    
                    time.sleep(1)
            
            print(f"\n{'='*60}")
            print(f"[OK] Todos los materiales procesados")
            print(f"{'='*60}")
            
            # Registrar materiales omitidos si los hubo
            if materiales_omitidos:
                aviso = f"Materiales bloqueados/omitidos: {', '.join(str(m) for m in materiales_omitidos)}"
                print(f"[WARN] {aviso}")
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Completado con omisiones", aviso)
            
            # Guardar pedido en SAP
            print("\n>> Guardando pedido en SAP...")
            numero_pedido = consultas.guardar_pedido()
            
            if numero_pedido:
                print(f"[OK] Pedido guardado exitosamente - N° Pedido: {numero_pedido}")
                # Guardar número de pedido en Excel
                if self.gestor_excel:
                    self.gestor_excel.actualizar_numero_pedido(indice_excel, numero_pedido)
            else:
                print("[WARN] Pedido guardado pero no se pudo extraer el numero de pedido")
            
            print(f"\n[OK] Cliente {numero}/{total} procesado exitosamente")
            
            # Actualizar estado en Excel
            if self.gestor_excel:
                detalle = f"Proceso completado - Pedido: {numero_pedido}" if numero_pedido else "Proceso completado exitosamente"
                self.gestor_excel.actualizar_estado(indice_excel, "Pedido creado", detalle)
            
            time.sleep(1)
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Error al procesar cliente {numero}: {error_msg}")
            
            # Actualizar estado en Excel
            if self.gestor_excel:
                # Detectar si es un cliente que debe ser omitido por requerimientos especiales
                if "hay que seleccionar detalle de venta" in error_msg:
                    print(f"  [SKIP] Cliente omitido por requerimiento: {error_msg}")
                    self.gestor_excel.actualizar_estado(indice_excel, "Omitido", "Determinar area de venta")
                    raise  # Re-lanzar para que el loop no reintente
                elif any(txt in error_msg.lower() for txt in ["bloqueado", "bloqueo", "org de venta", "org.ventas", "no puede ser procesado", "no está previsto", "no est\u00e1 previsto"]):
                    print(f"  [SKIP] Cliente omitido: {error_msg}")
                    self.gestor_excel.actualizar_estado(indice_excel, "Bloqueado", error_msg[:200])
                    raise  # Re-lanzar para que el loop no reintente
                else:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error al crear pedido", error_msg[:200])
            
            import traceback
            traceback.print_exc()
            return False
    
    def ejecutar(self):
        """
        Ejecuta el flujo completo del RPA
        """
        try:
            print("="*60)
            print("INICIANDO RPA AUTECO")
            print("="*60)
            
            # 0. Cargar clientes del Excel
            if not self.cargar_clientes():
                return False
            
            # Procesar cada cliente del Excel (con navegador independiente)
            total_clientes = len(self.clientes)
            clientes_exitosos = 0
            clientes_fallidos = 0
            
            for idx, cliente in enumerate(self.clientes, start=1):
                print("\n" + "="*60)
                print(f">>> CLIENTE {idx}/{total_clientes} <<<")
                print("="*60)
                
                try:
                    # 1. Crear driver para este cliente
                    print(f"\n1. Abriendo navegador para cliente {idx}...")
                    self.driver_sap = DriverSAP()
                    if not self.driver_sap.crear_driver():
                        print(f"[ERROR] No se pudo crear el driver para cliente {idx}")
                        clientes_fallidos += 1
                        continue
                    
                    # 2. Navegar a SAP
                    print(f"\n2. Navegando a SAP...")
                    self.driver_sap.ir_a_url(URL_SAP)
                    time.sleep(3)
                    
                    # 3. Realizar login
                    print(f"\n3. Realizando login en SAP...")
                    login = LoginSAP(self.driver_sap)
                    if not login.iniciar_sesion(USUARIO, CONTRASEÑA):
                        print(f"[ERROR] Error durante el login para cliente {idx}")
                        clientes_fallidos += 1
                        # Cerrar navegador antes de continuar
                        self.driver_sap.cerrar_driver()
                        continue
                    
                    print("[OK] Login completado exitosamente")
                    time.sleep(2)
                    
                    # 4. Procesar el cliente CON REINTENTOS para errores de portal
                    max_reintentos = 3
                    reintento = 0
                    exito = False
                    ultimo_error = None
                    
                    while reintento < max_reintentos and not exito:
                        try:
                            exito = self.procesar_cliente(cliente, idx, total_clientes)
                            if exito:
                                break  # Éxito, salir del loop de reintentos
                            else:
                                # procesar_cliente retornó False (error no crítico)
                                reintento += 1
                                if reintento < max_reintentos:
                                    print(f"\n[REINTENTO {reintento}/{max_reintentos}] Cliente devolvió False. Reiniciando navegador...")
                                    try:
                                        if self.driver_sap:
                                            self.driver_sap.cerrar_driver()
                                    except:
                                        pass
                                    time.sleep(3)
                                    self.driver_sap = DriverSAP()
                                    if not self.driver_sap.crear_driver():
                                        print(f"[ERROR] No se pudo recrear el driver en reintento {reintento}")
                                        break
                                    self.driver_sap.ir_a_url(URL_SAP)
                                    time.sleep(3)
                                    login = LoginSAP(self.driver_sap)
                                    if not login.iniciar_sesion(USUARIO, CONTRASEÑA):
                                        print(f"[ERROR] Error durante el login en reintento {reintento}")
                                        break
                                    print(f"[INFO] Reintentando procesamiento del cliente...")
                                    time.sleep(2)
                                else:
                                    print(f"\n[ERROR] Se agotaron los {max_reintentos} reintentos (retorno False)")
                                    break
                                
                        except Exception as e:
                            ultimo_error = str(e)
                            error_lower = str(e).lower()
                            
                            # Errores NO recuperables: bloqueos y org de ventas -> saltar cliente inmediatamente
                            if "bloqueo" in error_lower or "bloqueado" in error_lower or "org" in error_lower and "venta" in error_lower or "no puede ser procesado" in error_lower:
                                print(f"\n[SKIP] Error de bloqueo/org ventas detectado, saltando cliente sin reintentar: {str(e)[:150]}")
                                exito = False
                                break
                            
                            # Verificar si es un error recuperable (portal, precio o intercepciones)
                            if "No se obtuvo precio del portal" in str(e) or "No se pudo ingresar precio sin IVA" in str(e) or "element click intercepted" in str(e) or "reintentando cliente" in str(e):
                                reintento += 1
                                
                                if reintento < max_reintentos:
                                    print(f"\n[REINTENTO {reintento}/{max_reintentos}] Error de portal/precio/intercepciones detectado. Reiniciando el cliente...")
                                    print(f"  Cerrando navegador...")
                                    try:
                                        if self.driver_sap:
                                            self.driver_sap.cerrar_driver()
                                    except:
                                        pass
                                    
                                    time.sleep(3)
                                    
                                    print(f"  Recreando driver...")
                                    self.driver_sap = DriverSAP()
                                    if not self.driver_sap.crear_driver():
                                        print(f"[ERROR] No se pudo recrear el driver en reintento {reintento}")
                                        break
                                    
                                    self.driver_sap.ir_a_url(URL_SAP)
                                    time.sleep(3)
                                    
                                    print(f"  Realizando login nuevamente...")
                                    login = LoginSAP(self.driver_sap)
                                    if not login.iniciar_sesion(USUARIO, CONTRASEÑA):
                                        print(f"[ERROR] Error durante el login en reintento {reintento}")
                                        break
                                    
                                    print(f"[INFO] Reintentando procesamiento del cliente...")
                                    time.sleep(2)
                                    # El loop continuará automáticamente
                                else:
                                    # Se agotaron los reintentos
                                    print(f"\n[ERROR] Se agotaron los {max_reintentos} reintentos por error de portal/precio/intercepciones")
                                    exito = False
                                    break
                            else:
                                # No es un error de portal, lanzar normalmente
                                raise
                    
                    if exito:
                        clientes_exitosos += 1
                        if reintento > 0:
                            print(f"[OK] Cliente {idx} procesado exitosamente después de {reintento} reintento(s)")
                    else:
                        clientes_fallidos += 1
                        if reintento > 0:
                            print(f"[WARN] Cliente {idx} falló después de {reintento} reintento(s)")
                        else:
                            print(f"[WARN] Cliente {idx} falló")
                    
                except Exception as e:
                    print(f"\n[ERROR] Error al procesar cliente {idx}: {str(e)}")
                    clientes_fallidos += 1
                
                finally:
                    # 5. SIEMPRE cerrar el navegador después de cada cliente
                    print(f"\n>> Cerrando navegador del cliente {idx}...")
                    try:
                        if self.driver_sap:
                            self.driver_sap.cerrar_driver()
                            print(f"[OK] Navegador cerrado para cliente {idx}")
                    except Exception as e:
                        print(f"[WARN] Error al cerrar navegador: {str(e)}")
                    
                    # Guardar estados en Excel después de cada cliente
                    if self.gestor_excel:
                        try:
                            self.gestor_excel.guardar()
                            print(f"  [OK] Estados guardados en Excel")
                        except Exception as e:
                            print(f"  [WARN] Error al guardar Excel: {str(e)[:100]}")
                    
                    # Pequeña pausa entre clientes
                    if idx < total_clientes:
                        print(f"\n[INFO] Esperando 2 segundos antes del siguiente cliente...")
                        time.sleep(2)
            
            # Resumen final
            print("\n" + "="*60)
            print(">>> RPA COMPLETADO <<<")
            print("="*60)
            print(f"Total de clientes: {total_clientes}")
            print(f"Exitosos: {clientes_exitosos}")
            print(f"Fallidos: {clientes_fallidos}")
            print("="*60)
            
            # Guardar Excel con estados actualizados
            if self.gestor_excel:
                print("\n>> Guardando estados en Excel...")
                if self.gestor_excel.guardar():
                    print("[OK] Excel actualizado correctamente")
                    
                    # Mostrar resumen de estados
                    resumen = self.gestor_excel.obtener_resumen()
                    if resumen:
                        print("\n--- RESUMEN DE ESTADOS ---")
                        for estado, cantidad in resumen.items():
                            print(f"  {estado}: {cantidad}")
                        print("-" * 60)
                else:
                    print("[WARN] No se pudo guardar el Excel con estados")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Error general: {str(e)}")
            # Intentar guardar el Excel aunque haya error
            if self.gestor_excel:
                print("\n>> Intentando guardar Excel con estados parciales...")
                self.gestor_excel.guardar()
            return False


def seleccionar_archivo_excel():
    """
    Abre un diálogo para seleccionar el archivo Excel de clientes
    """
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    root.attributes('-topmost', True)  # Mantener al frente

    # Configurar el diálogo
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel de clientes",
        filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")],
        initialdir=os.path.expanduser("~\\Downloads")  # Iniciar en Downloads
    )

    root.destroy()
    return archivo


def main():
    """Función principal"""

    print("="*60)
    print("RPA AUTECO - SELECCIÓN DE ARCHIVO")
    print("="*60)

    # Seleccionar archivo Excel de clientes
    ruta_excel = seleccionar_archivo_excel()

    if not ruta_excel:
        print("[ERROR] No se seleccionó ningún archivo Excel")
        input("Presiona Enter para salir...")
        return

    print(f"[OK] Archivo seleccionado: {ruta_excel}")

    # Verificar que el archivo existe
    if not os.path.exists(ruta_excel):
        print(f"[ERROR] El archivo no existe: {ruta_excel}")
        input("Presiona Enter para salir...")
        return

    # ============================================================
    # MODO ACTUAL: Procesar todos, omitiendo los que ya tienen Numero Pedido
    # ============================================================
    rpa = RPA_AUTECO(ruta_excel)

    # Ejecutar el RPA
    exito = rpa.ejecutar()

    if exito:
        print("\n[OK] RPA completado exitosamente")
    else:
        print("\n[ERROR] El RPA terminó con errores")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
