import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import queue
import time

# Ayarlar
SAMPLE_RATE = 192000  # Örnekleme frekansı (Yüksek olmalı)
DURATION = 0.05  # 50 ms'lik pencere
FREQ_MIN = 4000  # 4 kHz
FREQ_MAX = 40000  # 40 kHz
TIME_WINDOW = 5  # Dominant frekansın son 5 saniyesini göster

# Ses verisini saklamak için kuyruk oluştur
audio_queue = queue.Queue()
dominant_freqs = []  # Zaman içinde dominant frekansı tutacak liste
timestamps = []  # Zaman damgaları

def audio_callback(indata, frames, time, status):
    """ Mikrofon verisini kuyruk içine atar """
    if status:
        print(status)
    audio_queue.put(indata[:, 0])  # Mono hale getir ve kuyruğa ekle

# Matplotlib başlat
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))  # İki grafik için
plt.ion()

# Mikrofonu dinlemeye başla
start_time = time.time()
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

            # Dominant frekansı bul
            dominant_index = np.argmax(fft_magnitudes)
            dominant_freq = filtered_freqs[dominant_index]
            dominant_amp = fft_magnitudes[dominant_index]

            # Zamanı kaydet
            current_time = time.time() - start_time
            dominant_freqs.append(dominant_freq)
            timestamps.append(current_time)

            # Eski verileri temizle (5 saniyeden uzun olanları sil)
            while timestamps and timestamps[0] < current_time - TIME_WINDOW:
                timestamps.pop(0)
                dominant_freqs.pop(0)
            """
            # Spektrum Grafiği (ax1)
            ax1.clear()
            ax1.plot(filtered_freqs, fft_magnitudes, color='blue', label="Spektrum")
            ax1.scatter(dominant_freq, dominant_amp, color='red', s=50, label=f"Dominant: {dominant_freq:.1f} Hz")
            ax1.set_xlabel("Frekans (Hz)")
            ax1.set_ylabel("Genlik")
            ax1.set_title("Gerçek Zamanlı Frekans Spektrumu (4 kHz - 40 kHz)")
            ax1.set_xlim(FREQ_MIN, FREQ_MAX)
            ax1.set_ylim(0, np.max(fft_magnitudes) * 1.1)
            ax1.legend()

            # Dominant Frekansın Zamana Göre Grafiği (ax2)
            ax2.clear()
            ax2.plot(timestamps, dominant_freqs, color='green', marker='o', linestyle='-', label="Dominant Frekans")
            ax2.set_xlabel("Zaman (s)")
            ax2.set_ylabel("Dominant Frekans (Hz)")
            ax2.set_title("Dominant Frekansın Zamana Göre Değişimi")
            ax2.set_xlim(max(0, current_time - TIME_WINDOW), current_time)
            ax2.set_ylim(FREQ_MIN, FREQ_MAX)
            ax2.legend()

            plt.pause(0.01)
            """

            # Terminale yazdır
            print(f"Dominant Frekans: {dominant_freq:.1f} Hz")

        except queue.Empty:
            pass  # Veri gelmesini bekle
