from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
import time
import os
import datetime
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import csv
import re
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ====================== CONFIGURACIÓN ======================
count = 50  # Número de seguidores a analizar
account = "teeli__peachmuffin"  # Cuenta objetivo
page = "followers"  # "followers" o "following"

# Obtener credenciales desde variables de entorno (SIN valores por defecto)
yourusername = os.getenv("IG_USERNAME")
yourpassword = os.getenv("IG_PASSWORD")

# Validar que las credenciales existan
if not yourusername or not yourpassword:
    print("❌ ERROR: Credenciales no configuradas")
    print("Por favor, crea un archivo .env con:")
    print("IG_USERNAME=tu_usuario")
    print("IG_PASSWORD=tu_contraseña")
    exit(1)

# ====================== CONFIGURACIÓN DE LOGGING ======================
class Logger:
    def __init__(self, log_dir="logs"):
        self.logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_dir)
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_file = os.path.join(self.logs_dir, f"followers_stats_log_{self.timestamp}.txt")
        self.csv_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            f"{account}_followers_stats_{self.timestamp}.csv"
        )
        self.txt_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            f"{account}_followers_stats_{self.timestamp}.txt"
        )
        
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] [{level}] {message}"
        print(formatted_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted_message + "\n")
    
    def error(self, message):
        self.log(message, "ERROR")
    
    def warning(self, message):
        self.log(message, "WARNING")
    
    def success(self, message):
        self.log(message, "SUCCESS")
    
    def debug(self, message):
        self.log(message, "DEBUG")

logger = Logger()
logger.log(f"🚀 Iniciando análisis de seguidores de {account}")
logger.log(f"📊 Objetivo: Obtener estadísticas de {count} seguidores")

# ====================== FUNCIONES AUXILIARES ======================
def human_delay(min_seconds=1.0, max_seconds=3.0):
    """Pausa aleatoria para simular comportamiento humano"""
    sleep(random.uniform(min_seconds, max_seconds))

def type_like_human(element, text):
    """Escribe texto simulando velocidad humana"""
    for char in text:
        element.send_keys(char)
        sleep(random.uniform(0.05, 0.15))

def save_debug_info(driver, name, logger):
    """Guarda screenshot y HTML para debugging"""
    try:
        screenshot_path = os.path.join(logger.logs_dir, f"{name}_{logger.timestamp}.png")
        driver.save_screenshot(screenshot_path)
        logger.debug(f"Screenshot: {screenshot_path}")
        
        html_path = os.path.join(logger.logs_dir, f"{name}_{logger.timestamp}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.debug(f"HTML: {html_path}")
        return True
    except Exception as e:
        logger.error(f"Error guardando debug: {str(e)}")
        return False

def parse_follower_count(text):
    """
    Extrae el número de seguidores de un texto
    Ejemplos: "1,234 followers" -> 1234
              "1.2M followers" -> 1200000
              "10K followers" -> 10000
    """
    if not text:
        return None
    
    text = text.lower().strip()
    
    # Buscar patrones como "1,234 followers" o "1.2M"
    patterns = [
        r'([\d,\.]+)\s*m\s*followers?',  # Millones
        r'([\d,\.]+)\s*k\s*followers?',  # Miles
        r'([\d,\.]+)\s*followers?',      # Número normal
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '.')
            num = float(num_str)
            
            if 'm' in text:
                return int(num * 1000000)
            elif 'k' in text:
                return int(num * 1000)
            else:
                return int(num)
    
    return None

# ====================== CONFIGURACIÓN DEL NAVEGADOR ======================
def setup_driver():
    """Configura y retorna un driver de Chrome optimizado"""
    options = webdriver.ChromeOptions()
    
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.success("Navegador iniciado")
        return driver
    except Exception as e:
        logger.error(f"Error al iniciar navegador: {str(e)}")
        raise

# ====================== FUNCIONES DE INSTAGRAM ======================
def handle_cookies(driver, logger):
    """Maneja diálogos de cookies con múltiples estrategias"""
    logger.debug("Buscando diálogos de cookies...")
    
    cookie_selectors = [
        (By.XPATH, "//button[contains(text(),'Allow essential and optional cookies')]"),
        (By.XPATH, "//button[contains(text(),'Accept')]"),
        (By.XPATH, "//button[contains(text(),'Accept All')]"),
        (By.XPATH, "//button[contains(text(),'Aceptar')]"),
        (By.XPATH, "//button[contains(text(), 'Allow all cookies')]"),
        (By.CSS_SELECTOR, "button._a9--._a9_1"),
    ]
    
    for by, selector in cookie_selectors:
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((by, selector))
            )
            cookie_button.click()
            logger.success(f"✓ Cookies aceptadas: {selector}")
            human_delay(1, 2)
            return True
        except:
            continue
    
    logger.debug("No se encontraron diálogos de cookies (puede ser normal)")
    return False

