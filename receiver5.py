import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Ayarlar
SAMPLE_RATE = 44100  # Örnekleme hızı (Hz)
NUM_SAMPLES = 2000   # Örnek sayısı
FORMAT = pyaudio.paInt16  # Veri formatı (16-bit PCM)
CHANNELS = 1  # Kanal sayısı (mono)

# PyAudio nesnesi oluştur
audio = pyaudio.PyAudio()

# Ses akışını başlat
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=NUM_SAMPLES)

fig, ax = plt.subplots()
x = np.arange(0, NUM_SAMPLES)
line, = ax.plot(x, np.random.rand(NUM_SAMPLES))

def update(frame):
    data = stream.read(NUM_SAMPLES)
    samples = np.frombuffer(data, dtype=np.int16)
    
    # Fourier dönüşümünü uygula
    fft_result = np.fft.fft(samples)
    frequencies = np.fft.fftfreq(len(fft_result), 1 / SAMPLE_RATE)
    
    # Baskın frekansı bul
    magnitude = np.abs(fft_result)
    dominant_frequency = frequencies[np.argmax(magnitude)]
    
    print(f"Baskın frekans: {dominant_frequency} Hz")
    
    # Grafiği güncelle
    line.set_ydata(samples)
    return line,

ani = FuncAnimation(fig, update, blit=True)
plt.show()

# Temizleme işlemi
stream.stop_stream()
stream.close()
audio.terminate()
