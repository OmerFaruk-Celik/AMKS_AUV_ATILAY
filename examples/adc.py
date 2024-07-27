import numpy as np
import pyaudio
import matplotlib.pyplot as plt

# Ses parametreleri
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# PyAudio nesnesini başlat
p = pyaudio.PyAudio()

# Akışı başlat
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

def update_frame(frame):
    # Ses verilerini oku
    data = stream.read(CHUNK, exception_on_overflow=False)
    # Verileri int16 formatına çevir
    data_int = np.frombuffer(data, dtype=np.int16)

    # Verileri görselleştir
    plt.plot(data_int)
    plt.title('Mikrofon Sinyali')
    plt.xlabel('Örnek Numarası')
    plt.ylabel('Genlik')
    plt.show()

# Akışı kapat
stream.stop_stream()
stream.close()
p.terminate()

