# whisper_loader.py
import whisper
import torch
import os
import subprocess
import warnings
from dotenv import load_dotenv
import aiohttp
import asyncio

# Ignorar la advertencia de FP16 en CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Verificar disponibilidad de CUDA
print(f"CUDA disponible: {torch.cuda.is_available()}")

# Cargar el modelo Whisper
def load_whisper_model(model_name="small"):
    print("Cargando modelo Whisper...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_name, device=device)
    print(f"Modelo cargado exitosamente.")
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
            subprocess.run(
                ["ffmpeg", "-y", "-i", audio_path, converted_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
            print(f"Archivo convertido exitosamente a: {converted_path}")
            return converted_path
        except subprocess.CalledProcessError as e:
            print(f"Error al convertir el archivo: {e}")
            return None
        except FileNotFoundError:
            print("Error: ffmpeg no está instalado o no se encuentra en el PATH del sistema.")
            return None
    else:
        print(f"El archivo {audio_path} no requiere conversión.")
        return audio_path

def transcribir_audio(model, audio_path, language='es') -> str:
    """
    Transcribe el archivo de audio usando el modelo Whisper.
    Args:
        model: El modelo Whisper cargado.
        audio_path (str): Ruta del archivo de audio.
        language (str): Idioma para la transcripción.
    Returns:
        str: Texto de la transcripción, o None si hubo un error.
    """
    if not audio_path:
        return None

    try:
        print(f"Iniciando transcripción del archivo {audio_path}...")
        
        result = model.transcribe(audio_path, language=language)
        text = result['text']
        
        return text
    except Exception as e:
        print(f"Error al transcribir el archivo {audio_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_transcription(text, transcription_path):
    """
    Guarda la transcripción en un archivo de texto.
    Args:
        text (str): Texto de la transcripción.
        transcription_path (str): Ruta donde guardar la transcripción.
    """
    with open(transcription_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Transcripción guardada en {transcription_path}.")
