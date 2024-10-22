from datetime import datetime

class Contacto:
    def __init__(self, numero_telefono: str = None, nombre: str = None):
        self.prioridad = "baja"  # Prioridad del contacto: 'baja', 'alta' o 'VIP'
        self.numero_telefono = numero_telefono  # Número de teléfono del contacto
        self.nombre = nombre  # Nombre del contacto
        self.ultima_conversacion = None  # Fecha y hora de la última conversación (datetime)
        self.etiquetas = []  # Lista de etiquetas para clasificar el contacto
        self.estado = "nuevo"  # Estado actual del contacto
        self.respuesta = ""  # Campo para almacenar una respuesta generada o prevista
        self.path_archivos = {  # Diccionario para las rutas de archivos relacionadas con el contacto
            "contacto": None,
            "historial": None,
            "notas": None,
            "audios": None,
            "imagenes": None,
            "otros": None
        }
    
    # Método para actualizar la última conversación
    def actualizar_ultima_conversacion(self, fecha: datetime):
        self.ultima_conversacion = fecha
    
    # Método para agregar etiquetas
    def agregar_etiqueta(self, etiqueta: str):
        etiquetas_validas = ['potencial', 'activo', 'inactivo', 'nuevo', 'recurrente', 'contacto frío', 'prospecto', 'contacto cálido', 'en curso', ]
        if etiqueta in etiquetas_validas and etiqueta not in self.etiquetas:
            self.etiquetas.append(etiqueta)
    
    # Método para actualizar el estado del contacto
    def actualizar_estado(self, nuevo_estado: str):
        estados_validos = ['pendiente', 'activo', 'archivado', 'nuevo']
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
    
    # Método para asignar rutas de archivos
    def asignar_path_archivos(self, archivo_tipo: str, path: str):
        if archivo_tipo in self.path_archivos:
            self.path_archivos[archivo_tipo] = path
    
    # Método para actualizar la prioridad del contacto
    def actualizar_prioridad(self, nueva_prioridad: str):
        if nueva_prioridad in ['baja', 'alta', 'VIP']:
            self.prioridad = nueva_prioridad
    
    # Método para mostrar un resumen del contacto
    def mostrar_resumen(self):
        resumen = f"Nombre: {self.nombre}, Teléfono: {self.numero_telefono}, Estado: {self.estado}, Prioridad: {self.prioridad}, Última conversación: {self.ultima_conversacion}"
        return resumen
