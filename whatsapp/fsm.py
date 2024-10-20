# maquina_estados.py

from whatsapp.ui import WhatsAppUI
from db_manager import cargar_contacto, actualizar_contacto
from whatsapp.contacto import Contacto
import logging
import time
from enum import Enum

class Estado(Enum):
    INIT = "INIT"
    STAND_BY = "STAND_BY"
    PROCESAR_PANEL = "PROCESAR_PANEL"
    AGREGAR_CONTACTOS = "AGREGAR_CONTACTOS"
    ACTUALIZAR_CONTACTOS = "ACTUALIZAR_CONTACTOS"
    PRUEBA = "PRUEBA"

def estado_standby(whatsapp):
    hay_contactos_pendientes = whatsapp.contactos_pendientes
    time.sleep(2)
    if not hay_contactos_pendientes:
        return Estado.PROCESAR_PANEL
    return Estado.STAND_BY

def estado_procesar_panel(whatsapp):
    ui = WhatsAppUI(whatsapp)
    lista_contactos = ui.obtener_lista_contactos()
    time.sleep(2)
    if not lista_contactos:
        return Estado.STAND_BY, []
    return Estado.AGREGAR_CONTACTOS, lista_contactos

def estado_agregar_contactos(whatsapp, lista_contactos):
    for nombre_contacto in lista_contactos:
        if nombre_contacto not in whatsapp.contactos_pendientes:
            whatsapp.agregar_contacto_pendiente(nombre_contacto)
    return Estado.STAND_BY

# Puedes agregar más funciones para otros estados aquí.