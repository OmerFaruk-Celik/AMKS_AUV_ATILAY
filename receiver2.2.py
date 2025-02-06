import numpy as np
import sounddevice as sd
import queue
import time

# Ayarlar
SAMPLE_RATE = 192000  # Örnekleme frekansı
DURATION = 0.01  # 10 ms pencere
FREQ_MIN = 14000  # Minimum frekans sınırı
FREQ_MAX = 17000  # Maksimum frekans sınırı
TOLERANCE = 100  # Frekans toleransı

# Özel bit frekansları
START_BIT = 16000
SEPARATOR_BIT = 15100
BIT_0 = 15400
BIT_1 = 15700

# Ses verisi kuyruğu
audio_queue = queue.Queue()

# 16 bitlik diziyi saklamak için
bit_array = []
is_receiving = False  # Veri alımı başladı mı?
waiting_for_separator = False  # Yeni bit eklemek için ayraç bekleniyor

def frequency_in_range(frequency, target):
    """Belirli bir frekansın hedef frekans aralığında olup olmadığını kontrol eder."""
    return abs(frequency - target) <= TOLERANCE

def audio_callback(indata, frames, time, status):
    """Mikrofondan alınan veriyi kuyruğa ekler."""
    if status:
        print(status)
    audio_queue.put(indata[:, 0])  # Mono hale getir

# Mikrofonu başlat
with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=int(SAMPLE_RATE * DURATION)):
    print("Gerçek zamanlı veri alımı başlıyor...")

    while True:
        try:
            # Kuyruktan ses verisini al
            audio_data = audio_queue.get_nowait()
            
            # FFT işlemi
            fft_data = np.fft.rfft(audio_data)
            freqs = np.fft.rfftfreq(len(audio_data), d=1/SAMPLE_RATE)
            
            # 14 kHz - 17 kHz arasını filtrele
            mask = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
            fft_magnitudes = np.abs(fft_data)[mask]
            filtered_freqs = freqs[mask]

            # Dominant frekansı belirle
            dominant_index = np.argmax(fft_magnitudes)
            dominant_freq = filtered_freqs[dominant_index]
            #print(dominant_freq)

            # **Start biti (16000 Hz) algılandı mı?**
            if frequency_in_range(dominant_freq, START_BIT):
                print("\n[START] Başlangıç biti algılandı, veri alımı başlıyor!")
                bit_array = []  # 16 bitlik diziyi sıfırla
                is_receiving = True
                waiting_for_separator = True  # İlk olarak ayraç frekansı bekle

            # **Veri alımı başladıysa**
            elif is_receiving:
                # **Ayraç biti (15100 Hz) algılandı mı?**
                if waiting_for_separator and frequency_in_range(dominant_freq, SEPARATOR_BIT):
                    print("[INFO] Ayraç algılandı, sonraki bit okunacak...")
                    waiting_for_separator = False  # Artık veri bekliyoruz
                
                # **Ayraç algılandıktan sonra bit okunuyor**
                elif not waiting_for_separator:
                    if frequency_in_range(dominant_freq, BIT_0):
                        bit_array.append(0)
                        print("[BIT] 0 eklendi.")
                        waiting_for_separator = True  # Yeniden ayraç bekle
                    elif frequency_in_range(dominant_freq, BIT_1):
                        bit_array.append(1)
                        print("[BIT] 1 eklendi.")
                        waiting_for_separator = True  # Yeniden ayraç bekle

                # **16 bit tamamlandıysa**
                if len(bit_array) == 16:
                    print(f"[COMPLETED] 16-bit veri alındı: {bit_array}")
                    is_receiving = False  # Veri alımını durdur

        except queue.Empty:
            pass  # Veri gelmesini bekle

