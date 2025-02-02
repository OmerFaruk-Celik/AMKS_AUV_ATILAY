import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import queue
import threading
import matplotlib.pyplot as plt

# Sabitler
sampling_rate = 20000  # Örnekleme frekansı (Hz)
block_duration = 0.1  # Blok süresi (saniye) - 0.25 ms
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı) = 10
scale_factor = 10  # Genlik ölçekleme faktörü

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue(maxsize=blocksize)  # Maksimum boyutu belirleyin
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

def detect_signal(data, threshold=0.01):
    """Belirlenen eşiği geçen sinyalleri algılar."""
    return np.any(np.abs(data) > threshold)

def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
       # print(f"Received {len(indata)} samples")  # Veri örneklerini yazdır
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
            #filtered_10kHz = bandpass_filter(indata[:, 0], 9500, 10500, sampling_rate)
            #signal_10kHz = detect_signal(filtered_10kHz)
            #print(f"15 kHz Signal: {'1' if signal_15kHz else '0'}, 10 kHz Signal: {'1' if signal_10kHz else '0'}")
            xor_or(signal_15kHz, signal_10kHz)
            #print(list(q2.queue)) ##Bu yorum satırlarını silme lazım olacak şekilde tekrardan kullanmak için şimdilik yorum satırına alıyorum

def update_plot():
    """Bu fonksiyon grafiği günceller."""
    plt.ion()  # Interaktif modu etkinleştir
    fig, ax = plt.subplots()  # Tek grafik oluştur
    x = np.arange(0, blocksize)
    y = np.zeros(blocksize)
    line, = ax.plot(x, y)
    ax.set_ylim([-1, 1])
    ax.set_xlim([0, blocksize])

    while True:
        if not q.empty():
            indata = q.get()
            line.set_ydata(indata[:, 0])
            fig.canvas.draw()
            fig.canvas.flush_events()

def listen_microphone():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        process_thread = threading.Thread(target=process_audio)
        process_thread.daemon = True
        process_thread.start()
        
        plot_thread = threading.Thread(target=update_plot)
        plot_thread.daemon = True
        plot_thread.start()
        
        process_thread.join()
        plot_thread.join()

if __name__ == "__main__":
    listen_microphone()
