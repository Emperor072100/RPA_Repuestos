"""
Módulo para crear y configurar el driver de Selenium
Con opciones anti-detección para evitar ser bloqueado por navegadores
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class DriverSAP:
    """
    Clase para manejar el driver de Selenium conectado a SAP
    Implementa opciones anti-detección y esperas explícitas
    """
    
    def __init__(self):
        """Inicializa el driver con opciones anti-detección"""
        self.driver = None
        self.wait = None
    
    def crear_driver(self):
        """
        Crea un driver de Chrome con opciones anti-detección
        Usa Selenium puro en lugar de undetected-chromedriver para mejor compatibilidad
        
        Returns:
            Driver de Selenium configurado
        """
        try:
            # Opciones de Chrome
            opciones = Options()
            
            # Opciones anti-detección comunes
            opciones.add_argument("disable-blink-features=AutomationControlled")
            opciones.add_argument("--disable-gpu")
            opciones.add_argument("--no-sandbox")
            opciones.add_argument("--disable-dev-shm-usage")
            
            # Crear el driver
            self.driver = webdriver.Chrome(options=opciones)
            
            # Inyectar script para ocultar que es automatizado
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                '''
            })
            
            # Configurar espera implícita
            self.driver.implicitly_wait(10)
            
            # Crear objeto de espera explícita
            self.wait = WebDriverWait(self.driver, 20)
            
            print("[OK] Driver de Selenium creado correctamente")
            return self.driver
            
        except Exception as e:
            print(f"[ERROR] Error al crear el driver: {str(e)}")
            return None
    
    def ir_a_url(self, url: str):
        """
        Navega a una URL específica

        Args:
            url: URL a la que navegar
        """
        try:
            self.driver.get(url)
            print(f"[OK] Navegando a: {url}")
        except Exception as e:
            print(f"[ERROR] Error al navegar: {str(e)}")
    
    def escribir_en_elemento(self, selector: str, valor: str, tipo_selector=By.ID):
        """
        Escribe texto en un elemento HTML
        
        Args:
            selector: Selector del elemento
            valor: Valor a escribir
            tipo_selector: Tipo de selector (ID, NAME, XPATH, etc)
        """
        try:
            # Espera a que el elemento sea visible
            elemento = self.wait.until(
                EC.presence_of_element_located((tipo_selector, selector))
            )
            
            # Limpia el campo y escribe
            elemento.clear()
            elemento.send_keys(valor)
            
            print(f"[OK] Escrito '{valor}' en elemento: {selector}")
            
        except Exception as e:
            print(f"[ERROR] Error al escribir en elemento: {str(e)}")
    
    def hacer_click(self, selector: str, tipo_selector=By.ID):
        """
        Hace click en un elemento HTML
        
        Args:
            selector: Selector del elemento
            tipo_selector: Tipo de selector (ID, NAME, XPATH, CSS_SELECTOR, etc)
        """
        try:
            # Espera a que el elemento sea clickeable
            elemento = self.wait.until(
                EC.element_to_be_clickable((tipo_selector, selector))
            )
            
            # Scroll hasta el elemento si es necesario
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)

            elemento.click()
            
            print(f"[OK] Click realizado en: {selector}")
            
        except Exception as e:
            print(f"[ERROR] Error al hacer click: {str(e)}")
            # Intenta un click con JavaScript si el click normal falla
            try:
                self.driver.execute_script("arguments[0].click();", elemento)
                print(f"[OK] Click por JavaScript realizado en: {selector}")
            except:
                print(f"[ERROR] No se pudo hacer click en: {selector}")
    
    def obtener_texto_elemento(self, selector: str, tipo_selector=By.ID) -> str:
        """
        Obtiene el texto de un elemento HTML
        
        Args:
            selector: Selector del elemento
            tipo_selector: Tipo de selector
            
        Returns:
            Texto del elemento
        """
        try:
            elemento = self.wait.until(
                EC.presence_of_element_located((tipo_selector, selector))
            )
            
            texto = elemento.text
            print(f"[OK] Texto obtenido de {selector}: {texto}")
            return texto
            
        except Exception as e:
            print(f"[ERROR] Error al obtener texto: {str(e)}")
            return ""
    
    def esperar_elemento(self, selector: str, tipo_selector=By.ID, tiempo=20):
        """
        Espera a que un elemento esté presente en la página
        
        Args:
            selector: Selector del elemento
            tipo_selector: Tipo de selector
            tiempo: Tiempo máximo de espera en segundos
        """
        try:
            self.wait.until(
                EC.presence_of_element_located((tipo_selector, selector))
            )
            print(f"[OK] Elemento {selector} encontrado")
            return True
            
        except Exception as e:
            print(f"[ERROR] Elemento {selector} no encontrado: {str(e)}")
            return False
    
    def cerrar_driver(self):
        """Cierra el driver y libera recursos"""
        try:
            if self.driver:
                self.driver.quit()
                print("[OK] Driver cerrado correctamente")
        except Exception as e:
            print(f"[ERROR] Error al cerrar driver: {str(e)}")
