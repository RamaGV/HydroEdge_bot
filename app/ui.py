from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

from whatsapp import WhatsAppWeb

class WhatsAppUI:
    def __init__(self, WhatsappWeb: WhatsAppWeb):
        self.WhatsappWeb = WhatsappWeb
        self.driver = WhatsappWeb.getDriver()
        self.PATHS = {
            "panel": '//*[@id="pane-side"]',
            "contactos": '//*[@id="pane-side"]//div[@role="listitem"]',
            "contacto_nombre": './/span[contains(@class, "_ccCW") or contains(@class, "x1iyjqo2")]',
            "nuevo_mensaje": './/span[@aria-label][contains(@aria-label, "no leído") or contains(@aria-label, "no leídos")]',
            "search_box": '//div[@role="textbox" and contains(@class, "x1whj5v")]',
            "message_box": '//div[@role="textbox" and @aria-placeholder="Escribe un mensaje"]',
            "send_element": '//button[@aria-label="Enviar"]'
        }
    
    def abrir_whatsapp_web(self):
        self.driver.get("https://web.whatsapp.com/")
        try:
            wait = WebDriverWait(self.driver, 60)
            wait.until(EC.presence_of_element_located((By.XPATH, self.PATHS["panel"])))
        except Exception as e:
            self.driver.quit()
            raise
    
    def obtener_lista_contactos(self):
        lista_contactos = []
        try:
            contactos = self.driver.find_elements(By.XPATH, self.PATHS["contactos"])
            for contacto in contactos:
                nombre_contacto = contacto.find_element(By.XPATH, self.PATHS["contacto_nombre"]).get_attribute("title")
                lista_contactos.append(nombre_contacto)

            logging.info(f"Lista de contactos obtenida: {lista_contactos}")
            return lista_contactos
        except Exception as e:
            logging.error(f"Error al obtener lista de contactos: {e}")
            return []
        
    def buscar_contacto(self, nombre):
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, self.PATHS["panel"])))
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, self.PATHS["search_box"])))
            
            search_box.clear()
            search_box.send_keys(nombre)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            return True
        except Exception as e:
            logging.error(f"Error al buscar el contacto '{nombre}': {e}")
            return False

    def enviar_mensaje(self, mensaje):
        try:
            wait = WebDriverWait(self.driver, 10)
            message_box = wait.until(EC.presence_of_element_located((By.XPATH, self.PATHS["message_box"])))
            message_box.click()
            message_box.send_keys(mensaje)
            time.sleep(2)

            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, self.PATHS["send_element"])))
            send_button.click()
            time.sleep(2)
            logging.info(f"Mensaje enviado.")
        except Exception as e:
            logging.error(f"Error al enviar el mensaje: {e}")
    
    """
    def buscar_mensajes(self):
        contactos_con_buscar_mensajes = []
        try:
            contactos = self.driver.find_elements(By.XPATH, self.PATHS["contactos"])
            for contacto in contactos:
                if contacto.find_elements(By.XPATH, self.PATHS["nuevo_mensaje"]):
                    nombre_contacto = contacto.find_element(By.XPATH, self.PATHS["contacto_nombre"]).get_attribute("title")
                    contactos_con_buscar_mensajes.append(nombre_contacto)

            logging.info(f"Contactos con nuevos mensajes: {contactos_con_buscar_mensajes}")
            return contactos_con_buscar_mensajes
        except Exception as e:
            logging.error(f"Error al obtener contactos con nuevos mensajes: {e}")
            return []
    
    def archivar_contacto(self, nombre):
        contacto = self.buscar_contacto(nombre)
        if contacto:
            contacto.click()
            try:
                wait = WebDriverWait(self.driver, 10)
                menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, self.PATHS["submenu_button"])))
                menu_button.click()
                archive_button = wait.until(EC.element_to_be_clickable((By.XPATH, self.PATHS["archive_chat"])))
                archive_button.click()
                logging.info(f"Chat con '{nombre}' archivado")
            except Exception as e:
                logging.error(f"Error al archivar el chat con '{nombre}': {e}")
        else:
            logging.warning(f"No se puede archivar el chat, contacto '{nombre}' no encontrado")

"""
