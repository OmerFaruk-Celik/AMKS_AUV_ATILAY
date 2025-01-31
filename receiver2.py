import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from queue import Queue

def decimal_to_binary_array(decimal_number):
    # Onluk sayıyı 16 bitlik binary stringe dönüştür
    binary_string = format(decimal_number, '016b')
    
    # Binary stringi bir diziye dönüştür
    binary_array = [int(bit) for bit in binary_string]
    
    return binary_array

def plot_time_domain_signals(t, data_signal, carrier, modulated_signal):
    # Grafik oluşturma
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(t, data_signal)
    plt.title("Veri Sinyali (Binary)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Genlik")
    plt.ylim(-0.5, 1.5)

    plt.subplot(3, 1, 2)
    plt.plot(t, carrier)
    plt.title("Taşıyıcı Sinyal (5 kHz)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Genlik")

    plt.subplot(3, 1, 3)
    plt.plot(t, modulated_signal)
    plt.title("Modüle Edilmiş Sinyal (FM)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Genlik")

    plt.tight_layout()
    plt.show()

def plot_frequency_domain(modulated_signal, sampling_rate, highlight_freq=None, lowlight_freq=None):
    # Fourier dönüşümü
    n = len(modulated_signal)
    freq = np.fft.fftfreq(n, d=1/sampling_rate)
    fft_values = np.fft.fft(modulated_signal)
    fft_magnitude = np.abs(fft_values) / n
    
    # Sadece pozitif frekansları al
    pos_freq = freq[:n // 2]
    pos_fft_magnitude = fft_magnitude[:n // 2]

    # Frekans spektrumunu çizme
    plt.figure(figsize=(12, 6))
    plt.plot(pos_freq, pos_fft_magnitude, label='Frekans Spektrumu')
    
    # Belirli bir frekans bileşenini vurgulama
    if highlight_freq is not None:
        plt.axvline(x=highlight_freq, color='r', linestyle='--', label=f'{highlight_freq} Hz')
        plt.axvline(x=lowlight_freq, color='g', linestyle='--', label=f'{lowlight_freq} Hz')
    
    plt.title("Modüle Edilmiş Sinyalin Frekans Spektrumu")
    plt.xlabel("Frekans (Hz)")
    plt.ylabel("Genlik")
    plt.grid(True)
    plt.legend()
    plt.show()

def play_modulated_signal(modulated_signal, sampling_rate):
    # Modüle edilmiş sinyali oynatma
    sd.play(modulated_signal, sampling_rate)
    sd.wait()  # Oynatma tamamlanana kadar bekle

def process_and_play(decimal_number, carrier_freq, sampling_rate, duration, mod_index):
    binary_array = decimal_to_binary_array(decimal_number)
    
    # Zaman dizisi oluşturma
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    
    # 16 bitlik veriyi zaman dizisine genişletme
    data_signal = np.repeat(binary_array, len(t) // len(binary_array))
    
    # Eğer data_signal uzunluğu t uzunluğundan kısa ise, data_signal'ı t uzunluğuna tamamla
    if len(data_signal) < len(t):
        data_signal = np.append(data_signal, np.zeros(len(t) - len(data_signal)))
    
    # Taşıyıcı sinyal
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    
    # Frekans modülasyonu
    modulated_signal = np.sin(2 * np.pi * t * (carrier_freq + mod_index * data_signal))
    
    # Modüle edilmiş sinyali oynatma
    play_modulated_signal(modulated_signal, sampling_rate)
    
    return t, data_signal, carrier, modulated_signal

def cizim(t, data_signal, carrier, modulated_signal, sampling_rate, mod_index):
    # Zaman domaininde sinyalleri çizme
    plot_time_domain_signals(t, data_signal, carrier, modulated_signal)
    
    # Frekans domaininde modüle edilmiş sinyali analiz etme ve çizme
    Fm = (carrier_freq + mod_index * data_signal)
    highlight_freq = max(Fm)  # Vurgulanacak frekans
    lowlight_freq = min(Fm)
    plot_frequency_domain(modulated_signal, sampling_rate, highlight_freq, lowlight_freq)

# Sabitler
carrier_freq = 15000  # Taşıyıcı frekans 5 kHz (örnek)
sampling_rate = 50000  # Örnekleme frekansı 100 kHz
duration = 0.1  # Sinyal süresi 100 ms
mod_index = 4000  # Modülasyon indeksi (değeri deneyerek ayarlayabilirsiniz)

# Kuyruk oluşturma
q2 = Queue(maxsize=16)

# 1'den 50'ye kadar olan sayıları binary'ye çevirme ve işlemler
for decimal_number in range(1, 50):
    t, data_signal, carrier, modulated_signal = process_and_play(decimal_number, carrier_freq, sampling_rate, duration, mod_index)
    # Kuyruğa binary diziyi ekleme
    binary_array = decimal_to_binary_array(decimal_number)
    if q2.full():
        q2.get()  # Kuyruktan bir veri çıkar
    q2.put(binary_array)  # Kuyruğa yeni veri ekle

# Kuyruktaki binary dizileri onluk tabana çevirme ve yazdırma
def queue_to_decimal(q):
    decimal_list = []
    while not q.empty():
        binary_array = q.get()
        decimal_number = int("".join(str(bit) for bit in binary_array), 2)
        decimal_list.append(decimal_number)
    return decimal_list

# Kuyruktaki sayıları onluk tabana çevir ve yazdır
decimal_numbers = queue_to_decimal(q2)
print("Kuyruktaki onluk sayılar:", decimal_numbers)

# Son sinyal için çizimleri yapma
cizim(t, data_signal, carrier, modulated_signal, sampling_rate, mod_index)
