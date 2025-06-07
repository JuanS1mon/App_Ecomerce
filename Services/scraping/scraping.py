import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from pydantic import BaseModel
from typing import List, Optional
from ...db.schemas.Scraping import ScraperTestConfig , SelectorConfig

def extract_with_beautifulsoup(config: ScraperTestConfig, max_items: int = 10):
    """
    Realiza la extracción de datos utilizando Beautiful Soup
    """
    # Configuración de sesión y proxies
    session = requests.Session()
    if config.proxy.enabled and config.proxy.address:
        proxies = {config.proxy.proxy_type or 'http': config.proxy.address}
        session.proxies.update(proxies)
    
    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Lista para almacenar resultados
    results = []
    current_url = config.url
    page_count = 0
    
    # Loop para paginación
    while page_count < config.pagination.max_pages if config.pagination.enabled else 1:
        # Añadir retraso si está configurado
        if config.request_delay > 0 and page_count > 0:
            time.sleep(config.request_delay / 1000.0)  # Convertir ms a segundos
        
        # Realizar solicitud
        try:
            response = session.get(
                current_url, 
                headers=headers, 
                timeout=config.request_timeout
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Error al acceder a {current_url}: {str(e)}")
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Obtener contenedores si se ha especificado
        containers = [soup]  # Por defecto, usar toda la página
        if config.container_selector:
            container_elements = soup.select(config.container_selector)
            if container_elements:
                containers = container_elements
        
        # Procesar cada contenedor
        for container in containers:
            # Limitar la cantidad de resultados
            if len(results) >= max_items:
                break
                
            item_data = {}
            
            # Extraer datos según cada selector
            for selector in config.selectors:
                elements = container.select(selector.path)
                
                # Manejar elemento único o múltiple
                if not selector.multiple and elements:
                    item_data[selector.name] = extract_element_data(elements[0], selector)
                elif selector.multiple and elements:
                    item_data[selector.name] = [extract_element_data(el, selector) for el in elements]
                else:
                    item_data[selector.name] = None
            
            # Añadir item a resultados si contiene datos
            if any(value is not None for value in item_data.values()):
                results.append(item_data)
        
        # Manejar paginación
        if config.pagination.enabled and page_count < config.pagination.max_pages - 1:
            next_url = None
            
            # Paginación por enlace
            if config.pagination.type == "link" and config.pagination.next_selector:
                next_link = soup.select_one(config.pagination.next_selector)
                if next_link and next_link.has_attr('href'):
                    next_url = urljoin(current_url, next_link['href'])
            
            # Paginación por parámetro
            elif config.pagination.type == "parameter" and config.pagination.page_parameter:
                from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
                
                # Parsear URL actual
                parsed_url = urlparse(current_url)
                query_params = parse_qs(parsed_url.query)
                
                # Incrementar valor del parámetro de página
                param = config.pagination.page_parameter
                current_page = int(query_params.get(param, ['1'])[0])
                query_params[param] = [str(current_page + 1)]
                
                # Reconstruir URL
                parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
                next_url = urlunparse(parsed_url)
            
            # Si no hay siguiente URL, terminamos
            if not next_url or next_url == current_url:
                break
                
            current_url = next_url
        else:
            # No hay más paginación
            break
            
        page_count += 1
    
    return results

def extract_element_data(element, selector: SelectorConfig):
    """
    Extrae datos de un elemento según su tipo de selector
    """
    if not element:
        return None
        
    if selector.type == "text":
        return element.get_text(strip=True)
    elif selector.type == "html":
        return str(element)
    elif selector.type == "attribute" and selector.attribute:
        return element.get(selector.attribute)
    elif selector.type == "link":
        return element.get('href')
    elif selector.type == "image":
        return element.get('src')
    else:
        return element.get_text(strip=True)
    
def extract_with_selenium(config: ScraperTestConfig, max_items: int = 10):
    """
    Realiza la extracción de datos utilizando Selenium
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Añadir proxy si está configurado
    if config.proxy.enabled and config.proxy.address:
        chrome_options.add_argument(f'--proxy-server={config.proxy.address}')
    
    try:
        # Iniciar navegador
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(config.request_timeout)
        
        # Navegar a la URL
        driver.get(config.url)
        
        # Ejecutar JavaScript personalizado si está habilitado
        if config.javascript.enabled and config.javascript.code:
            driver.execute_script(config.javascript.code)
            
            # Dar tiempo para que se ejecute el JS
            time.sleep(1)
        
        results = []
        page_count = 0
        
        # Loop para paginación
        while page_count < config.pagination.max_pages if config.pagination.enabled else 1:
            # Esperar a que la página cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scrolling para scroll infinito
            if config.pagination.type == "infinite":
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # esperar a que carguen nuevos elementos
                
                # Esperar al selector de carga si está configurado
                if config.pagination.load_more_selector:
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, config.pagination.load_more_selector)
                            )
                        )
                    except:
                        pass  # Continuar si no se encuentra
            
            # Obtener contenedores si se ha especificado
            if config.container_selector:
                containers = driver.find_elements(By.CSS_SELECTOR, config.container_selector)
            else:
                containers = [driver.find_element(By.TAG_NAME, "body")]
            
            # Procesar cada contenedor
            for container in containers:
                # Limitar la cantidad de resultados
                if len(results) >= max_items:
                    break
                    
                item_data = {}
                
                # Extraer datos según cada selector
                for selector in config.selectors:
                    elements = container.find_elements(By.CSS_SELECTOR, selector.path)
                    
                    # Manejar elemento único o múltiple
                    if not selector.multiple and elements:
                        item_data[selector.name] = extract_selenium_element_data(elements[0], selector)
                    elif selector.multiple and elements:
                        item_data[selector.name] = [extract_selenium_element_data(el, selector) for el in elements]
                    else:
                        item_data[selector.name] = None
                
                # Añadir item a resultados si contiene datos
                if any(value is not None for value in item_data.values()):
                    results.append(item_data)
            
            # Manejar paginación
            if config.pagination.enabled and page_count < config.pagination.max_pages - 1:
                next_found = False
                
                # Paginación por enlace
                if config.pagination.type == "link" and config.pagination.next_selector:
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, config.pagination.next_selector)
                            )
                        )
                        # Hacer scroll al botón y hacer clic
                        driver.execute_script("arguments[0].scrollIntoView();", next_button)
                        next_button.click()
                        next_found = True
                        
                        # Esperar un momento para que cargue la siguiente página
                        time.sleep(config.request_delay / 1000.0 if config.request_delay > 0 else 1)
                    except Exception as e:
                        break  # No hay más páginas
                
                # Paginación por parámetro
                elif config.pagination.type == "parameter" and config.pagination.page_parameter:
                    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
                    
                    # Parsear URL actual
                    current_url = driver.current_url
                    parsed_url = urlparse(current_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    # Incrementar valor del parámetro de página
                    param = config.pagination.page_parameter
                    current_page = int(query_params.get(param, ['1'])[0])
                    query_params[param] = [str(current_page + 1)]
                    
                    # Reconstruir URL y navegar
                    parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
                    next_url = urlunparse(parsed_url)
                    driver.get(next_url)
                    next_found = True
                
                # Scroll infinito se maneja al inicio del loop
                elif config.pagination.type == "infinite":
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height != last_height:
                        next_found = True
                
                # Si no se encontró siguiente página, terminamos
                if not next_found:
                    break
            else:
                # No hay más paginación
                break
                
            page_count += 1
        
        return results
    
    except Exception as e:
        raise Exception(f"Error en la extracción con Selenium: {str(e)}")
    
    finally:
        # Asegurarse de cerrar el navegador
        if 'driver' in locals():
            driver.quit()

def extract_selenium_element_data(element, selector: SelectorConfig):
    """
    Extrae datos de un elemento Selenium según su tipo de selector
    """
    if not element:
        return None
        
    if selector.type == "text":
        return element.text.strip()
    elif selector.type == "html":
        return element.get_attribute('outerHTML')
    elif selector.type == "attribute" and selector.attribute:
        return element.get_attribute(selector.attribute)
    elif selector.type == "link":
        return element.get_attribute('href')
    elif selector.type == "image":
        return element.get_attribute('src')
    else:
        return element.text.strip()