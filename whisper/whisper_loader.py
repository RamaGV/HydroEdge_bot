import whisper
import torch
import os
import subprocess
import warnings
from dotenv import load_dotenv

# Ignorar la advertencia de FP16 en CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Cargar variables de entorno desde el archivo .env
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cargar el modelo Whisper
def load_whisper_model(model_name="small"):
    print("Loading Whisper model...")
    # Seleccionar dispositivo: GPU si está disponible, de lo contrario, CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_name, device=device)
    print(f"Model loaded successfully on {device}!")
    return model

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

def transcribir_audio(model, audio_path):
    # Convertir el archivo si es necesario
    audio_path = convertir_audio(audio_path)
    if not audio_path:
        return
    
    # Transcribir el archivo de audio completo usando el modelo Whisper
    try:
        print(f"Iniciando transcripción del archivo {audio_path}...")
        result = model.transcribe(audio_path)
        text = result['text']
        print(f"Transcripción del archivo {audio_path}:
{text}")
        save_transcription(text)
    except Exception as e:
        print(f"Error al transcribir el archivo {audio_path}: {e}")

def save_transcription(text):
    # Guardar la transcripción en un archivo de texto
    transcription_path = os.path.join(os.path.dirname(__file__), "transcription.txt")
    with open(transcription_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Transcripción guardada en {transcription_path}.")
