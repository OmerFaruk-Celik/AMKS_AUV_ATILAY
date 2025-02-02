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
    if(not q.full()):
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
    #print(len(list(q.queue)))

def calculate_frequency(data, sampling_rate):
    """Bu fonksiyon verilen veri için frekansı hesaplar."""
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    idx = np.argmax(np.abs(fft_data))
    freq = freqs[idx]
    return abs(freq)

def check_frequencies(freqs, target_freq, tolerance):
    """Bu fonksiyon verilen frekansların hedef frekansa yakın olup olmadığını kontrol eder."""
    result = [1 if abs(f - target_freq) <= tolerance else 0 for f in freqs]
    return result
freqs=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
def update_plot():
    """Bu fonksiyon grafiği günceller."""
    global freqs
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
                for i in range(16):
                
                calculate_frequency(q.get(), sampling_rate)
                

                freqs_array = check_frequencies(freqs, 2000, tolerance)

                if (freqs_array[0]) and freqs_array[1]:
                    freq_text1.set_text(f'Grup1 Frekansı: {freqs[0]:.2f} Hz')
                    freq_text2.set_text(f'Grup2 Frekansı: {freqs[1]:.2f} Hz')
                    line1.set_ydata(display_data)
                    #print(freqs_array)
                else:
                    freq_text1.set_text('Grup1 frekansı 2kHz civarında değil.')
                    freq_text2.set_text('Grup2 frekansı 2kHz civarında değil.')

                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                freq_text1.set_text('Yeterli veri yok.')
                freq_text2.set_text('Yeterli veri yok.')

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
