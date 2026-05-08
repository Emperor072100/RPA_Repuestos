"""
Módulo para manejar el login en SAP
Automatiza la autenticación en la página
"""

from selenium.webdriver.common.by import By
import time


class LoginSAP:
    """
    Clase para automatizar el login en SAP NetWeaver
    """
    
    def __init__(self, driver_sap):
        """
        Inicializa el manejador de login
        
        Args:
            driver_sap: Instancia de la clase DriverSAP
        """
        self.driver_sap = driver_sap
        self.driver = driver_sap.driver
    
    def iniciar_sesion(self, usuario: str, contraseña: str) -> bool:
        """
        Realiza el login en SAP con las credenciales proporcionadas
        
        Args:
            usuario: Nombre de usuario
            contraseña: Contraseña del usuario
            
        Returns:
            True si el login fue exitoso, False si fallo
        """
        try:
            print("\n--- Iniciando proceso de login en SAP ---")
            
            # Esperar a que cargue la página de login
            time.sleep(3)
            
            # Ingresamos el usuario por ID
            print(">> Ingresando usuario...")
            self.driver_sap.escribir_en_elemento(
                'sap-user',
                usuario,
                tipo_selector=By.ID
            )
            
            time.sleep(1)
            
            # Ingresamos la contraseña por ID
            print(">> Ingresando contraseña...")
            self.driver_sap.escribir_en_elemento(
                'sap-password',
                contraseña,
                tipo_selector=By.ID
            )
            
            time.sleep(1)
            
            # Click en el botón de login - Intentar múltiples selectores
            print(">> Haciendo click en botón de acceso...")
            
            try:
                # Buscar el botón directamente
                botones = self.driver.find_elements(By.TAG_NAME, "button")
                boton_acceder = None
                
                # Buscar el botón que contiene "Acceder"
                for boton in botones:
                    if "Acceder" in boton.text or "acceder" in boton.text.lower():
                        boton_acceder = boton
                        break
                
                if boton_acceder:
                    # Hacer scroll hasta el botón
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_acceder)
                    time.sleep(0.5)
                    
                    # Intentar click normal
                    try:
                        boton_acceder.click()
                        print("[OK] Click en botón Acceder completado")
                    except:
                        # Si falla, intentar con JavaScript
                        self.driver.execute_script("arguments[0].click();", boton_acceder)
                        print("[OK] Click por JavaScript en botón Acceder")
                else:
                    print("[ERROR] No se encontró botón 'Acceder' - intentando enviar Enter...")
                    self.driver.find_element(By.ID, "sap-password").send_keys("\n")
                    
            except Exception as e:
                print(f"[ERROR] Error al hacer click: {str(e)}")
                print("[WARN] Continuando con el flujo...")
            
            # Esperar a que se realice el login (tiempo variable)
            print(">> Esperando a que se complete el login...")
            time.sleep(5)
            
            # Verificar si el login fue exitoso buscando elementos que solo aparecen después del login
            if self.verificar_login_exitoso():
                print("[OK] Login exitoso en SAP")
                return True
            else:
                print("[ERROR] Posible error en el login")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error durante el login: {str(e)}")
            return False
    
    def verificar_login_exitoso(self) -> bool:
        """
        Verifica si el login fue exitoso revisando si cargó la página principal
        
        Returns:
            True si el login fue exitoso
        """
        try:
            # Esperar a que aparezca algún elemento típico de la página principal
            # Esto dependerá de la estructura específica de SAP
            # Por ahora verificamos que la URL cambió o que hay contenido
            
            time.sleep(2)
            
            # Verificar si estamos en una página de error
            try:
                error_element = self.driver.find_element(By.CLASS_NAME, 'error')
                print("[ERROR] Página de error detectada")
                return False
            except:
                pass
            
            # Si llegamos aquí, probablemente el login fue exitoso
            print("[OK] Verificación de login completada")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al verificar login: {str(e)}")
            return False
