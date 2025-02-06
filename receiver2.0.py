import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import queue

# Ayarlar
SAMPLE_RATE = 192000  # Örnekleme frekansı (Yüksek olmalı)
DURATION = 0.05  # 50 ms'lik pencere
FREQ_MIN = 4000  # 4 kHz
FREQ_MAX = 40000  # 40 kHz

# Ses verisini saklamak için kuyruk oluştur
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """ Mikrofon verisini kuyruk içine atar """
    if status:
        print(status)
    audio_queue.put(indata[:, 0])  # Mono hale getir ve kuyruğa ekle

# Matplotlib başlat
fig, ax = plt.subplots()
plt.ion()

# Mikrofonu dinlemeye başla
with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * DURATION)):
    print("Gerçek zamanlı analiz başlıyor...")

    while True:
        try:
            # Kuyruktan veri al
            audio_data = audio_queue.get_nowait()
            
            # FFT uygula
            fft_data = np.fft.rfft(audio_data)
            freqs = np.fft.rfftfreq(len(audio_data), d=1/SAMPLE_RATE)

            # 4 kHz - 40 kHz arasını filtrele
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

        except queue.Empty:
            pass  # Veri gelmesini bekle
