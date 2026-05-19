"""
Módulo para crear y configurar el driver de Selenium
Con opciones anti-detección para evitar ser bloqueado por navegadores
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import socket
import time
import os

_DEBUG_PORT = 9222
_DEBUG_PROFILE = os.path.join(os.environ.get('TEMP', r'C:\Temp'), 'ChromeDebugProfile')
_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]


class DriverSAP:
    """
    Clase para manejar el driver de Selenium conectado a SAP
    Implementa opciones anti-detección y esperas explícitas
    """

    def __init__(self):
        self.driver = None
        self.wait = None

    def _cerrar_procesos_chrome(self):
        """Mata todos los procesos de Chrome y ChromeDriver activos"""
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True)
        time.sleep(1.5)

    def _iniciar_chrome_debug(self):
        """
        Lanza Chrome en modo debug via subprocess.
        Retorna True si se encontró y lanzó el ejecutable, False si no.
        """
        for path in _CHROME_PATHS:
            if os.path.exists(path):
                os.makedirs(_DEBUG_PROFILE, exist_ok=True)
                subprocess.Popen([
                    path,
                    f'--remote-debugging-port={_DEBUG_PORT}',
                    f'--user-data-dir={_DEBUG_PROFILE}',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-popup-blocking',
                    '--no-first-run',
                    '--no-default-browser-check',
                    'about:blank',
                ])
                print(f"[OK] Chrome iniciado en modo debug (puerto {_DEBUG_PORT})")
                return True
        print("[WARN] Ejecutable de Chrome no encontrado en rutas conocidas")
        return False

    def _esperar_puerto_debug(self, timeout=20):
        """Espera a que Chrome tenga al menos una pestaña de tipo page disponible"""
        import urllib.request
        import json as _json
        for _ in range(timeout):
            try:
                with urllib.request.urlopen(
                    f'http://127.0.0.1:{_DEBUG_PORT}/json/list', timeout=2
                ) as resp:
                    targets = _json.loads(resp.read())
                    if any(t.get('type') == 'page' for t in targets):
                        return True
            except Exception:
                pass
            time.sleep(1)
        return False

    def crear_driver(self):
        """
        Cierra Chrome, lo relanza en modo debug y conecta Selenium.

        Returns:
            Driver de Selenium configurado
        """
        try:
            self._cerrar_procesos_chrome()

            opciones = Options()
            chrome_iniciado = self._iniciar_chrome_debug()

            if chrome_iniciado:
                if not self._esperar_puerto_debug():
                    print("[WARN] Puerto debug no disponible, usando modo estándar")
                    chrome_iniciado = False
                else:
                    # Conectar Selenium al Chrome ya lanzado
                    opciones.add_experimental_option("debuggerAddress", f"127.0.0.1:{_DEBUG_PORT}")

            if not chrome_iniciado:
                # Fallback: Selenium lanza Chrome con opciones anti-detección
                opciones.add_argument(f"--remote-debugging-port={_DEBUG_PORT}")
                opciones.add_argument("--disable-blink-features=AutomationControlled")
                opciones.add_argument("--disable-gpu")
                opciones.add_argument("--no-sandbox")
                opciones.add_argument("--disable-dev-shm-usage")
                opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
                opciones.add_experimental_option("useAutomationExtension", False)

            self.driver = webdriver.Chrome(options=opciones)

            # Ocultar navigator.webdriver
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                '''
            })

            self.driver.implicitly_wait(10)
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
