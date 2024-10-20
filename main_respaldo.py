# main
from driver_setup import configurar_driver
from db_manager import cargar_contacto
from whatsapp.contacto import Contacto
from whatsapp.maquina_estados import Estado
import whatsapp.utils as ut

INIT = Estado.INIT
STAND_BY = Estado.STAND_BY
PROCESAR_PANEL = Estado.PROCESAR_PANEL
AGREGAR_CONTACTOS = Estado.AGREGAR_CONTACTOS
ACTUALIZAR_CONTACTOS = Estado.ACTUALIZAR_CONTACTOS

# Cargar el modelo Whisper

# Transcribir todos los archivos de audio en el directorio especificado
directory_historiales = "C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales"
#model_whisper = wis.load_whisper_model("small")

def inicializar():
    pass
    """
    representante = cargar_contacto("Gregorio")
    if not representante or not isinstance(representante, Contacto):
        logging.error("No se pudo encontrar el representante 'Gregorio' o no es un Contacto válido. Terminando el proceso.")
        return None, False
    whatsapp = WhatsAppWeb(configurar_driver(), representante)
    ui = WhatsAppUI(whatsapp)
    ui.abrir_whatsapp_web()
    time.sleep(2)
    return whatsapp, True"""

def main():

    #ut.procesar_archivos(directory_historiales)
    text_file_path = 'C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales/+598 98 453 709/Chat de WhatsApp con +598 98 453 709.txt'
    ut.procesar_historial_chat(text_file_path)

    
    """
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
            whatsapp.driver.quit()"""


if __name__ == "__main__":
    main()