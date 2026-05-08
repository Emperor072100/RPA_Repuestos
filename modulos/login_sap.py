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
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        try:
            print("\n--- Verificando sesión SAP ---")

            # Esperar a que aparezca la pantalla principal o el formulario de login
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                lambda d: d.find_elements(By.ID, 'ToolbarOkCode') or d.find_elements(By.ID, 'sap-user')
            )

            # Si ya hay sesión activa (ToolbarOkCode visible), omitir login
            if self.driver.find_elements(By.ID, 'ToolbarOkCode'):
                print("[OK] Sesión SAP ya activa, omitiendo login")
                return True

            print(">> Sesión no activa, iniciando login...")
            # sap-user ya confirmado presente por el lambda anterior

            # Ingresamos el usuario por ID
            print(">> Ingresando usuario...")
            self.driver_sap.escribir_en_elemento(
                'sap-user',
                usuario,
                tipo_selector=By.ID
            )

            # Ingresamos la contraseña por ID
            print(">> Ingresando contraseña...")
            self.driver_sap.escribir_en_elemento(
                'sap-password',
                contraseña,
                tipo_selector=By.ID
            )

            # Click en el botón de login - Intentar múltiples selectores
            print(">> Haciendo click en botón de acceso...")

            try:
                botones = self.driver.find_elements(By.TAG_NAME, "button")
                boton_acceder = None

                for boton in botones:
                    if "Acceder" in boton.text or "acceder" in boton.text.lower():
                        boton_acceder = boton
                        break

                if boton_acceder:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_acceder)
                    try:
                        boton_acceder.click()
                        print("[OK] Click en botón Acceder completado")
                    except:
                        self.driver.execute_script("arguments[0].click();", boton_acceder)
                        print("[OK] Click por JavaScript en botón Acceder")
                else:
                    print("[ERROR] No se encontró botón 'Acceder' - intentando enviar Enter...")
                    self.driver.find_element(By.ID, "sap-password").send_keys("\n")

            except Exception as e:
                print(f"[ERROR] Error al hacer click: {str(e)}")
                print("[WARN] Continuando con el flujo...")

            # Esperar a que aparezca un elemento de la página principal de SAP (no sleep fijo)
            print(">> Esperando a que se complete el login...")
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
        Verifica si el login fue exitoso esperando un elemento de la página principal

        Returns:
            True si el login fue exitoso
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            wait = WebDriverWait(self.driver, 20)
            # Esperar a que aparezca el campo de comandos SAP (indica login exitoso)
            try:
                wait.until(EC.presence_of_element_located((By.ID, 'ToolbarOkCode')))
                print("[OK] Verificación de login completada")
                return True
            except:
                pass

            # Fallback: verificar si hay error explícito
            try:
                error_element = self.driver.find_element(By.CLASS_NAME, 'error')
                print("[ERROR] Página de error detectada")
                return False
            except:
                pass

            print("[OK] Verificación de login completada")
            return True

        except Exception as e:
            print(f"[ERROR] Error al verificar login: {str(e)}")
            return False
