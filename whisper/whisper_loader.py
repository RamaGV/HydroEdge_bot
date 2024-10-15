# whisper_loader.py
import whisper
import torch
import warnings

# Ignorar la advertencia de FP16 en CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def load_whisper_model(model_name="small"):
    print("Loading Whisper model...")
    # Seleccionar dispositivo: GPU si está disponible, de lo contrario, CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_name, device=device)
    print(f"Model loaded successfully on {device}!")
    return model

def transcribe_audio(model, audio_path):
    result = model.transcribe(audio_path)
    return result['text']

def translate_audio(model, audio_path, target_language="es"):
    result = model.transcribe(audio_path, task="translate", language=target_language)
    return result['text']
