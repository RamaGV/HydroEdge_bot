import pymongo
from pymongo import MongoClient
from bson import ObjectId

class DBManager:
    def __init__(self, mongodb_uri: str, database_name: str):
        # Conectar a la base de datos
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.contactos_collection = self.db['contactos']
        self.mensajes_collection = self.db['mensajes']
        print(f"Conectado a la base de datos: {database_name}")

    def cargar_contacto(self, contacto_data: dict):
        # Cargar un nuevo contacto en la base de datos
        filtro = {"numero_telefono": contacto_data.get("numero_telefono")}
        contacto_existente = self.contactos_collection.find_one(filtro)

        if contacto_existente:
            print(f"El contacto ya existe: {contacto_data.get('numero_telefono')}")
        else:
            resultado = self.contactos_collection.insert_one(contacto_data)
            print(f"Contacto creado con ID: {resultado.inserted_id}")

    def actualizar_contacto(self, contacto_id: ObjectId, nuevos_datos: dict):
        # Actualizar un contacto existente en la base de datos
        filtro = {"_id": ObjectId(contacto_id)}
        actualizacion = {"$set": nuevos_datos}
        resultado = self.contactos_collection.update_one(filtro, actualizacion)

        if resultado.matched_count > 0:
            print(f"Contacto con ID {contacto_id} actualizado correctamente.")
        else:
            print(f"No se encontró el contacto con ID {contacto_id} para actualizar.")

    def cargar_mensaje(self, mensaje_data: dict):
        # Cargar un nuevo mensaje en la base de datos
        resultado = self.mensajes_collection.insert_one(mensaje_data)
        print(f"Mensaje creado con ID: {resultado.inserted_id}")

    def cerrar_conexion(self):
        # Cerrar la conexión a la base de datos
        self.client.close()
        print("Conexión a la base de datos cerrada")

# Ejemplo de uso
"""
if __name__ == "__main__":
    mongodb_uri = "mongodb://localhost:27017/"
    database_name = "whatsapp_db"
    db_manager = DBManager(mongodb_uri, database_name)

    # Crear un contacto de ejemplo
    contacto_data = {
        "nombre": "Gregorio Martínez",
        "numero_telefono": "+598 98 453 709",
        "alias": "Greg",
        "estado": "nuevo"
    }
    db_manager.cargar_contacto(contacto_data)

    # Actualizar el contacto
    nuevos_datos = {"estado": "activo"}
    db_manager.actualizar_contacto(contacto_data.get("_id"), nuevos_datos)

    # Cerrar la conexión
    db_manager.cerrar_conexion()
"""