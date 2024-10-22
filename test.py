import torch
import whisper_loader as whisper_loader

def gpu_info():
    print("GPU disponible:", torch.cuda.is_available())
    print("CUDA disponible:", torch.cuda.is_available())
    print("Versión de PyTorch:", torch.__version__)
    print("Versión de CUDA:", torch.version.cuda)

def convertir_ruta(ruta):
    return ruta.replace("\\", "/")

def whisper(audio_path):
    model = whisper_loader.load_whisper_model("small")
    result = whisper_loader.transcribir_audio(model, audio_path, language="es")
    print(result)

