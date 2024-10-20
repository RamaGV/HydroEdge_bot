from datetime import datetime
import zipfile
import os
import re
import pymongo
from time import sleep
import threading

class HistoryZipProcessor:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.state = "INIT"
    
    #                                        #
    #       FSM - Finite State Machine       #
    #                                        #
    
    def run(self):
        while True:
            self.display_status()
            sleep(1)
            
            if self.state == "INIT":
                self.init_state()
            elif self.state == "PROCESS_FILES":
                self.process_files_state()
            elif self.state == "PROCESS_DIRECTORIES":
                self.process_directories_state()
            elif self.state == "END":
                self.end_state()
                break
    
    def get_current_action(self):
        if self.state == "INIT":
            return "Inicializando el procesador"
        elif self.state == "PROCESS_FILES":
            return "Procesando archivos ZIP en /data/historiales"
        elif self.state == "PROCESS_DIRECTORIES":
            return "Clasificando directorios de contactos"
        elif self.state == "END":
            return "Proceso finalizado"
        return "Esperando..."
    
    def display_status(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        header = "FSM - WhatsApp History Processor"
        action = self.get_current_action()
        status_line = "ESTADO ACTUAL> {}".format(self.state)
        border = "*" * 73
        
        print(border)
        print("**{:^69}**".format(header))
        print(border)
        print("** {:<68} **".format(status_line))
        print("** {:<68} **".format(action))
        print(border)
    
    #                                        #
    #    Métodos de estados y transiciones   #
    #                                        #
    
    def init_state(self):
        self.state = "PROCESS_FILES"
    
    def process_files_state(self):
        # Procesar todos los archivos .zip del directorio base
        
        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".zip"):
                    # Crear un hilo para procesar cada archivo de forma independiente
                    
                    processing_thread = threading.Thread(target=self.process_zip, args=(entry.path,))
                    processing_thread.start()
                    processing_thread.join()
        
        self.state = "PROCESS_DIRECTORIES"
    
    def process_directories_state(self):
        # Clasificar los directorios de contactos
        
        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Crear un hilo para procesar cada directorio de forma independiente
                    
                    processing_thread = threading.Thread(target=self.process_directory, args=(entry.path,))
                    processing_thread.start()
                    processing_thread.join()
                    
        self.state = "END"

    def end_state(self):
        # Eliminar todos los archivos .zip del directorio base

        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.zip'):
                    os.remove(entry.path)
    
    #                                        #
    #   Thread - Procesamiento de archivos   #
    #                                        #
    
    def process_zip(self, zip_file_path):
        # Descomprimir el archivo .zip y crear una carpeta para cada contacto
        print("Procesando archivo: {}".format(zip_file_path))
        sleep(2)

        zip_filename = os.path.basename(zip_file_path)
        contacto = self.obtener_contacto(zip_filename)
        if contacto:
            output_dir = self.crear_carpeta(contacto, self.base_directory)
            self.descomprimir(zip_file_path, output_dir)
    
    def obtener_contacto(self, zip_filename):
        # Extraer el nombre de contacto del nombre del archivo .zip
        
        match = re.search(r'Chat de WhatsApp con (.+)\.zip', zip_filename)
        if match:
            contacto = match.group(1).strip()
            return contacto
        return None
    
    def crear_carpeta(self, contacto, output_base_dir):
        # Crear una carpeta para el contacto
        
        output_dir = os.path.join(output_base_dir, contacto)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def descomprimir(self, zip_file_path, output_dir):
        # Descomprimir el archivo .zip en la carpeta correspondiente
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
    
    #                                        #
    #   Thread - Clasificación de archivos   #
    #                                        #

    def process_directory(self, directory_path):
        # Crear subcarpetas y clasificar los archivos del directorio correspondiente
        print("Clasificando directorio: {}".format(directory_path))
        sleep(2)

        self.crear_subcarpetas(directory_path)
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    self.clasificar_archivo(entry, directory_path)
                    nombre_de_carpeta = os.path.basename(directory_path)
    
    def crear_subcarpetas(self, dir_path):
        # Crear subcarpetas para organizar archivos dentro del directorio de contacto
        
        subfolders = ["audios", "images", "otros"]
        for subfolder in subfolders:
            os.makedirs(os.path.join(dir_path, subfolder), exist_ok=True)
    
    def clasificar_archivo(self, entry, directory_path):
        # Clasificar archivo individual según su tipo
        
        if entry.name.endswith('.txt'):
            # Renombrar archivo .txt a 'historial.txt'
            new_name = "historial.txt"
            os.rename(entry.path, os.path.join(directory_path, new_name))
        elif entry.name.endswith('.opus'):
            # Mover archivo .opus a la carpeta 'audios'
            os.rename(entry.path, os.path.join(directory_path, "audios", entry.name))
        elif entry.name.endswith('.jpg'):
            # Mover archivo .jpg a la carpeta 'images'
            os.rename(entry.path, os.path.join(directory_path, "images", entry.name))
        else:
            # Mover cualquier otro archivo a la carpeta 'otros'
            os.rename(entry.path, os.path.join(directory_path, "otros", entry.name))
    
    def crear_contacto(self, nombre_de_carpeta):
        # Crear contacto en MongoDB
        
        pass

    #                                        #
    #             Ejemplo de uso             #
    #                                        #

    # directory_historiales = "C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales"
    # processor = HistoryZipProcessor(directory_historiales)
    # processor.run()

