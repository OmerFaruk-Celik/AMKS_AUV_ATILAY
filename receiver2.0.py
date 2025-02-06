import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

# Ayarlar
SAMPLE_RATE = 192000  # Örnekleme hızı (Yüksek olmalı, min 96 kHz önerilir)
DURATION = 0.05  # 50 ms'lik pencere (gerçek zamanlı için)
FREQ_MIN = 4000  # Alt frekans sınırı
FREQ_MAX = 40000  # Üst frekans sınırı

def audio_callback(indata, frames, time, status):
    """ Mikrofon verisini FFT ile analiz edip grafiği günceller """
    if status:
        print(status)
    
    # Mono hale getir
    audio_data = indata[:, 0]

    # FFT uygula
    fft_data = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), d=1/SAMPLE_RATE)

    # Belirtilen frekans aralığını seç
    mask = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
    fft_magnitudes = np.abs(fft_data)[mask]
    filtered_freqs = freqs[mask]

    # Grafiği güncelle
    ax.clear()
    ax.plot(filtered_freqs, fft_magnitudes, color='blue')
    ax.set_xlabel("Frekans (Hz)")
    ax.set_ylabel("Genlik")
    ax.set_title("Gerçek Zamanlı Frekans Spektrumu (4 kHz - 40 kHz)")
    ax.set_xlim(FREQ_MIN, FREQ_MAX)
    ax.set_ylim(0, np.max(fft_magnitudes) * 1.1)
    plt.pause(0.01)

# Matplotlib ayarları
fig, ax = plt.subplots()
plt.ion()

# Mikrofonu dinlemeye başla
with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * DURATION)):
    print("Gerçek zamanlı analiz başlıyor...")
    while True:
        plt.pause(0.01)  # Sürekli güncelle
