import numpy as np
import sounddevice as sd
import queue
import time
import threading
from kalman_filter import KalmanFilter

# Ayarlar
SAMPLE_RATE = 300000  # Örnekleme frekansı
DURATION = 0.006  # 5 ms pencere
FREQ_MIN = 17000  # Minimum frekans sınırı
FREQ_MAX = 20000  # Maksimum frekans sınırı
TOLERANCE = 200  # Frekans toleransı

# Özel bit frekansları
START_BIT = 20000
SEPARATOR_BIT = 17800
BIT_0 = 18600
BIT_1 = 19500
ilk = False
# Ses verisi kuyruğu
audio_queue = queue.Queue()

# 16 bitlik diziyi saklamak için
bit_array = []
is_receiving = False  # Veri alımı başladı mı?
waiting_for_separator = False  # Yeni bit eklemek için ayraç bekleniyor
start_time = None  # Başlangıç zamanı

# Global zaman değişkeni
global_time = 0  # Global zaman değişkeni

# Kalman filtresi
kalman_filter = KalmanFilter(process_variance=1e-5, measurement_variance=0.1**2, estimated_measurement_variance=1.0)

def baslat():
    global global_time
    hedef_zaman = time.perf_counter_ns()  # Başlangıç zamanı (nano-saniye cinsinden)
    
    while True:
        simdiki_zaman = time.perf_counter_ns()
        if simdiki_zaman - hedef_zaman >= 100_000:  # 100 µs (mikro-saniye)
            global_time += 1
            if global_time >= 1048576:
                global_time = 0
            hedef_zaman = simdiki_zaman  # Yeni hedef zamanı güncelle

# Yeni bir thread başlat
thread = threading.Thread(target=baslat, daemon=True)
thread.start()

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
            
            # 17 kHz - 20 kHz arasını filtrele
            mask = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
            fft_magnitudes = np.abs(fft_data)[mask]
            filtered_freqs = freqs[mask]

            # Dominant frekansı belirle ve Kalman filtresini uygula
            dominant_index = np.argmax(fft_magnitudes)
            dominant_freq = filtered_freqs[dominant_index]
            filtered_freq = kalman_filter.update(dominant_freq)
            #print(global_time)  # 🛠 Test için global_time yazdır
            #print(filtered_freq)
            filtered_freq=dominant_freq

            # **Start biti (20000 Hz) algılandı mı?**
            if frequency_in_range(filtered_freq, START_BIT):
                
                start_time = time.time() * 1000  # Milisaniye cinsinden zamanı kaydet
                bit_array = []  # 16 bitlik diziyi sıfırla
                is_receiving = True
                waiting_for_separator = True  # İlk olarak ayraç frekansı bekle
                t = global_time
                print("[Start] Starttt")

            # **Veri alımı başladıysa**
            elif is_receiving:
                # **Ayraç biti (17800 Hz) algılandı mı?**
                if waiting_for_separator and frequency_in_range(filtered_freq, SEPARATOR_BIT):
                    waiting_for_separator = False  # Artık veri bekliyoruz
                    #print("[info] Ayrac Algılandı ...")
                
                # **Ayraç algılandıktan sonra bit okunuyor**
                elif not waiting_for_separator:
                    if frequency_in_range(filtered_freq, BIT_0):
                        bit_array.append(0)
                        waiting_for_separator = True  # Yeniden ayraç bekle
                        #print("[info] added 0")
                    elif frequency_in_range(filtered_freq, BIT_1):
                        bit_array.append(1)
                        waiting_for_separator = True  # Yeniden ayraç bekle
                        #print("[info] added 1")

                # **20 bit tamamlandıysa**
                if len(bit_array) == 20:
                    decimal_value = int("".join(map(str, bit_array)), 2)  # Binary to decimal çevirme
                    
                    # Zaman farkını hesapla
                    end_time = time.time() * 1000  # Şu anki zamanı al
                    if decimal_value > t:
                        t += 1048576
                    if not ilk: 
                        ilk = True
                        global_time = decimal_value + ((40 + 100 * 20) * 1000 / 100)
                        t = global_time
                    delay = abs(t - decimal_value) * 100 / (1000)
                    
                    # Sonuçları yazdır
                    print(f"Decimal: {decimal_value}, Gecikme: {delay:.2f} ms")
                    #print(int(1/(delay*400/10000000)*100))
                    
                    is_receiving = False  # Veri alımını durdur

        except queue.Empty:
            pass  # Veri gelmesini bekle
