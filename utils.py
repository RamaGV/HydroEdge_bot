# utils.py
import logging

def tomar_captura(driver, nombre_archivo):
    try:
        driver.save_screenshot(nombre_archivo)
        logging.info(f"Captura de pantalla guardada como '{nombre_archivo}'.")
    except Exception as e:
        logging.error(f"No se pudo tomar la captura de pantalla: {e}")
