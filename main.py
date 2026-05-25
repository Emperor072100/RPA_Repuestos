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
import requests

# Agregar rutas para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modulos.driver_selenium import DriverSAP
from modulos.login_sap import LoginSAP
from modulos.consultas_sap import ConsultasSAP
from modulos.leer_excel import leer_clientes_excel, obtener_marca, obtener_datos_organizativos, extraer_cedula, extraer_telefono, procesar_referencia, extraer_ciudad, GestorExcelEstados, extraer_id
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
        self.gestor_excel = None
        self.solo_filas = solo_filas
        self.solo_cedulas = solo_cedulas
        self.limite = limite
        self.portal_paso3_listo = False  # True solo tras la primera navegación exitosa en este run
    
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
    
    def notificar_pedido_creado(self, cliente_id: str) -> bool:
        """
        Notifica al API externo que un pedido fue creado exitosamente.

        Args:
            cliente_id: ID del registro en el Excel (columna 'ID')
        """
        url = f"https://cx-andesbpo-auteco-rnd-backend.agwhdq.easypanel.host/api/rpa/pedido-creado/{cliente_id}"
        headers = {
            "X-API-Key": "TmZFKOoU8SiKuWyczEn9Ji4BtpAoOZTMXDS-Qvf_QEQ",
            "Content-Type": "application/json"
        }
        body = {
            "ok": True,
            "cliente_id": int(cliente_id),
            "estado": "PEDIDO_CREADO",
            "mensaje": f"Solicitud {cliente_id} actualizada a Pedido creado"
        }
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            if response.ok:
                print(f"  [OK] API notificada correctamente (HTTP {response.status_code})")
                return True
            else:
                print(f"  [WARN] API respondio con error: HTTP {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            print(f"  [WARN] Error al notificar API: {str(e)}")
            return False

    def procesar_cliente(self, cliente: dict, numero: int, total: int, precios_precargados=None):
        """
        Procesa un cliente individual

        Args:
            cliente: Diccionario con la información del cliente
            numero: Número del cliente actual
            total: Total de clientes a procesar
            precios_precargados: Lista de dicts {codigo, cantidad, precio_sin_iva, precio_con_iva}
                                 obtenida antes de entrar a SAP. Si se provee, se omite FASE 1.

        Returns:
            True si el procesamiento fue exitoso
        """
        consultas = None  # inicializar para que el except pueda recargar aunque falle temprano
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

            # [SHIELD] Limpiar modales antes de ingresar solicitante
            consultas._limpiar_modales_bloqueantes()

            # Ingresar cédula del solicitante
            print("\n>> Ingresando cedula del solicitante...")
            if not consultas.ingresar_cedula_solicitante(cedula):
                print("[WARN] No se pudo ingresar la cedula del solicitante, continuando...")

            time.sleep(1)

            # [SHIELD] Limpiar modales antes de ingresar destinatario
            consultas._limpiar_modales_bloqueantes()

            # Ingresar cédula del destinatario de mercancía
            print("\n>> Ingresando cedula del destinatario...")
            if not consultas.ingresar_cedula_destinatario(cedula):
                print("[WARN] No se pudo ingresar la cedula del destinatario, continuando...")

            time.sleep(1)

            # Ingresar referencia en N° ped.cliente (cedula-material para detección de duplicados)
            primer_material = materiales_lista[0][0] if materiales_lista else None
            print("\n>> Ingresando referencia en N ped.cliente...")
            if not consultas.ingresar_numero_pedido_cliente(cedula, material=primer_material):
                print("[WARN] No se pudo ingresar N ped.cliente, continuando...")

            time.sleep(1)

            # Seleccionar Modific.cantidad
            print("\n>> Seleccionando Modific.cantidad...")
            if not consultas.seleccionar_modific_cantidad():
                print("[WARN] No se pudo seleccionar Modific.cantidad, continuando...")

            # [SHIELD] Limpiar modales antes de seleccionar tipo de pedido
            consultas._limpiar_modales_bloqueantes()

            # Seleccionar Pedido Ecommerce Cliente Final
            print("\n>> Seleccionando Pedido Ecommerce Cliente Final...")
            if not consultas.seleccionar_pedido_ecommerce():
                print("[WARN] No se pudo seleccionar Pedido Ecommerce, continuando...")

            # Verificar si hay error de pedido duplicado y corregirlo
            print("\n>> Verificando pedido duplicado...")
            if not consultas.verificar_y_corregir_pedido_duplicado(telefono):
                print("[WARN] Hubo problema al verificar/corregir pedido duplicado, continuando...")

            time.sleep(1)

            # Confirmar N° ped.cliente con Enter para habilitar Material/Cantidad
            print("\n>> Confirmando N ped.cliente con Enter...")
            if not consultas.confirmar_numero_pedido_cliente(telefono=telefono):
                print("[WARN] No se pudo confirmar N ped.cliente, continuando...")

            time.sleep(3)

            # [SHIELD] Limpiar modales antes de ingresar materiales
            consultas._limpiar_modales_bloqueantes()

            # Ingresar Material y Cantidad para cada repuesto
            print(f"\n>> Ingresando {len(materiales_lista)} Material(es) y Cantidad(es)...")
            materiales_exitosos = 0
            primer_material_exitoso = None
            materiales_omitidos = []

            for idx, (material, cantidad) in enumerate(materiales_lista, 1):
                print(f"\n   ========================================")
                print(f"   [{idx}/{len(materiales_lista)}] Material: {material}, Cantidad: {cantidad}")
                print(f"   ========================================")

                # [SHIELD] Limpiar modales antes de cada material
                consultas._limpiar_modales_bloqueantes()

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
                    time.sleep(1)
            
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
            
            # [SHIELD] Limpiar modales antes de condiciones
            consultas._limpiar_modales_bloqueantes()

            print("\n>> Haciendo click en pestaña Condiciones...")
            if not consultas.hacer_click_condiciones():
                motivo = "No se pudo abrir la pestana Condiciones en SAP"
                print(f"[ERROR] {motivo}")
                if self.gestor_excel:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error - Pestana Condiciones", motivo)
                raise Exception(motivo)

            # Hacer click en el campo de condiciones
            print("\n>> Haciendo click en campo de condiciones...")
            if not consultas.hacer_click_campo_condiciones():
                print("[WARN] No se pudo hacer click en campo de condiciones, continuando...")
            
            # ============================================================
            # FASE 1: PRECIOS DEL PORTAL (precargados o consultados ahora)
            # ============================================================
            print(f"\n{'='*60}")
            materiales_con_precios = []
            suma_total_con_iva = 0

            if precios_precargados is not None:
                # Usar precios ya obtenidos antes de entrar a SAP
                print(f"[FASE 1] Usando {len(precios_precargados)} precio(s) precargado(s) del portal")
                print(f"{'='*60}")
                materiales_con_precios = precios_precargados
                for item in materiales_con_precios:
                    precio_con_iva = item['precio_con_iva']
                    cantidad_material = int(item['cantidad'])
                    suma_total_con_iva += precio_con_iva * cantidad_material
                    print(f"  Material {item['codigo']}: sin IVA={item['precio_sin_iva']}, con IVA={precio_con_iva:,} (x{cantidad_material})")
            else:
                # Flujo original: consultar portal desde dentro de SAP
                print(f"[FASE 1] Obteniendo precios de {len(materiales_lista)} material(es) del portal...")
                print(f"{'='*60}")

                for indice, material_item in enumerate(materiales_lista):
                    material_codigo = material_item[0]
                    print(f"\n>> Buscando material {indice + 1}/{len(materiales_lista)}: {material_codigo} en portal...")

                    resultado_portal = consultas.abrir_portal_socios(cedula, material_codigo)

                    if not resultado_portal:
                        motivo = f"No se obtuvo precio del portal para material {material_codigo}"
                        print(f"  [ERROR] {motivo}")
                        if self.gestor_excel:
                            self.gestor_excel.actualizar_estado(indice_excel, "Error - Precio no disponible", motivo)
                        consultas.recargar_pagina()
                        raise Exception(motivo)

                    precio_sin_iva = resultado_portal.get('precio_sin_iva')
                    precio_con_iva = resultado_portal.get('precio_con_iva')

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

                    materiales_con_precios.append({
                        'codigo': material_codigo,
                        'cantidad': material_item[1],
                        'precio_sin_iva': precio_sin_iva,
                        'precio_con_iva': precio_con_iva
                    })

                    cantidad_material = int(material_item[1])
                    suma_total_con_iva += precio_con_iva * cantidad_material
                    print(f"       Suma parcial (x{cantidad_material}): {precio_con_iva * cantidad_material:,} COP")

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
            LIMITE_FLETE = 200000 #el flete es 200k 
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
                if self.gestor_excel:
                    self.gestor_excel.actualizar_numero_pedido(indice_excel, numero_pedido)
                # Notificar API con el ID del Excel
                cliente_id = extraer_id(cliente)
                if cliente_id:
                    print(f"\n>> Notificando API para ID {cliente_id}...")
                    self.notificar_pedido_creado(cliente_id)
                else:
                    print("[WARN] No se encontro columna 'ID' en el Excel, omitiendo notificacion API")
            else:
                print("[WARN] Pedido guardado pero no se pudo extraer el numero de pedido")

            print(f"\n[OK] Cliente {numero}/{total} procesado exitosamente")

            if self.gestor_excel:
                detalle = f"Proceso completado - Pedido: {numero_pedido}" if numero_pedido else "Proceso completado exitosamente"
                self.gestor_excel.actualizar_estado(indice_excel, "Pedido creado", detalle)

            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ERROR] Error al procesar cliente {numero}: {error_msg}")

            # CAPA 3 - BLINDAJE: recargar SAP siempre para garantizar estado limpio al siguiente cliente
            try:
                if consultas is not None:
                    print("  [SHIELD] Recargando SAP para limpiar estado...")
                    consultas.recargar_pagina()
            except Exception as e_reload:
                print(f"  [SHIELD] Advertencia al recargar: {str(e_reload)[:80]}")

            # Actualizar estado en Excel y decidir si re-lanzar (skip sin reintento) o retornar False
            if self.gestor_excel:
                if "hay que seleccionar detalle de venta" in error_msg:
                    print(f"  [SKIP] Cliente omitido - multiples areas de venta en SAP")
                    self.gestor_excel.actualizar_estado(indice_excel, "Creado en SAS", "Imposible crear pedido SAP - multiples areas de venta")
                    raise
                elif "sin solicitante valido" in error_msg:
                    print(f"  [SKIP] Cliente omitido - sin solicitante 11 ni 22")
                    self.gestor_excel.actualizar_estado(indice_excel, "Omitido", "Sin solicitante valido (sin prefijo 11 ni 22)")
                    raise
                elif "sin destinatario valido" in error_msg:
                    print(f"  [SKIP] Cliente omitido - sin destinatario 55")
                    self.gestor_excel.actualizar_estado(indice_excel, "Omitido", "Sin destinatario valido (sin prefijo 55)")
                    raise
                elif "pedido ya existe" in error_msg.lower():
                    print(f"  [SKIP] Pedido duplicado detectado: {error_msg}")
                    self.gestor_excel.actualizar_estado(indice_excel, "Pedido ya existe", error_msg[:200])
                    raise
                elif any(txt in error_msg.lower() for txt in ["bloqueado", "bloqueo", "org de venta", "org.ventas", "no puede ser procesado", "no está previsto", "no est\u00e1 previsto"]):
                    print(f"  [SKIP] Cliente omitido: {error_msg}")
                    self.gestor_excel.actualizar_estado(indice_excel, "Bloqueado", error_msg[:200])
                    raise  # Re-lanzar para que el loop no reintente
                else:
                    self.gestor_excel.actualizar_estado(indice_excel, "Error al crear pedido", error_msg[:200])
            
            import traceback
            traceback.print_exc()
            return False
    
    def _sesion_viva(self) -> bool:
        """Comprueba si la sesión de Chrome sigue activa"""
        try:
            _ = self.driver_sap.driver.window_handles
            return True
        except Exception:
            return False

    def _abrir_tabs(self, url_portal: str):
        """Abre (o reabre) las dos pestañas del navegador y devuelve sus handles"""
        self.driver_sap.ir_a_url(url_portal)
        portal_tab = self.driver_sap.driver.current_window_handle

        # Abrir segunda pestaña con reintento por si el popup blocker tarda en desactivarse
        for intento in range(5):
            self.driver_sap.driver.execute_script("window.open('', '_blank');")
            time.sleep(1)
            nuevos = [h for h in self.driver_sap.driver.window_handles if h != portal_tab]
            if nuevos:
                sap_tab = nuevos[0]
                break
        else:
            raise RuntimeError("No se pudo abrir la segunda pestaña para SAP")

        self.driver_sap.driver.switch_to.window(sap_tab)
        self.driver_sap.driver.get(URL_SAP)
        return portal_tab, sap_tab

    def _recuperar_sesion(self, url_portal: str):
        """Recreates the Chrome driver and re-opens both tabs after a crash"""
        print("[RECOVER] Recreando sesión de Chrome...")
        try:
            self.driver_sap.cerrar_driver()
        except Exception:
            pass
        if not self.driver_sap.crear_driver():
            raise RuntimeError("No se pudo recrear el driver de Chrome")
        portal_tab, sap_tab = self._abrir_tabs(url_portal)
        print("[RECOVER] Sesión recreada correctamente")
        return portal_tab, sap_tab

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
            
            # Procesar cada cliente del Excel con UN SOLO navegador
            total_clientes = len(self.clientes)
            clientes_exitosos = 0
            clientes_fallidos = 0

            # Crear driver UNA SOLA VEZ para todos los clientes
            print("\n>> Abriendo navegador...")
            self.driver_sap = DriverSAP()
            if not self.driver_sap.crear_driver():
                print("[ERROR] No se pudo crear el driver")
                return False

            url_portal = "https://portal-socios-auteco-portal-approuter.cfapps.us10.hana.ondemand.com/autecoPortalApp/index.html"

            # Abrir portal en pestaña 1 y SAP en pestaña 2
            print("\n>> Inicializando pestañas (Portal + SAP)...")
            portal_tab, sap_tab = self._abrir_tabs(url_portal)
            print("[OK] Dos pestañas abiertas: Portal (pestaña 1) y SAP (pestaña 2)")

            # ============================================================
            # PRECARGA: obtener TODOS los precios del portal de una sola vez
            # ============================================================
            print("\n>> Precargando precios del portal para todos los clientes...")
            self.driver_sap.driver.switch_to.window(portal_tab)
            consultas_preload = ConsultasSAP(self.driver_sap)

            # Recopilar materiales únicos de todos los clientes
            materiales_unicos = {}
            for c in self.clientes:
                rd = procesar_referencia(c)
                if not rd['descartar']:
                    for mat, cant in rd['materiales']:
                        if mat not in materiales_unicos:
                            materiales_unicos[mat] = cant

            lista_todos_materiales = list(materiales_unicos.items())
            print(f"  [INFO] {len(lista_todos_materiales)} material(es) únicos entre todos los clientes")

            # Intentar la precarga hasta 3 veces si falla la navegación al portal
            cache_precios_portal = {}
            for intento_preload in range(3):
                cache_precios_portal = consultas_preload.precargar_precios_batch(lista_todos_materiales)
                encontrados = sum(1 for v in cache_precios_portal.values() if v is not None)
                if encontrados > 0:
                    break
                print(f"  [WARN] Precarga intento {intento_preload+1}/3 sin resultados, reintentando en 5s...")
                time.sleep(5)

            encontrados = sum(1 for v in cache_precios_portal.values() if v is not None)
            print(f"[OK] Cache del portal listo: {encontrados}/{len(cache_precios_portal)} materiales con precio")
            # ============================================================

            try:
                for idx, cliente in enumerate(self.clientes, start=1):
                    print("\n" + "="*60)
                    print(f">>> CLIENTE {idx}/{total_clientes} <<<")
                    print("="*60)

                    try:
                        # 0. Pre-extraer materiales (sin navegacion)
                        ref_data_previo = procesar_referencia(cliente)
                        if ref_data_previo["descartar"]:
                            nombre_previo = cliente.get("Nombre completo", "N/A")
                            print(f"[SKIP] Cliente {idx} ({nombre_previo}) descartado por referencia invalida")
                            indice_excel_previo = cliente.get("_indice_original", idx - 1)
                            if self.gestor_excel:
                                self.gestor_excel.actualizar_estado(indice_excel_previo, "Omitido", "Referencia invalida")
                            clientes_fallidos += 1
                            continue
                        materiales_para_portal = ref_data_previo["materiales"]

                        # 1. Obtener precios desde cache precargado (sin tocar el portal)
                        print("\n1. Obteniendo precios del portal (cache)...")
                        precios_portal = []
                        alguno_fallo = False
                        for mat, cant in materiales_para_portal:
                            info = cache_precios_portal.get(mat)
                            if info is None:
                                print(f"  [ERROR] Material {mat} sin precio en cache del portal")
                                alguno_fallo = True
                                break
                            precios_portal.append({**info, 'cantidad': cant})

                        if alguno_fallo or not precios_portal:
                            print(f"[ERROR] No se pudieron obtener precios del portal para cliente {idx}")
                            clientes_fallidos += 1
                            indice_excel_previo = cliente.get("_indice_original", idx - 1)
                            if self.gestor_excel:
                                self.gestor_excel.actualizar_estado(indice_excel_previo, "Error - Portal sin precio", "No se obtuvieron precios del portal")
                            continue

                        # Filtrar solo materiales NO DISPONIBLES en página 1
                        materiales_no_disponibles = [p for p in precios_portal if p.get('no_disponible', False)]
                        materiales_disponibles = [p for p in precios_portal if not p.get('no_disponible', False)]

                        if materiales_disponibles:
                            codigos_disponibles = ', '.join(p['codigo'] for p in materiales_disponibles)
                            print(f"  [INFO] Materiales DISPONIBLES en página 1 (no se pedirán): {codigos_disponibles}")

                        if not materiales_no_disponibles:
                            print(f"[SKIP] Todos los materiales están disponibles en página 1 → no se crea pedido SAP")
                            indice_excel_previo = cliente.get("_indice_original", idx - 1)
                            if self.gestor_excel:
                                self.gestor_excel.actualizar_estado(
                                    indice_excel_previo,
                                    "Disponibilidad dealer",
                                    f"Disponibles en página 1: {', '.join(p['codigo'] for p in precios_portal)}"
                                )
                            clientes_fallidos += 1
                            continue

                        # Solo continuar con los materiales no disponibles
                        precios_portal = materiales_no_disponibles
                        print(f"  [INFO] Se crearán pedidos SAP para {len(precios_portal)} material(es) no disponible(s)")

                        # 2. Cambiar a pestaña SAP (portal queda intacto en Paso 3)
                        print("\n2. Cambiando a pestaña SAP...")
                        if not self._sesion_viva():
                            print("[WARN] Sesión de Chrome caída, recreando...")
                            portal_tab, sap_tab = self._recuperar_sesion(url_portal)
                            self.portal_paso3_listo = False
                        try:
                            self.driver_sap.driver.switch_to.window(sap_tab)
                        except Exception as e_sw:
                            if "invalid session" in str(e_sw).lower() or "session deleted" in str(e_sw).lower() or "no such window" in str(e_sw).lower():
                                print("[WARN] Handle SAP inválido, recreando sesión...")
                                portal_tab, sap_tab = self._recuperar_sesion(url_portal)
                                self.driver_sap.driver.switch_to.window(sap_tab)
                            else:
                                raise

                        # 3. Login (inteligente: omite si la sesion ya esta activa)
                        print("\n3. Verificando sesion SAP...")
                        login = LoginSAP(self.driver_sap)
                        if not login.iniciar_sesion(USUARIO, CONTRASEÑA):
                            print(f"[ERROR] Error durante el login para cliente {idx}")
                            clientes_fallidos += 1
                            continue

                        print("[OK] Sesion SAP lista")

                        # 4. Procesar el cliente SIN REINTENTOS
                        max_reintentos = 1
                        reintento = 0
                        exito = False
                        ultimo_error = None

                        while reintento < max_reintentos and not exito:
                            try:
                                exito = self.procesar_cliente(cliente, idx, total_clientes, precios_precargados=precios_portal)
                                if exito:
                                    break
                                else:
                                    reintento += 1
                                    print(f"\n[ERROR] Se agotaron los {max_reintentos} reintentos (retorno False)")
                                    break

                            except Exception as e:
                                ultimo_error = str(e)
                                error_lower = str(e).lower()

                                if "pedido ya existe" in error_lower:
                                    print(f"\n[SKIP] Pedido duplicado, saltando cliente: {str(e)[:150]}")
                                    exito = False
                                    break
                                elif "sin solicitante valido" in error_lower or "sin destinatario valido" in error_lower or "hay que seleccionar detalle de venta" in error_lower:
                                    print(f"\n[SKIP] Cliente omitido por datos SAP invalidos: {str(e)[:150]}")
                                    exito = False
                                    break
                                elif "bloqueo" in error_lower or "bloqueado" in error_lower or ("org" in error_lower and "venta" in error_lower) or "no puede ser procesado" in error_lower:
                                    print(f"\n[SKIP] Error de bloqueo/org ventas: {str(e)[:150]}")
                                    exito = False
                                    break

                                print(f"\n[ERROR] Error no recuperable, pasando al siguiente cliente: {str(e)[:150]}")
                                exito = False
                                break

                        if exito:
                            clientes_exitosos += 1
                            print(f"[OK] Cliente {idx} procesado exitosamente")
                        else:
                            clientes_fallidos += 1
                            print(f"[WARN] Cliente {idx} fallo")

                    except Exception as e:
                        print(f"\n[ERROR] Error al procesar cliente {idx}: {str(e)}")
                        clientes_fallidos += 1

                    finally:
                        # Guardar Excel despues de cada cliente (sin cerrar navegador)
                        if self.gestor_excel:
                            try:
                                self.gestor_excel.guardar()
                                print(f"  [OK] Estados guardados en Excel")
                            except Exception as e:
                                print(f"  [WARN] Error al guardar Excel: {str(e)[:100]}")

                        # BLINDAJE FINAL: recargar SAP después de cada cliente sin importar el resultado
                        # Garantiza estado limpio para el siguiente pedido
                        try:
                            print("  [SHIELD] Recargando SAP para garantizar estado limpio...")
                            self.driver_sap.driver.switch_to.default_content()
                            self.driver_sap.driver.refresh()
                            time.sleep(3)
                            print("  [SHIELD] SAP recargado correctamente")
                        except Exception as e_ref:
                            print(f"  [SHIELD] Advertencia al recargar SAP: {str(e_ref)[:80]}")

                        # Pausa entre clientes
                        if idx < total_clientes:
                            time.sleep(1)

            finally:
                # Cerrar navegador UNA SOLA VEZ al terminar todos los clientes
                print("\n>> Cerrando navegador...")
                try:
                    if self.driver_sap:
                        self.driver_sap.cerrar_driver()
                        print("[OK] Navegador cerrado")
                except Exception as e:
                    print(f"[WARN] Error al cerrar navegador: {str(e)}")

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
