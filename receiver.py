import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import queue
import threading

# Sabitler
sampling_rate = 50000  # Örnekleme frekansı (Hz)
duration = 1.0  # Ses kayıt süresi (saniye)

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    q.put(indata.copy())

def update_plot():
    """Bu fonksiyon kuyruktaki ses verilerini alır ve frekans spektrumunu çizer."""
    plt.ion()
    fig, ax = plt.subplots()
    while True:
        if not q.empty():
            indata = q.get()
            # Fourier dönüşümü
            fft_values = fft(indata[:, 0])
            fft_magnitude = np.abs(fft_values) / len(fft_values)
            freq = np.fft.fftfreq(len(fft_values), d=1/sampling_rate)

            # Sadece pozitif frekansları al
            pos_freq = freq[:len(freq) // 2]
            pos_fft_magnitude = fft_magnitude[:len(fft_magnitude) // 2]

            # Frekans spektrumunu çizme
            ax.cla()
            ax.plot(pos_freq, pos_fft_magnitude)
            ax.set_title("Gerçek Zamanlı Frekans Spektrumu")
            ax.set_xlabel("Frekans (Hz)")
            ax.set_ylabel("Genlik")
            ax.grid(True)
            plt.pause(0.01)

def listen_microphone():
    """Bu fonksiyon mikrofon girişini dinler ve frekans spektrumunu gösterir."""
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        update_plot()

if __name__ == "__main__":
    listen_microphone()
