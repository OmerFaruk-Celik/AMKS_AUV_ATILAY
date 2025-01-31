import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft

# Sabitler
sampling_rate = 44100  # Örnekleme frekansı (Hz)
duration = 1.0  # Ses kayıt süresi (saniye)

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve Fourier dönüşümü ile frekansları analiz eder."""
    if status:
        print(status)
    
    # Fourier dönüşümü
    fft_values = fft(indata[:, 0])
    fft_magnitude = np.abs(fft_values) / len(fft_values)
    freq = np.fft.fftfreq(len(fft_values), d=1/sampling_rate)

    # Sadece pozitif frekansları al
    pos_freq = freq[:len(freq) // 2]
    pos_fft_magnitude = fft_magnitude[:len(fft_magnitude) // 2]

    # Frekans spektrumunu çizme
    plt.clf()
    plt.plot(pos_freq, pos_fft_magnitude)
    plt.title("Gerçek Zamanlı Frekans Spektrumu")
    plt.xlabel("Frekans (Hz)")
    plt.ylabel("Genlik")
    plt.grid(True)
    plt.pause(0.01)

def listen_microphone():
    """Bu fonksiyon mikrofon girişini dinler ve frekans spektrumunu gösterir."""
    plt.ion()
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        plt.show(block=True)

if __name__ == "__main__":
    listen_microphone()
