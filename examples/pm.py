import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import hilbert, butter, filtfilt, lfilter
import time

# Ses kayıt parametreleri
CHUNK = 1024  # Her seferde alınacak örnek sayısı
FORMAT = pyaudio.paInt16  # Örnek formatı
CHANNELS = 1  # Kanal sayısı
RATE = 44100  # Örnekleme hızı

# PyAudio nesnesi oluştur
p = pyaudio.PyAudio()

# Giriş akışını aç (mikrofonu dinleme)
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# PM parametreleri
fc = 2000  # Taşıyıcı sinyal frekansı (Hz)
kp = 2 * np.pi * 10  # Faz sapması (radyan)

# Grafik hazırlıkları
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(-1000, 1000)
ax.set_xlim(0, CHUNK)
plt.xlabel('Zaman')
plt.ylabel('Genlik')
plt.title('Osiloskop')

# Veri bitleri
bit_array = np.zeros(32, dtype=int)  # Başlangıçta tüm bitleri sıfır olarak ayarla

def parca_kontrol(s, sutun_sayisi, rate):
    """
    Verilen 's' verisini 'sutun_sayisi' kadar parçaya bölerek, her bir parçanın içindeki fazı hesaplar.
    Eğer parçanın fazı belirli bir aralıkta ise 1, değilse 0 değerini döndüren bir dizi oluşturur.

    Args:
      s: Kontrol edilecek verilerin numpy dizisi.
      sutun_sayisi: Verinin bölüneceği parça sayısı.
      rate: Örnekleme oranı (Hz).

    Returns:
      Her bir parçanın faz kontrol sonucunu (1: aralıkta, 0: dışında) gösteren bir numpy dizisi.
    """

    global bit_array  # Global bit_array değişkenine erişmek için

    fazlar = []
    sutun_genisligi = len(s) / sutun_sayisi

    for i in range(sutun_sayisi):
        baslangic_indeksi = int(i * sutun_genisligi)
        bitis_indeksi = int((i + 1) * sutun_genisligi)

        parca = s[baslangic_indeksi:bitis_indeksi]

        # Parçanın fazını hesaplama
        faz = np.unwrap(np.angle(hilbert(parca)))
        faz_ortalama = np.mean(faz)
        fazlar.append(faz_ortalama)

    fazlar = np.array(fazlar)

    # Faz kontrolü (Belirli bir aralıkta mı?)
    # Bu aralık PM iletim sinyalindeki faz değişikliklerine göre ayarlanmalı
    kosul = (fazlar > 0.5) & (fazlar < 1.5)

    bits = np.where(kosul, 1, 0)

    # Bitleri güncelle (32 bitlik diziyi döndürmek yerine)
    bit_array[:sutun_sayisi] = bits

    return None

def update_frame(frame):
    # Ses verilerini oku
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = np.frombuffer(data, dtype=np.int16)

    # Veriyi güncelle
    line.set_ydata(data_int)

    # Faz değişimini hesaplama
    # (PM demodülasyonu için, faz değişimini analiz ediyoruz)
    faz_degisim = np.unwrap(np.angle(hilbert(data_int)))

    # Faz değişimini bitlere dönüştür
    parca_kontrol(faz_degisim, 16, RATE)

    # Bit dizisini yazdır
    print(bit_array)

    # Veri bitlerini grafiğe çizdir
    plt.figure(2)  # İkinci bir grafik oluştur (eğer yoksa)
    plt.clf()  # Grafiği temizle
    plt.plot(bit_array)
    plt.xlabel('Bit İndeksi')
    plt.ylabel('Bit Değeri')
    plt.title('Demodüle Edilmiş Veri')
    plt.ylim(-0.2, 1.2)  # Bit değerleri için y eksenini ayarlayın

    return line, 

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=2, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
