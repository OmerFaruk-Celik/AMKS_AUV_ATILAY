import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt

# Sabitler
sampling_rate = 20000  # Örnekleme frekansı (Hz)
block_duration = 0.1  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü
tolerance = 100  # Frekans toleransı (Hz)

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(maxsize=blocksize)  # Maksimum boyutu belirleyin

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

def calculate_frequency(data, sampling_rate):
    """Bu fonksiyon verilen veri için frekansı hesaplar."""
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    idx = np.argmax(np.abs(fft_data))
    freq = freqs[idx]
    return abs(freq)

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
    freq_text3 = ax2.text(0.5, 0.3, '', transform=ax2.transAxes, ha='center')
    ax2.axis('off')
    
    while True:
        if not q.empty():
            indata = q.get()
            if len(indata) >= 2000:
                display_data = indata[:2000, 0]  # İlk 2000 noktayı al
                grup1 = indata[:125, 0]  # İlk 125 noktayı al
                grup2 = indata[125:250, 0]  # İkinci 125 noktayı al
                #grup16 = indata[1875:2000, 0]  # Son 125 noktayı al
                
                # Grup frekanslarını hesapla
                freq1 = calculate_frequency(grup1, sampling_rate)
                freq2 = calculate_frequency(grup2, sampling_rate)
                #freq16 = calculate_frequency(grup16, sampling_rate)

                # Frekansları kontrol et
                if (abs(freq1 - 2000) <= tolerance and 
                    abs(freq2 - 2000) <= tolerance):
                    freq_text1.set_text(f'Grup1 Frekansı: {freq1:.2f} Hz')
                    freq_text2.set_text(f'Grup2 Frekansı: {freq2:.2f} Hz')
                    #freq_text3.set_text(f'Grup16 Frekansı: {freq16:.2f} Hz')
                    
                    # Zaman domeni sinyali güncelle
                    line1.set_ydata(display_data)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                else:
                    freq_text1.set_text('Grup1 frekansı 2kHz civarında değil.')
                    freq_text2.set_text('Grup2 frekansı 2kHz civarında değil.')
                    #freq_text3.set_text('Grup16 frekansı 2kHz civarında değil.')

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
