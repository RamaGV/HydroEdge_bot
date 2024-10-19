from datetime import datetime
import subprocess
import zipfile
import os
import re
import pymongo

# Conexión a MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['whatsapp_db']
mensajes_collection = db['mensajes']

def obtener_contacto(zip_filename):
    """
    Extrae el nombre del contacto del nombre del archivo zip.
    """
    match = re.search(r'Chat de WhatsApp con (.+)\.zip', zip_filename)
    if match:
        return match.group(1).strip()
    return None

def crear_carpeta(contacto, output_base_dir):
    """
    Crea una carpeta con el nombre del contacto si no existe.
    """
    output_dir = os.path.join(output_base_dir, contacto)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def descomprimir(zip_file_path, output_dir):
    """
    Descomprime el archivo zip en la carpeta especificada.
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Archivo '{os.path.basename(zip_file_path)}' descomprimido en '{output_dir}'")

def descomprimir_y_crear(zip_file_path, output_base_dir):
    """
    Procesa el archivo zip para extraer el nombre del contacto, crear la carpeta y descomprimir el contenido.
    """
    zip_filename = os.path.basename(zip_file_path)
    contacto = obtener_contacto(zip_filename)
    if contacto:
        output_dir = crear_carpeta(contacto, output_base_dir)
        descomprimir(zip_file_path, output_dir)
    else:
        print(f"No se pudo extraer el nombre del contacto del archivo '{zip_filename}'")

def procesar_archivos(directory_historiales):
    """
    Recorre todos los archivos zip en el directorio y los procesa.
    """
    with os.scandir(directory_historiales) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".zip"):
                zip_file_path = entry.path
                descomprimir_y_crear(zip_file_path, directory_historiales)

def procesar_historial_chat(txt_file_path):
    """
    Procesa un historial de chat de WhatsApp y lo almacena en MongoDB.
    """
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
    """
    Procesa un mensaje completo del historial de chat.
    """
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
            texto_adicional = contenido[adjunto_match.end():].strip()
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
    """
    Almacena un mensaje en la base de datos de MongoDB.
    """
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
    """
    Convierte un archivo de audio .opus a .mp3 si es necesario.
    Args:
        audio_path (str): Ruta del archivo de audio.
    Returns:
        str: Ruta del archivo convertido o el original si no es necesario convertir.
    """
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

