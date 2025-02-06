import numpy as np
import sounddevice as sd
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import time
tolarance=100
start_time=time.time()
end_time=time.time()
time_list=[]
v2=time.time()

StartBiti=15000
AyracBiti=14000
BirBiti=13000
SifirBiti=12000
def gray_to_bin(gray_array):
    """
    Bir Gray kodu dizisini binary (ikilik) dizisine dönüştürür.
    
    Args:
        gray_array (list): Dönüştürülecek Gray kodu dizisi.
    
    Returns:
        list: Binary dizisi (liste).
    """
    binary_array = [gray_array[0]]  # Binary kodunun ilk biti, Gray kodunun ilk bitidir.
    for i in range(1, len(gray_array)):
        binary_array.append(binary_array[i - 1] ^ gray_array[i])
    return binary_array


def hamming_8_4_decode(encoded):
    """ Hamming(8,4) kodundan hataları tespit edip düzeltir """
    p1, p2, d1, p3, d2, d3, d4, p4 = encoded

    # Parite kontrolleri
    c1 = p1 ^ d1 ^ d2 ^ d4  # 1, 2, 4. bitlerin kontrolü
    c2 = p2 ^ d1 ^ d3 ^ d4  # 1, 3, 4. bitlerin kontrolü
    c3 = p3 ^ d2 ^ d3 ^ d4  # 2, 3, 4. bitlerin kontrolü
    c4 = p1 ^ p2 ^ p3 ^ d1 ^ d2 ^ d3 ^ d4 ^ p4  # Genel parite kontrolü

    error_pos = c1 * 1 + c2 * 2 + c3 * 4  # Hata konumunu belirle

    if error_pos > 0:  # Hata varsa düzelt
        #print(f"Hata bulundu! {error_pos}. bit düzeltiliyor.")
        encoded[error_pos - 1] ^= 1  # Hatalı biti düzelt

    # Veri bitlerini al
    decoded = [encoded[2], encoded[4], encoded[5], encoded[6]]
    return decoded

def BinToDec(binary_array):
    """
    Bir binary (ikilik) diziyi decimal (onluk) sayıya dönüştürür.
    
    Args:
        binary_array (list): Dönüştürülecek binary dizisi.
    
    Returns:
        int: Decimal sayı.
    """
    binary_string = ''.join(map(str, binary_array))
    decimal_number = int(binary_string, 2)
    return decimal_number
    
def listen_and_decode(duration_per_bit=0.5, num_bits=10, sampling_rate=44100):
    """Gelen sinyali dinler ve Fourier dönüşümü ile 8 bitlik diziyi decode eder."""
    global tolarance,start_time, end_time,v2,BirBiti,SifirBiti,AyracBiti,StartBiti
    bit_array = []
    start_detected = False
    ayrac_detected = False
    

    while len(bit_array) < num_bits:
        # Sinyali kaydetme
        recorded_signal = sd.rec(int(sampling_rate * duration_per_bit), samplerate=sampling_rate, channels=1)
        sd.wait()

        # Fourier dönüşümünü hesaplama
        """Bu fonksiyon verilen veri için frekansı hesaplar."""
        fft_data = np.fft.fft(recorded_signal[:,0])
        freqs = np.fft.fftfreq(len(recorded_signal[:,0]), 1 / sampling_rate)
        idx = np.argmax(np.abs(fft_data))
        freq = freqs[idx]
        dominant_freq = abs(freq)
        if dominant_freq<1800 or dominant_freq > 46500:
            continue
        print(dominant_freq )
        if(abs(dominant_freq-StartBiti)<tolarance):
            bit_array=[]
            start_detected=True
            #print("StartBiti Algılandı")
            start_time = time.time()
            elapsed_time_str= str(round(start_time  - int(start_time),2))[2:3]
            v2= int(elapsed_time_str)#* (1 if len(elapsed_time_str) == 1 else 1)-1
            continue
            

        # Başlangıç frekansını kontrol et
        elif not ayrac_detected and  start_detected and abs(dominant_freq-AyracBiti)<tolarance:
            start_detected = False
            ayrac_detected=True
            print("Ayrac Algılandı")
            continue

        # Başlangıç frekansı algılandıktan sonra bitleri al
        elif ayrac_detected and not abs(dominant_freq - AyracBiti)<tolarance:
                # Sıradaki bitin frekansını kontrol et
                #print("Bitler Tespit ediliyor ...")
                if abs(dominant_freq-BirBiti) < tolarance:
                    bit_array.append(1)
                    print(f"Bit alındı: {bit_array[-1]}")
                    
                elif abs(dominant_freq-SifirBiti) < tolarance:
                    bit_array.append(0)
                    print(f"Bit alındı: {bit_array[-1]}")
                start_detected=False
    #end_time=time.time()
    #elapsed_time=end_time-start_time

    return bit_array, v2

def plot_recorded_signal(recorded_signal, sampling_rate):
    """Kaydedilmiş sinyalin zaman ve frekans spektrumunu çizer."""
    t = np.linspace(0, len(recorded_signal) / sampling_rate, num=len(recorded_signal))
    
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(t, recorded_signal)
    plt.title("Kaydedilmiş Sinyal")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Genlik")

    N = len(recorded_signal)
    yf = fft(recorded_signal)
    xf = fftfreq(N, 1 / sampling_rate)

    plt.subplot(2, 1, 2)
    plt.plot(xf[:N // 2], np.abs(yf)[:N // 2])
    plt.title("Frekans Spektrumu")
    plt.xlabel("Frekans (Hz)")
    plt.ylabel("Genlik")

    plt.tight_layout()
    plt.show()

while True:
	
    # Gelen sinyali dinle ve decode et
    bit_array,v2= listen_and_decode(duration_per_bit=0.05, num_bits=8, sampling_rate=88200)
    hamming_array=hamming_8_4_decode(bit_array)
    #print("Alınan Bit Dizisi:", bit_array)
    binary_array = gray_to_bin(hamming_array)
    Dec=BinToDec(binary_array )
    print("alinan :",Dec)
    #print("gecen_sure :",v2,"Alinan Veri :",Dec)
    if Dec>v2:
        v2+=10
    #print("sure farkı :",abs(v2-Dec))
    
