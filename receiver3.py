import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt
import time
import ctypes

# Sabitler
sampling_rate = 12500  # Örnekleme frekansı (Hz)
block_duration = 0.01  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü
tolerance = 100  # Frekans toleransı (Hz)
say = 0
# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(16)  # Maksimum boyutu belirleyin

basla = time.time()

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    global basla
    if status:
        print(status)
    
    # Zaman bilgilerini okuyun
    son = time.currentTime
    fark = son - basla
    basla = time.currentTime
    if not q.full():
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle

def calculate_frequency(data, sampling_rate):
    """Bu fonksiyon verilen veri için frekansı hesaplar."""
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    idx = np.argmax(np.abs(fft_data))
    freq = freqs[idx]
    return abs(freq)

def check_frequencies(freqs, target_freq, tolerance):
    """Bu fonksiyon verilen frekansların hedef frekansa yakın olup olmadığını kontrol eder."""
    result = abs(target_freq - freqs) <= tolerance
    return result

def update_plot():
    """Bu fonksiyon grafiği günceller."""
    global say
    plt.ion()  # Interaktif modu etkinleştir
    fig, (ax1, ax2) = plt.subplots(2, 1)  # İki alt grafik oluştur
    x = np.arange(0, 2000)  # 2000 nokta
    y = np.zeros(2000)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-0.2, 0.2])
    ax1.set_xlim([0, 2000])
    ax1.set_title("Time Domain Signal")

    freq_text1 = ax2.text(0.5, 0.5, '', transform=ax2.transAxes, ha='center')
    freq_text2 = ax2.text(0.5, 0.4, '', transform=ax2.transAxes, ha='center')
    ax2.axis('off')

    while True:
        # Grup frekanslarını hesapla
        while say <= 16 and not q.empty():
            say += 1
            if not q.empty():
                freqs = calculate_frequency(q.get(), sampling_rate)
                hesaplanan_frekans = check_frequencies(freqs, 2000, tolerance)
                if say == 1:
                    if not hesaplanan_frekans:
                        say = 0
                elif say == 2:
                    if not hesaplanan_frekans:
                        say = 0
                else:
                    break
        
        if q.full():
            combined_data = []
            while not q.empty():
                combined_data.extend(q.get())
            combined_data = np.array(combined_data)
            if len(combined_data) >= 2000:
                display_data = combined_data[:2000]
                line1.set_ydata(display_data)
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                freq_text1.set_text('Yeterli veri yok.')
                freq_text2.set_text('Yeterli veri yok.')
        else:
            freq_text1.set_text('Grup1 frekansı 2kHz civarında değil.')
            freq_text2.set_text('Grup2 frekansı 2kHz civarında değil.')

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
    plt.show(block=True)  # Ana iş parçacığında grafiği göster
