import numpy as np
import sounddevice as sd
from scipy.fftpack import fft
from scipy.signal import butter, lfilter
import queue
import threading

# Sabitler
sampling_rate = 50000  # Örnekleme frekansı (Hz)
block_duration = 0.006  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue()
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
    q.put(indata.copy())

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
    if signal2 and signal1:
        if q2.full():
            q2.get()  # Kuyruktan bir veri çıkar
        q2.put(int(signal2))  # Kuyruğa yeni veri ekle

def process_audio():
    """Bu fonksiyon kuyruktaki ses verilerini alır ve band geçiren filtre uygular."""
    while True:
        if not q.empty():
            indata = q.get()
            # 19 kHz band geçiren filtre
            filtered_19kHz = bandpass_filter(indata[:, 0], 18000, 19500, sampling_rate)
            signal_19kHz = detect_signal(filtered_19kHz)
            
            # 15 kHz band geçiren filtre
            filtered_15kHz = bandpass_filter(indata[:, 0], 14500, 15500, sampling_rate)
            signal_15kHz = detect_signal(filtered_15kHz)
            #print(f"19 kHz Signal: {'1' if signal_19kHz else '0'}, 15 kHz Signal: {'1' if signal_15kHz else '0'}")
            xor_or(signal_19kHz, signal_15kHz)
            print(list(q2.queue))

def listen_microphone():
    """Bu fonksiyon mikrofon girişini dinler ve frekans spektrumunu gösterir."""
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        process_thread = threading.Thread(target=process_audio)
        process_thread.daemon = True
        process_thread.start()
        process_thread.join()

if __name__ == "__main__":
    listen_microphone()
