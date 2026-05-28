# -*- coding: utf-8 -*-
"""
Módulo para navegar y llenar formularios en SAP
Contiene funciones para automatizar las consultas después del login
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re


class ConsultasSAP:
    """
    Clase para manejar las consultas y navegación en SAP
    Después de que el usuario inicia sesión
    """
    
    def __init__(self, driver_sap):
        """
        Inicializa el manejador de consultas
        
        Args:
            driver_sap: Instancia de la clase DriverSAP
        """
        self.driver_sap = driver_sap
        self.driver = driver_sap.driver
        self._portal_recargado = False
    
    def buscar_va01(self):
        """
        Busca y ejecuta la transacción VA01 (Crear Pedido de Cliente)
        Esto navega a la pantalla de creación de pedidos
        """
        try:
            print("\n--- Buscando transacción VA01 ---")
            
            # Intentar encontrar el campo en el documento raíz primero
            print(">> Buscando campo ToolbarOkCode...")
            
            try:
                # Buscar en iframes
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                print(f"  Encontrados {len(iframes)} iframes")
                
                # Intentar en cada iframe
                for idx, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(iframe)
                        elemento = self.driver.find_element(By.ID, 'ToolbarOkCode')
                        print(f"  [OK] Campo encontrado en iframe {idx}")
                        
                        # Escribir /nVA01 para forzar navegación limpia descartando estado anterior
                        print(">> Escribiendo /nVA01...")
                        elemento.clear()
                        elemento.send_keys('/nVA01')
                        time.sleep(0.5)
                        
                        # Presionar Enter
                        print(">> Presionando Enter...")
                        elemento.send_keys(Keys.RETURN)
                        
                        # Volver al contenido principal
                        self.driver.switch_to.default_content()

                        # Esperar a que cargue la pantalla de VA01 (iframe con campos organizativos)
                        try:
                            WebDriverWait(self.driver, 15).until(
                                EC.frame_to_be_available_and_switch_to_it("ITSFRAME1")
                            )
                            self.driver.switch_to.default_content()
                        except:
                            time.sleep(2)

                        print("[OK] Navegación a VA01 completada")
                        return True
                        
                    except:
                        self.driver.switch_to.default_content()
                        continue
                
                # Si no está en iframes, intentar directamente
                print("  Intentando en contenido principal...")
                elemento = self.driver.find_element(By.ID, 'ToolbarOkCode')
                print(">> Escribiendo /nVA01...")
                elemento.clear()
                elemento.send_keys('/nVA01')
                time.sleep(0.5)
                
                print(">> Presionando Enter...")
                elemento.send_keys(Keys.RETURN)
                
                time.sleep(3)
                print("[OK] Navegación a VA01 completada")
                return True
                
            except Exception as e:
                print(f"  [ERROR] Campo no encontrado: {str(e)}")
                print("  Intentando alternativas...")
                
                # Alternativa: buscar por name o cualquier otro atributo
                campo = self.driver.find_element(By.NAME, 'ToolbarOkCode')
                campo.send_keys('/nVA01')
                campo.send_keys(Keys.RETURN)
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.frame_to_be_available_and_switch_to_it("ITSFRAME1")
                    )
                    self.driver.switch_to.default_content()
                except:
                    time.sleep(2)
                print("[OK] VA01 encontrado con método alternativo")
                return True
            
        except Exception as e:
            print(f"[ERROR] Error al buscar VA01: {str(e)}")
            return False
    
    def llenar_datos_organizativos(self, clase_pedido: str, org_ventas: str, canal_dist: str, sector: str):
        """
        Llena los datos organizativos en la pantalla de VA01
        Clase pedido, Organización ventas, Canal distribución, Sector
        
        Args:
            clase_pedido: Clase de pedido (ej: "zpec")
            org_ventas: Organización de ventas (ej: "2100")
            canal_dist: Canal de distribución (ej: "10")
            sector: Sector (ej: "43")
        """
        try:
            print("\n--- Rellenando datos organizativos ---")

            # Los campos están dentro del iframe ITSFRAME1
            # Cambiar al iframe donde están los campos
            self.driver.switch_to.frame("ITSFRAME1")
            print("  [OK] Cambiado al iframe ITSFRAME1")
            
            # Llenar cada campo usando su ID exacto
            # Campo 1: Clase de pedido - ID: M0:46:::2:22
            print(f">> Ingresando Clase de pedido: {clase_pedido}")
            campo_clase = self.driver.find_element(By.ID, "M0:46:::2:22")
            campo_clase.clear()
            campo_clase.send_keys(clase_pedido)
            print(f"  [OK] Clase de pedido: {clase_pedido}")
            time.sleep(0.3)
            
            # Campo 2: Organización ventas - ID: M0:46:::5:22
            print(f">> Ingresando Organización ventas: {org_ventas}")
            campo_org = self.driver.find_element(By.ID, "M0:46:::5:22")
            campo_org.clear()
            campo_org.send_keys(org_ventas)
            print(f"  [OK] Organización ventas: {org_ventas}")
            time.sleep(0.3)
            
            # Campo 3: Canal distribución - ID: M0:46:::6:22
            print(f">> Ingresando Canal distribución: {canal_dist}")
            campo_canal = self.driver.find_element(By.ID, "M0:46:::6:22")
            campo_canal.clear()
            campo_canal.send_keys(canal_dist)
            print(f"  [OK] Canal distribución: {canal_dist}")
            time.sleep(0.3)
            
            # Campo 4: Sector - ID: M0:46:::7:22
            print(f">> Ingresando Sector: {sector}")
            campo_sector = self.driver.find_element(By.ID, "M0:46:::7:22")
            campo_sector.clear()
            campo_sector.send_keys(sector)
            print(f"  [OK] Sector: {sector}")
            time.sleep(0.5)
            
            # Presionar Enter para continuar
            print(">> Presionando Enter para continuar...")
            campo_toolbar = self.driver.find_element(By.ID, "ToolbarOkCode")
            campo_toolbar.send_keys(Keys.ENTER)
            
            # Esperar a que SAP procese y recargue la página de pedido
            self.driver.switch_to.default_content()
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.frame_to_be_available_and_switch_to_it("ITSFRAME1")
                )
                self.driver.switch_to.default_content()
            except:
                time.sleep(2)
            print("  [OK] Datos organizativos completados y enviados")
            return True
            
        except Exception as e:
            # Si hay error, volver al contenido principal
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al llenar datos: {str(e)}")
            return False
    
    def _llenar_campo_por_label(self, nombre_etiqueta: str, valor: str):
        """
        Auxiliar para encontrar y llenar un campo por su label/nombre en SAP
        
        Args:
            nombre_etiqueta: Texto del label (ej: "Organización ventas")
            valor: Valor a ingresar
        """
        try:
            # En SAP NetWeaver, los campos suelen estar en inputs que están cerca del label
            # Intentamos varios XPath para encontrar el campo
            
            selectores = [
                # Busca input después del label
                f"//*[contains(text(), '{nombre_etiqueta}')]/following::input[1]",
                # Busca input en el mismo contenedor
                f"//*[contains(text(), '{nombre_etiqueta}')]/../following-sibling::*//input[1]",
                # Busca input cercano (dentro del mismo div/span)
                f"//*[contains(., '{nombre_etiqueta}')]//following-sibling::input[1]",
                # Busca todos los inputs y usa el primero que esté visible
                f"//input[@*[contains(., '{nombre_etiqueta}')]] | //input[@title[contains(., '{nombre_etiqueta}')]]",
            ]
            
            for xpath in selectores:
                try:
                    campos = self.driver.find_elements(By.XPATH, xpath)
                    if campos and len(campos) > 0:
                        for campo in campos:
                            try:
                                if campo.is_displayed():
                                    campo.clear()
                                    time.sleep(0.2)
                                    campo.send_keys(valor)
                                    print(f"  [OK] {nombre_etiqueta}: {valor}")
                                    return True
                            except:
                                continue
                except:
                    continue
            
            # Si no encontró, buscar por valor más general
            # Buscar todos los inputs y esperar que el usuario haya hecho click en el campo
            print(f"  [WARN] Campo '{nombre_etiqueta}' no encontrado automáticamente")
            print(f"    -> Asegúrate de que el campo esté visible en pantalla")
                    
        except Exception as e:
            print(f"  [WARN] Error al llenar {nombre_etiqueta}: {str(e)}")
    
    def ingresar_cedula_solicitante(self, cedula: str):
        """
        Ingresa la cédula del cliente en el campo Solicitante
        En la pantalla de "Crear Pedido Ecommerce CF"
        
        Args:
            cedula: Cédula del cliente
        """
        try:
            print(f"\n--- Ingresando cedula del cliente ---")
            print(f">> Buscando campo Solicitante...")
            
            # Cambiar al iframe si es necesario
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except:
                pass
            
            # Buscar el campo Solicitante por su ID
            campo_solicitante = None
            try:
                # Intentar por el ID específico del campo
                campo_solicitante = self.driver.find_element(By.ID, "M0:46:1:1::0:17")
                print("  [OK] Campo Solicitante encontrado por ID")
            except:
                # Si no funciona, buscar por title
                try:
                    campo_solicitante = self.driver.find_element(By.XPATH, "//input[@title='Solicitante']")
                    print("  [OK] Campo Solicitante encontrado por title")
                except:
                    print("  [ERROR] No se encontro el campo Solicitante")
                    return False
            
            # Hacer click en el campo para que aparezca la lupa
            print(">> Haciendo click en el campo Solicitante...")
            campo_solicitante.click()
            time.sleep(0.5)
            
            # En lugar de buscar la lupa, usar F4 (atajo estándar de SAP)
            print(">> Presionando F4 para abrir popup de busqueda...")
            campo_solicitante.send_keys(Keys.F4)
            time.sleep(2)
            print("[OK] Popup de busqueda abierto")
            
            # El popup "Limitar ámbito de valores" se abre
            # El campo "Conc.búsq." suele quedar enfocado automáticamente
            # Usar el elemento activo directamente
            print(">> Escribiendo cedula en campo 'Conc.busq.'...")
            
            # Primero intentar con el elemento activo (ya enfocado)
            try:
                campo_busqueda = self.driver.switch_to.active_element
                campo_busqueda.clear()
                campo_busqueda.send_keys(str(cedula))
                time.sleep(0.5)
                
                print(f"  [OK] Cedula '{cedula}' escrita en campo activo")
                
                print(">> Presionando Enter...")
                campo_busqueda.send_keys(Keys.RETURN)
                time.sleep(2)
                print("[OK] Busqueda ejecutada")
                
                # Seleccionar el solicitante: número que empieza con '11' o '22'
                print(">> Seleccionando solicitante (prefijo 11 o 22)...")
                resultado = self._seleccionar_fila_popup_por_prefijo('11')
                if resultado is None:
                    print("  [INFO] No encontrado con prefijo 11, intentando con 22...")
                    resultado = self._seleccionar_fila_popup_por_prefijo('22')
                if resultado is None:
                    raise Exception("sin solicitante valido - no se encontro cliente con prefijo 11 ni 22")
                print("[OK] Solicitante seleccionado")
                
            except Exception as ex:
                if "sin solicitante valido" in str(ex):
                    raise
                print(f"[WARN] Error con elemento activo: {str(ex)}")

            # Volver al contenido principal
            self.driver.switch_to.default_content()

            print("[OK] Cedula ingresada y busqueda activada")
            return True

        except Exception as e:
            self.driver.switch_to.default_content()
            if "sin solicitante valido" in str(e):
                raise
            print(f"[ERROR] Error al ingresar cedula: {str(e)}")
            return False

    def _seleccionar_fila_popup_por_prefijo(self, prefijo: str):
        """
        En el popup Lst.aciertos, selecciona la fila cuyo número de cliente
        empieza con el prefijo dado (ej: '11' para Solicitante, '55' para Destinatario).
        Los números de cliente están en los divs con ID patrón M1:46:::ROW:27_l.

        Returns:
            True si encontró y seleccionó la fila correcta.
            None si no pudo determinar (el llamador debe aplicar su fallback).
        """
        try:
            time.sleep(1)

            # Los números de cliente están en la columna 27 del popup (M1:46:::ROW:27_l)
            celdas_numero = self.driver.find_elements(
                By.XPATH,
                "//*[contains(@id, ':27_l') and contains(@id, 'M1:46:::')]"
            )

            if not celdas_numero:
                print(f"  [INFO] No se encontraron celdas de numero en popup, usando fallback")
                return None

            print(f"  [INFO] {len(celdas_numero)} fila(s) en popup - analizando prefijos...")

            for celda in celdas_numero:
                numero = celda.text.strip()
                print(f"  [INFO] Celda {celda.get_attribute('id')}: '{numero}'")
                if numero.startswith(prefijo):
                    print(f"  [OK] Seleccionando fila con cliente {numero} (prefijo '{prefijo}')")
                    ActionChains(self.driver).double_click(celda).perform()
                    time.sleep(2)
                    return True

            print(f"  [WARN] No se encontro fila con prefijo '{prefijo}', aplicando fallback")
            return None

        except Exception as e:
            print(f"  [WARN] Error en _seleccionar_fila_popup_por_prefijo: {str(e)}")
            return None

    def ingresar_cedula_destinatario(self, cedula: str):
        """
        Ingresa la cédula del cliente en el campo Destinat.mcía.
        (campo debajo de Solicitante) y selecciona la SEGUNDA coincidencia.
        
        Args:
            cedula: Cédula del cliente
        """
        try:
            print(f"\n--- Ingresando cedula en Destinat.mcia. ---")
            print(f">> Buscando campo Destinat.mcia...")
            
            # Primero volver al default y luego entrar al iframe limpio
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False
            
            # Buscar el campo Destinat.mcía. por su ID
            campo_destinatario = None
            ids_posibles = ["M0:46:1:1::1:17", "M0:46:1:1::0:34", "M0:46:1:2::0:17"]
            
            for id_campo in ids_posibles:
                try:
                    campo_destinatario = self.driver.find_element(By.ID, id_campo)
                    print(f"  [OK] Campo Destinat.mcia. encontrado por ID: {id_campo}")
                    break
                except:
                    print(f"  -- ID {id_campo} no encontrado")
                    continue
            
            if not campo_destinatario:
                try:
                    campo_destinatario = self.driver.find_element(By.XPATH, "//input[contains(@title,'Destinat')]")
                    print("  [OK] Campo Destinat.mcia. encontrado por title")
                except:
                    pass
            
            if not campo_destinatario:
                try:
                    campo_destinatario = self.driver.find_element(By.XPATH, "//*[contains(text(),'Destinat')]/following::input[1]")
                    print("  [OK] Campo Destinat.mcia. encontrado por label")
                except:
                    pass
            
            if not campo_destinatario:
                # Listar todos los inputs visibles para debug
                print("  [WARN] Campo no encontrado, listando inputs visibles...")
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        if inp.is_displayed():
                            inp_id = inp.get_attribute("id") or "sin-id"
                            inp_title = inp.get_attribute("title") or ""
                            inp_val = inp.get_attribute("value") or ""
                            print(f"    input: id={inp_id}, title='{inp_title}', value='{inp_val}'")
                except:
                    pass
                print("  [ERROR] No se encontro el campo Destinat.mcia.")
                self.driver.switch_to.default_content()
                return False
            
            # Click en el campo y F4
            print(">> Haciendo click en el campo Destinat.mcia...")
            campo_destinatario.click()
            time.sleep(0.5)
            
            print(">> Presionando F4 para abrir popup de busqueda...")
            campo_destinatario.send_keys(Keys.F4)
            time.sleep(2)
            print("[OK] Popup de busqueda abierto")
            
            # Escribir cedula y buscar
            print(">> Escribiendo cedula en campo 'Conc.busq.'...")
            try:
                campo_busqueda = self.driver.switch_to.active_element
                campo_busqueda.clear()
                campo_busqueda.send_keys(str(cedula))
                time.sleep(0.5)
                print(f"  [OK] Cedula '{cedula}' escrita")
                
                print(">> Presionando Enter para buscar...")
                campo_busqueda.send_keys(Keys.RETURN)
                time.sleep(3)
                print("[OK] Busqueda ejecutada")
                
                # Seleccionar el destinatario: solo el número que empieza con '55'
                print(">> Seleccionando destinatario (prefijo 55)...")
                resultado = self._seleccionar_fila_popup_por_prefijo('55')
                if resultado is None:
                    raise Exception("sin destinatario valido - no se encontro cliente con prefijo 55")
                
            except Exception as ex:
                if "sin destinatario valido" in str(ex):
                    raise
                print(f"[WARN] Error: {str(ex)}")

            # Volver al contenido principal
            self.driver.switch_to.default_content()

            print("[OK] Destinat.mcia. completado")
            return True

        except Exception as e:
            self.driver.switch_to.default_content()
            if "sin destinatario valido" in str(e):
                raise
            print(f"[ERROR] Error al ingresar destinatario: {str(e)}")
            return False

    def ingresar_numero_pedido_cliente(self, cedula: str, material: str = None):
        """
        Ingresa la referencia en el campo N° ped.cliente.
        Si se provee material, usa el formato {cedula}-{material} para que SAP
        detecte automáticamente pedidos duplicados de la misma referencia.

        Args:
            cedula: Cédula del cliente
            material: Código del primer material del pedido (opcional)
        """
        try:
            print(f"\n--- Ingresando N ped.cliente ---")

            # Construir referencia: cedula-material o solo cedula
            if material:
                referencia = f"{cedula}-{material}"
            else:
                referencia = str(cedula)
            print(f"  [INFO] Referencia a escribir: '{referencia}'")

            # Volver al default y entrar al iframe limpio
            self.driver.switch_to.default_content()
            time.sleep(1)

            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False

            # Buscar el campo N ped.cliente
            campo_pedido = None
            ids_posibles = ["M0:46:1::3:17", "M0:46:1:1::2:17", "M0:46:1:1::0:51", "M0:46:1:3::0:17"]

            for id_campo in ids_posibles:
                try:
                    campo_pedido = self.driver.find_element(By.ID, id_campo)
                    print(f"  [OK] Campo N ped.cliente encontrado por ID: {id_campo}")
                    break
                except:
                    continue

            if not campo_pedido:
                try:
                    campo_pedido = self.driver.find_element(By.XPATH, "//input[contains(@title,'ped.cliente')]")
                    print("  [OK] Campo N ped.cliente encontrado por title")
                except:
                    pass

            if not campo_pedido:
                try:
                    campo_pedido = self.driver.find_element(By.XPATH, "//*[contains(text(),'ped.cliente')]/following::input[1]")
                    print("  [OK] Campo N ped.cliente encontrado por label")
                except:
                    pass

            if not campo_pedido:
                print("  [WARN] Campo no encontrado, listando inputs visibles...")
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        if inp.is_displayed():
                            inp_id = inp.get_attribute("id") or "sin-id"
                            inp_title = inp.get_attribute("title") or ""
                            inp_val = inp.get_attribute("value") or ""
                            print(f"    input: id={inp_id}, title='{inp_title}', value='{inp_val}'")
                except:
                    pass
                print("  [ERROR] No se encontro el campo N ped.cliente")
                self.driver.switch_to.default_content()
                return False

            # Escribir la referencia en el campo
            print(f">> Escribiendo '{referencia}' en N ped.cliente...")
            campo_pedido.click()
            time.sleep(0.3)
            campo_pedido.clear()
            campo_pedido.send_keys(referencia)
            time.sleep(0.5)
            print(f"  [OK] '{referencia}' escrito en N ped.cliente")

            # Volver al contenido principal
            self.driver.switch_to.default_content()

            print("[OK] N ped.cliente completado")
            return True

        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al ingresar N ped.cliente: {str(e)}")
            return False

    def confirmar_numero_pedido_cliente(self, telefono=None):
        """
        Presiona Enter en el campo N° ped.cliente para confirmar y habilitar Material/Cantidad
        
        Args:
            telefono: Número de teléfono del cliente del Excel (opcional, ya no se usa aquí)
        """
        try:
            print(f"\n--- Confirmando N ped.cliente con Enter ---")
            
            # Volver al default y entrar al iframe limpio
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False
            
            # Buscar el campo N ped.cliente
            campo_pedido = None
            ids_posibles = ["M0:46:1::3:17", "M0:46:1:1::2:17", "M0:46:1:1::0:51", "M0:46:1:3::0:17"]
            
            for id_campo in ids_posibles:
                try:
                    campo_pedido = self.driver.find_element(By.ID, id_campo)
                    print(f"  [OK] Campo N ped.cliente encontrado por ID: {id_campo}")
                    break
                except:
                    continue
            
            if not campo_pedido:
                print("  [ERROR] No se encontro el campo N ped.cliente")
                self.driver.switch_to.default_content()
                return False
            
            # Hacer click y presionar Enter
            print(">> Presionando Enter en N ped.cliente...")
            campo_pedido.click()
            time.sleep(0.3)
            campo_pedido.send_keys(Keys.ENTER)
            time.sleep(1.5)
            print("  [OK] Enter presionado")
            
            # Volver al contenido principal
            self.driver.switch_to.default_content()
            
            print("[OK] N ped.cliente confirmado")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al confirmar N ped.cliente: {str(e)}")
            return False

    def verificar_y_corregir_pedido_duplicado(self, telefono):
        """
        Verifica si hay error de pedido duplicado después de seleccionar Pedido Ecommerce
        Si lo detecta, espera a que se desbloqueen los campos y reemplaza la cédula por el teléfono
        
        Args:
            telefono: Número de teléfono del cliente del Excel
            
        Returns:
            True si se corrigió el error o no hubo error, False si hubo problema
        """
        try:
            print(f"\n--- Verificando pedido duplicado ---")
            
            # Entrar al iframe para verificar mensaje
            self.driver.switch_to.default_content()

            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False

            # Esperar hasta 1.5s a que aparezca el mensaje de duplicado.
            # Si no aparece en ese tiempo, no hay duplicado y continuamos.
            from selenium.common.exceptions import TimeoutException
            texto_mensaje = ""
            try:
                WebDriverWait(self.driver, 1.5, poll_frequency=0.2).until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, "//span[@id='wnd[0]/sbar_msg-txt']"),
                        "ya existente en documento"
                    )
                )
                mensaje_span = self.driver.find_element(By.XPATH, "//span[@id='wnd[0]/sbar_msg-txt']")
                texto_mensaje = mensaje_span.text.strip()
                print(f"  [WARN] Pedido duplicado detectado: {texto_mensaje}")
                self.driver.switch_to.default_content()
                raise Exception(f"Pedido ya existe - referencia '{texto_mensaje}' ya tiene un pedido activo en SAP")
            except TimeoutException:
                print("  [OK] No se detectó error de pedido duplicado")
                self.driver.switch_to.default_content()
                return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al verificar pedido duplicado: {str(e)}")
            return False

    def seleccionar_modific_cantidad(self):
        """
        Selecciona 'Modific.cantidad' en el campo dropdown correspondiente
        """
        try:
            print(f"\n--- Seleccionando Modific.cantidad ---")
            
            # Volver al default y entrar al iframe limpio
            self.driver.switch_to.default_content()

            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False
            
            # Buscar el campo por ID
            campo_modific = None
            ids_posibles = ["M0:46:2:3B256:1::2:17", "M0:46:2:3B256:1::2:22"]
            
            for id_campo in ids_posibles:
                try:
                    campo_modific = self.driver.find_element(By.ID, id_campo)
                    print(f"  [OK] Campo Modific.cantidad encontrado por ID: {id_campo}")
                    break
                except:
                    continue
            
            if not campo_modific:
                print("  [ERROR] No se encontro el campo Modific.cantidad")
                print("  [DEBUG] Listando inputs disponibles...")
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs[:20]:  # Solo los primeros 20
                        if inp.is_displayed():
                            inp_id = inp.get_attribute("id") or "sin-id"
                            inp_ct = inp.get_attribute("ct") or ""
                            inp_val = inp.get_attribute("value") or ""
                            print(f"    input: id={inp_id}, ct={inp_ct}, value='{inp_val}'")
                except:
                    pass
                self.driver.switch_to.default_content()
                return False
            
            # Hacer click y escribir el valor
            print(">> Seleccionando 'Modific.cantidad'...")
            print(f"  [DEBUG] Campo encontrado - ID: {campo_modific.get_attribute('id')}")
            
            # Click simple en el campo
            campo_modific.click()
            time.sleep(0.3)
            print("  [DEBUG] Click realizado")

            campo_modific.send_keys("mod")
            time.sleep(0.3)
            print("  [DEBUG] 'mod' enviado al campo")

            valor = campo_modific.get_attribute("value")
            print(f"  [DEBUG] Valor actual en el campo: '{valor}'")

            campo_modific.send_keys(Keys.TAB)
            time.sleep(0.3)
            print("  [OK] 'mod' escrito y dropdown cerrado con TAB")
            
            # Volver al contenido principal
            self.driver.switch_to.default_content()
            
            print("[OK] Modific.cantidad completado")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al seleccionar Modific.cantidad: {str(e)}")
            return False

    def seleccionar_pedido_ecommerce(self):
        """
        Selecciona 'Pedido Ecommerce Cliente Final' en el campo de tipo de pedido
        """
        try:
            print(f"\n--- Seleccionando Pedido Ecommerce Cliente Final ---")
            
            # Volver al default y esperar a que el iframe esté disponible
            self.driver.switch_to.default_content()

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it("ITSFRAME1")
                )
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False

            # Buscar el campo por ID
            campo_pedido = None
            ids_posibles = ["M0:46:2:3B256:1::8:17", "M0:46:2:3B256:1::8:22"]

            for id_campo in ids_posibles:
                try:
                    campo_pedido = self.driver.find_element(By.ID, id_campo)
                    print(f"  [OK] Campo Pedido Ecommerce encontrado por ID: {id_campo}")
                    break
                except:
                    continue

            if not campo_pedido:
                print("  [ERROR] No se encontro el campo Pedido Ecommerce")
                self.driver.switch_to.default_content()
                return False

            # Hacer click y escribir "P"
            print(">> Seleccionando 'Pedido Ecommerce Cliente Final'...")
            campo_pedido.click()

            elemento_activo = self.driver.switch_to.active_element
            elemento_activo.send_keys("P")
            time.sleep(0.2)  # Esperar a que aparezca el dropdown

            # Bajar con flechas hasta "Pedido Ecommerce Cliente Final"
            for i in range(9):
                elemento_activo.send_keys(Keys.ARROW_DOWN)

            elemento_activo.send_keys(Keys.ENTER)
            time.sleep(0.5)  # Esperar a que SAP procese la selección
            print("  [OK] 'Pedido Ecommerce Cliente Final' seleccionado")
            
            # Verificar si apareció modal informativo y cerrarlo con ENTER
            self.verificar_y_cerrar_modal_informativo()
            
            # Volver al contenido principal
            self.driver.switch_to.default_content()
            
            print("[OK] Pedido Ecommerce completado")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            error_msg = str(e)
            
            # Re-lanzar excepciones críticas que requieren omisión de cliente
            if "hay que seleccionar detalle de venta" in error_msg:
                print(f"[CRITICAL] Re-lanzando error crítico: {error_msg}")
                raise
            
            print(f"[ERROR] Error al seleccionar Pedido Ecommerce: {error_msg}")
            return False
    
    def verificar_y_continuar_control_disponibilidad(self):
        """
        Verifica si aparece la ventana de "Control de disponibilidad" después de ingresar material
        y hace click en el botón "Continuar" si está presente
        
        Returns:
            bool: True si se hizo click en continuar o no apareció, False si hubo error
        """
        try:
            # Intentar encontrar el botón "Continuar" (puede o no aparecer)
            # Estrategia 1: Por title que contiene "Continuar sin confirmación"
            boton_continuar = None
            try:
                boton_continuar = self.driver.find_element(By.XPATH, 
                    "//div[@role='button' and contains(@title, 'Continuar sin confirmación')]")
                print("  [INFO] Detectada ventana 'Control de disponibilidad'")
            except:
                # Estrategia 2: Por lsdata que contiene 'Continuar'
                try:
                    boton_continuar = self.driver.find_element(By.XPATH, 
                        "//*[@role='button' and contains(@lsdata, \"0:'Continuar'\")]")
                    print("  [INFO] Detectada ventana 'Control de disponibilidad' (estrategia 2)")
                except:
                    # Estrategia 3: Por id que contiene btn[18]
                    try:
                        boton_continuar = self.driver.find_element(By.XPATH, 
                            "//*[contains(@id, 'btn[18]') and @role='button']")
                        print("  [INFO] Detectada ventana 'Control de disponibilidad' (estrategia 3)")
                    except:
                        # No apareció la ventana, es normal
                        return True
            
            # Si encontramos el botón, hacer click
            if boton_continuar:
                print("  >> Haciendo click en 'Continuar'...")
                boton_continuar.click()
                time.sleep(1)
                print("  [OK] Click en 'Continuar' realizado")
                return True
            
            return True
            
        except Exception as e:
            # Si hay error aquí no es crítico, el material ya se ingresó
            print(f"  [DEBUG] No se detectó ventana de control de disponibilidad: {str(e)[:100]}")
            return True

    def verificar_y_cerrar_modal_informativo(self):
        """
        Verifica si aparece un modal informativo después de seleccionar el tipo de pedido
        (por ejemplo: "Área de ventas 1100 10 94 se ha determinado de nuevo")
        y lo cierra presionando ENTER
        
        Returns:
            bool: True si se cerró el modal o no apareció, False si hubo error
        """
        try:
            # **VALIDACIÓN ESPECIAL**: Detectar modal SAPMSSY0120_1 que requiere selección de detalle de venta
            # El modal está en el documento principal, no dentro del iframe
            def _check_modal_detalle_venta():
                """Busca el modal SAPMSSY0120_1 en el doc principal y dentro del iframe"""
                # Buscar en documento principal
                try:
                    self.driver.switch_to.default_content()
                    m = self.driver.find_element(By.ID, "SAPMSSY0120_1")
                    if m.is_displayed():
                        return True
                except NoSuchElementException:
                    pass
                except Exception:
                    pass
                # Buscar por ct='PW' en documento principal (por si el ID cambia)
                try:
                    self.driver.switch_to.default_content()
                    m = self.driver.find_element(By.XPATH,
                        "//div[@ct='PW' and @role='dialog' and contains(@id,'SAPMSSY0120')]")
                    if m.is_displayed():
                        return True
                except Exception:
                    pass
                return False

            if _check_modal_detalle_venta():
                print("  [CRITICAL] Modal 'Areas de ventas para cliente' detectado (SAPMSSY0120_1)")
                print("  [INFO] Cerrando modal con boton X...")
                try:
                    self.driver.switch_to.default_content()
                    btn_cerrar = self.driver.find_element(By.ID, "SAPMSSY0120_1-close")
                    btn_cerrar.click()
                    time.sleep(1)
                    print("  [OK] Modal cerrado")
                except Exception as e_close:
                    print(f"  [WARN] No se pudo cerrar modal: {str(e_close)[:80]}")
                raise Exception("hay que seleccionar detalle de venta")
            
            # Volver al iframe para buscar modales informativos normales
            try:
                self.driver.switch_to.frame("ITSFRAME1")
            except:
                pass
            
            # Buscar el modal por diferentes estrategias
            modal_encontrado = False
            
            # Estrategia 1: Buscar por clase lsPopupWindow que es un modal
            try:
                modal = self.driver.find_element(By.CLASS_NAME, "lsPopupWindow")
                if modal.is_displayed():
                    # Verificar que no sea el modal especial SAPMSSY0120_1
                    modal_id = modal.get_attribute("id") or ""
                    if "SAPMSSY0120" in modal_id:
                        print("  [CRITICAL] Modal 'Areas de ventas para cliente' detectado en estrategia 1")
                        print("  [INFO] Cerrando modal con boton X...")
                        try:
                            btn_cerrar = self.driver.find_element(By.ID, "SAPMSSY0120_1-close")
                            btn_cerrar.click()
                            time.sleep(1)
                            print("  [OK] Modal cerrado")
                        except Exception as e_close:
                            print(f"  [WARN] No se pudo cerrar modal: {str(e_close)[:80]}")
                        raise Exception("hay que seleccionar detalle de venta")
                    print("  [INFO] Modal informativo detectado (estrategia 1)")
                    modal_encontrado = True
            except (NoSuchElementException,):
                pass
            
            # Estrategia 2: Buscar por GuiModalWindow en lsdata
            if not modal_encontrado:
                try:
                    modal = self.driver.find_element(By.XPATH, 
                        "//*[contains(@lsdata, 'GuiModalWindow') and @role='dialog']")
                    if modal.is_displayed():
                        print("  [INFO] Modal informativo detectado (estrategia 2)")
                        modal_encontrado = True
                except:
                    pass
            
            # Estrategia 3: Buscar por div con ct='PW' (Popup Window)
            if not modal_encontrado:
                try:
                    modal = self.driver.find_element(By.XPATH, 
                        "//div[@ct='PW' and contains(@class, 'lsPopupWindow')]")
                    if modal.is_displayed():
                        print("  [INFO] Modal informativo detectado (estrategia 3)")
                        modal_encontrado = True
                except:
                    pass
            
            if modal_encontrado:
                # Primero intentar hacer click en botón "Continuar (Entrada)"
                boton_continuar_entrada = None
                try:
                    # Buscar botón "Continuar (Entrada)" - aparece después de ingresar cantidad
                    boton_continuar_entrada = self.driver.find_element(By.XPATH,
                        "//*[@role='button' and contains(@title, 'Continuar (Entrada)')]")
                    if boton_continuar_entrada and boton_continuar_entrada.is_displayed():
                        print("  >> Haciendo click en botón 'Continuar (Entrada)'...")
                        boton_continuar_entrada.click()
                        time.sleep(1)
                        print("  [OK] Click en 'Continuar (Entrada)' realizado")
                        return True
                except:
                    pass
                
                # Si no encontró el botón "Continuar (Entrada)", cerrar con ENTER
                # Cerrar el modal presionando ENTER
                print("  >> Cerrando modal informativo con ENTER...")
                try:
                    # Intentar primero con el elemento activo
                    elemento_activo = self.driver.switch_to.active_element
                    elemento_activo.send_keys(Keys.RETURN)
                    time.sleep(0.8)
                    print("  [OK] Modal cerrado con ENTER")
                    return True
                except:
                    # Si falla, usar ActionChains
                    try:
                        ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                        time.sleep(0.8)
                        print("  [OK] Modal cerrado con ENTER (ActionChains)")
                        return True
                    except Exception as e:
                        print(f"  [WARN] No se pudo cerrar modal con ENTER: {str(e)[:100]}")
                        return True  # Continuar de todos modos
            else:
                # No apareció modal, es normal
                print("  [DEBUG] No se detectó modal informativo")
                return True
            
        except Exception as e:
            error_msg = str(e)
            # Re-lanzar excepciones críticas que requieren omisión de cliente
            if "hay que seleccionar detalle de venta" in error_msg:
                print(f"  [CRITICAL] Re-lanzando error crítico desde verificar_y_cerrar_modal_informativo")
                raise
            
            # Si hay error aquí no es crítico
            print(f"  [DEBUG] Error detectando modal informativo: {error_msg[:100]}")
            return True

    def ingresar_material_cantidad(self, material: str, cantidad: str):
        """
        Ingresa el material y la cantidad en las posiciones de la tabla
        Después del control de disponibilidad, SAP automáticamente posiciona el cursor
        en el siguiente campo de material vacío.
        
        Args:
            material: Código del material
            cantidad: Cantidad del material
        """
        try:
            print(f"\n--- Ingresando Material y Cantidad ---")
            print(f"  Material: {material}, Cantidad: {cantidad}")
            
            # Volver al default y entrar al iframe limpio
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False
            
            # Obtener el elemento activo (SAP posiciona el cursor automáticamente)
            # Si es el primer material, estará en el primer campo
            # Si es el segundo+, estará donde SAP dejó el cursor después del "Continuar"
            print(f">> Escribiendo Material '{material}' en elemento activo...")
            
            # Esperar hasta que el campo activo NO sea N° ped.cliente (SAP desbloqueando)
            max_espera = 10
            for intento_espera in range(max_espera):
                time.sleep(1)
                elemento_activo = self.driver.switch_to.active_element
                try:
                    elemento_id = elemento_activo.get_attribute('id') or 'sin-id'
                except:
                    elemento_id = 'sin-id'
                
                # Si el campo activo ya no es N° ped.cliente, los campos están desbloqueados
                if 'M0:46:1::3:17' not in elemento_id:
                    print(f"  [OK] Campos desbloqueados en intento {intento_espera + 1} (activo: {elemento_id})")
                    break
                else:
                    print(f"  [WAIT] Intento {intento_espera + 1}/{max_espera} - Campos aun bloqueados (activo: {elemento_id})")
                    if intento_espera == max_espera - 1:
                        print(f"  [WARN] Campos no se desbloquearon tras {max_espera}s, intentando continuar...")
            
            # Re-obtener elemento activo
            elemento_activo = self.driver.switch_to.active_element
            try:
                elemento_id = elemento_activo.get_attribute('id') or 'sin-id'
                print(f"  [DEBUG] Elemento activo final: {elemento_id}")
            except:
                print(f"  [DEBUG] No se pudo obtener ID del elemento activo")
            
            # Limpiar el campo (por seguridad)
            try:
                elemento_activo.clear()
            except:
                pass
            
            # Seleccionar todo y escribir el material
            elemento_activo.send_keys(Keys.CONTROL + 'a')
            time.sleep(0.1)
            elemento_activo.send_keys(material)
            time.sleep(0.5)
            print(f"  [OK] Material '{material}' escrito")
            
            # Mover al campo de cantidad con TAB
            print(f">> Moviendo al campo Cantidad con TAB...")
            elemento_activo.send_keys(Keys.TAB)
            time.sleep(0.5)
            
            # Escribir la cantidad en el nuevo elemento activo
            elemento_activo = self.driver.switch_to.active_element
            
            try:
                elemento_id = elemento_activo.get_attribute('id') or 'sin-id'
                print(f"  [DEBUG] Campo cantidad: {elemento_id}")
            except:
                pass
            
            # Limpiar campo de cantidad
            try:
                elemento_activo.clear()
            except:
                pass
            
            elemento_activo.send_keys(Keys.CONTROL + 'a')
            time.sleep(0.1)
            elemento_activo.send_keys(cantidad)
            time.sleep(0.5)
            print(f"  [OK] Cantidad '{cantidad}' escrita")
            
            # Presionar ENTER para confirmar la fila
            print(f">> Confirmando fila con ENTER...")
            elemento_activo.send_keys(Keys.ENTER)
            print(f"  [OK] ENTER presionado, esperando respuesta de SAP...")
            
            # Esperar a que SAP procese
            time.sleep(2)
            
            # Verificar si apareció ventana de "Control de disponibilidad" y hacer click en Continuar
            print(f"  [INFO] Verificando si aparece control de disponibilidad...")
            self.verificar_y_continuar_control_disponibilidad()
            
            # Verificar si aparece modal informativo (incluyendo "Continuar (Entrada)")
            print(f"  [INFO] Verificando si aparece modal informativo...")
            self.verificar_y_cerrar_modal_informativo()
            
            # Esperar adicional después del control de disponibilidad
            # SAP posiciona automáticamente el cursor en el siguiente campo
            time.sleep(1)
            
            # Verificar si hay mensajes de error
            hay_error = False
            texto_mensaje = ""
            
            for intento in range(3):  # Intentar 3 veces con pausas
                time.sleep(0.8)
                
                try:
                    mensaje_span = self.driver.find_element(By.XPATH, "//span[@id='wnd[0]/sbar_msg-txt']")
                    texto_mensaje = mensaje_span.text.strip()
                    
                    if texto_mensaje:
                        print(f"  [DEBUG] Mensaje SAP encontrado en intento {intento + 1}: '{texto_mensaje}'")
                        
                        # Verificar si es un mensaje de error
                        if ("Bloqueo" in texto_mensaje or 
                            "status" in texto_mensaje or 
                            "Error" in texto_mensaje or 
                            "error" in texto_mensaje or
                            "no está previsto" in texto_mensaje or
                            "no esta previsto" in texto_mensaje):
                            print(f"  [ERROR] {texto_mensaje}")
                            print(f"  [CRITICAL] Material {material} tiene error/bloqueo. Omitiendo cliente")
                            
                            # Detectar si es un bloqueo específico
                            if "Bloqueo" in texto_mensaje or "bloqueado" in texto_mensaje.lower():
                                error_msg = f"Cliente bloqueado - Material {material} bloqueado: {texto_mensaje[:100]}"
                            else:
                                error_msg = f"Material {material} no puede ser procesado: {texto_mensaje[:100]}"
                            
                            self.driver.switch_to.default_content()
                            raise Exception(error_msg)
                        else:
                            # Es un mensaje informativo
                            print(f"  [INFO] Mensaje SAP (informativo): {texto_mensaje}")
                            break
                except Exception as ex_msg:
                    # Re-lanzar si es un error de bloqueo que acabamos de crear
                    if "bloqueado" in str(ex_msg).lower() or "no puede ser procesado" in str(ex_msg):
                        raise
                    pass
            
            # Si no hay error, material procesado correctamente
            if not hay_error:
                if not texto_mensaje:
                    print(f"  [DEBUG] No se detectó mensaje (material procesado OK)")
                
                self.driver.switch_to.default_content()
                print(f"[OK] Material '{material}' y Cantidad '{cantidad}' ingresados correctamente")
                return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            error_str = str(e)
            # Re-lanzar errores críticos de bloqueo para que se propaguen al main
            if "bloqueado" in error_str.lower() or "no puede ser procesado" in error_str:
                raise
            print(f"[ERROR] Error al ingresar Material y Cantidad: {error_str}")
            import traceback
            traceback.print_exc()
            return False
    
    def volver_al_primer_material(self, num_flechas: int, material_objetivo: str = None):
        """
        Regresa al primer material ingresado y hace doble click en ese campo.
        Estrategia: Ctrl+Home para ir al inicio de la tabla, luego doble click
        en el primer input de material que tenga un valor escrito.
        """
        try:
            self.driver.switch_to.default_content()
            time.sleep(0.2)
            self.driver.switch_to.frame("ITSFRAME1")
            time.sleep(0.5)

            # Paso 1: Enviar Ctrl+Home desde el elemento activo para subir al inicio
            print("  [INFO] Enviando Ctrl+Home para subir al inicio de la tabla...")
            try:
                elemento = self.driver.switch_to.active_element
                elemento.send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(0.8)
            except Exception as e:
                print(f"  [WARN] Ctrl+Home fallo: {str(e)[:80]}")

            # Paso 2: Buscar el primer input de material que tenga valor
            print("  [INFO] Buscando el primer campo de material con valor...")
            campos_mabnr = self.driver.find_elements(
                By.XPATH,
                "//input[contains(@lsdata, 'MABNR')]"
            )
            print(f"  [DEBUG] Campos MABNR encontrados: {len(campos_mabnr)}")

            primer_campo = None
            for campo in campos_mabnr:
                try:
                    valor = (campo.get_attribute("value") or "").strip()
                    if valor:
                        primer_campo = campo
                        campo_id = campo.get_attribute("id") or "sin-id"
                        print(f"  [OK] Primer campo con valor '{valor}': {campo_id}")
                        break
                except Exception:
                    continue

            if not primer_campo:
                print("  [WARN] No se encontro ningun campo de material con valor")
                self.driver.switch_to.default_content()
                return False

            # Paso 3: Re-buscar el elemento justo antes del click (evita stale element)
            # porque SAP puede haber regenerado el DOM
            campo_id_guardado = primer_campo.get_attribute("id") or ""
            valor_guardado = (primer_campo.get_attribute("value") or "").strip()
            
            time.sleep(0.3)  # Pequeña pausa antes de re-buscar
            
            # Re-buscar por ID si se guardó
            primer_campo = None
            if campo_id_guardado:
                try:
                    primer_campo = self.driver.find_element(By.ID, campo_id_guardado)
                    print(f"  [INFO] Campo re-encontrado por ID: {campo_id_guardado}")
                except Exception:
                    pass
            
            # Si no funciona por ID, re-buscar por valor
            if not primer_campo:
                try:
                    campos_mabnr = self.driver.find_elements(
                        By.XPATH,
                        "//input[contains(@lsdata, 'MABNR')]"
                    )
                    for campo in campos_mabnr:
                        try:
                            valor = (campo.get_attribute("value") or "").strip()
                            if valor == valor_guardado:
                                primer_campo = campo
                                print(f"  [INFO] Campo re-encontrado por valor: {valor}")
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
            
            if not primer_campo:
                print("  [WARN] No se pudo re-encontrar el campo antes del click")
                self.driver.switch_to.default_content()
                return False

            # Paso 4: Doble click en ese primer campo
            try:
                ActionChains(self.driver).move_to_element(primer_campo).double_click(primer_campo).perform()
                time.sleep(0.5)
                print("  [OK] Doble click en primer material realizado")
            except Exception as e:
                print(f"  [WARN] Error en doble click: {str(e)[:100]}, reinentando...")
                time.sleep(0.5)
                try:
                    primer_campo.click()
                    time.sleep(0.2)
                    primer_campo.click()
                    print("  [OK] Doble click realizado con dos clicks separados")
                except Exception:
                    print(f"  [ERROR] No se pudo hacer doble click")
                    self.driver.switch_to.default_content()
                    return False

            self.driver.switch_to.default_content()
            return True

        except Exception as e:
            print(f"[ERROR] volver_al_primer_material: {str(e)[:200]}")
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
            return False
    
    def hacer_click_condiciones(self):
        """
        Hace click en la pestaña 'Condiciones' para continuar con el proceso
        """
        try:
            print(f"\n--- Haciendo click en pestaña Condiciones ---")
            
            # Volver al default y entrar al iframe limpio
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False
            
            # Buscar el div de la pestaña Condiciones
            tab_condiciones = None
            
            # Intentar por ID
            try:
                tab_condiciones = self.driver.find_element(By.ID, "M0:46:2::0:4-title")
                print("  [OK] Pestaña Condiciones encontrada por ID")
            except:
                pass
            
            if not tab_condiciones:
                # Intentar por texto y role="tab"
                try:
                    tab_condiciones = self.driver.find_element(By.XPATH, 
                        "//div[@role='tab' and contains(text(), 'Condiciones')]")
                    print("  [OK] Pestaña Condiciones encontrada por XPath")
                except:
                    pass
            
            if not tab_condiciones:
                print("  [ERROR] No se encontró la pestaña Condiciones")
                self.driver.switch_to.default_content()
                return False
            
            # Hacer click en la pestaña
            print(">> Haciendo click en Condiciones...")
            tab_condiciones.click()
            time.sleep(0.5)
            print("  [OK] Click en Condiciones realizado")
            
            # Volver al contenido principal
            self.driver.switch_to.default_content()
            
            print("[OK] Pestaña Condiciones seleccionada")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al hacer click en Condiciones: {str(e)}")
            return False
    
    def hacer_click_campo_condiciones(self):
        """
        Hace click en el campo de condiciones donde se ingresará el valor del portal
        """
        try:
            print(f"\n--- Haciendo click en campo de condiciones ---")

            self.driver.switch_to.default_content()

            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [ERROR] No se pudo cambiar al iframe: {str(eframe)}")
                return False

            campo_condicion = None
            
            # Intentar por XPath que contenga KOMV-KBETR (campo de condiciones)
            try:
                campo_condicion = self.driver.find_element(By.XPATH, 
                    "//input[@ct='CBS' and contains(@lsdata, 'KOMV-KBETR') and @inputmode='numeric']")
                print("  [OK] Campo de condiciones encontrado por XPath KOMV-KBETR")
            except:
                pass
            
            if not campo_condicion:
                # Intentar por patrón de ID en tabla
                try:
                    campo_condicion = self.driver.find_element(By.XPATH, 
                        "//input[@ct='CBS' and @inputmode='numeric' and contains(@id, 'tbl')]")
                    print(f"  [OK] Campo de condiciones encontrado por patrón de ID")
                except:
                    pass
            
            if not campo_condicion:
                print("  [ERROR] No se encontró el campo de condiciones")
                self.driver.switch_to.default_content()
                return False
            
            # Hacer click en el campo
            print(">> Haciendo click en campo de condiciones...")
            campo_condicion.click()
            time.sleep(0.5)
            print("  [OK] Click en campo de condiciones realizado")
            
            # Dejar el iframe activo para que el siguiente paso pueda escribir
            # No volver al contenido principal todavía
            
            print("[OK] Campo de condiciones activado")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al hacer click en campo de condiciones: {str(e)}")
            return False
    
    def ingresar_valor_condiciones(self, valor: str):
        """
        Ingresa un valor en el campo de condiciones de SAP
        
        Args:
            valor: El valor a ingresar (sin formato, solo números)
            
        Returns:
            True si se ingresó correctamente, False en caso de error
        """
        try:
            print(f"[INFO] Ingresando valor en campo de condiciones: {valor}")
            
            # Asegurarse de estar en el iframe correcto
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("ITSFRAME1")
            
            # Hacer scroll hacia arriba en la tabla de condiciones por si quedó
            # posicionada abajo (ej. después de ingresar flete manual)
            try:
                activo = self.driver.switch_to.active_element
                activo.send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(0.5)
            except:
                pass
            
            # Función helper para encontrar el campo
            def encontrar_campo():
                # Estrategia 1: Por ID con patrón flexible
                try:
                    campo = self.driver.find_element(
                        By.XPATH,
                        "//*[contains(@id, '[5,4]_c') and @inputmode='numeric']"
                    )
                    return campo
                except:
                    pass
                
                # Estrategia 2: Por lsdata que contiene KOMV-KBETR
                try:
                    campo = self.driver.find_element(
                        By.XPATH,
                        "//*[contains(@lsdata, 'KOMV-KBETR') and @inputmode='numeric']"
                    )
                    return campo
                except:
                    pass
                
                # Estrategia 3: Por role=textbox
                try:
                    campo = self.driver.find_element(
                        By.XPATH,
                        "//span[@role='textbox' and @inputmode='numeric' and contains(@lsdata, 'KOMV-KBETR')]"
                    )
                    return campo
                except:
                    pass
                
                return None
            
            # Buscar el campo inicial
            campo_condiciones = encontrar_campo()
            if not campo_condiciones:
                raise Exception("No se pudo encontrar el campo de condiciones")
            
            campo_id = campo_condiciones.get_attribute('id')
            print(f"  [OK] Campo encontrado: {campo_id}")
            
            # Hacer scroll al campo
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_condiciones)

            # Hacer click en el campo
            try:
                campo_condiciones.click()
                print("  [OK] Click en campo realizado")
            except:
                self.driver.execute_script("arguments[0].click();", campo_condiciones)
                print("  [OK] Click en campo realizado con JavaScript")
            
            # Re-encontrar el campo después del click (puede haber cambiado el DOM)
            campo_condiciones = encontrar_campo()
            if not campo_condiciones:
                raise Exception("Campo no encontrado después del click")
            
            # Intentar ingresar el valor con múltiples métodos
            ingreso_exitoso = False
            
            # Método 1: send_keys directo
            try:
                campo_condiciones.clear()
                campo_condiciones.send_keys(valor)
                print(f"  [OK] Valor '{valor}' ingresado con send_keys")
                ingreso_exitoso = True
            except Exception as e1:
                print(f"  [WARN] send_keys falló: {str(e1)}")
                
                # Método 2: JavaScript setAttribute + dispatchEvent
                try:
                    # Re-encontrar el campo por si acaso
                    campo_condiciones = encontrar_campo()
                    if campo_condiciones:
                        # Establecer el valor con JavaScript
                        self.driver.execute_script(f"arguments[0].value = '{valor}';", campo_condiciones)
                        # Disparar evento input
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", campo_condiciones)
                        # Disparar evento change
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", campo_condiciones)
                        print(f"  [OK] Valor '{valor}' ingresado con JavaScript")
                        ingreso_exitoso = True
                except Exception as e2:
                    print(f"  [ERROR] JavaScript setValue falló: {str(e2)}")
            
            if not ingreso_exitoso:
                raise Exception("No se pudo ingresar el valor con ningún método")

            # Presionar Enter para confirmar (re-encontrar el campo una vez más)
            try:
                campo_condiciones = encontrar_campo()
                if campo_condiciones:
                    campo_condiciones.send_keys(Keys.ENTER)
                    print("  [OK] Enter presionado para confirmar")
                else:
                    # Si no se puede re-encontrar, usar TAB como alternativa
                    ActionChains(self.driver).send_keys(Keys.TAB).perform()
                    print("  [OK] TAB presionado como alternativa")
            except:
                # Como último recurso, enviar TAB
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                print("  [OK] TAB presionado (fallback)")

            print(f"  [OK] Valor '{valor}' ingresado en campo de condiciones")
            return True
            
        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"[ERROR] Error al ingresar valor en condiciones: {str(e)}")
            return False
    
    def _cerrar_alerta_portal(self, max_espera=5):
        """
        Espera hasta max_espera segundos por la alerta SAP UI5 del portal dealer y la cierra.
        Usa la API interna de SAP UI5 (firePress/close) porque click() DOM no funciona.
        Retorna True si encontró y cerró el diálogo, False si no había alerta.
        """
        for intento in range(max_espera):
            try:
                result = self.driver.execute_script("""
                    try {
                        var core = sap.ui.getCore();
                        // Estrategia 1: botón OK fijo de SAP MessageBox
                        var btn = core.byId('__mbox-btn-0');
                        if (btn) { btn.firePress(); return 'btn-pressed'; }
                        // Estrategia 2: buscar cualquier alertdialog abierto y cerrarlo
                        var dialogs = document.querySelectorAll('[role="alertdialog"]');
                        for (var i = 0; i < dialogs.length; i++) {
                            var sapD = core.byId(dialogs[i].id);
                            if (sapD && sapD.isOpen && sapD.isOpen()) {
                                sapD.close();
                                return 'dialog-closed:' + dialogs[i].id;
                            }
                        }
                        return 'no-dialog';
                    } catch(e) {
                        return 'error:' + e.message;
                    }
                """)
                if result and str(result) not in ('no-dialog', 'null') and not str(result).startswith('error'):
                    print(f"  [PORTAL] Alerta cerrada ({result})")
                    time.sleep(0.5)
                    return True
            except Exception as e:
                print(f"  [DEBUG] _cerrar_alerta_portal excepcion: {str(e)[:80]}")
            time.sleep(1)
        return False

    def detectar_codigo_reemplazante_portal(self):
        """
        Detecta si existe un modal con código reemplazante en el portal del dealer
        El modal aparece cuando se busca un material que tiene código reemplazante
        
        Returns:
            str: Código reemplazante si existe, None si no aparece el modal
        """
        try:
            print("  [PORTAL] Buscando modal de código reemplazante...")
            
            # Esperar más tiempo para que aparezca el modal si existe
            time.sleep(2)
            
            # Intentar múltiples estrategias para encontrar el span del mensaje
            mensaje_span = None
            texto_mensaje = ""
            
            # Estrategia 1: Buscar por texto "reemplazante" o "reemplazan"
            try:
                mensaje_span = self.driver.find_element(By.XPATH, 
                    "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reemplazante') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reemplazan')]")
                texto_mensaje = mensaje_span.text.strip()
                print(f"  [PORTAL] Modal encontrado (estrategia 1): {texto_mensaje}")
            except:
                pass
            
            # Estrategia 2: Buscar por clase sapMText y verificar texto
            if not mensaje_span:
                try:
                    spans_texto = self.driver.find_elements(By.CLASS_NAME, "sapMText")
                    for span in spans_texto:
                        texto = span.text.strip()
                        if "reemplazante" in texto.lower() or "reemplazan" in texto.lower():
                            mensaje_span = span
                            texto_mensaje = texto
                            print(f"  [PORTAL] Modal encontrado (estrategia 2): {texto_mensaje}")
                            break
                except:
                    pass
            
            # Estrategia 3: Buscar por atributo data-sap-ui que contenga "text"
            if not mensaje_span:
                try:
                    spans_sap = self.driver.find_elements(By.XPATH, "//span[@data-sap-ui]")
                    for span in spans_sap:
                        texto = span.text.strip()
                        if "reemplazante" in texto.lower() or "reemplazan" in texto.lower():
                            mensaje_span = span
                            texto_mensaje = texto
                            print(f"  [PORTAL] Modal encontrado (estrategia 3): {texto_mensaje}")
                            break
                except:
                    pass
            
            # Estrategia 4: Buscar cualquier span visible que contenga dígitos y "material"
            if not mensaje_span:
                try:
                    spans_todos = self.driver.find_elements(By.TAG_NAME, "span")
                    for span in spans_todos:
                        if span.is_displayed():
                            texto = span.text.strip()
                            if "material" in texto.lower() and re.search(r'\d{7,}', texto):
                                mensaje_span = span
                                texto_mensaje = texto
                                print(f"  [PORTAL] Modal encontrado (estrategia 4): {texto_mensaje}")
                                break
                except:
                    pass
            
            if not mensaje_span or not texto_mensaje:
                print("  [PORTAL] No se detectó modal de código reemplazante")
                return None
            
            # Extraer el número del mensaje usando regex más flexible
            # Buscar cualquier número de 7+ dígitos en el mensaje
            match = re.search(r'(\d{7,})', texto_mensaje)
            if match:
                codigo_reemplazante = match.group(1)
                print(f"  [PORTAL] [OK] Codigo reemplazante extraido: {codigo_reemplazante}")
                
                # Buscar y hacer click en el boton OK/confirmacion
                try:
                    boton_ok = None
                    
                    # Estrategia 0: Buscar por ID __mbox-btn-0 (usuario lo menciona)
                    try:
                        boton_ok = self.driver.find_element(By.ID, "__mbox-btn-0")
                        print("  [PORTAL] Boton encontrado por ID __mbox-btn-0 (estrategia 0)")
                    except:
                        pass
                    
                    # Estrategia 1: Buscar por texto "OK" en bdi
                    if not boton_ok:
                        try:
                            boton_ok = self.driver.find_element(By.XPATH, "//bdi[text()='OK']")
                            print("  [PORTAL] Boton OK encontrado (estrategia 1)")
                        except:
                            pass
                    
                    # Estrategia 2: Buscar button que contenga bdi con OK
                    if not boton_ok:
                        try:
                            boton_ok = self.driver.find_element(By.XPATH, "//button[.//bdi[text()='OK']]")
                            print("  [PORTAL] Boton OK encontrado (estrategia 2)")
                        except:
                            pass
                    
                    # Estrategia 3: Buscar por clase de boton en modal
                    if not boton_ok:
                        try:
                            botones = self.driver.find_elements(By.CLASS_NAME, "sapMBtn")
                            for btn in botones:
                                if "OK" in btn.text or btn.get_attribute("title") == "OK":
                                    boton_ok = btn
                                    print("  [PORTAL] Boton OK encontrado (estrategia 3)")
                                    break
                        except:
                            pass
                    
                    if boton_ok:
                        # Hacer click en el boton
                        time.sleep(0.3)
                        try:
                            boton_ok.click()
                            print("  [PORTAL] [OK] Click en boton realizado")
                        except:
                            # Si falla, intentar con JavaScript
                            self.driver.execute_script("arguments[0].click();", boton_ok)
                            print("  [PORTAL] [OK] Click en boton realizado (JavaScript)")
                        time.sleep(1)
                        
                        return codigo_reemplazante
                    else:
                        print(f"  [WARN] No se encontro boton, intentando ENTER")
                        ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                        time.sleep(1)
                        return codigo_reemplazante
                        
                except Exception as e_btn:
                    print(f"  [ERROR] Error haciendo click: {str(e_btn)[:150]}")
                    # Aun asi retornar el codigo para que se use
                    return codigo_reemplazante
            else:
                print(f"  [WARN] No se pudo extraer código del mensaje: {texto_mensaje}")
                return None
                
        except Exception as e:
            print(f"  [DEBUG] Error detectando código reemplazante en portal: {str(e)[:150]}")
            return None
    
    def abrir_portal_socios(self, cedula: str, material: str):
        """
        Abre el portal de socios en una nueva pestaña y hace login
        Si el portal ya está abierto de una búsqueda anterior, lo reutiliza
        
        Args:
            cedula: Cédula del cliente para buscar en el portal
            material: Número de referencia del repuesto (material)
            
        Returns:
            El valor obtenido del portal, o None si hay error
        """
        try:
            print(f"\n--- Buscando material en Portal de Socios ---")
            
            # Guardar la ventana actual de SAP
            ventana_sap = self.driver.current_window_handle
            print(f"  [OK] Ventana SAP guardada: {ventana_sap}")
            
            # Verificar si ya existe una ventana del portal abierta
            ventana_portal = None
            portal_recien_abierto = False
            url_portal = "https://portal-socios-auteco-portal-approuter.cfapps.us10.hana.ondemand.com"
            
            for ventana in self.driver.window_handles:
                if ventana != ventana_sap:
                    self.driver.switch_to.window(ventana)
                    if url_portal in self.driver.current_url:
                        ventana_portal = ventana
                        print(f"  [OK] Portal ya abierto detectado, reutilizando...")
                        break
            
            # Si no hay portal abierto, abrir uno nuevo con login completo
            if not ventana_portal:
                portal_recien_abierto = True
                # Volver a SAP primero
                self.driver.switch_to.window(ventana_sap)
                
                # Abrir nueva pestaña con el portal
                print(f">> Abriendo nueva pestaña con el portal...")
                self.driver.execute_script(f"window.open('{url_portal}/autecoPortalApp/index.html', '_blank');")
                time.sleep(1)  # Esperar a que abra la nueva pestaña
                
                # Cambiar a la nueva pestaña
                ventanas = self.driver.window_handles
                for ventana in ventanas:
                    if ventana != ventana_sap:
                        self.driver.switch_to.window(ventana)
                        print(f"  [OK] Cambiado a pestaña del portal")
                        break
                
                # Esperar a que cargue el formulario de login
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "j_username"))
                    )
                except:
                    time.sleep(3)
                print(f"  [OK] Portal abierto, esperando formulario de login...")
                
                # Buscar el campo de correo
                try:
                    campo_email = self.driver.find_element(By.ID, "j_username")
                    print("  [OK] Campo de correo encontrado")
                    
                    # Escribir el correo
                    campo_email.click()
                    time.sleep(0.3)
                    campo_email.clear()
                    campo_email.send_keys("daniela.munoz@andesbpo.com")
                    time.sleep(0.5)
                    print("  [OK] Correo ingresado")
                except Exception as e:
                    print(f"  [ERROR] No se pudo ingresar el correo: {str(e)}")
                    return None
                
                # Buscar el campo de contraseña
                try:
                    campo_password = self.driver.find_element(By.ID, "j_password")
                    print("  [OK] Campo de contraseña encontrado")
                    
                    # Escribir la contraseña
                    campo_password.click()
                    time.sleep(0.3)
                    campo_password.clear()
                    campo_password.send_keys("Andes2025.")
                    time.sleep(0.5)
                    print("  [OK] Contraseña ingresada")
                except Exception as e:
                    print(f"  [ERROR] No se pudo ingresar la contraseña: {str(e)}")
                    return None
                
                # Hacer click en el botón de iniciar sesión
                try:
                    boton_login = self.driver.find_element(By.ID, "logOnFormSubmit")
                    print("  [OK] Botón de login encontrado")
                    
                    boton_login.click()
                    # Esperar a que cargue la página principal del portal
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.ID, "__button0-img"))
                        )
                    except:
                        time.sleep(3)
                    print("  [OK] Login realizado, esperando carga de la página principal...")
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click en botón de login: {str(e)}")
                    return None
                
                # Hacer click en la imagen de Auteco para continuar
                try:
                    imagen_auteco = self.driver.find_element(By.ID, "__button0-img")
                    print("  [OK] Imagen de Auteco encontrada")
                    
                    # Hacer click en la imagen (o en su contenedor button)
                    try:
                        # Intentar hacer click en el botón padre de la imagen
                        boton_auteco = imagen_auteco.find_element(By.XPATH, "..")
                        boton_auteco.click()
                        print("  [OK] Click en botón de Auteco realizado")
                    except:
                        # Si no funciona el padre, hacer click directo en la imagen
                        imagen_auteco.click()
                        print("  [OK] Click en imagen de Auteco realizado")
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"  [WARN] No se pudo hacer click en imagen de Auteco (ignorado): {str(e)[:80]}")
                    time.sleep(1)
            
            # Si el portal fue recién abierto, navegar por Pedidos -> Paso 2 -> Paso 3
            # Si el portal ya estaba abierto, saltamos directamente a la búsqueda del material
            if portal_recien_abierto:
                # Hacer click en el menú "Pedidos"
                try:
                    span_pedidos = self.driver.find_element(By.XPATH, 
                        "//span[@class='sapMText sapTntNavLIText sapMTextNoWrap' and text()='Pedidos']")
                    print("  [OK] Menú 'Pedidos' encontrado")
                    
                    span_pedidos.click()
                    time.sleep(1)
                    print("  [OK] Click en 'Pedidos' realizado")
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click en 'Pedidos': {str(e)}")
                    return None
                
                # Hacer click en el botón (puede ser un botón de acción o filtro)
                try:
                    boton_bdi = self.driver.find_element(By.ID, "__button2-BDI-content")
                    print("  [OK] Botón de acción encontrado")
                    
                    # Intentar hacer click directamente
                    try:
                        boton_bdi.click()
                        print("  [OK] Click en botón realizado")
                    except:
                        # Si no funciona, intentar en el botón padre
                        boton_padre = boton_bdi.find_element(By.XPATH, "..")
                        boton_padre.click()
                        print("  [OK] Click en botón padre realizado")
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click en botón: {str(e)}")
                    return None

                # Escribir "R" en el campo de ventas y presionar Enter
                try:
                    campo_ventas = self.driver.find_element(By.ID, "container-PortalApp---Pedidos--comboVentas-inner")
                    print("  [OK] Campo de ventas encontrado")

                    campo_ventas.click()
                    time.sleep(0.3)
                    campo_ventas.clear()
                    campo_ventas.send_keys("R")
                    time.sleep(0.3)
                    print("  [OK] Letra 'R' escrita en campo de ventas")

                    campo_ventas.send_keys(Keys.ENTER)
                    # Esperar a que el indicador de carga desaparezca
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.invisibility_of_element_located((By.ID, "container-PortalApp---Pedidos--page-busyIndicator"))
                        )
                    except:
                        time.sleep(3)
                    print("  [OK] Enter presionado en campo de ventas, esperando carga completa...")
                except Exception as e:
                    print(f"  [ERROR] No se pudo escribir en campo de ventas: {str(e)}")
                    return None
                
                # Buscar por cédula en el campo de búsqueda
                try:
                    # Esperar explícitamente a que el busy indicator desaparezca
                    print("  [INFO] Esperando a que desaparezca el indicador de carga...")
                    try:
                        WebDriverWait(self.driver, 15).until(
                            EC.invisibility_of_element_located((By.ID, "container-PortalApp---Pedidos--page-busyIndicator"))
                        )
                        print("  [OK] Indicador de carga desaparecido")
                    except:
                        print("  [WARN] Timeout esperando indicador, continuando...")
                    
                    # Esperar a que el campo de búsqueda sea clickeable
                    campo_busqueda = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "container-PortalApp---Pedidos--searchField-I"))
                    )
                    print("  [OK] Campo de búsqueda encontrado y clickeable")
                    
                    campo_busqueda.click()
                    time.sleep(0.3)
                    campo_busqueda.clear()
                    campo_busqueda.send_keys("550005491")
                    time.sleep(1.5)  # Esperar a que se filtren los resultados
                    print("  [OK] Valor '550005491' escrito en campo de búsqueda")
                except Exception as e:
                    print(f"  [ERROR] No se pudo escribir en campo de búsqueda: {str(e)}")
                    return None
                
                # Hacer doble click en la celda del resultado (TODO MOTOS SAS PTO BOYACA)
                try:
                    # Buscar la celda por el texto contenido o por la clase
                    celda_resultado = None
                    
                    # Intentar buscar por XPath que contenga el texto específico
                    try:
                        celda_resultado = self.driver.find_element(By.XPATH, 
                            "//td[contains(@class, 'sapMListTblCell')]//span[contains(@class, 'sapMText')]")
                        print(f"  [OK] Celda de resultado encontrada")
                    except:
                        # Si no encuentra por texto, buscar por la primera celda visible en la tabla
                        celda_resultado = self.driver.find_element(By.XPATH, 
                            "//td[contains(@class, 'sapMListTblCell') and contains(@id, '_cell0')]")
                        print(f"  [OK] Celda de resultado encontrada (por ID)")
                    
                    # Hacer doble click en la celda
                    ActionChains(self.driver).double_click(celda_resultado).perform()
                    print("  [OK] Doble click en resultado realizado, esperando carga...")
                    # Esperar a que cargue el detalle del pedido (botón Paso 2 debe aparecer)
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.ID, "container-PortalApp---Pedidos--WS_TipoVenta-nextButton"))
                        )
                    except:
                        time.sleep(4)
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer doble click en resultado: {str(e)}")
                    return None
                
                # Hacer click en el botón "Paso 2"
                try:
                    print("  [INFO] Buscando botón 'Paso 2'...")
                    time.sleep(1)  # Pausa adicional antes de buscar
                    
                    # Intentar encontrar el botón directamente por su ID completo
                    boton_paso2 = None
                    try:
                        # Probar con diferentes IDs posibles del botón
                        posibles_ids = [
                            "container-PortalApp---Pedidos--WS_TipoVenta-nextButton",
                            "container-PortalApp---Pedidos--WS_TipoVenta-nextButton-inner"
                        ]
                        for btn_id in posibles_ids:
                            try:
                                boton_paso2 = self.driver.find_element(By.ID, btn_id)
                                print(f"  [OK] Botón 'Paso 2' encontrado por ID: {btn_id}")
                                break
                            except:
                                continue
                    except:
                        pass
                    
                    # Si no encontró el botón por ID, buscar por el BDI y navegar al ancestro
                    if not boton_paso2:
                        elemento_bdi = None
                        try:
                            elemento_bdi = self.driver.find_element(By.XPATH, "//bdi[contains(text(), 'Paso 2')]")
                            print("  [OK] Elemento BDI 'Paso 2' encontrado por texto")
                        except:
                            elemento_bdi = self.driver.find_element(By.ID, "container-PortalApp---Pedidos--WS_TipoVenta-nextButton-BDI-content")
                            print("  [OK] Elemento BDI 'Paso 2' encontrado por ID")
                        
                        # Buscar el botón padre
                        boton_paso2 = elemento_bdi.find_element(By.XPATH, "./ancestor::button")
                        print(f"  [OK] Botón padre encontrado vía BDI: {boton_paso2.get_attribute('id')}")
                    
                    # Verificar propiedades del botón
                    print(f"  [DEBUG] ID del botón: {boton_paso2.get_attribute('id')}")
                    print(f"  [DEBUG] Botón visible: {boton_paso2.is_displayed()}")
                    print(f"  [DEBUG] Botón habilitado: {boton_paso2.is_enabled()}")
                    print(f"  [DEBUG] Clases del botón: {boton_paso2.get_attribute('class')}")
                    
                    # Hacer scroll al botón
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_paso2)
                    time.sleep(1)
                    
                    # Intentar múltiples métodos de click
                    click_exitoso = False
                    
                    # Método 1: ActionChains click
                    try:
                        ActionChains(self.driver).move_to_element(boton_paso2).click().perform()
                        print("  [OK] Click en 'Paso 2' con ActionChains")
                        click_exitoso = True
                    except Exception as e1:
                        print(f"  [WARN] ActionChains falló: {str(e1)}")
                        
                        # Método 2: Click normal
                        try:
                            boton_paso2.click()
                            print("  [OK] Click normal en 'Paso 2'")
                            click_exitoso = True
                        except Exception as e2:
                            print(f"  [WARN] Click normal falló: {str(e2)}")
                            
                            # Método 3: JavaScript click
                            try:
                                self.driver.execute_script("arguments[0].click();", boton_paso2)
                                print("  [OK] Click JavaScript en 'Paso 2'")
                                click_exitoso = True
                            except Exception as e3:
                                print(f"  [ERROR] JavaScript click falló: {str(e3)}")
                    
                    if not click_exitoso:
                        raise Exception("No se pudo hacer click en 'Paso 2' con ningún método")

                    time.sleep(1)  # Pausa mínima tras click
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click en botón 'Paso 2': {str(e)}")
                    return None
                
                # Hacer click en el botón "Paso 3"
                try:
                    print("  [INFO] Buscando botón 'Paso 3'...")
                    time.sleep(1)  # Pausa adicional antes de buscar
                    
                    # Intentar encontrar el botón directamente por su ID completo
                    boton_paso3 = None
                    try:
                        # Probar con diferentes IDs posibles del botón
                        posibles_ids = [
                            "container-PortalApp---Pedidos--WS_DatosGrles-nextButton",
                            "container-PortalApp---Pedidos--WS_DatosGrles-nextButton-inner"
                        ]
                        for btn_id in posibles_ids:
                            try:
                                boton_paso3 = self.driver.find_element(By.ID, btn_id)
                                print(f"  [OK] Botón 'Paso 3' encontrado por ID: {btn_id}")
                                break
                            except:
                                continue
                    except:
                        pass
                    
                    # Si no encontró el botón por ID, buscar por el BDI y navegar al ancestro
                    if not boton_paso3:
                        # Esperar hasta 15 segundos intentando encontrar el elemento BDI
                        elemento_bdi = None
                        for intento in range(15):
                            try:
                                # Estrategia 1: Por texto
                                elemento_bdi = self.driver.find_element(By.XPATH, "//bdi[contains(text(), 'Paso 3')]")
                                print("  [OK] Elemento BDI 'Paso 3' encontrado por texto")
                                break
                            except:
                                pass
                            
                            try:
                                # Estrategia 2: Por ID del BDI
                                elemento_bdi = self.driver.find_element(By.ID, "container-PortalApp---Pedidos--WS_DatosGrles-nextButton-BDI-content")
                                print("  [OK] Elemento BDI 'Paso 3' encontrado por ID")
                                break
                            except:
                                pass
                            
                            time.sleep(1)
                        
                        if not elemento_bdi:
                            raise Exception("No se pudo encontrar el elemento BDI Paso 3 después de 15 segundos")
                        
                        # Buscar el botón padre
                        boton_paso3 = elemento_bdi.find_element(By.XPATH, "./ancestor::button")
                        print(f"  [OK] Botón padre encontrado vía BDI: {boton_paso3.get_attribute('id')}")
                    
                    # Verificar propiedades del botón
                    print(f"  [DEBUG] ID del botón: {boton_paso3.get_attribute('id')}")
                    print(f"  [DEBUG] Botón visible: {boton_paso3.is_displayed()}")
                    print(f"  [DEBUG] Botón habilitado: {boton_paso3.is_enabled()}")
                    print(f"  [DEBUG] Clases del botón: {boton_paso3.get_attribute('class')}")
                    
                    # Hacer scroll al botón
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_paso3)
                    time.sleep(1)
                    
                    # Intentar múltiples métodos de click
                    click_exitoso = False
                    
                    # Método 1: ActionChains click
                    try:
                        ActionChains(self.driver).move_to_element(boton_paso3).click().perform()
                        print("  [OK] Click en 'Paso 3' con ActionChains")
                        click_exitoso = True
                    except Exception as e1:
                        print(f"  [WARN] ActionChains falló: {str(e1)}")
                        
                        # Método 2: Click normal
                        try:
                            boton_paso3.click()
                            print("  [OK] Click normal en 'Paso 3'")
                            click_exitoso = True
                        except Exception as e2:
                            print(f"  [WARN] Click normal falló: {str(e2)}")
                            
                            # Método 3: JavaScript click
                            try:
                                self.driver.execute_script("arguments[0].click();", boton_paso3)
                                print("  [OK] Click JavaScript en 'Paso 3'")
                                click_exitoso = True
                            except Exception as e3:
                                print(f"  [ERROR] JavaScript click falló: {str(e3)}")
                    
                    if not click_exitoso:
                        raise Exception("No se pudo hacer click en 'Paso 3' con ningún método")
                    
                    print("  [INFO] Esperando a que cargue la pantalla del Paso 3...")
                    time.sleep(8)  # Esperar más tiempo a que cargue completamente
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click en botón 'Paso 3': {str(e)}")
                    return None
            else:
                # Portal ya estaba abierto, reutilizando sesión
                print("  [INFO] Portal ya abierto, saltando navegación y reutilizando sesión...")
            
            # Buscar el material en el input de búsqueda (esto se ejecuta siempre)
            try:
                print(f"  [INFO] Buscando material '{material}' en el portal...")
                
                # Intentar múltiples estrategias para encontrar el input
                input_busqueda_mat = None
                
                # Estrategia 1: Por ID completo
                print("  [INFO] Intentando buscar input por ID...")
                for intento in range(10):
                    try:
                        input_busqueda_mat = self.driver.find_element(By.ID, "container-PortalApp---Pedidos--searchFieldMat-I")
                        print("  [OK] Input de búsqueda encontrado por ID")
                        break
                    except:
                        print(f"  [DEBUG] Intento {intento+1}/10 - Input no encontrado aún, esperando...")
                        time.sleep(1)
                
                # Estrategia 2: Por atributos del input
                if not input_busqueda_mat:
                    print("  [INFO] Intentando buscar input por atributos...")
                    try:
                        input_busqueda_mat = self.driver.find_element(
                            By.XPATH,
                            "//input[@type='search' and @placeholder='Buscar en la lista']"
                        )
                        print("  [OK] Input de búsqueda encontrado por placeholder")
                    except:
                        pass
                
                # Estrategia 3: Por clase sapMSFI
                if not input_busqueda_mat:
                    print("  [INFO] Intentando buscar input por clase...")
                    try:
                        inputs_search = self.driver.find_elements(By.CLASS_NAME, "sapMSFI")
                        if len(inputs_search) > 0:
                            # Buscar el que está visible y en la sección de materiales
                            for inp in inputs_search:
                                if inp.is_displayed() and 'Mat' in inp.get_attribute('id'):
                                    input_busqueda_mat = inp
                                    print(f"  [OK] Input encontrado por clase: {input_busqueda_mat.get_attribute('id')}")
                                    break
                    except:
                        pass
                
                if not input_busqueda_mat:
                    raise Exception("No se pudo encontrar el input de búsqueda de material con ninguna estrategia")
                
                # Hacer scroll al input
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_busqueda_mat)
                time.sleep(1)
                
                # Verificar que el input esté visible y habilitado
                print(f"  [DEBUG] Input visible: {input_busqueda_mat.is_displayed()}")
                print(f"  [DEBUG] Input habilitado: {input_busqueda_mat.is_enabled()}")
                
                # Intentar escribir con múltiples métodos
                escritura_exitosa = False
                error_intercepciones = False
                
                # Método 1: Click y send_keys normal
                try:
                    input_busqueda_mat.click()
                    time.sleep(0.5)
                    input_busqueda_mat.clear()
                    time.sleep(0.3)
                    input_busqueda_mat.send_keys(material)
                    print(f"  [OK] Material '{material}' escrito con método normal")
                    escritura_exitosa = True
                except Exception as e1:
                    print(f"  [WARN] Método normal falló: {str(e1)}")
                    
                    # Verificar si es por intercepciones
                    if "element click intercepted" in str(e1):
                        error_intercepciones = True
                        print(f"  [WARN] Error de intercepciones de elemento detectado")
                    
                    # Método 2: JavaScript setValue
                    try:
                        self.driver.execute_script(f"arguments[0].value = '{material}';", input_busqueda_mat)
                        # Disparar evento input para que se procese el cambio
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_busqueda_mat)
                        print(f"  [OK] Material '{material}' escrito con JavaScript")
                        escritura_exitosa = True
                    except Exception as e2:
                        print(f"  [ERROR] JavaScript setValue falló: {str(e2)}")
                
                if not escritura_exitosa:
                    if error_intercepciones:
                        raise Exception("element click intercepted: No se pudo hacer click en campo de búsqueda del portal")
                    else:
                        raise Exception("No se pudo escribir el material con ningún método")
                
                print(f"  [OK] Material '{material}' escrito en búsqueda")
                time.sleep(2)  # Esperar a que cargue el resultado
                
            except Exception as e:
                print(f"  [ERROR] No se pudo buscar el material: {str(e)}")
                return None
            
            # Hacer click en el span que muestra el código
            try:
                print(f"  [INFO] Buscando resultado con código del material...")
                
                # Buscar el span que contiene "CODIGO: [material]"
                span_codigo = self.driver.find_element(By.XPATH, f"//span[contains(text(), 'CODIGO: {material}')]")
                print(f"  [OK] Span con código encontrado")
                
                # Hacer scroll y click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_codigo)
                time.sleep(0.5)
                
                # Intentar click
                try:
                    span_codigo.click()
                    print("  [OK] Click en span del código realizado")
                except:
                    # Si falla, usar JavaScript
                    self.driver.execute_script("arguments[0].click();", span_codigo)
                    print("  [OK] Click en span del código realizado con JavaScript")
                
                time.sleep(3)  # Esperar a que cargue el detalle o aparezca modal

                # Cerrar alerta de error del portal si apareció, y reintentar click si fue necesario
                if self._cerrar_alerta_portal():
                    print(f"  [PORTAL] Reintentando click en material tras cerrar alerta...")
                    try:
                        span_codigo.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", span_codigo)
                    time.sleep(3)
                    self._cerrar_alerta_portal()  # Por si vuelve a aparecer

                # AQUÍ es donde aparece el modal de código reemplazante
                print(f"  [INFO] Verificando si aparece modal de código reemplazante...")
                codigo_reemplazante = self.detectar_codigo_reemplazante_portal()
                
                if codigo_reemplazante:
                    # Hay un código reemplazante - reintentar búsqueda con el nuevo código
                    print(f"\n>> ==========================================")
                    print(f">> PORTAL: Material reemplazante detectado")
                    print(f">> Material Original: {material}")
                    print(f">> Material Reemplazante: {codigo_reemplazante}")
                    print(f">> ==========================================")
                    print(f"   Volviendo a buscar y haciendo click en el material reemplazante...")
                    
                    # Actualizar la variable material
                    material = codigo_reemplazante
                    
                    # Buscar el material reemplazante
                    try:
                        # Buscar el input de búsqueda nuevamente
                        input_busqueda_reintentar = None
                        try:
                            input_busqueda_reintentar = self.driver.find_element(By.ID, "container-PortalApp---Pedidos--searchFieldMat-I")
                        except:
                            try:
                                input_busqueda_reintentar = self.driver.find_element(By.XPATH, "//input[@type='search' and @placeholder='Buscar en la lista']")
                            except:
                                pass
                        
                        if not input_busqueda_reintentar:
                            print(f"  [ERROR] No se pudo encontrar input de búsqueda para reintentar")
                            return None
                        
                        # Scroll al input
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_busqueda_reintentar)
                        time.sleep(0.8)
                        
                        # Intentar hacer click - si falla por elemento interceptado, usar JavaScript
                        try:
                            input_busqueda_reintentar.click()
                            print(f"  [OK] Click en campo de busqueda realizado")
                        except Exception as e_click:
                            if "element click intercepted" in str(e_click):
                                print(f"  [WARN] Click interceptado, usando JavaScript para enfoque...")
                                self.driver.execute_script("arguments[0].focus();", input_busqueda_reintentar)
                                time.sleep(0.3)
                            else:
                                raise
                        
                        time.sleep(0.3)
                        
                        # Limpiar campo con JavaScript para evitar problemas
                        self.driver.execute_script("arguments[0].value = '';", input_busqueda_reintentar)
                        time.sleep(0.2)
                        
                        # Simular eventos de change para que SAP se entere
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_busqueda_reintentar)
                        time.sleep(0.3)
                        
                        print(f"   Escribiendo codigo reemplazante: {material}")
                        try:
                            input_busqueda_reintentar.send_keys(material)
                            print(f"  [OK] Material reemplazante escrito")
                        except:
                            self.driver.execute_script(f"arguments[0].value = '{material}';", input_busqueda_reintentar)
                            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_busqueda_reintentar)
                            print(f"  [OK] Material reemplazante escrito con JavaScript")
                        
                        time.sleep(2)  # Esperar a que cargue el resultado
                        
                        # Buscar y hacer click en el nuevo span con el código reemplazante
                        print(f"  [INFO] Buscando resultado con código reemplazante...")
                        span_codigo_nuevo = self.driver.find_element(By.XPATH, f"//span[contains(text(), 'CODIGO: {material}')]")
                        print(f"  [OK] Span con código reemplazante encontrado")
                        
                        # Scroll y click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_codigo_nuevo)
                        time.sleep(0.5)
                        
                        try:
                            span_codigo_nuevo.click()
                            print("  [OK] Click en span del código reemplazante realizado")
                        except:
                            self.driver.execute_script("arguments[0].click();", span_codigo_nuevo)
                            print("  [OK] Click en span del código reemplazante realizado con JavaScript")
                        
                        time.sleep(3)  # Esperar a que cargue el detalle

                        # Cerrar alerta de error del portal si apareció
                        self._cerrar_alerta_portal()

                        # Verificar si hay otro modal (poco probable)
                        codigo_reemplazante_2do = self.detectar_codigo_reemplazante_portal()
                        if codigo_reemplazante_2do:
                            print(f"  [WARN] Segundo código reemplazante detectado: {codigo_reemplazante_2do}")
                            print(f"  [NOTE] Usando el primer reemplazo: {material}")
                        
                    except Exception as e_reintentar:
                        print(f"  [ERROR] Error durante reintento con material reemplazante: {str(e_reintentar)}")
                        return None
                else:
                    print(f"  [INFO] No se detectó modal, continuando con material original: {material}")
                
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer click en el código: {str(e)}")
                return None
            
            # Extraer los valores de precio sin IVA y con IVA
            try:
                # Cerrar alerta por si apareció durante la carga del detalle
                self._cerrar_alerta_portal()
                print(f"  [INFO] Extrayendo precios del portal...")

                def _buscar_precios():
                    spans = self.driver.find_elements(By.CLASS_NAME, "sapMText")
                    sin_iva = None
                    con_iva = None
                    for span in spans:
                        texto = span.text.strip()
                        if "COP" in texto and "$" in texto:
                            if sin_iva is None:
                                sin_iva = texto
                                print(f"  [OK] Precio sin IVA encontrado: {sin_iva}")
                            elif con_iva is None:
                                con_iva = texto
                                print(f"  [OK] Precio con IVA encontrado: {con_iva}")
                                break
                    return sin_iva, con_iva

                precio_sin_iva_texto, precio_con_iva_texto = _buscar_precios()

                # Si no encontró precio, puede ser que la alerta bloqueó la carga — cerrar y reintentar
                if not precio_sin_iva_texto:
                    print(f"  [WARN] Precio no encontrado, verificando alerta y reintentando...")
                    self._cerrar_alerta_portal(max_espera=8)
                    time.sleep(2)
                    precio_sin_iva_texto, precio_con_iva_texto = _buscar_precios()

                if not precio_sin_iva_texto:
                    raise Exception("No se pudo encontrar el precio sin IVA")
                
                if not precio_con_iva_texto:
                    print(f"  [WARN] No se encontró precio con IVA, continuando sin validación")
                
                # Limpiar el valor sin IVA (eliminar $, puntos, COP, espacios)
                import re
                precio_sin_iva_limpio = re.sub(r'[^\d]', '', precio_sin_iva_texto)
                print(f"  [OK] Precio sin IVA limpio: {precio_sin_iva_limpio}")
                
                # Si tenemos precio con IVA, validar que sea mayor a 150000
                if precio_con_iva_texto:
                    precio_con_iva_limpio = re.sub(r'[^\d]', '', precio_con_iva_texto)
                    precio_con_iva_valor = int(precio_con_iva_limpio)
                    print(f"  [INFO] Validando precio con IVA: {precio_con_iva_valor} COP")
                    
                    if precio_con_iva_valor < 150000:
                        print(f"  [WARN] Precio con IVA ({precio_con_iva_valor}) es menor a 150,000 COP")
                        print(f"  [WARN] Se requiere proceso adicional (no implementado aún)")
                    else:
                        print(f"  [OK] Precio con IVA ({precio_con_iva_valor}) es válido (>= 150,000)")
                
            except Exception as e:
                print(f"  [ERROR] No se pudieron extraer los precios: {str(e)}")
                return None
            
            # Volver a SAP pero SIN cerrar el portal (para reutilizarlo en siguiente material)
            try:
                print(f"  [INFO] Volviendo a SAP (portal permanece abierto)...")
                self.driver.switch_to.window(ventana_sap)  # Volver a SAP
                
                # Asegurarse de estar en el iframe correcto de SAP
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame("ITSFRAME1")
                
                print(f"  [OK] Vuelta a SAP completada")
            except Exception as e:
                print(f"  [WARN] Error al volver a SAP: {str(e)}")
                # Intentar volver a SAP de todas formas
                try:
                    self.driver.switch_to.window(ventana_sap)
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame("ITSFRAME1")
                except:
                    pass
            
            print("[OK] Portal de Socios procesado exitosamente")
            print(f"[INFO] Valor sin IVA: {precio_sin_iva_limpio}")
            print(f"[INFO] Valor con IVA: {precio_con_iva_valor}")
            
            # Retornar diccionario con información completa
            return {
                'precio_sin_iva': precio_sin_iva_limpio,
                'precio_con_iva': precio_con_iva_valor if precio_con_iva_texto else None,
                'es_mayor_150k': precio_con_iva_valor >= 150000 if precio_con_iva_texto else True
            }
            
        except Exception as e:
            print(f"[ERROR] Error al abrir portal de socios: {str(e)}")
            # Intentar volver a la ventana de SAP
            try:
                self.driver.switch_to.window(ventana_sap)
            except:
                pass
            return None
    
    def hacer_click_posicion_siguiente(self):
        """
        Hace click en el botón 'Posición siguiente' (Mayús+F7)
        para moverse al siguiente material en SAP VA01
        
        Returns:
            bool: True si el click fue exitoso, False si no
        """
        try:
            print("\n[INFO] Haciendo click en botón 'Posición siguiente'...")
            
            # Asegurarse de estar en el iframe
            self.driver.switch_to.default_content()
            time.sleep(0.3)
            self.driver.switch_to.frame("ITSFRAME1")
            time.sleep(0.5)
            
            boton = None
            # Estrategia 1: Buscar por título "Posición siguiente"
            for xpath in [
                "//div[@role='button' and contains(@title, 'siguiente')]",
                "//div[@role='button' and contains(@id, 'btn[19]')]",
                "//div[@role='button' and contains(@lsdata, 'Posici')]",
                "//div[contains(@lsdata, 'SHIFT_F7') and @role='button']",
            ]:
                try:
                    boton = self.driver.find_element(By.XPATH, xpath)
                    print(f"  [OK] Botón encontrado con: {xpath}")
                    break
                except:
                    continue
            
            if not boton:
                # Fallback: enviar Shift+F7 directamente
                print("  [WARN] Botón no encontrado, enviando Shift+F7...")
                elemento_activo = self.driver.switch_to.active_element
                elemento_activo.send_keys(Keys.SHIFT + Keys.F7)
                time.sleep(2)
                self.driver.switch_to.default_content()
                print("[OK] Shift+F7 enviado para posición siguiente")
                return True
            
            # Hacer scroll al botón
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
            time.sleep(0.5)
            
            # Intentar click
            try:
                boton.click()
                print("  [OK] Click realizado en botón 'Posición siguiente'")
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", boton)
                    print("  [OK] Click con JavaScript realizado en botón 'Posición siguiente'")
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click: {str(e)[:100]}")
                    self.driver.switch_to.default_content()
                    return False
            
            # Esperar a que cambie la posición
            time.sleep(2)
            
            self.driver.switch_to.default_content()
            print("[OK] Posición siguiente activada correctamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al hacer click en 'Posición siguiente': {str(e)[:200]}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def obtener_tarifa_flete(self, ciudad):
        """
        Obtiene la tarifa de flete sin IVA para una ciudad.
        Usa el diccionario interno _TARIFAS_FLETE (no depende de archivos externos).

        Valores posibles sin IVA:
          8.823  -> REGIONAL  (zonas metropolitanas: Bello, Caldas, etc.)
          13.445 -> NACIONAL  (ciudades principales: Bogotá, Cali, Barranquilla...)
          28.991 -> REEXPEDICIÓN (resto del país)

        Args:
            ciudad (str): Nombre de la ciudad (acepta tildes, mayúsculas/minúsculas, con/sin depto)

        Returns:
            int: Valor del flete sin IVA, None si la ciudad no está en el listado
        """
        import re
        import unicodedata
        from config.tarifas_flete import _TARIFAS_FLETE

        try:
            print(f"\n[INFO] Buscando tarifa de flete para ciudad: {ciudad}")

            def norm(texto):
                nfd = unicodedata.normalize('NFD', str(texto).strip().upper())
                return unicodedata.normalize('NFC', ''.join(
                    c for c in nfd if unicodedata.category(c) != 'Mn'
                ))

            ciudad_norm = norm(ciudad)
            # Versión sin la abreviatura de departamento entre paréntesis
            ciudad_base = re.sub(r'\s*\([^)]*\)', '', ciudad_norm).strip()

            # Pre-procesamiento: si el municipio incluye el nombre del departamento al final
            # (ej: "SAN JOSE DE CUCUTA NORTE DE SANTANDER"), intentar extraer solo la ciudad.
            _DEPTOS = [
                'NORTE DE SANTANDER', 'VALLE DEL CAUCA', 'SAN ANDRES', 'LA GUAJIRA',
                'ANTIOQUIA', 'ATLANTICO', 'BOLIVAR', 'BOYACA', 'CALDAS', 'CAQUETA',
                'CASANARE', 'CAUCA', 'CESAR', 'CHOCO', 'CORDOBA', 'CUNDINAMARCA',
                'GUAINIA', 'GUAVIARE', 'HUILA', 'MAGDALENA', 'META', 'NARINO',
                'PUTUMAYO', 'QUINDIO', 'RISARALDA', 'SANTANDER', 'SUCRE', 'TOLIMA',
                'VAUPES', 'VICHADA', 'AMAZONAS', 'ARAUCA', 'BOGOTA',
            ]
            ciudad_solo = ciudad_base
            for depto in _DEPTOS:
                if ciudad_base.endswith(' ' + depto):
                    ciudad_solo = ciudad_base[:-(len(depto) + 1)].strip()
                    break

            # Estrategia 1: clave exacta con nombre completo
            tarifa = _TARIFAS_FLETE.get(ciudad_norm)
            if tarifa:
                print(f"  [OK] Match exacto: '{ciudad_norm}' -> {tarifa:,} sin IVA")
                return tarifa

            # Estrategia 2: clave exacta sin departamento en paréntesis
            tarifa = _TARIFAS_FLETE.get(ciudad_base)
            if tarifa:
                print(f"  [OK] Match sin depto (paréntesis): '{ciudad_base}' -> {tarifa:,} sin IVA")
                return tarifa

            # Estrategia 3: clave exacta con solo el municipio (sin departamento al final)
            if ciudad_solo != ciudad_base:
                tarifa = _TARIFAS_FLETE.get(ciudad_solo)
                if tarifa:
                    print(f"  [OK] Match ciudad sola: '{ciudad_solo}' -> {tarifa:,} sin IVA")
                    return tarifa

            # Estrategia 4: alguna clave del dict empieza por el nombre de ciudad
            for clave, valor in _TARIFAS_FLETE.items():
                if clave.startswith(ciudad_solo) or clave.startswith(ciudad_base):
                    print(f"  [OK] Match prefijo: '{clave}' -> {valor:,} sin IVA")
                    return valor

            # Estrategia 5: alguna clave del dict contenida en ciudad_solo
            # Ordenar por longitud desc para preferir coincidencias más específicas
            for clave, valor in sorted(_TARIFAS_FLETE.items(), key=lambda x: len(x[0]), reverse=True):
                if len(clave) > 4 and clave in ciudad_solo:
                    print(f"  [OK] Match inverso (ciudad_solo): '{clave}' en '{ciudad_solo}' -> {valor:,} sin IVA")
                    return valor

            # Estrategia 6: palabra larga (>4 chars) de ciudad_solo contenida en alguna clave
            palabras = sorted([p for p in ciudad_solo.split() if len(p) > 4], key=len, reverse=True)
            for palabra in palabras:
                for clave, valor in _TARIFAS_FLETE.items():
                    if palabra in clave:
                        print(f"  [OK] Match parcial '{palabra}' en '{clave}' -> {valor:,} sin IVA")
                        return valor

            print(f"  [WARN] Ciudad '{ciudad}' no encontrada en el listado de tarifas")
            return None

        except Exception as e:
            print(f"  [ERROR] Error al buscar tarifa de flete: {str(e)}")
            return None
    
    def hacer_click_campo_flete_manual(self):
        """
        Hace scroll en la tabla de condiciones de SAP hasta encontrar la fila ZFLM
        y hace click en el campo de importe (KWERT) de esa fila.
        SAP requiere scroll interno de tabla, no scrollIntoView del navegador.
        """
        try:
            print("\n[INFO] Buscando campo 'Flete manual' (ZFLM) en condiciones...")
            
            # Asegurarse de estar en el iframe
            self.driver.switch_to.default_content()
            time.sleep(0.3)
            self.driver.switch_to.frame("ITSFRAME1")
            
            # Primero intentar encontrar ZFLM directamente (puede estar visible)
            campo = self._encontrar_campo_zflm()
            
            if not campo:
                # No está visible, hay que hacer scroll en la tabla de condiciones
                print("  [INFO] ZFLM no visible, haciendo scroll en la tabla de condiciones...")
                
                # Buscar cualquier celda visible en la tabla de condiciones para hacer scroll
                celda_tabla = None
                try:
                    # Buscar una celda en la tabla de condiciones (cualquier campo KWERT visible)
                    celda_tabla = self.driver.find_element(By.XPATH, 
                        "//*[contains(@lsdata, 'KOMV-KSCHL') or contains(@lsdata, 'KOMV-KWERT')]")
                except:
                    pass
                
                if celda_tabla:
                    # Click en la celda para dar foco a la tabla
                    try:
                        celda_tabla.click()
                        time.sleep(0.3)
                    except:
                        pass
                
                # Hacer scroll con Page Down dentro de la tabla (hasta 5 intentos)
                for intento in range(5):
                    # Enviar Page Down al elemento activo
                    elemento_activo = self.driver.switch_to.active_element
                    elemento_activo.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.8)
                    
                    # Verificar si ahora ZFLM es visible
                    campo = self._encontrar_campo_zflm()
                    if campo:
                        print(f"  [OK] ZFLM encontrado despues de {intento + 1} Page Down(s)")
                        break
                
                if not campo:
                    print("  [ERROR] No se encontro ZFLM despues de hacer scroll")
                    self.driver.switch_to.default_content()
                    return False
            else:
                print("  [OK] Campo ZFLM ya visible")
            
            # Hacer click en el campo de importe de ZFLM
            try:
                campo.click()
                time.sleep(0.5)
                print("  [OK] Click en campo 'Flete manual' realizado")
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", campo)
                    time.sleep(0.5)
                    print("  [OK] Click en campo 'Flete manual' realizado (JS)")
                except Exception as e:
                    print(f"  [ERROR] No se pudo hacer click: {str(e)[:100]}")
                    self.driver.switch_to.default_content()
                    return False
            
            self.driver.switch_to.default_content()
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al buscar campo 'Flete manual': {str(e)[:200]}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def _encontrar_texto_flete_manual(self):
        """
        Busca el SPAN con texto 'Flete manual' en la tabla de condiciones.
        Al hacer doble click abre la pantalla de detalle.
        """
        # Estrategia 1: span con lsdata que contiene 'Flete\x20manual'
        try:
            return self.driver.find_element(By.XPATH,
                "//span[contains(@lsdata, 'Flete') and contains(@lsdata, 'manual') and @role='textbox']")
        except:
            pass
        
        # Estrategia 2: span con texto exacto
        try:
            return self.driver.find_element(By.XPATH,
                "//span[@role='textbox'][normalize-space()='Flete manual']")
        except:
            pass
        
        # Estrategia 3: span en fila que contiene ZFLM
        try:
            return self.driver.find_element(By.XPATH,
                "//tr[.//text()[contains(., 'ZFLM')]]//span[@role='textbox'][contains(., 'Flete')]")
        except:
            pass
        
        # Estrategia 4: td con texto 'Flete manual' -> span hijo
        try:
            return self.driver.find_element(By.XPATH,
                "//td[normalize-space()='Flete manual']//span[@role='textbox']")
        except:
            pass
        
        return None
    
    def scroll_click_y_escribir_flete(self, valor):
        """
        Hace scroll hasta encontrar 'Flete manual', doble click en el texto
        para abrir pantalla de detalle, escribe el valor en 'Valor condicion'
        y presiona Atras (F3) para volver.
        """
        try:
            print(f"\n[INFO] Scroll + click + escribir flete manual: {valor}")
            valor_str = str(valor)
            
            # Entrar al iframe
            self.driver.switch_to.default_content()
            time.sleep(0.3)
            self.driver.switch_to.frame("ITSFRAME1")
            time.sleep(0.5)
            
            # === PASO 1: Encontrar el texto 'Flete manual' en la tabla ===
            span_flete = self._encontrar_texto_flete_manual()
            
            if not span_flete:
                print("  [INFO] Flete manual no visible, haciendo scroll...")
                
                # Dar foco a la tabla de condiciones
                try:
                    celda_tabla = self.driver.find_element(By.XPATH, 
                        "//*[contains(@lsdata, 'KOMV-KSCHL') or contains(@lsdata, 'KOMV-KWERT')]")
                    celda_tabla.click()
                    time.sleep(0.3)
                except:
                    pass
                
                # Page Down hasta encontrar
                for intento in range(5):
                    elemento_activo = self.driver.switch_to.active_element
                    elemento_activo.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.8)
                    
                    span_flete = self._encontrar_texto_flete_manual()
                    if span_flete:
                        print(f"  [OK] Flete manual encontrado tras {intento + 1} Page Down(s)")
                        break
                
                if not span_flete:
                    print("  [ERROR] No se encontro 'Flete manual' tras scroll")
                    self.driver.switch_to.default_content()
                    return False
            else:
                print("  [OK] Flete manual ya visible")
            
            # === PASO 2: Doble click en el texto para abrir detalle ===
            span_id = span_flete.get_attribute('id') or 'sin-id'
            print(f"  [DEBUG] Span encontrado: id={span_id}")
            
            ActionChains(self.driver).double_click(span_flete).perform()
            time.sleep(1.5)
            print("  [OK] Doble click en 'Flete manual' => pantalla de detalle")
            
            # === PASO 3: Escribir valor en campo 'Valor condicion' ===
            campo_valor = None
            # Buscar el input de valor de condicion
            for xpath in [
                "//input[@id='M0:46:::6:20']",
                "//input[contains(@lsdata, 'KOMV-KWERT')]",
                "//input[@title='Valor de la condición' or @title='Valor condición']",
                "//input[@inputmode='numeric' and contains(@lsdata, 'KWERT')]",
            ]:
                try:
                    campo_valor = self.driver.find_element(By.XPATH, xpath)
                    print(f"  [OK] Campo valor encontrado con: {xpath}")
                    break
                except:
                    continue
            
            if not campo_valor:
                print("  [ERROR] No se encontro campo 'Valor condicion'")
                self.driver.switch_to.default_content()
                return False
            
            # Click para activar el campo
            campo_valor.click()
            time.sleep(0.3)
            
            # Escribir valor
            elemento_activo = self.driver.switch_to.active_element
            elemento_activo.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            elemento_activo.send_keys(Keys.DELETE)
            time.sleep(0.2)
            elemento_activo.send_keys(valor_str)
            time.sleep(0.3)
            print(f"  [OK] Valor '{valor_str}' escrito en campo")
            
            # === PASO 4: Presionar Atras (F3) para volver ===
            time.sleep(0.5)
            # F3 en SAP funciona como Enter en el botón Atrás
            elemento_activo = self.driver.switch_to.active_element
            elemento_activo.send_keys(Keys.ENTER)
            time.sleep(0.5)
            
            # Click en boton Atras
            btn_atras = None
            for xpath in [
                "//div[@id='M0:36::btn[3]']",
                "//div[@title='Atrás (F3)']",
                "//div[contains(@lsdata, 'F3') and @role='button']",
            ]:
                try:
                    btn_atras = self.driver.find_element(By.XPATH, xpath)
                    break
                except:
                    continue
            
            if btn_atras:
                btn_atras.click()
                time.sleep(1)
                print("  [OK] Click en Atras (F3) => volviendo a condiciones")
            else:
                # Fallback: enviar F3 directamente
                elemento_activo = self.driver.switch_to.active_element
                elemento_activo.send_keys(Keys.F3)
                time.sleep(1)
                print("  [OK] F3 enviado => volviendo a condiciones")
            
            self.driver.switch_to.default_content()
            print(f"[OK] Flete manual {valor_str} ingresado correctamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] scroll_click_y_escribir_flete: {str(e)[:200]}")
            import traceback
            traceback.print_exc()
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def ingresar_valor_flete_manual(self, valor):
        """
        Ingresa un valor en el campo 'Flete manual' (ZFLM).
        Se llama DESPUÉS de hacer_click_campo_flete_manual() que ya hizo scroll.
        """
        try:
            print(f"\n[INFO] Ingresando valor {valor} en campo 'Flete manual'...")
            
            valor_str = str(valor)
            
            # Asegurarse de estar en el iframe correcto
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("ITSFRAME1")
            time.sleep(0.5)
            
            # Buscar el campo ZFLM
            campo = self._encontrar_campo_zflm()
            
            if not campo:
                print("  [ERROR] No se pudo encontrar el campo 'Flete manual'")
                self.driver.switch_to.default_content()
                return False
            
            campo_id = campo.get_attribute('id') or 'sin-id'
            print(f"  [DEBUG] Campo flete encontrado: {campo_id}")
            
            # Doble click en el campo para activarlo
            try:
                ActionChains(self.driver).double_click(campo).perform()
                time.sleep(0.5)
                print(f"  [OK] Doble click en campo {campo_id}")
            except:
                self.driver.execute_script("arguments[0].click();", campo)
                time.sleep(0.5)
                print(f"  [OK] Click en campo {campo_id} (JS)")
            
            # Re-encontrar después del click (SAP puede regenerar el DOM)
            campo = self._encontrar_campo_zflm()
            if campo:
                campo_id_nuevo = campo.get_attribute('id') or 'sin-id'
                if campo_id_nuevo != campo_id:
                    print(f"  [DEBUG] Campo regenerado: {campo_id_nuevo}")
                    ActionChains(self.driver).double_click(campo).perform()
                    time.sleep(0.5)
            
            # Usar active element para escribir
            elemento_activo = self.driver.switch_to.active_element
            activo_id = elemento_activo.get_attribute('id') or 'sin-id'
            print(f"  [DEBUG] Elemento activo: {activo_id}")
            
            # Verificar que el activo es el campo correcto (contiene [7,8])
            if '[7,8]' not in activo_id and campo:
                print(f"  [WARN] Active element no es el campo flete, forzando click...")
                campo.click()
                time.sleep(0.3)
                elemento_activo = self.driver.switch_to.active_element
                activo_id = elemento_activo.get_attribute('id') or 'sin-id'
                print(f"  [DEBUG] Elemento activo ahora: {activo_id}")
            
            # Escribir el valor
            try:
                elemento_activo.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                elemento_activo.send_keys(Keys.DELETE)
                time.sleep(0.2)
                elemento_activo.send_keys(valor_str)
                print(f"  [OK] Valor '{valor_str}' escrito")
            except Exception as e:
                print(f"  [WARN] send_keys fallo: {str(e)[:100]}")
                # Fallback: escribir directamente en el campo encontrado
                if campo:
                    try:
                        campo.clear()
                        campo.send_keys(valor_str)
                        print(f"  [OK] Valor '{valor_str}' escrito directo en campo")
                    except:
                        ActionChains(self.driver).click(campo).pause(0.3).send_keys(valor_str).perform()
                        print(f"  [OK] Valor '{valor_str}' escrito con ActionChains")
            
            time.sleep(0.5)
            
            # Confirmar con Enter
            try:
                elemento_activo = self.driver.switch_to.active_element
                elemento_activo.send_keys(Keys.ENTER)
                print("  [OK] Enter presionado")
            except:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                print("  [OK] Enter presionado (ActionChains)")
            
            time.sleep(1)
            
            self.driver.switch_to.default_content()
            print("[OK] Valor ingresado en 'Flete manual' correctamente")
            return True
            
        except Exception as e:
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            print(f"[ERROR] Error al ingresar valor en 'Flete manual': {str(e)}")
            return False
            import traceback
            traceback.print_exc()
            return False
    
    def guardar_pedido(self):
        """
        Hace click en el botón 'Grabar' (Guardar) para confirmar y guardar el pedido
        
        Returns:
            str o None: Número de pedido extraído del mensaje de SAP, o None si falló
        """
        try:
            print("\n[INFO] Guardando pedido en SAP...")
            
            # El botón Grabar está dentro del iframe ITSFRAME1
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            try:
                self.driver.switch_to.frame("ITSFRAME1")
                print("  [OK] Cambiado al iframe ITSFRAME1")
            except Exception as eframe:
                print(f"  [WARN] No se pudo cambiar al iframe: {str(eframe)}, buscando en doc principal")
            
            boton_grabar = None
            
            # Estrategia 1: Buscar por título "Grabar"
            try:
                boton_grabar = self.driver.find_element(By.XPATH, "//div[@role='button' and (contains(@title, 'Grabar') or contains(@title, 'Guardar'))]")
                print("  [OK] Botón 'Grabar' encontrado por título")
            except:
                pass
            
            # Estrategia 2: Buscar por id común del botón grabar (btn[11])
            if not boton_grabar:
                try:
                    boton_grabar = self.driver.find_element(By.XPATH, "//div[@role='button' and contains(@id, 'btn[11]')]")
                    print("  [OK] Botón 'Grabar' encontrado por ID btn[11]")
                except:
                    pass
            
            # Estrategia 3: Buscar por lsdata que contenga CTRL_S
            if not boton_grabar:
                try:
                    boton_grabar = self.driver.find_element(By.XPATH, "//div[@role='button' and contains(@lsdata, 'CTRL_S')]")
                    print("  [OK] Botón 'Grabar' encontrado por shortcut Ctrl+S")
                except:
                    pass
            
            # Estrategia 4: Buscar cualquier botón con "Grab" en el título
            if not boton_grabar:
                try:
                    boton_grabar = self.driver.find_element(By.XPATH, "//div[@role='button' and contains(@title, 'Grab')]")
                    print("  [OK] Botón 'Grabar' encontrado por texto parcial")
                except:
                    pass
            
            if boton_grabar:
                # Hacer scroll al botón
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_grabar)
                time.sleep(0.5)
                
                print(f"  [INFO] Haciendo click en botón 'Grabar'...")
                try:
                    boton_grabar.click()
                    print("  [OK] Click realizado en botón 'Grabar'")
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", boton_grabar)
                        print("  [OK] Click con JavaScript realizado en botón 'Grabar'")
                    except Exception as e:
                        print(f"  [WARN] Click falló ({str(e)[:80]}), usando Ctrl+S como fallback")
                        self.driver.switch_to.default_content()
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                        print("  [OK] Ctrl+S enviado")
            else:
                # Fallback final: Ctrl+S desde el documento principal
                print("  [WARN] Botón 'Grabar' no encontrado, usando Ctrl+S...")
                self.driver.switch_to.default_content()
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                print("  [OK] Ctrl+S enviado")
            
            # Esperar a que se procese el guardado
            print("  [INFO] Esperando confirmación de guardado...")
            time.sleep(3)
            
            # Extraer número de pedido del mensaje de la barra de estado
            numero_pedido = None
            
            # Buscar en ambos contextos: doc principal e iframe
            contextos = ['default', 'iframe']
            for contexto in contextos:
                if numero_pedido:
                    break
                    
                try:
                    if contexto == 'default':
                        self.driver.switch_to.default_content()
                    else:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame("ITSFRAME1")
                except:
                    continue
                
                # Estrategia 1: ID exacto del span de la barra de estado
                if not numero_pedido:
                    try:
                        msg_element = self.driver.find_element(By.ID, "wnd[0]/sbar_msg-txt")
                        texto_msg = msg_element.text.strip()
                        if texto_msg:
                            print(f"  [OK] Mensaje barra de estado ({contexto}): {texto_msg}")
                            numeros = re.findall(r'\d{8,}', texto_msg)
                            if numeros:
                                numero_pedido = numeros[0]
                    except:
                        pass
                
                # Estrategia 2: clase CSS lsMessageBar__text
                if not numero_pedido:
                    try:
                        msg_element = self.driver.find_element(By.CSS_SELECTOR, "span.lsMessageBar__text")
                        texto_msg = msg_element.text.strip()
                        if texto_msg:
                            print(f"  [OK] Mensaje barra CSS ({contexto}): {texto_msg}")
                            numeros = re.findall(r'\d{8,}', texto_msg)
                            if numeros:
                                numero_pedido = numeros[0]
                    except:
                        pass
                
                # Estrategia 3: buscar por texto de confirmación
                if not numero_pedido:
                    try:
                        mensajes = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'se ha grabado') or contains(text(), 'se grabó') or contains(text(), 'se creó')]")
                        for mensaje in mensajes:
                            texto = mensaje.text.strip()
                            if texto:
                                print(f"  [OK] Mensaje SAP ({contexto}): {texto}")
                                numeros = re.findall(r'\d{8,}', texto)
                                if numeros:
                                    numero_pedido = numeros[0]
                                    break
                    except:
                        pass
            
            # Volver al doc principal
            self.driver.switch_to.default_content()
            
            print("[OK] Pedido guardado exitosamente")
            return numero_pedido
            
        except Exception as e:
            print(f"[ERROR] Error al guardar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _navegar_portal_paso3(self):
        """
        Realiza la navegación completa en el portal hasta Paso 3:
        login → Auteco → Pedidos → nuevo pedido → 550005491 → Paso 2 → Paso 3.
        Debe llamarse solo cuando no se está ya en Paso 3.

        Returns:
            True si la navegación fue exitosa, False si hubo error
        """
        from selenium.common.exceptions import TimeoutException as _TimeoutException
        try:
            # 0. Verificar que la sesión de Chrome esté activa antes de navegar
            try:
                _ = self.driver.window_handles
            except Exception:
                print("  [ERROR] Sesión de Chrome inactiva al entrar a _navegar_portal_paso3")
                return False

            # 1. Detectar si se requiere login
            login_requerido = False
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "j_username"))
                )
                login_requerido = True
            except _TimeoutException:
                print("  [OK] Sesión del portal ya activa, omitiendo login")

            # 2. Login si es necesario
            if login_requerido:
                print("  [INFO] Iniciando login en portal...")
                campo_email = self.driver.find_element(By.ID, "j_username")
                campo_email.click()
                time.sleep(0.3)
                campo_email.clear()
                campo_email.send_keys("daniela.munoz@andesbpo.com")
                time.sleep(0.3)

                campo_password = self.driver.find_element(By.ID, "j_password")
                campo_password.click()
                time.sleep(0.3)
                campo_password.clear()
                campo_password.send_keys("Andes2025.")
                time.sleep(0.3)

                boton_login = self.driver.find_element(By.ID, "logOnFormSubmit")
                boton_login.click()
                print("  [OK] Login enviado")

            # Esperar botón Auteco (punto de convergencia) y dar tiempo a SAP UI5 para inicializar
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.ID, "__button0-img"))
                )
            except:
                time.sleep(3)
            # Pausa extra para que el framework SAP UI5 termine de registrar event handlers
            if login_requerido:
                time.sleep(4)
                print("  [OK] Login exitoso")
            else:
                time.sleep(1)

            # 3. Click en imagen Auteco
            try:
                imagen_auteco = self.driver.find_element(By.ID, "__button0-img")
                try:
                    imagen_auteco.find_element(By.XPATH, "..").click()
                except:
                    imagen_auteco.click()
            except Exception as e:
                print(f"  [WARN] Click en Auteco falló (ignorado): {str(e)[:80]}")
            time.sleep(1)

            # 4. Click en menú Pedidos
            try:
                span_pedidos = self.driver.find_element(By.XPATH,
                    "//span[@class='sapMText sapTntNavLIText sapMTextNoWrap' and text()='Pedidos']")
                span_pedidos.click()
                time.sleep(3)  # Espera fija para que SAP UI5 termine de renderizar la pantalla
                print("  [OK] Click en 'Pedidos'")
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer click en 'Pedidos': {str(e)}")
                return False

            # 5. Click en botón de acción (Nuevo pedido)
            # Selenium .click() despacha la secuencia completa de eventos de mouse que SAP Fiori
            # necesita. JS element.click() solo dispara "click" y no abre el formulario correctamente.
            try:
                boton_bdi = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "__button2-BDI-content"))
                )
                try:
                    boton_bdi.click()
                except Exception:
                    boton_bdi.find_element(By.XPATH, "..").click()
                print("  [OK] Click en botón de acción")
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer click en botón: {str(e)}")
                return False

            # 6. Escribir "R" en campo ventas y presionar Enter
            try:
                campo_ventas = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "container-PortalApp---Pedidos--comboVentas-inner"))
                )
                campo_ventas.click()
                time.sleep(0.3)
                campo_ventas.clear()
                campo_ventas.send_keys("R")
                time.sleep(0.3)
                campo_ventas.send_keys(Keys.ENTER)
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.invisibility_of_element_located((By.ID, "container-PortalApp---Pedidos--page-busyIndicator"))
                    )
                except:
                    time.sleep(3)
                print("  [OK] Campo ventas 'R' ingresado")
            except Exception as e:
                print(f"  [ERROR] No se pudo completar campo ventas: {str(e)}")
                return False

            # 7. Escribir "550005491" en campo de búsqueda y presionar Enter
            try:
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.invisibility_of_element_located((By.ID, "container-PortalApp---Pedidos--page-busyIndicator"))
                    )
                except:
                    pass
                campo_busqueda = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "container-PortalApp---Pedidos--searchField-I"))
                )
                campo_busqueda.click()
                time.sleep(0.3)
                campo_busqueda.clear()
                campo_busqueda.send_keys("550005491")
                time.sleep(0.5)
                campo_busqueda.send_keys(Keys.ENTER)  # Disparar la búsqueda
                # Esperar a que cargue la lista de resultados
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.invisibility_of_element_located((By.ID, "container-PortalApp---Pedidos--page-busyIndicator"))
                    )
                except:
                    time.sleep(3)
                print("  [OK] Búsqueda '550005491' ingresada y ejecutada")
            except Exception as e:
                print(f"  [ERROR] No se pudo escribir en campo de búsqueda: {str(e)}")
                return False

            # 8. Doble click en celda resultado (esperar que aparezca antes de clickear)
            try:
                celda_resultado = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//td[contains(@class, 'sapMListTblCell')]//span[contains(@class, 'sapMText')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", celda_resultado)
                time.sleep(0.5)
                ActionChains(self.driver).double_click(celda_resultado).perform()
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "container-PortalApp---Pedidos--WS_TipoVenta-nextButton"))
                    )
                except:
                    time.sleep(4)
                print("  [OK] Doble click en resultado, cargando detalle...")
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer doble click en resultado: {str(e)}")
                return False

            # 9. Click en Paso 2
            try:
                time.sleep(1)
                boton_paso2 = None
                for btn_id in ["container-PortalApp---Pedidos--WS_TipoVenta-nextButton",
                               "container-PortalApp---Pedidos--WS_TipoVenta-nextButton-inner"]:
                    try:
                        boton_paso2 = self.driver.find_element(By.ID, btn_id)
                        break
                    except:
                        continue
                if not boton_paso2:
                    try:
                        bdi = self.driver.find_element(By.XPATH, "//bdi[contains(text(), 'Paso 2')]")
                    except:
                        bdi = self.driver.find_element(By.ID,
                            "container-PortalApp---Pedidos--WS_TipoVenta-nextButton-BDI-content")
                    boton_paso2 = bdi.find_element(By.XPATH, "./ancestor::button")

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_paso2)
                time.sleep(0.5)
                try:
                    ActionChains(self.driver).move_to_element(boton_paso2).click().perform()
                except:
                    try:
                        boton_paso2.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", boton_paso2)
                time.sleep(1)
                print("  [OK] Click en 'Paso 2'")
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer click en 'Paso 2': {str(e)}")
                return False

            # 10. Click en Paso 3
            try:
                time.sleep(1)
                boton_paso3 = None
                for btn_id in ["container-PortalApp---Pedidos--WS_DatosGrles-nextButton",
                               "container-PortalApp---Pedidos--WS_DatosGrles-nextButton-inner"]:
                    try:
                        boton_paso3 = self.driver.find_element(By.ID, btn_id)
                        break
                    except:
                        continue
                if not boton_paso3:
                    elemento_bdi = None
                    for intento in range(15):
                        try:
                            elemento_bdi = self.driver.find_element(By.XPATH, "//bdi[contains(text(), 'Paso 3')]")
                            break
                        except:
                            pass
                        try:
                            elemento_bdi = self.driver.find_element(By.ID,
                                "container-PortalApp---Pedidos--WS_DatosGrles-nextButton-BDI-content")
                            break
                        except:
                            pass
                        time.sleep(1)
                    if not elemento_bdi:
                        raise Exception("No se encontró botón Paso 3 después de 15 segundos")
                    boton_paso3 = elemento_bdi.find_element(By.XPATH, "./ancestor::button")

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_paso3)
                time.sleep(0.5)
                try:
                    ActionChains(self.driver).move_to_element(boton_paso3).click().perform()
                except:
                    try:
                        boton_paso3.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", boton_paso3)
                print("  [INFO] Esperando carga de Paso 3 (8s)...")
                time.sleep(8)
                print("  [OK] Paso 3 cargado")
            except Exception as e:
                print(f"  [ERROR] No se pudo hacer click en 'Paso 3': {str(e)}")
                return False

            return True

        except Exception as e:
            print(f"[ERROR] Error en _navegar_portal_paso3: {str(e)}")
            return False

    def obtener_todos_precios_portal(self, materiales_lista, ya_inicializado=False):
        """
        Obtiene precios y disponibilidad de todos los materiales en el portal.

        Args:
            materiales_lista: Lista de tuplas (codigo_material, cantidad)
            ya_inicializado: True si en este run ya se navegó exitosamente a Paso 3.
                             Solo entonces se intenta reutilizar el estado del portal.
                             False (defecto) siempre fuerza la navegación completa.

        Returns:
            Lista de dicts {codigo, cantidad, precio_sin_iva, precio_con_iva, no_disponible}
            o None si falla
        """
        from selenium.common.exceptions import TimeoutException as _TimeoutException
        try:
            print("\n--- Obteniendo precios del Portal de Socios ---")

            # Solo reutilizar el estado del portal si ya navegamos exitosamente en este run.
            # Sin el flag, siempre navegamos desde cero (evita falsos positivos por cookies).
            ya_en_paso3 = False
            if ya_inicializado:
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.ID, "container-PortalApp---Pedidos--searchFieldMat-I"))
                    )
                    ya_en_paso3 = True
                    print("  [OK] Portal ya en Paso 3, omitiendo navegación completa")
                except Exception:
                    print("  [INFO] Paso 3 no detectado, renavedando...")
            else:
                print("  [INFO] Navegando hasta Paso 3 por primera vez...")

            if not ya_en_paso3:
                if not self._navegar_portal_paso3():
                    return None

            # Buscar precios y disponibilidad para cada material
            precios = []
            for material_codigo, cantidad in materiales_lista:
                print(f"\n  >> Material: {material_codigo} (cantidad: {cantidad})")
                resultado = self._buscar_precio_material_portal(material_codigo)
                if resultado is None:
                    print(f"  [ERROR] No se pudo obtener precio para material {material_codigo}")
                    return None
                precios.append({
                    'codigo': resultado['codigo'],
                    'cantidad': cantidad,
                    'precio_sin_iva': resultado['precio_sin_iva'],
                    'precio_con_iva': resultado['precio_con_iva'],
                    'no_disponible': resultado.get('no_disponible', False)
                })
                disponibilidad_txt = "NO DISPONIBLE" if resultado.get('no_disponible') else "DISPONIBLE"
                print(f"  [OK] Material {material_codigo}: sin IVA={resultado['precio_sin_iva']}, con IVA={resultado['precio_con_iva']} | Página 1: {disponibilidad_txt}")

            print(f"\n  [OK] Precios obtenidos para {len(precios)} material(es)")
            return precios

        except Exception as e:
            print(f"[ERROR] Error en obtener_todos_precios_portal: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def precargar_precios_batch(self, lista_materiales):
        """
        Navega al portal UNA SOLA VEZ y obtiene precios de todos los materiales en batch.

        Args:
            lista_materiales: Lista de tuplas (material_code, cantidad)

        Returns:
            Dict {material_code: {codigo, precio_sin_iva, precio_con_iva, no_disponible} o None si falló}
        """
        try:
            print("\n--- Precargando precios del portal (batch) ---")
            print(f"  [INFO] {len(lista_materiales)} material(es) a consultar")

            # La página del portal puede quedar en blanco al abrirse por primera vez.
            # Solo en la primera llamada: esperar 5s y recargar.
            if not self._portal_recargado:
                print("  [INFO] Esperando 5s y recargando portal para asegurar carga correcta...")
                time.sleep(5)
                self.driver.refresh()
                time.sleep(3)
                self._portal_recargado = True

            print("  [INFO] Navegando hasta Paso 3...")
            if not self._navegar_portal_paso3():
                print("  [ERROR] No se pudo navegar al Paso 3 del portal")
                return {mat: None for mat, _ in lista_materiales}

            cache = {}
            for material_codigo, cantidad in lista_materiales:
                print(f"\n  >> Material: {material_codigo}")
                resultado = self._buscar_precio_material_portal(material_codigo)
                if resultado is None:
                    print(f"  [WARN] No se pudo obtener precio para {material_codigo}")
                    cache[material_codigo] = None
                else:
                    cache[material_codigo] = resultado
                    disponibilidad = "NO DISPONIBLE" if resultado.get('no_disponible') else "DISPONIBLE"
                    print(f"  [OK] {material_codigo}: sin IVA={resultado['precio_sin_iva']}, con IVA={resultado['precio_con_iva']} | {disponibilidad}")

            encontrados = sum(1 for v in cache.values() if v is not None)
            print(f"\n  [OK] Precios precargados: {encontrados}/{len(cache)} material(es)")
            return cache

        except Exception as e:
            print(f"[ERROR] Error en precargar_precios_batch: {str(e)}")
            import traceback
            traceback.print_exc()
            return {mat: None for mat, _ in lista_materiales}

    def _buscar_precio_material_portal(self, material):
        """
        Busca un material en el portal (ya posicionado en Paso 3) y extrae precios.

        Args:
            material: Código de material a buscar

        Returns:
            Dict {codigo, precio_sin_iva (str), precio_con_iva (int)} o None si falla
        """
        import re
        try:
            # Encontrar input de búsqueda de material
            input_busqueda = None
            for intento in range(10):
                try:
                    input_busqueda = self.driver.find_element(
                        By.ID, "container-PortalApp---Pedidos--searchFieldMat-I")
                    break
                except:
                    time.sleep(1)

            if not input_busqueda:
                try:
                    input_busqueda = self.driver.find_element(
                        By.XPATH, "//input[@type='search' and @placeholder='Buscar en la lista']")
                except:
                    pass

            if not input_busqueda:
                raise Exception("No se encontró input de búsqueda de material")

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_busqueda)
            time.sleep(0.5)

            # Asignar valor completo de una vez (igual que en consola) para que SAP Fiori filtre correctamente
            self.driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, input_busqueda, str(material))

            time.sleep(3)

# Leer cantidad desde vista de lista (antes de navegar al detalle)
            no_disponible = True
            try:
                resultado_disp = self.driver.execute_script("""
                    const rows = document.querySelectorAll(".sapMObjectIdentifierTopRow");
                    const targetRow = rows[3];
                    const cantidadElement = targetRow ? targetRow.nextElementSibling : null;
                    if (cantidadElement) {
                        const cantidadTexto = cantidadElement.textContent.trim();
                        const cantidadNum = cantidadTexto.replace(/[^0-9]/g, "");
                        return {
                            textoOriginal: cantidadTexto,
                            cantidad: cantidadNum || "0",
                            disponible: !!(cantidadNum && parseInt(cantidadNum) > 0)
                        };
                    }
                    return { error: "No se encontro rows[3] o su siguiente hermano" };
                """)
                if resultado_disp and 'error' not in resultado_disp:
                    disponible = resultado_disp.get('disponible', False)
                    texto_original = resultado_disp.get('textoOriginal', '')
                    no_disponible = not disponible
                    estado_txt = "DISPONIBLE en dealer" if disponible else "NO DISPONIBLE en dealer"
                    print(f"    [INFO] Material {material}: {estado_txt} (cantidad: {texto_original})")
                else:
                    error_msg = resultado_disp.get('error', 'desconocido') if resultado_disp else 'sin respuesta'
                    print(f"    [WARN] No se pudo leer cantidad de {material}: {error_msg} → se asume no disponible")
            except Exception as e_disp:
                print(f"    [WARN] Error al verificar disponibilidad de {material}: {str(e_disp)[:100]} → se asume no disponible")

            # Click en span con código
            codigo_actual = material
            span_codigo = self.driver.find_element(By.XPATH, f"//span[contains(text(), 'CODIGO: {material}')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_codigo)
            time.sleep(0.3)
            try:
                span_codigo.click()
            except:
                self.driver.execute_script("arguments[0].click();", span_codigo)
            time.sleep(3)

            # Si aparece alerta de error del portal, no hay precio disponible — saltar registro
            if self._cerrar_alerta_portal(max_espera=2):
                print(f"    [WARN] Alerta del portal detectada para {material}, precio no disponible")
                return None

            # Verificar código reemplazante
            codigo_reemplazante = self.detectar_codigo_reemplazante_portal()
            if codigo_reemplazante:
                print(f"    [INFO] Material reemplazado: {material} -> {codigo_reemplazante}")
                codigo_actual = codigo_reemplazante

                # Buscar el input nuevamente
                input_reintentar = None
                try:
                    input_reintentar = self.driver.find_element(
                        By.ID, "container-PortalApp---Pedidos--searchFieldMat-I")
                except:
                    try:
                        input_reintentar = self.driver.find_element(
                            By.XPATH, "//input[@type='search' and @placeholder='Buscar en la lista']")
                    except:
                        pass

                if not input_reintentar:
                    raise Exception("No se encontró input de búsqueda para reintento con reemplazante")

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_reintentar)
                time.sleep(0.5)
                try:
                    input_reintentar.click()
                except Exception as e_click:
                    if "element click intercepted" in str(e_click):
                        self.driver.execute_script("arguments[0].focus();", input_reintentar)
                    else:
                        raise

                time.sleep(0.3)
                self.driver.execute_script("arguments[0].value = '';", input_reintentar)
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_reintentar)
                time.sleep(0.3)

                try:
                    input_reintentar.send_keys(codigo_actual)
                except:
                    self.driver.execute_script(f"arguments[0].value = '{codigo_actual}';", input_reintentar)
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_reintentar)
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", input_reintentar)

                time.sleep(2)

                # Releer cantidad para el código reemplazante (desde vista de lista)
                try:
                    resultado_reemplazo = self.driver.execute_script("""
                        (() => {
                            const cantidadElement = $($(".sapMObjectIdentifierTopRow")[3]).next();
                            if (cantidadElement && cantidadElement.length > 0) {
                                const cantidadTexto = cantidadElement.text().trim();
                                const cantidadNum = cantidadTexto.replace(/[^0-9]/g, "");
                                return {
                                    textoOriginal: cantidadTexto,
                                    cantidad: cantidadNum || "0",
                                    disponible: !!(cantidadNum && parseInt(cantidadNum) > 1)
                                };
                            }
                            return { error: "No encontré el elemento de cantidad" };
                        })();
                    """)
                    if resultado_reemplazo and 'error' not in resultado_reemplazo:
                        disponible_r = resultado_reemplazo.get('disponible', False)
                        texto_r = resultado_reemplazo.get('textoOriginal', '')
                        no_disponible = not disponible_r
                        estado_r = "DISPONIBLE en dealer" if disponible_r else "NO DISPONIBLE en dealer"
                        print(f"    [INFO] Reemplazante {codigo_actual}: {estado_r} (cantidad: {texto_r})")
                    else:
                        error_r = resultado_reemplazo.get('error', 'desconocido') if resultado_reemplazo else 'sin respuesta'
                        print(f"    [WARN] No se pudo leer cantidad del reemplazante {codigo_actual}: {error_r} → se mantiene valor anterior")
                except Exception as e_r:
                    print(f"    [WARN] Error verificando disponibilidad del reemplazante {codigo_actual}: {str(e_r)[:100]}")

                span_nuevo = self.driver.find_element(By.XPATH, f"//span[contains(text(), 'CODIGO: {codigo_actual}')]")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_nuevo)
                time.sleep(0.3)
                try:
                    span_nuevo.click()
                except:
                    self.driver.execute_script("arguments[0].click();", span_nuevo)
                time.sleep(3)

                # Si aparece alerta en material reemplazante, saltar registro
                if self._cerrar_alerta_portal(max_espera=2):
                    print(f"    [WARN] Alerta del portal detectada para reemplazante {codigo_actual}, precio no disponible")
                    return None

            # Si aparece alerta justo antes de extraer precios, saltar registro
            if self._cerrar_alerta_portal(max_espera=2):
                print(f"    [WARN] Alerta del portal detectada antes de extraer precio de {material}, saltando")
                return None

            # Extraer precios
            precio_sin_iva_texto = None
            precio_con_iva_texto = None
            for span in self.driver.find_elements(By.CLASS_NAME, "sapMText"):
                texto = span.text.strip()
                if "COP" in texto and "$" in texto:
                    if precio_sin_iva_texto is None:
                        precio_sin_iva_texto = texto
                    elif precio_con_iva_texto is None:
                        precio_con_iva_texto = texto
                        break

            if not precio_sin_iva_texto:
                raise Exception("No se encontró precio sin IVA en el portal")

            precio_sin_iva_limpio = re.sub(r'[^\d]', '', precio_sin_iva_texto)
            precio_con_iva_valor = int(re.sub(r'[^\d]', '', precio_con_iva_texto)) if precio_con_iva_texto else None

            resultado = {
                'codigo': codigo_actual,
                'precio_sin_iva': precio_sin_iva_limpio,
                'precio_con_iva': precio_con_iva_valor,
                'no_disponible': no_disponible
            }

            return resultado

        except Exception as e:
            print(f"    [ERROR] Error al buscar precio de material {material}: {str(e)}")
            return None

    def _limpiar_modales_bloqueantes(self):
        """
        CAPA 1 - BLINDAJE: Detecta y cierra cualquier modal/popup bloqueante.
        Llamar al inicio de cada paso crítico para garantizar estado limpio.

        - SAPMSSY0120_1 (Áreas de ventas): cierra + raise para skip del cliente
        - Modal de control de disponibilidad: hace click en Continuar
        - Cualquier otro dialog visible: intenta cerrar con Escape
        - Errores del propio shield: se loguean pero nunca detienen el RPA
        """
        try:
            self.driver.switch_to.default_content()

            # 0. Detectar capa bloqueante urPopupWindowBlockLayer
            # Aparece cuando un popup quedó abierto y tapa todos los elementos clickables
            try:
                block_layer = self.driver.find_element(By.ID, "urPopupWindowBlockLayer")
                if block_layer.is_displayed():
                    print("  [SHIELD] Capa bloqueante 'urPopupWindowBlockLayer' detectada, cerrando popup con Escape...")
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.8)
                    # Si persiste, intentar con Enter
                    try:
                        if block_layer.is_displayed():
                            ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                            time.sleep(0.5)
                    except Exception:
                        pass
                    print("  [SHIELD] Capa bloqueante eliminada")
            except NoSuchElementException:
                pass

            # 1. SAPMSSY0120_1 — requiere skip del cliente
            try:
                modal_ventas = self.driver.find_element(By.ID, "SAPMSSY0120_1")
                if modal_ventas.is_displayed():
                    print("  [SHIELD] Modal 'Areas de ventas' bloqueando, cerrando...")
                    try:
                        self.driver.find_element(By.ID, "SAPMSSY0120_1-close").click()
                        time.sleep(0.8)
                    except Exception:
                        pass
                    raise Exception("hay que seleccionar detalle de venta")
            except NoSuchElementException:
                pass

            # 2. Buscar cualquier otro dialog/popup visible
            dialogs = self.driver.find_elements(
                By.XPATH, "//*[(@role='dialog' or @ct='PW') and not(contains(@id,'SAPMSSY0120'))]"
            )
            for dialog in dialogs:
                try:
                    if not dialog.is_displayed():
                        continue
                    dialog_id = dialog.get_attribute("id") or "sin-id"

                    # Intentar botón "Continuar" (control de disponibilidad)
                    cerrado = False
                    try:
                        btn_continuar = dialog.find_element(
                            By.XPATH,
                            ".//*[@role='button' and (contains(@title,'Continuar') or contains(@title,'Continue'))]"
                        )
                        if btn_continuar.is_displayed():
                            btn_continuar.click()
                            time.sleep(0.5)
                            print(f"  [SHIELD] Modal '{dialog_id}' cerrado con Continuar")
                            cerrado = True
                    except Exception:
                        pass

                    # Si no había botón Continuar, cerrar con Escape
                    if not cerrado:
                        print(f"  [SHIELD] Modal inesperado '{dialog_id}' detectado, cerrando con Escape...")
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(0.5)
                except Exception:
                    continue

            return True

        except Exception as e:
            if "hay que seleccionar detalle de venta" in str(e):
                raise
            # Nunca bloquear el RPA por un error del propio shield
            print(f"  [SHIELD] Advertencia en limpiar_modales: {str(e)[:100]}")
            return True

    def recargar_pagina(self):
        """
        Recarga la página de SAP para volver al estado inicial
        y preparar el procesamiento del siguiente cliente
        """
        try:
            print("\n--- Recargando pagina para siguiente cliente ---")
            
            # Volver al contexto principal antes de recargar
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            
            # Recargar la página
            self.driver.refresh()
            print("  [OK] Pagina recargada")
            
            # Esperar a que cargue completamente
            time.sleep(3)
            
            print("[OK] Listo para procesar siguiente cliente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al recargar pagina: {str(e)}")
            return False