class ContactProcessor:
    def __init__(self, mongodb_uri: str, database_name: str, base_directory: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.base_directory = base_directory
        self.state = "INIT"
        
        # Ejemplo de uso del procesador
        # directory_historiales = "C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales"
        # processor = ContactProcessor("mongodb://localhost:27017/", "whatsapp_db", directory_historiales)
        # processor.run()
    
    #                                        #
    #       FSM - Finite State Machine       #
    #                                        #
    
    def run(self):
        while True:
            self.display_status()
            sleep(1)
            
            if self.state == "INIT":
                self.init_state()
            elif self.state == "PROCESS_FILES":
                self.process_files_state()
            elif self.state == "END":
                self.end_state()
                break
    
    def get_current_action(self):
        if self.state == "INIT":
            return "Inicializando el procesador"
        elif self.state == "PROCESS_FILES":
            return "Procesando archivos ZIP en el directorio"
        elif self.state == "END":
            return "Proceso finalizado"
        return "Esperando..."
    
    def display_status(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        header = "FSM - WhatsApp History Processor"
        action = self.get_current_action()
        status_line = "ESTADO ACTUAL> {}".format(self.state)
        border = "*" * 73
        
        print(border)
        print("**{:^69}**".format(header))
        print(border)
        print("** {:<68} **".format(status_line))
        print("** {:<68} **".format(action))
        print(border)
    
    #                                        #
    #    Métodos de estado y transiciones    #
    #                                        #
    
    def init_state(self):
        self.state = "PROCESS_FILES"
    
    def process_files_state(self):
        # Procesar todos los archivos .zip del directorio base

        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".zip"):
                    zip_file_path = entry.path
                    
                    # Crear un hilo para procesar cada archivo de forma independiente
                    processing_thread = threading.Thread(target=self.process_zip, args=(zip_file_path,))
                    processing_thread.start()
                    processing_thread.join()
        
        self.state = "END"
    
    def end_state(self):
        # Eliminar todos los archivos .zip del directorio base

        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.zip'):
                    os.remove(entry.path)
    
    #                                        #
    #   Métodos de procesamiento paralelo    #
    #                                        #
    





























"""
def procesar_historial_chat(txt_file_path):
    print(f"Procesando historial de chat de '{txt_file_path}'...")
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
        mensajes = []
        mensaje_actual = ''
        for line in txt_file:
            line = line.rstrip('\n')
            if re.match(r'^\d{1,2}/\d{1,2}/\d{4},', line):
                if mensaje_actual:
                    mensajes.append(mensaje_actual)
                mensaje_actual = line
            else:
                # Línea que continúa el mensaje anterior
                mensaje_actual += '\n' + line

        # Procesar el último mensaje
        if mensaje_actual:
            mensajes.append(mensaje_actual)

    # Procesar cada mensaje completo
    for mensaje in mensajes:
        procesar_linea(mensaje)

def procesar_linea(mensaje):
    if not mensaje.strip():
        return  # Ignorar mensajes vacíos

    # Normalizar espacios y caracteres especiales
    mensaje = mensaje.replace('\u202F', ' ')  # Reemplazar espacios estrechos de no separación
    mensaje = mensaje.replace('\u200e', '')   # Eliminar marcas de izquierda a derecha
    mensaje = mensaje.strip()

    # Expresión regular para extraer fecha, hora, periodo, remitente y contenido
    pattern = r'^(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2})\s*([ap]\.?\s*m\.?)\s*-\s*(.+?): (.*)'
    match = re.match(pattern, mensaje, re.DOTALL | re.UNICODE)
    if match:
        fecha = match.group(1)
        hora = match.group(2)
        periodo = match.group(3)
        remitente = match.group(4)
        contenido = match.group(5)

        # Normalizar el periodo (AM/PM)
        periodo = periodo.lower().replace('.', '').replace(' ', '')
        if periodo in ['am', 'a.m', 'a.m.']:
            periodo = 'AM'
        elif periodo in ['pm', 'p.m', 'p.m.']:
            periodo = 'PM'
        else:
            print(f"Periodo desconocido: {periodo}")
            return

        # Convertir la fecha y hora a un objeto datetime
        try:
            timestamp = datetime.strptime(f"{fecha} {hora} {periodo}", '%d/%m/%Y %I:%M %p')
        except ValueError as e:
            print(f"Error al convertir la fecha y hora: {fecha} {hora} {periodo} - {e}")
            return

        # Separar el contenido del adjunto y el texto adicional
        adjunto = None
        texto_adicional = None

        # Verificar si hay un adjunto al inicio del contenido
        adjunto_pattern = r'^\u200e?([\w-]+\.\w{3,4}) \(archivo adjunto\)'
        adjunto_match = re.match(adjunto_pattern, contenido)

        if adjunto_match:
            adjunto = adjunto_match.group(1)
            # Obtener cualquier texto adicional
            texto_adicional = contenido[adjunto_match.end_state():].strip()
            if texto_adicional:
                contenido = texto_adicional
            else:
                contenido = ''
        else:
            adjunto = None  # No hay adjunto

        # Determinar el tipo de mensaje
        if adjunto:
            # Obtener la extensión del archivo para determinar el tipo
            extension = adjunto.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif']:
                message_type = 'image'
            elif extension in ['opus', 'mp3', 'wav', 'm4a']:
                message_type = 'audio'
            elif extension in ['mp4', 'mov', 'avi']:
                message_type = 'video'
            else:
                message_type = 'file'

            print(f"[{timestamp}] {message_type.capitalize()} de {remitente}: {contenido}")
            # almacenar_mensaje(remitente, timestamp, contenido, message_type=message_type, attachment=adjunto)
        else:
            message_type = 'text'
            print(f"[{timestamp}] Mensaje de {remitente}: {contenido}")
            # almacenar_mensaje(remitente, timestamp, contenido, message_type=message_type)
    else:
        print(f"Línea no coincidente o no válida: {mensaje}")

def almacenar_mensaje(remitente, timestamp, contenido, message_type='text', attachment=None):
    # Crear el documento del mensaje
    mensaje = {
        "remitente": remitente,
        "timestamp": timestamp,
        "message_type": message_type,
        "content": contenido,
        "attachment": attachment,
        "processed": False
    }

    # Asegurarse de que el mensaje se inserta correctamente en la base de datos
    try:
        mensajes_collection.insert_one(mensaje)
        print(f"Mensaje de {remitente} almacenado en la base de datos.")
    except pymongo.errors.PyMongoError as e:
        print(f"Error al almacenar el mensaje en la base de datos: {e}")


# Ejemplo de uso
txt_file_path = 'C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales/+598 98 453 709/Chat de WhatsApp con +598 98 453 709.txt'
procesar_historial_chat(txt_file_path)


def convertir_audio(audio_path):
    if audio_path.endswith(".opus"):
        converted_path = os.path.splitext(audio_path)[0] + ".mp3"
        try:
            print(f"Iniciando conversión de {audio_path} a formato MP3...")
            subprocess.run(["ffmpeg", "-i", audio_path, converted_path], check=True)
            print(f"Archivo convertido exitosamente a: {converted_path}")
            return converted_path
        except subprocess.CalledProcessError as e:
            print(f"Error al convertir el archivo: {e}")
            return None
        except FileNotFoundError:
            print("Error: ffmpeg no está instalado o no se encuentra en el PATH del sistema. Puedes instalar ffmpeg siguiendo las instrucciones en https://ffmpeg.org/download.html y asegurándote de agregarlo al PATH de tu sistema.")
            return None
    else:
        print(f"El archivo {audio_path} no requiere conversión.")
        return audio_path

def transcribir_audio(audio_path):
    # Convertir el archivo si es necesario
    audio_path = convertir_audio(audio_path)
    if not audio_path:
        return
    
    # Transcribir el archivo de audio completo usando la API de OpenAI
    try:
        print(f"Iniciando transcripción del archivo {audio_path}...")
        with open(audio_path, "rb") as audio_file:
            response = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        print(f"Transcripción del archivo {audio_path}:{response['text']}")
    except Exception as e:
        print(f"Error al transcribir el archivo {audio_path}: {e}")

"""