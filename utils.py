from datetime import datetime
import zipfile
import os
import re
import pymongo
from time import sleep
from db_manager import DBManager
import threading
import whisper_loader


class ContactProcessor:
    
    #                                        #
    #               Pendientes               #
    #                                        #
    
    # Hacer metodo de muestra progresivo cuándo procesa los archivos, Ej: 1 de 5 archivos procesados, archivo actual: audio.mp3 - contacto basename
    
    def __init__(self, base_directory: str, mongodb_uri: str, database_name: str, whisper_model: whisper_loader.load_whisper_model = None):
        self.base_directory = base_directory
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.state = "INIT"
        self.db_manager = None
        self.whisper_model = whisper_model
    
    #                                        #
    #       FSM - Finite State Machine       #
    #                                        #
    
    def run(self):
        while True:
            self.display_status()
            
            if self.state == "INIT":
                self.init_state()
            elif self.state == "PROCESS_CONTACTS":
                self.process_contacts_state()
                
                self.state = "END"
            elif self.state == "SAVE_MESSAGES":
                # Primero PROCESS_CONTACTS, luego SAVE_MESSAGES

                #self.save_messages_state()
                self.state = "END"
            elif self.state == "END":
                self.end_state()
                break

    def get_current_action(self):
        if self.state == "INIT":
            return "Inicializando el procesador"
        elif self.state == "PROCESS_CONTACTS":
            return "Procesando contactos en paralelo"
        elif self.state == "SAVE_MESSAGES":
            return "Guardando mensajes en la base de datos"
        elif self.state == "END":
            return "Proceso finalizado"
        return "Esperando..."
    
    def display_status(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        header = "FSM - Contact Processor"
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
        # Carga y conecta la base de datos
        self.db_manager = DBManager(self.mongodb_uri, self.database_name)
        self.whisper_model = whisper_loader.load_whisper_model("small")
        print(f"Conexión a la base de datos '{self.database_name}' establecida")
        
        self.state = "PROCESS_CONTACTS"
    
    def process_contacts_state(self):
        # Whisper no permite la transcripción en paralelo, por lo que hay que procesar los contactos de manera secuencial
        
        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Procesar directorio de cada contacto
                    
                    self.process_contact(entry.path)
        
        self.state = "SAVE_MESSAGES"
    
    def save_messages_state(self):
        # Procesar y guardar los mensajes de cada contacto
        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Procesar historial de cada contacto
                    self.save_messages(entry.path)
        
        self.state = "END"
    
    def end_state(self):
        # Cerrar la conexión a la base de datos
        self.db_manager.cerrar_conexion()
        print(f"Conexión a la base de datos '{self.database_name}' cerrada")
    
    #                                        #
    #    Proceso de archivos de contactos    #
    #                                        #
    
    def process_contact(self, directory_path):
        # Procesa los archivos dentro de los directorios audios, images y otros
        print(f"Procesando archivos de {directory_path}")
        
        audio_dir = os.path.join(directory_path, 'audios')
        images_dir = os.path.join(directory_path, 'images')
        others_dir = os.path.join(directory_path, 'otros')
        
        for dir_path in [audio_dir, images_dir, others_dir]:
            print(f"Procesando directorio: {dir_path}")
            
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    # Recorre los tres directorios y ejecuta el méotodo correspondiente
                    
                    if dir_path == audio_dir:
                        #self.process_audio(entry.path)
                        pass
                    elif dir_path == images_dir:
                        self.process_images(entry.path)
                        #pass
                    elif dir_path == others_dir:
                        #self.process_other_files(entry.path)
                        pass
    
    def process_audio(self, audio_path):
        # Convierte archivos .opus -> .mp3 y utiliza whisper para transcribir, creando un archivo .txt con el resultado
        # Ejemplo: PTT-20230401-WA0007.opus -> PTT-20230401-WA0007.mp3 -> PTT-20230401-WA0007.txt
        print(f"Procesando audio: {audio_path}")
        
        audio_mp3 = whisper_loader.convertir_audio(audio_path)
        if audio_mp3 is not None:
            os.remove(audio_path)
            print(f"Transcribiendo audio {audio_mp3}")
            text = whisper_loader.transcribir_audio(self.whisper_model, audio_mp3, language='es')
            
            if text is not None:
                # Guardar la transcripción en un archivo .txt con el mismo nombre base
                
                base_name = os.path.splitext(os.path.basename(audio_mp3))[0]
                audio_dir = os.path.dirname(audio_mp3)
                txt_path = os.path.join(audio_dir, f"{base_name}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Transcripción guardada en {txt_path}")
            else:
                print(f"No se pudo transcribir el archivo {os.path.basename(audio_mp3)}")
    
    def process_images(self, image_path):
        # Procesar las imágenes (interpretar, etc.)
        if image_path.endswith('.jpg'):
            print(f"Procesando imágen: {image_path}")
        
        # Implementar lógica de procesamiento de las imágenes
        # Llamar a API de openAI
        # Solicitar la interpretación de la imagen
        # Guardar la interpretación en un archivo .txt
        # Implementar lógica de guardado de la interpretación en un archivo .txt
    
    def process_other_files(self, directory_path):
        # Procesar otros archivos (PDFs, etc.)

        print(f"Procesando otros archivos en {directory_path}")
        pass  # Implementar lógica de procesamiento de otros archivos
    
    #                                        #
    #        Guardar mensajes                #
    #                                        #
    
    def save_messages(self, directory_path):
        # Procesar el historial.txt de cada contacto y guardar los mensajes

        historial_path = os.path.join(directory_path, 'historial.txt')
        if os.path.exists(historial_path):
            print(f"Guardando mensajes desde {historial_path}")
            self.recorrer_lineas(historial_path)
    
    def recorrer_lineas(self, historial_path):
        # Leer líneas del historial y generar/guardar mensajes
        with open(historial_path, 'r', encoding='utf-8') as file:
            for line in file:
                mensaje = self.generar_mensaje(line)
                self.guardar_mensaje(mensaje)
    
    def generar_mensaje(self, linea):
        # Generar un objeto mensaje basado en la línea del historial
        print(f"Generando mensaje: {linea.strip()}")
        pass  # Implementar lógica para generar el mensaje
    
    def guardar_mensaje(self, mensaje):
        # Guardar el mensaje en la base de datos
        print(f"Guardando mensaje: {mensaje}")
        pass  # Implementar lógica para guardar el mensaje en la base de datos
    
    def anexar_mensaje(self, mensaje, historial_path):
        # Anexar el mensaje al archivo de historial.txt
        with open(historial_path, 'a', encoding='utf-8') as file:
            file.write(f"{mensaje}\n")
        print(f"Mensaje anexado en {historial_path}")

class HistoryZipProcessor:
    
    #                                        #
    #               Pendientes               #
    #                                        #
    
    # Procesar en otros .pdf y .webp -> .webp son stickers, podria eliminarlos
    
    def __init__(self, base_directory: str, mongodb_uri: str, database_name: str):
        self.base_directory = base_directory
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.state = "INIT"
        self.db_manager = None
    
    #                                        #
    #       FSM - Finite State Machine       #
    #                                        #
    
    def run(self):
        while True:
            self.display_status()
            
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
        # Carga y conecta la base de datos
        self.db_manager = DBManager(self.mongodb_uri, self.database_name)
        print(f"Conexión a la base de datos '{self.database_name}' establecida")

        self.state = "PROCESS_FILES"
    
    def process_files_state(self):
        # Procesar todos los archivos .zip del directorio base
        
        with os.scandir(self.base_directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".zip"):
                    # Crear un hilo para procesar cada archivo de forma paralela y borrarlo
                    
                    processing_thread = threading.Thread(target=self.process_zip, args=(entry.path,))
                    processing_thread.start()
                    processing_thread.join()
                    os.remove(entry.path)
        
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
        # Cerrar la conexión a la base de datos
        
        if self.db_manager:
            self.db_manager.cerrar_conexion()
            print(f"Conexión a la base de datos '{self.database_name}' cerrada")
    
    #                                        #
    #   Thread - Procesamiento de archivos   #
    #                                        #
    
    def process_zip(self, zip_file_path):
        # Descomprimir el archivo .zip y crear una carpeta para cada contacto
        print("Procesando archivo: {}".format(zip_file_path))
        sleep(.5)
        
        zip_filename = os.path.basename(zip_file_path)
        contacto = self.obtener_contacto(zip_filename)
        if contacto:
            output_dir = self.crear_carpeta(contacto, self.base_directory)
            self.descomprimir(zip_file_path, output_dir)
            self.crear_contacto(contacto)
    
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
    
    def crear_contacto(self, nombre_contacto):
        # Crear contacto en MongoDB
        
        contacto_data = {}
        if nombre_contacto.startswith("+"):
            contacto_data['numero_telefono'] = nombre_contacto
        else:
            contacto_data['nombre'] = nombre_contacto

        self.db_manager.cargar_contacto(contacto_data)
    
    #                                        #
    #   Thread - Clasificación de archivos   #
    #                                        #
    
    def process_directory(self, directory_path):
        # Crear subcarpetas y clasificar los archivos del directorio correspondiente
        print("Clasificando directorio: {}".format(directory_path))
        sleep(.1)

        
        self.crear_subcarpetas(directory_path)
        sleep(.1)
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    self.clasificar_archivos(entry, directory_path)
                    sleep(.1)
    
    def crear_subcarpetas(self, dir_path):
        # Crear subcarpetas para organizar archivos dentro del directorio de contacto
        
        subfolders = ["audios", "images", "otros"]
        for subfolder in subfolders:
            os.makedirs(os.path.join(dir_path, subfolder), exist_ok=True)
    
    def clasificar_archivos(self, entry, directory_path):
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
    
    #                                        #
    #             Ejemplo de uso             #
    #                                        #
    
    # if __name__ == "__main__":
    #     # Directorio donde están los archivos ZIP a procesar
    #     base_directory = "C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales"
    
    #     # Datos de conexión a MongoDB
    #     mongodb_uri = "mongodb://localhost:27017/"
    #     database_name = "whatsapp_db"
    
    #     # Instancia del procesador de archivos ZIP
    #     processor = HistoryZipProcessor(base_directory, mongodb_uri, database_name)
    #     processor.run()




if __name__ == "__main__":
    # Directorio donde están los archivos ZIP a procesar
    base_directory = "C:/Users/ramag/OneDrive/Desktop/HydroEdge/HydroEdge_bot/data/historiales"
    
    # Datos de conexión a MongoDB
    mongodb_uri = "mongodb://localhost:27017/"
    database_name = "whatsapp_db"
    
    # Instancia del procesador de archivos ZIP
    # processor = HistoryZipProcessor(base_directory, mongodb_uri, database_name)
    # processor.run()

    # Instancia del procesador de contactos
    processor = ContactProcessor(base_directory, mongodb_uri, database_name)
    processor.run()


























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