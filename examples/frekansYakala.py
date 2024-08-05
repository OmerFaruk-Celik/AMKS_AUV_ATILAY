import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, filtfilt

# Ses kayıt parametreleri
CHUNK = 512  # Her seferde alınacak örnek sayısı
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

# Frekans aralığı
lowcut = 13000.0
highcut = 15000.0

# Grafik hazırlıkları
fig, ax = plt.subplots()
line, = ax.plot(np.random.rand(CHUNK))

ax.set_ylim(-1000, 1000)
plt.xlabel('Zaman')
plt.ylabel('Genlik')
plt.title('Osiloskop')

# Frekans değeri için metin ekleyin
text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

def update_frame(frame):
    # Ses verilerini oku
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = np.frombuffer(data, dtype=np.int16)
    
    # Frekans spektrumunu hesapla
    frekans = np.fft.rfftfreq(len(data_int), 1/RATE)
    spektrum = np.fft.rfft(data_int)
    frekans_peak = frekans[np.argmax(np.abs(spektrum))]
    
    # Eğer frekans koşulu sağlanıyorsa:
    if lowcut < frekans_peak < highcut:
        # Band-pass filtre uygulama
        filtered_data = bandpass_filter(data_int, lowcut, highcut, RATE, order=5)
        
        # Dalga boyunu hesapla
        wave_length = int(RATE / frekans_peak)
        
        # Bir dalga boyu kadar veriyi al
        single_wave = filtered_data[:wave_length]
        
        # Veriyi güncelle
        line.set_ydata(single_wave)
        
        # X eksenini güncelle
        line.set_xdata(np.arange(wave_length))
        
        # Frekans değerini güncelle
        text.set_text(f'Frekans: {frekans_peak:.2f} Hz')
    else:
        line.set_ydata(np.zeros(CHUNK))  # Grafiğe sıfır veri gönder
        text.set_text('Frekans: Dışı')

    return line, text

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=50, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
