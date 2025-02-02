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
amplitude_factor = 4  # Fourier dönüşümündeki genlikleri artırmak için faktör
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
        fft_magnitude = np.abs(fft_data) / group_size * amplitude_factor
        freqs = np.fft.fftfreq(group_size, 1 / sampling_rate)
        freq_groups.append((freqs[:group_size // 2], fft_magnitude[:group_size // 2]))
    
    return freq_groups

def update_plot():
    """Bu fonksiyon grafiği günceller."""
    plt.ion()  # Interaktif modu etkinleştir
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))  # İki alt grafik oluştur
    x = np.arange(0, 2000)  # 2000 nokta
    y = np.zeros(2000)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-1, 1])
    ax1.set_xlim([0, 2000])
    ax1.set_title("Time Domain Signal")
    
    while True:
        if not q.empty():
            indata = q.get()
            if len(indata) >= 2000:
                display_data = indata[:2000, 0]  # İlk 2000 noktayı al
            else:
                display_data = np.pad(indata[:, 0], (0, 2000 - len(indata)), 'constant')  # Yetersizse sıfırla doldur
                
            # Zaman domeni sinyali güncelle
            line1.set_ydata(display_data)
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Fourier dönüşümü ve frekans analizi
            freq_groups = fourier_transform_groups(display_data)
            
            ax2.clear()
            for i, (freqs, magnitudes) in enumerate(freq_groups):
                ax2.plot([i + 1] * len(freqs), freqs, 'o', label=f"Group {i + 1}" if i == 0 else "")
            ax2.set_xlim([0, num_groups + 1])
            ax2.set_ylim([0, sampling_rate / 2])
            ax2.set_title("Frequency Components per Group")
            ax2.set_xlabel("Group")
            ax2.set_ylabel("Frequency (Hz)")
            ax2.legend()
            fig.canvas.draw()
            fig.canvas.flush_events()

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
