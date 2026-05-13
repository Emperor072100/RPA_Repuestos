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
        self.driver_sap = driver_sap
        self.driver = driver_sap.driver

    def _sesion_sap_activa(self) -> bool:
        """
        Verifica si la sesión SAP ya está activa buscando ToolbarOkCode
        en el documento principal Y en todos los iframes disponibles.
        Deja el driver en default_content al terminar.
        """
        try:
            self.driver.switch_to.default_content()
            # Intentar en documento principal
            if self.driver.find_elements(By.ID, 'ToolbarOkCode'):
                return True
            # Buscar en cada iframe
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    if self.driver.find_elements(By.ID, 'ToolbarOkCode'):
                        return True
                except Exception:
                    pass
                finally:
                    self.driver.switch_to.default_content()
        except Exception:
            pass
        return False

    def iniciar_sesion(self, usuario: str, contraseña: str) -> bool:
        """
        Realiza el login en SAP con las credenciales proporcionadas.
        Si la sesión ya está activa (ToolbarOkCode presente en algún iframe),
        omite el login y retorna True inmediatamente.

        Returns:
            True si el login fue exitoso o ya estaba activo
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            print("\n--- Verificando sesión SAP ---")

            # Salir de cualquier iframe activo
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass

            # Comprobar si la sesión ya está activa (ToolbarOkCode en iframe)
            if self._sesion_sap_activa():
                print("[OK] Sesión SAP ya activa, omitiendo login")
                return True

            # Verificar si la página de login está disponible
            wait = WebDriverWait(self.driver, 20)
            try:
                wait.until(
                    lambda d: d.find_elements(By.ID, 'sap-user')
                )
            except Exception:
                # Si no aparece login form, verificar una vez más si la sesión está activa
                if self._sesion_sap_activa():
                    print("[OK] Sesión SAP activa (detectada tarde), omitiendo login")
                    return True
                print("[ERROR] No se encontró ni sesión activa ni formulario de login")
                return False

            print(">> Sesión no activa, iniciando login...")

            print(">> Ingresando usuario...")
            self.driver_sap.escribir_en_elemento('sap-user', usuario, tipo_selector=By.ID)

            print(">> Ingresando contraseña...")
            self.driver_sap.escribir_en_elemento('sap-password', contraseña, tipo_selector=By.ID)

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
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", boton_acceder)
                        print("[OK] Click por JavaScript en botón Acceder")
                else:
                    print("[ERROR] No se encontró botón 'Acceder' - intentando enviar Enter...")
                    self.driver.find_element(By.ID, "sap-password").send_keys("\n")

            except Exception as e:
                print(f"[ERROR] Error al hacer click: {str(e)}")
                print("[WARN] Continuando con el flujo...")

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
        Verifica si el login fue exitoso esperando ToolbarOkCode en iframes.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            # Esperar hasta 20s a que ToolbarOkCode aparezca en algún iframe
            for _ in range(40):  # 40 × 0.5s = 20s
                if self._sesion_sap_activa():
                    print("[OK] Verificación de login completada")
                    return True
                time.sleep(0.5)

            # Fallback: verificar si hay error explícito
            try:
                self.driver.switch_to.default_content()
                error_element = self.driver.find_element(By.CLASS_NAME, 'error')
                print("[ERROR] Página de error detectada")
                return False
            except Exception:
                pass

            print("[OK] Verificación de login completada")
            return True

        except Exception as e:
            print(f"[ERROR] Error al verificar login: {str(e)}")
            return False
