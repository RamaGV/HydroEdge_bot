# main.py
import os
import tkinter as tk
import sounddevice as sd
import numpy as np
import whisper_loader
import scipy.io.wavfile as wav

# Cargar el modelo Whisper
model = whisper_loader.load_whisper_model("small")

# Variable para el manejo de la grabación
is_recording = False
recording = None
sample_rate = 44100

def record_audio():
    global is_recording, recording
    duration = 5  # Duración inicial de la grabación en segundos (puede cambiarse)
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    is_recording = True
    sd.wait()  # Espera a que termine la grabación si se detiene manualmente
    save_audio()

def stop_recording():
    global is_recording
    if is_recording:
        sd.stop()
        is_recording = False
        print("Recording stopped.")
        save_audio()

def save_audio():
    # Guardar el audio en la misma carpeta que main.py
    output_path = os.path.join(os.path.dirname(__file__), "recorded_audio.wav")
    wav.write(output_path, sample_rate, np.array(recording))
    print(f"Recording saved at {output_path}.")
    transcribe_audio(output_path)

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

# Interfaz gráfica
root = tk.Tk()
root.title("Whisper Audio Recorder")

# Botón para empezar la grabación
record_button = tk.Button(root, text="Start Recording", command=record_audio)
record_button.pack(pady=10)

# Botón para detener la grabación
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack(pady=10)

# Iniciar la interfaz gráfica
root.mainloop()
