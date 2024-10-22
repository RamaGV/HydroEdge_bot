import torch
import whisper_loader as whisper_loader

def gpu_info():
    print("GPU disponible:", torch.cuda.is_available())
    print("CUDA disponible:", torch.cuda.is_available())
    print("Versión de PyTorch:", torch.__version__)
    print("Versión de CUDA:", torch.version.cuda)

def convertir_ruta(ruta):
    return ruta.replace("\\", "/")

# Ejemplo de uso:

def whisper(audio_path):
    model = whisper_loader.load_whisper_model("small")
    result = whisper_loader.transcribir_audio(model, audio_path, language="es")
    print(result)

ruta_original = r"C:\Users\ramag\OneDrive\Desktop\HydroEdge\HydroEdge_bot\data\historiales\+598 98 453 709\audios\PTT-20230401-WA0007.mp3"
ruta_convertida = convertir_ruta(ruta_original)
print(ruta_convertida)

whisper(ruta_convertida)
