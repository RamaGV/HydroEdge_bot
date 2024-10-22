# test.py
import whisper_loader
import os

# Cargar el modelo Whisper
model = whisper_loader.load_whisper_model("small")

# Variable para el manejo de la grabación
is_recording = False
recording = None
sample_rate = 44100

def transcribe_audio(audio_path):
    text = whisper_loader.transcribe_audio(model, audio_path)
    print("Transcription:", text)
    save_transcription(text)

def save_transcription(text):
    # Guardar la transcripción en un archivo de texto
    transcription_path = os.path.join(os.path.dirname(__file__), "transcription.txt")
    with open(transcription_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Transcription saved at {transcription_path}.")
