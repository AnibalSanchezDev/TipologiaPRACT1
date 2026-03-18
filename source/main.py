from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sys
import os
from datetime import datetime

busqueda = "Python"
busqueda = "Python"
if len(sys.argv) > 1:
    busqueda = " ".join(sys.argv[1:])

print(f"Iniciando búsqueda para: {busqueda}")

fecha_hora = datetime.now().strftime("%Y%m%d_%H%M")

termino_limpio = busqueda.replace(" ", "_")
nombre_archivo = f"data_{termino_limpio}_{fecha_hora}.csv"

ruta_completa = os.path.join("data", nombre_archivo)

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Accediendo a Tecnoempleo")
    driver.get("https://www.tecnoempleo.com")

    boton_cookies = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-cookie-accept"))
    )
    boton_cookies.click()
    print("Cookies aceptadas.")

    caja_texto = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "te"))
    )
    driver.execute_script("arguments[0].focus();", caja_texto)
    caja_texto.clear()
    caja_texto.send_keys(busqueda) 
    print(f"Filtrando por: {busqueda}")
    boton_buscar = driver.find_element(By.XPATH, "//button[contains(., 'Buscar Trabajo')]")
    boton_buscar.click()
    print("Búsqueda realizada. Cargando resultados...")
 
    time.sleep(5) 

    print("Extrayendo datos de la lista...")
    bloques_ofertas = driver.find_elements(By.CSS_SELECTOR, "div.p-3.border.rounded.mb-3.bg-white")

    lista_final = []
    num_pagina =1;
    while True:
        print(f"--- Procesando Página {num_pagina} ---")
        time.sleep(3) 

        bloques = driver.find_elements(By.CSS_SELECTOR, "div.p-3.border.rounded.mb-3.bg-white")
        
        for bloque in bloques:
            try:
                elemento_titulo = bloque.find_element(By.CLASS_NAME, "text-cyan-700")
                titulo = elemento_titulo.text
                enlace = elemento_titulo.get_attribute("href")
                empresa = bloque.find_element(By.CLASS_NAME, "text-primary").text
                detalles = bloque.find_element(By.CLASS_NAME, "col-lg-3").text
                
                lista_final.append({
                    "Puesto": titulo,
                    "Empresa": empresa,
                    "Detalles": detalles.replace("\n", " | "),
                    "Enlace": enlace
                })
            except:
                continue
        
        try:
            boton_siguiente = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Next') or contains(text(), 'siguiente')]")
            
            driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
            time.sleep(1)
            
            driver.execute_script("arguments[0].click();", boton_siguiente)
            
            num_pagina += 1
        except:
            print(f"Fin de la búsqueda. No hay más páginas después de la {num_pagina}.")
            break 

    if lista_final:
        df = pd.DataFrame(lista_final)
        df.to_csv(ruta_completa, index=False, encoding="utf-8-sig")
        print(f"¡Proceso terminado! Archivo generado: {ruta_completa}")
        print(f"Se han extraído {len(lista_final)} ofertas.")

finally:
    driver.quit()