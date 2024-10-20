# db_manager.py
from whatsapp.contacto import Contacto
from pymongo import MongoClient
import logging

# Configuración de la conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.whatsapp_db
chats_collection = db.chats

def cargar_contacto(nombre):
    # Busca el contacto en la base de datos por su nombre
    resultado = chats_collection.find_one({"nombre": nombre})
    
    if resultado:
        # Crea y devuelve una instancia de Contacto usando los datos de la base de datos
        return Contacto(
            nombre=resultado["nombre"],
            celular=resultado["celular"],
            estado=resultado.get("estado", "activo"),
            ultimo_mensaje=resultado.get("ultimo_mensaje"),
            fecha_ultimo_mensaje=resultado.get("fecha_ultimo_mensaje"),
            mensajes_no_leidos=resultado.get("mensajes_no_leidos", 0),
            historial_txt=resultado.get("historial_txt", f"historial_{resultado['celular']}.txt")
        )
    else:
        # Si no se encuentra el contacto, devuelve None y muestra un mensaje de advertencia
        logging.warning(f"No se encontró un contacto con el nombre: {nombre}")
        return None

def actualizar_contacto(contacto):
    # Busca si el contacto ya existe en la base de datos
    resultado = chats_collection.find_one({"nombre": contacto.nombre})
    
    if resultado:
        # Si el contacto existe, actualiza la información
        chats_collection.update_one(
            {"nombre": contacto.nombre},
            {"$set": {
                "celular": contacto.celular,
                "estado": contacto.estado,
                "ultimo_mensaje": contacto.ultimo_mensaje,
                "fecha_ultimo_mensaje": contacto.fecha_ultimo_mensaje,
                "mensajes_no_leidos": contacto.mensajes_no_leidos,
                "historial_txt": contacto.historial_txt
            }}
        )
        logging.info(f"Contacto '{contacto.nombre}' actualizado en la base de datos.")
    else:
        # Si el contacto no existe, inserta un nuevo registro
        nuevo_contacto = {
            "nombre": contacto.nombre,
            "celular": contacto.celular,
            "estado": contacto.estado,
            "ultimo_mensaje": contacto.ultimo_mensaje,
            "fecha_ultimo_mensaje": contacto.fecha_ultimo_mensaje,
            "mensajes_no_leidos": contacto.mensajes_no_leidos,
            "historial_txt": contacto.historial_txt
        }
        chats_collection.insert_one(nuevo_contacto)
        logging.info(f"Nuevo contacto '{contacto.nombre}' agregado a la base de datos.")
