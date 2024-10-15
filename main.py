# main
from driver_setup import configurar_driver
from whatsapp.whatsapp import WhatsAppWeb
from db_manager import cargar_contacto
from whatsapp.ui import WhatsAppUI
from whatsapp.contacto import Contacto
import time
import logging
from whatsapp.maquina_estados import Estado

INIT = Estado.INIT
STAND_BY = Estado.STAND_BY
PROCESAR_PANEL = Estado.PROCESAR_PANEL
AGREGAR_CONTACTOS = Estado.AGREGAR_CONTACTOS
ACTUALIZAR_CONTACTOS = Estado.ACTUALIZAR_CONTACTOS


def inicializar():
    representante = cargar_contacto("Gregorio")
    if not representante or not isinstance(representante, Contacto):
        logging.error("No se pudo encontrar el representante 'Gregorio' o no es un Contacto válido. Terminando el proceso.")
        return None, False
    whatsapp = WhatsAppWeb(configurar_driver(), representante)
    ui = WhatsAppUI(whatsapp)
    ui.abrir_whatsapp_web()
    time.sleep(2)
    return whatsapp, True


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("whatsapp_scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    estado = INIT
    whatsapp = None
    lista_contactos = []

    try:
        while True:
            if estado == INIT:
                whatsapp, success = inicializar()
                time.sleep(2)
                if not success:
                    break
                estado = STAND_BY
            
            elif estado == STAND_BY:
                estado = Estado.standby(whatsapp)
            
            elif estado == PROCESAR_PANEL:
                estado, lista_contactos = Estado.procesar_panel(whatsapp)
            
            elif estado == AGREGAR_CONTACTOS:
                estado = Estado.agregar_contactos(whatsapp, lista_contactos)
            
    
    except Exception as e:
        logging.error(f"Se produjo un error en el script: {e}")
    finally:
        if whatsapp:
            whatsapp.driver.quit()


if __name__ == "__main__":
    main()