def login_instagram_robust(driver, username, password, logger):
    """Login con múltiples estrategias y mejor manejo de errores"""
    try:
        logger.log("="*60)
        logger.log("PROCESO DE LOGIN")
        logger.log("="*60)
        
        # Ir a Instagram
        logger.log("1. Navegando a Instagram...")
        driver.get('https://www.instagram.com/')
        human_delay(5, 7)
        
        save_debug_info(driver, "step1_homepage", logger)
        
        # Manejar cookies
        logger.log("2. Manejando cookies...")
        handle_cookies(driver, logger)
        human_delay(2, 3)
        
        # Buscar campos de login con múltiples estrategias
        logger.log("3. Buscando campos de login...")
        
        # Estrategia 1: Por name
        username_input = None
        password_input = None
        
        strategies = [
            {
                "name": "Por atributo 'name'",
                "username": (By.CSS_SELECTOR, "input[name='username']"),
                "password": (By.CSS_SELECTOR, "input[name='password']")
            },
            {
                "name": "Por atributo 'aria-label'",
                "username": (By.CSS_SELECTOR, "input[aria-label*='username' i]"),
                "password": (By.CSS_SELECTOR, "input[aria-label*='password' i]")
            },
            {
                "name": "Por tipo de input",
                "username": (By.CSS_SELECTOR, "input[type='text']"),
                "password": (By.CSS_SELECTOR, "input[type='password']")
            }
        ]
        
        for strategy in strategies:
            try:
                logger.debug(f"   Probando: {strategy['name']}")
                username_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(strategy['username'])
                )
                password_input = driver.find_element(*strategy['password'])
                logger.success(f"   ✓ Campos encontrados con: {strategy['name']}")
                break
            except Exception as e:
                logger.debug(f"   ✗ {strategy['name']} falló: {str(e)}")
                continue
        
        if not username_input or not password_input:
            logger.error("❌ No se encontraron campos de login")
            save_debug_info(driver, "login_fields_not_found", logger)
            
            # Intentar ir directamente a /accounts/login/
            logger.log("4. Intentando ir a página de login directamente...")
            driver.get('https://www.instagram.com/accounts/login/')
            human_delay(5, 7)
            
            handle_cookies(driver, logger)
            save_debug_info(driver, "step2_login_page", logger)
            
            # Reintentar búsqueda de campos
            for strategy in strategies:
                try:
                    logger.debug(f"   Probando: {strategy['name']}")
                    username_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(strategy['username'])
                    )
                    password_input = driver.find_element(*strategy['password'])
                    logger.success(f"   ✓ Campos encontrados: {strategy['name']}")
                    break
                except:
                    continue
            
            if not username_input or not password_input:
                logger.error("❌ FALLO CRÍTICO: No se pueden encontrar campos de login")
                logger.log("Revisa los screenshots generados para ver qué está mostrando Instagram")
                return False
        
        # Limpiar campos por si tienen contenido
        logger.log("4. Limpiando campos...")
        username_input.clear()
        password_input.clear()
        human_delay(1, 2)
        
        # Escribir credenciales
        logger.log("5. Ingresando credenciales...")
        logger.debug(f"   Username: {username}")
        type_like_human(username_input, username)
        human_delay(0.5, 1)
        
        type_like_human(password_input, password)
        logger.debug("   Password: ********")
        human_delay(1, 2)
        
        save_debug_info(driver, "step3_credentials_entered", logger)
        
        # Buscar y hacer clic en botón de login
        logger.log("6. Buscando botón de login...")
        
        login_button = None
        button_selectors = [
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Log in')]"),
            (By.XPATH, "//button[contains(text(), 'Log In')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ]
        
        for by, selector in button_selectors:
            try:
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                logger.success(f"   ✓ Botón encontrado: {selector}")
                break
            except:
                continue
        
        if not login_button:
            logger.error("❌ No se encontró botón de login")
            # Intentar presionar Enter en el campo de password
            logger.log("   Intentando con tecla Enter...")
            password_input.send_keys(Keys.RETURN)
        else:
            login_button.click()
        
        logger.log("7. Esperando respuesta del servidor...")
        human_delay(10, 15)  # Espera más larga
        
        save_debug_info(driver, "step4_after_login_click", logger)
        
        # Verificar si el login fue exitoso
        logger.log("8. Verificando login...")
        
        success_indicators = [
            (By.XPATH, "//input[@placeholder='Search' or @aria-label='Search input']"),
            (By.XPATH, "//svg[@aria-label='Home']"),
            (By.XPATH, "//a[@href='/']//svg"),
            (By.XPATH, "//*[contains(@aria-label, 'Home')]"),
        ]
        
        login_success = False
        for by, selector in success_indicators:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.success(f"✓ Login exitoso! (indicador: {selector})")
                login_success = True
                break
            except:
                continue
        
        if not login_success:
            # Verificar si hay errores de login
            error_selectors = [
                (By.XPATH, "//*[contains(text(), 'Sorry')]"),
                (By.XPATH, "//*[contains(text(), 'incorrect')]"),
                (By.XPATH, "//*[contains(text(), 'wrong')]"),
                (By.XPATH, "//p[@role='alert']"),
            ]
            
            for by, selector in error_selectors:
                try:
                    error_element = driver.find_element(by, selector)
                    logger.error(f"❌ Error de login detectado: {error_element.text}")
                    save_debug_info(driver, "login_error_detected", logger)
                    return False
                except:
                    continue
            
            # Si no hay error pero tampoco indicadores de éxito
            logger.warning("⚠ No se pudo verificar el login definitivamente")
            logger.log("   Continuando de todos modos...")
            save_debug_info(driver, "login_uncertain", logger)
        
        logger.log("="*60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante login: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        save_debug_info(driver, "login_exception", logger)
        return False

def handle_post_login_dialogs(driver, logger):
    """Maneja diálogos post-login"""
    logger.log("Manejando diálogos post-login...")
    
    dialog_buttons = [
        (By.XPATH, "//button[contains(text(),'Not Now')]"),
        (By.XPATH, "//button[contains(text(),'Ahora no')]"),
        (By.XPATH, "//button[contains(text(),'Not now')]"),
    ]
    
    dialogs_closed = 0
    for attempt in range(3):
        human_delay(2, 3)
        for by, selector in dialog_buttons:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                button.click()
                logger.success(f"✓ Diálogo cerrado (#{dialogs_closed + 1})")
                dialogs_closed += 1
                break
            except:
                continue
        else:
            break
    
    if dialogs_closed == 0:
        logger.debug("No se encontraron diálogos post-login")

def close_modal_if_open(driver, logger):
    """Cierra cualquier modal abierto"""
    try:
        close_buttons = [
            (By.XPATH, "//button[contains(@aria-label, 'Close')]"),
            (By.XPATH, "//svg[@aria-label='Close']"),
            (By.XPATH, "//*[name()='svg' and contains(@aria-label, 'Close')]/.."),
        ]
        
        for by, selector in close_buttons:
            try:
                close_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                close_btn.click()
                logger.debug("Modal cerrado")
                human_delay(1, 2)
                return True
            except:
                continue
        
        # Presionar ESC
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        human_delay(1, 2)
        return True
        
    except Exception as e:
        return False

def get_follower_count_from_profile(driver, username, logger):
    """
    Navega al perfil de un usuario y obtiene su número de seguidores
    """
    try:
        url = f'https://www.instagram.com/{username}/'
        logger.debug(f"  → Visitando: {username}")
        
        driver.get(url)
        human_delay(3, 5)
        
        # Verificar si existe
        try:
            error = driver.find_element(By.XPATH, "//h2[contains(text(), 'Sorry')]")
            logger.warning(f"  ⚠ {username} no existe/privado")
            return None
        except NoSuchElementException:
            pass
        
        # Buscar el número de seguidores
        followers_selectors = [
            (By.XPATH, f'//a[contains(@href, "/{username}/followers/")]'),
            (By.XPATH, '//a[contains(@href, "/followers/")]'),
        ]
        
        for by, selector in followers_selectors:
            try:
                element = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((by, selector))
                )
                text = element.text
                
                follower_count = parse_follower_count(text)
                
                if follower_count is not None:
                    logger.success(f"  ✓ {username}: {follower_count:,} seguidores")
                    return follower_count
                
                # Intentar con title
                title = element.get_attribute('title')
                if title:
                    follower_count = parse_follower_count(title)
                    if follower_count is not None:
                        logger.success(f"  ✓ {username}: {follower_count:,} seguidores")
                        return follower_count
                        
            except Exception as e:
                continue
        
        # Método alternativo: buscar en el HTML
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "followers" in page_text.lower():
                lines = page_text.split('\n')
                for line in lines:
                    if "follower" in line.lower():
                        count = parse_follower_count(line)
                        if count is not None:
                            logger.success(f"  ✓ {username}: {count:,} (alternativo)")
                            return count
        except:
            pass
        
        logger.warning(f"  ⚠ No se pudo obtener seguidores de {username}")
        return None
        
    except Exception as e:
        logger.error(f"  ✗ Error en {username}: {str(e)}")
        return None

def get_followers_list(driver, account, page_type, target_count, logger):
    """Obtiene la lista de seguidores"""
    try:
        url = f'https://www.instagram.com/{account}/'
        logger.log(f"📍 Navegando a: {account}")
        driver.get(url)
        human_delay(5, 7)
        
        save_debug_info(driver, "profile_page", logger)
        
        # Verificar existencia
        try:
            error = driver.find_element(By.XPATH, "//h2[contains(text(), 'Sorry')]")
            logger.error(f"Cuenta {account} no existe")
            return []
        except NoSuchElementException:
            logger.success("Perfil cargado")
        
        # Click en followers
        logger.log(f"🔍 Buscando {page_type}...")
        
        link = None
        link_selectors = [
            (By.XPATH, f'//a[contains(@href, "/{page_type}")]'),
        ]
        
        for by, selector in link_selectors:
            try:
                link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                logger.success(f"✓ Enlace encontrado")
                break
            except:
                continue
        
        if not link:
            logger.error("No se encontró el enlace")
            return []
        
        logger.log("👆 Haciendo clic...")
        driver.execute_script("arguments[0].click();", link)
        human_delay(6, 8)
        
        save_debug_info(driver, f"modal_{page_type}", logger)
        
        # Buscar modal
        modal = None
        modal_selectors = [
            (By.CSS_SELECTOR, "div[role='dialog']"),
            (By.XPATH, "//div[@role='dialog']"),
        ]
        
        for by, selector in modal_selectors:
            try:
                modal = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.success("✓ Modal encontrado")
                break
            except:
                continue
        
        if not modal:
            logger.error("❌ Modal no encontrado")
            return []
        
        # Extraer usuarios
        logger.log(f"📥 Extrayendo {target_count} usuarios...")
        
        followers_list = []
        scraped = set()
        stall_count = 0
        max_stalls = 5
        
        while len(followers_list) < target_count and stall_count < max_stalls:
            user_links = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")
            
            new_users = 0
            for link in user_links:
                try:
                    href = link.get_attribute('href')
                    if href and 'instagram.com/' in href:
                        username = href.split('instagram.com/')[-1].strip('/').split('/')[0]
                        
                        if username and username not in scraped and username != account:
                            scraped.add(username)
                            followers_list.append(username)
                            new_users += 1
                            logger.log(f"  [{len(followers_list)}/{target_count}] {username}")
                            
                            if len(followers_list) >= target_count:
                                break
                except:
                    continue
            
            if new_users == 0:
                stall_count += 1
            else:
                stall_count = 0
            
            try:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                human_delay(2, 3)
            except:
                break
        
        logger.success(f"✓ Extraídos {len(followers_list)} usuarios")
        
        close_modal_if_open(driver, logger)
        human_delay(2, 3)
        
        return followers_list
        
    except Exception as e:
        logger.error(f"Error obteniendo lista: {str(e)}")
        save_debug_info(driver, "get_followers_error", logger)
        return []

def save_results(data, logger):
    """Guarda los resultados en CSV y TXT"""
    
    # CSV
    try:
        with open(logger.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Username', 'Username_Follower', 'Num_Followers'])
            
            for row in data:
                writer.writerow(row)
        
        logger.success(f"📊 CSV: {logger.csv_file}")
    except Exception as e:
        logger.error(f"Error CSV: {str(e)}")
    
    # TXT
    try:
        with open(logger.txt_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"ANÁLISIS DE SEGUIDORES - {account}\n")
            f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"{'Username':<20} | {'Follower':<25} | {'Num Seguidores':>15}\n")
            f.write(f"{'-'*20}-+-{'-'*25}-+-{'-'*15}\n")
            
            for username, follower, num_followers in data:
                follower_str = str(follower) if follower else "N/A"
                num_str = f"{num_followers:,}" if num_followers is not None else "N/A"
                f.write(f"{username:<20} | {follower_str:<25} | {num_str:>15}\n")
        
        logger.success(f"📄 TXT: {logger.txt_file}")
    except Exception as e:
        logger.error(f"Error TXT: {str(e)}")

# ====================== FUNCIÓN PRINCIPAL ======================
def main():
    driver = None
    try:
        logger.log("="*80)
        logger.log("INICIANDO ANÁLISIS DE SEGUIDORES CON ESTADÍSTICAS")
        logger.log("="*80)
        
        driver = setup_driver()
        
        # Login robusto
        if not login_instagram_robust(driver, yourusername, yourpassword, logger):
            logger.error("❌ Login fallido - Abortando")
            logger.log("\n📋 REVISA LOS ARCHIVOS DE DEBUG:")
            logger.log(f"   - {logger.logs_dir}")
            return
        
        handle_post_login_dialogs(driver, logger)
        
        # Obtener lista
        logger.log("\n" + "="*80)
        logger.log("PASO 1: Obteniendo lista de seguidores")
        logger.log("="*80)
        
        followers_list = get_followers_list(driver, account, page, count, logger)
        
        if not followers_list:
            logger.error("No se obtuvieron seguidores")
            return
        
        # Analizar perfiles
        logger.log("\n" + "="*80)
        logger.log(f"PASO 2: Analizando {len(followers_list)} perfiles")
        logger.log("="*80)
        
        results = []
        
        for i, follower_username in enumerate(followers_list, 1):
            logger.log(f"\n[{i}/{len(followers_list)}] {follower_username}")
            
            follower_count = get_follower_count_from_profile(driver, follower_username, logger)
            
            results.append([
                account,
                follower_username,
                follower_count
            ])
            
            human_delay(2, 4)
        
        # Guardar
        logger.log("\n" + "="*80)
        logger.log("PASO 3: Guardando resultados")
        logger.log("="*80)
        
        save_results(results, logger)
        
        # Resumen
        logger.log("\n" + "="*80)
        logger.success("✅ ANÁLISIS COMPLETADO")
        logger.log("="*80)
        logger.log(f"📊 Total: {len(results)} usuarios")
        
        successful = sum(1 for r in results if r[2] is not None)
        logger.log(f"✓ Exitosos: {successful}")
        logger.log(f"✗ Fallidos: {len(results) - successful}")
        logger.log(f"📁 Archivos:")
        logger.log(f"   CSV: {logger.csv_file}")
        logger.log(f"   TXT: {logger.txt_file}")
        logger.log(f"   LOG: {logger.log_file}")
        logger.log("="*80)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠ Interrumpido por usuario")
    except Exception as e:
        logger.error(f"\n❌ Error crítico: {str(e)}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        if driver:
            save_debug_info(driver, "critical_error", logger)
    finally:
        if driver:
            logger.log("\n💡 Navegador abierto para inspección")

if __name__ == "__main__":
    main()