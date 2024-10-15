# whatsapp/whatsapp_web.py
import logging
from whatsapp.contacto import Contacto
 
class WhatsAppWeb:
    _instance = None

    def __new__(cls, driver, representante, contactos_pendientes=None):
        if cls._instance is None:
            cls._instance = super(WhatsAppWeb, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, driver, representante, contactos_pendientes=None):
        if not hasattr(self, 'driver'):
            self.driver = driver
        # Establece el representante (contacto que atiende)
        if isinstance(representante, Contacto):
            self.representante = representante
        else:
            raise ValueError("El representante debe ser una instancia de la clase Contacto.")
        
        if contactos_pendientes is None:
            self.contactos_pendientes = []
        else:
            if all(isinstance(contacto, str) for contacto in contactos_pendientes):
                self.contactos_pendientes = contactos_pendientes
            else:
                raise ValueError("Todos los elementos de contactos_pendientes deben ser nombres de contacto (str)")

    def getDriver(self):
        return self.driver

    def set_representante(self, representante):
        if isinstance(representante, Contacto):
            self.representante = representante
            logging.info(f"Representante '{representante.nombre}' asignado.")
        else:
            logging.warning("El representante proporcionado no es una instancia válida de Contacto.")

    def get_representante(self):
        return self.representante

    def agregar_contacto_pendiente(self, nombre_contacto):
        if nombre_contacto not in self.contactos_pendientes:
            self.contactos_pendientes.insert(0, nombre_contacto)
            logging.info(f"Contacto '{nombre_contacto}' agregado a la lista de contactos activos.")
