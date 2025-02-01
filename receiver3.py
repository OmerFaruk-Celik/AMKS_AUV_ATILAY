import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import queue
import threading
import matplotlib.pyplot as plt

# Sabitler
sampling_rate = 40000  # Örnekleme frekansı (Hz)
block_duration = 0.001  # Blok süresi (saniye) - 5 ms
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(maxsize=sampling_rate*block_duration )  # Maksimum boyutu belirleyin
q2 = queue.Queue(maxsize=16)

def butter_bandpass(lowcut, highcut, fs, order=5):
    """Band geçiren filtre koeffsiyentlerini hesaplar."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Band geçiren filtre uygular."""
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def detect_signal(data, threshold=0.1):
    """Belirlenen eşiği geçen sinyalleri algılar."""
    return np.any(np.abs(data) > threshold)

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

def binary_queue_to_decimal(q):
    """Bu fonksiyon, q2 kuyruğundaki 16 bitlik binary dizileri alır ve onluk tabana çevirir."""
    decimal_list = []
    binary_str = ""
    
    while not q.empty():
        binary_str += str(q.get())
    
    if len(binary_str) >= 16:
        for i in range(0, len(binary_str), 16):
            binary_segment = binary_str[i:i+16]
            if len(binary_segment) == 16:
                decimal_number = int(binary_segment, 2)
                decimal_list.append(decimal_number)
    
    return decimal_list         

def xor_or(signal2, signal1):
    if signal2 ^ signal1:
        if q2.full():
            q2.get()  # Kuyruktan bir veri çıkar
        q2.put(int(signal2))  # Kuyruğa yeni veri ekle
    elif signal2 and signal1:
        print(1)

def process_audio():
    """Bu fonksiyon kuyruktaki ses verilerini alır ve band geçiren filtre uygular."""
    while True:
        if not q.empty():
            indata = q.get()
            # 15 kHz band geçiren filtre
            filtered_15kHz = bandpass_filter(indata[:, 0], 14500, 15500, sampling_rate)
            signal_15kHz = detect_signal(filtered_15kHz)
            
            # 10 kHz band geçiren filtre
            filtered_10kHz = bandpass_filter(indata[:, 0], 9500, 10500, sampling_rate)
            signal_10kHz = detect_signal(filtered_10kHz)
            #print(f"15 kHz Signal: {'1' if signal_15kHz else '0'}, 10 kHz Signal: {'1' if signal_10kHz else '0'}")
            xor_or(signal_15kHz, signal_10kHz)
            ##printlist(q2.queue)) ##Bu yorum satırlarını silme lazım lacak şekilde tekrardan kullanmak için şimdilik yotum satırına alıyorum

def update_plot(fig, ax, line1, line2):
    """Bu fonksiyon grafiği günceller."""
    while True:
        if not q.empty():
            indata = q.queue[-1]  # Son alınan veriyi kullan
            # 15 kHz band geçiren filtre
            filtered_15kHz = bandpass_filter(indata[:, 0], 14500, 15500, sampling_rate)
            # 10 kHz band geçiren filtre
            filtered_10kHz = bandpass_filter(indata[:, 0], 9500, 10500, sampling_rate)
            """
            # Anlık verileri güncelleme ve grafikte gösterme
            line1.set_ydata(filtered_15kHz)
            line2.set_ydata(filtered_10kHz)
            fig.canvas.draw()
            fig.canvas.flush_events()
            """

def listen_microphone():
    """
    plt.ion()  # Interaktif modu etkinleştir
    fig, ax = plt.subplots(2, 1)  # İki alt grafik oluştur
    x = np.linspace(0, block_duration, blocksize)
    y1 = np.zeros(blocksize)
    y2 = np.zeros(blocksize)
    line1, = ax[0].plot(x, y1, label='15 kHz Band')
    line2, = ax[1].plot(x, y2, label='10 kHz Band')
    ax[0].set_ylim([-1, 1])  # Genlik ölçeklendirme
    ax[1].set_ylim([-1, 1])  # Genlik ölçeklendirme
    ax[0].set_xlim([0, block_duration])  # Zaman ekseni ölçeklendirme
    ax[1].set_xlim([0, block_duration])  # Zaman ekseni ölçeklendirme
    ax[0].legend()
    ax[1].legend()
    """

    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        process_thread = threading.Thread(target=process_audio)
        process_thread.daemon = True
        process_thread.start()
        """
        plot_thread = threading.Thread(target=update_plot, args=(fig, ax, line1, line2))
        plot_thread.daemon = True
        plot_thread.start()
        plot_thread.join()
        """
        process_thread.join()
        

if __name__ == "__main__":
    listen_microphone()
