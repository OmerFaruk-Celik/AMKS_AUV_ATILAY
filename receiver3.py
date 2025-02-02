import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt
import pandas as pd

# Sabitler
sampling_rate = 20000  # Örnekleme frekansı (Hz)
block_duration = 0.1  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü
group_size = 125  # Her grup için nokta sayısı
num_groups = 2000 // group_size  # Toplam grup sayısı

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

def fourier_transform_groups(data):
    """Verilen veriyi 125 noktalık gruplara ayırır ve Fourier dönüşümü uygular."""
    groups = [data[i:i + group_size] for i in range(0, len(data), group_size)]
    freq_groups = []
    
    for group in groups:
        fft_data = np.fft.fft(group)
        fft_magnitude = np.abs(fft_data) / group_size
        freqs = np.fft.fftfreq(group_size, 1 / sampling_rate)
        freq_groups.append((freqs[:group_size // 2], fft_magnitude[:group_size // 2]))
    
    return freq_groups

def update_plot_and_table():
    """Bu fonksiyon grafiği günceller ve frekans bileşenlerini tablolaştırır."""
    plt.ion()  # Interaktif modu etkinleştir
    fig, ax = plt.subplots()  # Tek grafik oluştur
    x = np.arange(0, 2000)  # 2000 nokta
    y = np.zeros(2000)
    line, = ax.plot(x, y)
    ax.set_ylim([-1, 1])
    ax.set_xlim([0, 2000])
    ax.set_title("Time Domain Signal")
    
    while True:
        if not q.empty():
            indata = q.get()
            if len(indata) >= 2000:
                display_data = indata[:2000, 0]  # İlk 2000 noktayı al
            else:
                display_data = np.pad(indata[:, 0], (0, 2000 - len(indata)), 'constant')  # Yetersizse sıfırla doldur
                
            # Zaman domeni sinyali güncelle
            line.set_ydata(display_data)
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Fourier dönüşümü ve frekans analizi
            freq_groups = fourier_transform_groups(display_data)
            
            # Frekans bileşenlerini tablolaştır
            table_data = []
            for i, (freqs, magnitudes) in enumerate(freq_groups):
                for f, m in zip(freqs, magnitudes):
                    table_data.append({"Group": i + 1, "Frequency (Hz)": f, "Magnitude": m})

            df = pd.DataFrame(table_data)
            print(df)

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot_and_table)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
