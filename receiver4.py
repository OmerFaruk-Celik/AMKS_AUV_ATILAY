import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt

# Sabitler
sampling_rate = 40000  # Örnekleme frekansı (Hz)
block_duration = 0.0005  # Blok süresi (saniye) - 0.5 ms
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı) = 20
scale_factor = 10  # Genlik ölçekleme faktörü

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(maxsize=blocksize)  # Maksimum boyutu belirleyin
q2 = queue.Queue(16)  # Maksimum boyutu belirleyin

def find_dominant_frequency(data, fs):
    """Verilen verinin baskın frekansını bulur."""
    fft_data = np.fft.fft(data)
    fft_magnitude = np.abs(fft_data) / len(data)
    freqs = np.fft.fftfreq(len(data), 1/fs)
    dominant_freq = freqs[np.argmax(fft_magnitude)]
    return dominant_freq

def is16Khz(dominant_freq):
    """Baskın frekansın 18 kHz bandında olup olmadığını kontrol eder."""
    if 15500 <= dominant_freq <= 16500:
        return 1
    return 0

def is18Khz(dominant_freq):
    """Baskın frekansın 20 kHz bandında olup olmadığını kontrol eder."""
    if 17500 <= dominant_freq <= 18500:
        return 1
    return 0

def xor_or(signal2, signal1):
    if signal2 ^ signal1:
        if q2.full():
            q2.get()  # Kuyruktan bir veri çıkar
        q2.put(int(signal2))  # Kuyruğa yeni veri ekle
    elif signal2 and signal1:
        print(1)

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

def process_audio():
    """Bu fonksiyon kuyruktaki ses verilerini alır ve baskın frekans analizini yapar."""
    while True:
        if not q.empty():
            indata = q.get()
            dominant_freq = find_dominant_frequency(indata[:, 0], sampling_rate)
            #print(f"Dominant Frequency: {dominant_freq} Hz")
            is18 = is18Khz(dominant_freq)
            is16 = is16Khz(dominant_freq)
            #print(f"is20Khz: {is18}, is18Khz: {is16}")
            xor_or(is18, is16)
            print(list(q2.queue)) ##Bu yorum satırlarını silme! lazım olacak şekilde tekrardan kullanmak için şimdilik yorum satırına alıyorum

def update_plot_and_fft():
    """Bu fonksiyon grafiği günceller ve Fourier dönüşümü ile frekans analizini yapar."""
    plt.ion()  # Interaktif modu etkinleştir
    fig, (ax1, ax2) = plt.subplots(2, 1)  # İki alt grafik oluştur
    x = np.arange(0, blocksize)
    y = np.zeros(blocksize)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-1, 1])
    ax1.set_xlim([0, blocksize])
    
    freqs = np.fft.fftfreq(blocksize, 1/sampling_rate)
    line2, = ax2.plot(freqs, np.zeros(blocksize))
    ax2.set_xlim([0, sampling_rate / 2])
    ax2.set_ylim([0, 1])

    while True:
        if not q.empty():
            indata = q.get()
            line1.set_ydata(indata[:, 0])
            
            # Fourier dönüşümü ve frekans analizini yap
            fft_data = np.fft.fft(indata[:, 0])
            fft_magnitude = np.abs(fft_data) / blocksize
            line2.set_ydata(fft_magnitude)
            
            fig.canvas.draw()
            fig.canvas.flush_events()

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        process_thread = threading.Thread(target=process_audio)
        process_thread.daemon = True
        process_thread.start()
        
        plot_thread = threading.Thread(target=update_plot_and_fft)
        plot_thread.daemon = True
        plot_thread.start()
        
        process_thread.join()
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
