# test.py
<<<<<<< HEAD
import whisper_loader
=======
import app.whisper_loader as whisper_loader
>>>>>>> 54a2905435697338071f8ecd8469d96d97786f76
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
