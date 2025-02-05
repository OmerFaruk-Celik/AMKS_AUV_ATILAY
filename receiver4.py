import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt
from time import sleep

# Sabitler
sampling_rate = 20000  # Örnekleme frekansı (Hz)
block_duration = 0.01  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 2  # Genlik ölçekleme faktörü
indeks = 0
indeks2 = 0
boyut = 2000  # Dizinin boyutu
dizi = np.zeros(boyut)
frekanslar = np.zeros(10)

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(100)  # Maksimum boyutu belirleyin

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
        if q.full():
            q.get()  # Kuyruktan fazladan verileri çıkar
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

def frekans_kontrol(frekanslar):
    """
    Bu fonksiyon, frekanslar dizisinde 2 kHz civarında frekansları bulur, 
    bit dizisinde ilgili indiste 1, 1 kHz civarında frekansları bulur, 
    bit dizisinde ilgili indiste 0 ve diğer değerler için -1 ile doldurur.
    
    :param frekanslar: Frekans değerlerini içeren dizi
    :return: Bit dizisi
    """
    bit = np.zeros(len(frekanslar), dtype=int)
    
    for i, frekans in enumerate(frekanslar):
        if 1800 <= frekans <= 2200:  # 2 kHz civarında (±100 Hz)
            bit[i] = 1
        elif 800 <= frekans <= 1200:  # 1 kHz civarında (±100 Hz)
            bit[i] = 0
        else:
            bit[i] = -1
    
    return bit

def calculate_frequency2(data, sampling_rate):
    """Bu fonksiyon verilen veri için frekansı hesaplar ve belirli aralıklardaki frekansları yazdırır."""
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    freq_magnitude = np.abs(fft_data)
    
    # Belirli frekans aralıklarını filtreleme
    lower_bound = 1000  # Alt sınır (Hz)
    upper_bound = 2000  # Üst sınır (Hz)
    tolerance = 200  # Tolerans (Hz)
    
    filtered_indices = np.where((freqs >= lower_bound - tolerance) & 
                                (freqs <= upper_bound + tolerance))
    
    filtered_freqs = freqs[filtered_indices]
    filtered_magnitude = freq_magnitude[filtered_indices]
    
    # Filtrelenmiş frekansları yazdırma
    print(f"Filtrelenen frekanslar: {filtered_freqs}")
    print(f"Filtrelenen frekansların sayısı: {len(filtered_freqs)}")
    
    return filtered_freqs

def calculate_frequency(data, sampling_rate):
    """Bu fonksiyon verilen veri için frekansı hesaplar."""
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    idx = np.argmax(np.abs(fft_data))
    freq = freqs[idx]
    dominant_freq = abs(freq)
    return dominant_freq

def merge_queue_elements(q):
    """Kuyruktaki tüm dizileri tek bir dizide birleştirir."""
    global merged_array, indeks, indeks2, frekanslar
    bit = []
    if not q.empty():
        ikiyuzNokta = np.concatenate(q.get())
        F = calculate_frequency(ikiyuzNokta, 20000)
        F2 = calculate_frequency2(ikiyuzNokta, 20000)
        
        if 1800 <= F <= 2200:  # 2 kHz civarında (±100 Hz)
            bit = 1
        elif 800 <= F <= 1200:  # 1 kHz civarında (±100 Hz)
            bit = 0
        else:
            bit = -1
        
        if (indeks2 == 0 or indeks2 == 1) and (bit == 0 or bit == -1):
            pass
        else:
            for deger in ikiyuzNokta:
                if True:
                    dizi[indeks] = deger
                    indeks += 1
                    if indeks >= 2000:
                        indeks = 0
            
            frekanslar[indeks2] = F
            indeks2 += 1
            if indeks2 >= 10:
                indeks2 = 0

def show_queue_elements(q):
    """Bu fonksiyon kuyruktaki elemanları geçici olarak gösterir."""
    if not q.empty():
        liste = merge_queue_elements(q)
        return liste

def update_plot():
    """Bu fonksiyon grafiği günceller."""
    global dizi, frekanslar
    plt.ion()  # Interaktif modu etkinleştir
    fig, ax1 = plt.subplots()  # Tek alt grafik oluştur
    x = np.arange(0, 200)  # 2000 nokta
    y = np.zeros(200)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-1, 1])
    ax1.set_xlim([0, 200])
    ax1.set_title("Time Domain Signal")
    
    while True:
        show_queue_elements(q)
        
        # Zaman domeni sinyali güncelle
        line1.set_ydata(dizi[:200])
        fig.canvas.draw()
        fig.canvas.flush_events()
        sleep(0.5)

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
