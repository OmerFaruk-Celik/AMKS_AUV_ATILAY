import numpy as np
import sounddevice as sd
from scipy.fftpack import fft
from scipy.signal import butter, lfilter
import queue
import threading

# Sabitler
sampling_rate = 50000  # Örnekleme frekansı (Hz)
duration = 1.0  # Ses kayıt süresi (saniye)

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

def xor_or(signal2, signal1):
    #print(signal1 ^ signal2)
    if signal1 ^ signal2:
        if q2.full():
            a = q2.get()
            #print("Çıkarılan", a)
        #print("Eklenen", signal1)
        q2.put(signal1)

def process_audio():
    """Bu fonksiyon kuyruktaki ses verilerini alır ve band geçiren filtre uygular."""
    while True:
        if not q.empty():
            indata = q.get()
            # 19 kHz band geçiren filtre
            filtered_19kHz = bandpass_filter(indata[:, 0], 18000, 20000, sampling_rate)
            signal_19kHz = detect_signal(filtered_19kHz)
            
            # 15 kHz band geçiren filtre
            filtered_15kHz = bandpass_filter(indata[:, 0], 14500, 15500, sampling_rate)
            signal_15kHz = detect_signal(filtered_15kHz)
            
            xor_or(signal_19kHz, signal_15kHz)
            print(f"19 kHz Signal: {'1' if signal_19kHz else '0'}, 15 kHz Signal: {'1' if signal_15kHz else '0'}")
            #print(list(q2.queue))

def listen_microphone():
    """Bu fonksiyon mikrofon girişini dinler ve frekans spektrumunu gösterir."""
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        process_thread = threading.Thread(target=process_audio)
        process_thread.daemon = True
        process_thread.start()
        process_thread.join()

if __name__ == "__main__":
    listen_microphone()
