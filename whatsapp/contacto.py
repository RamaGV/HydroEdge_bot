from datetime import datetime

class Contacto:
    def __init__(self, celular, nombre=None, estado="PENDIENTE", ultimo_mensaje=None, fecha_ultimo_mensaje=None, mensajes_no_leidos=0, historial_txt=None):
        self.celular = celular
        self.nombre = nombre
        self.estado = estado
        self.ultimo_mensaje = ultimo_mensaje
        self.fecha_ultimo_mensaje = fecha_ultimo_mensaje or datetime.now().isoformat()
        self.mensajes_no_leidos = mensajes_no_leidos
        self.historial_txt = historial_txt or f"historial_{self.celular}.txt"

    def __str__(self):
        return (
            f"Nombre: {self.nombre}, Celular: {self.celular}, Estado: {self.estado}, "
            f"Último Mensaje: {self.ultimo_mensaje}, Fecha Último Mensaje: {self.fecha_ultimo_mensaje}, "
            f"Mensajes No Leídos: {self.mensajes_no_leidos}, Historial TXT: {self.historial_txt}"
        )
