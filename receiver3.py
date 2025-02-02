import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt
import time
import ctypes
# Sabitler
sampling_rate = 20000  # Örnekleme frekansı (Hz)
block_duration = 0.05  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü
tolerance = 100  # Frekans toleransı (Hz)

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue()  # Maksimum boyutu belirleyin
basla=time.time()
def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    global basla
    if status:
        print(status)
    
    # Zaman bilgilerini okuyun
    #input_time = time.inputBufferAdcTime
    son= time.currentTime
    fark=son-basla
    print(fark)
    basla=time.currentTime
    #output_time = time.outputBufferDacTime

    
    try:
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
        if q.qsize() > 2000:
            while q.qsize() > 2000:
                q.get()  # Kuyruktan fazladan verileri çıkar
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

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

def update_plot():
    """Bu fonksiyon grafiği günceller."""
    plt.ion()  # Interaktif modu etkinleştir
    fig, (ax1, ax2) = plt.subplots(2, 1)  # İki alt grafik oluştur
    x = np.arange(0, 2000)  # 2000 nokta
    y = np.zeros(2000)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-1, 1])
    ax1.set_xlim([0, 2000])
    ax1.set_title("Time Domain Signal")

    freq_text1 = ax2.text(0.5, 0.5, '', transform=ax2.transAxes, ha='center')
    freq_text2 = ax2.text(0.5, 0.4, '', transform=ax2.transAxes, ha='center')
    ax2.axis('off')

    freqs_array = np.zeros(16)  # 16 elemanlık dizi

    while True:
        if not q.empty():
            indata = q.get()
            if len(indata) >= 2000:
                display_data = indata[:2000, 0]  # İlk 2000 noktayı al
                grup1 = indata[:125, 0]  # İlk 125 noktayı al
                grup2 = indata[125:250, 0]  # İkinci 125 noktayı al
                grup3 = indata[250:375, 0]  # Üçüncü 125 noktayı al
                grup4 = indata[375:500, 0]  # Dördüncü 125 noktayı al
                grup5 = indata[500:625, 0]  # Beşinci 125 noktayı al
                grup6 = indata[625:750, 0]  # Altıncı 125 noktayı al
                grup7 = indata[750:875, 0]  # Yedinci 125 noktayı al
                grup8 = indata[875:1000, 0]  # Sekizinci 125 noktayı al
                grup9 = indata[1000:1125, 0]  # Dokuzuncu 125 noktayı al
                grup10 = indata[1125:1250, 0]  # Onuncu 125 noktayı al
                grup11 = indata[1250:1375, 0]  # On birinci 125 noktayı al
                grup12 = indata[1375:1500, 0]  # On ikinci 125 noktayı al
                grup13 = indata[1500:1625, 0]  # On üçüncü 125 noktayı al
                grup14 = indata[1625:1750, 0]  # On dördüncü 125 noktayı al
                grup15 = indata[1750:1875, 0]  # On beşinci 125 noktayı al
                grup16 = indata[1875:2000, 0]  # On altıncı 125 noktayı al

                # Grup frekanslarını hesapla
                freqs = [
                    calculate_frequency(grup1, sampling_rate),
                    calculate_frequency(grup2, sampling_rate),
                    calculate_frequency(grup3, sampling_rate),
                    calculate_frequency(grup4, sampling_rate),
                    calculate_frequency(grup5, sampling_rate),
                    calculate_frequency(grup6, sampling_rate),
                    calculate_frequency(grup7, sampling_rate),
                    calculate_frequency(grup8, sampling_rate),
                    calculate_frequency(grup9, sampling_rate),
                    calculate_frequency(grup10, sampling_rate),
                    calculate_frequency(grup11, sampling_rate),
                    calculate_frequency(grup12, sampling_rate),
                    calculate_frequency(grup13, sampling_rate),
                    calculate_frequency(grup14, sampling_rate),
                    calculate_frequency(grup15, sampling_rate),
                    calculate_frequency(grup16, sampling_rate)
                ]
                freqs_array = check_frequencies(freqs, 6000, tolerance)



                if all(freqs_array[:2]) and freqs_array[15] :
                    freq_text1.set_text(f'Grup1 Frekansı: {freqs[0]:.2f} Hz')
                    freq_text2.set_text(f'Grup2 Frekansı: {freqs[1]:.2f} Hz')
                    # Frekansları kontrol et
                    
                    # Frekans kontrol sonuçlarını yazdır
                    #print(freqs_array)
                    # Zaman domeni sinyali güncelle
                    line1.set_ydata(display_data)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                else:
                    freq_text1.set_text('Grup1 frekansı 6kHz civarında değil.')
                    freq_text2.set_text('Grup2 frekansı 6kHz civarında değil.')

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
