import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, filtfilt, lfilter
import time
from pyldpc import make_ldpc, encode, decode, get_message
import noisereduce as nr  # noisereduce kütüphanesini ekle

# Ses kayıt parametreleri
CHUNK = 512 * 5  # Her seferde alınacak örnek sayısı
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

# Butterworth band-pass filtre tasarımı
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Grafik hazırlıkları
fig, ax = plt.subplots()

# Zaman aralığını hesapla
x = np.arange(0, CHUNK) * (1.0 / RATE)  # Zaman ekseni

line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(-32000, 32000)
ax.set_xlim(0, CHUNK * (1.0 / RATE))  # X ekseni için zamansal ölçek

plt.xlabel('Zaman (saniye)')
plt.ylabel('Genlik')
plt.title('Osiloskop')

# Frekans değeri için metin ekleyin
text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

# Mesaj için metin ekleyin
message_text = ax.text(0.05, 0.85, '', transform=ax.transAxes)

def update_frame(frame):
    # Ses verilerini oku
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = np.frombuffer(data, dtype=np.int16)

    # Frekans spektrumunu hesapla
    frekans = np.fft.rfftfreq(len(data_int), 1/RATE)
    spektrum = np.fft.rfft(data_int)
    frekans_peak = frekans[np.argmax(np.abs(spektrum))]

    # Eğer frekans koşulu sağlanıyorsa:
    if frekans_peak > 18000.0 and frekans_peak < 19000.0:
        # Veriyi işleme ve grafiğe gönderme işlemlerini yap
        n = 2  # Sinyali yumuşatmak için
        b = [1.0 / n] * n
        a = 1
        yy = lfilter(b, a, data_int)

        filtered_data = yy

        # Veriyi güncelle
        line.set_ydata(filtered_data)

        # Frekans değerini güncelle
        text.set_text(f'Frekans: {frekans_peak:.2f} Hz')
        
    else:
        line.set_ydata(np.repeat(0, CHUNK))  # Grafiği sıfırla
        text.set_text('Frekans: Dışı')

    return line, text, message_text

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=5, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
