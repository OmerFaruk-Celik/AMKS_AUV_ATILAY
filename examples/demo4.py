import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, filtfilt, lfilter

# Ses kayıt parametreleri
CHUNK = 512 * 5
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# PyAudio nesnesi oluştur
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Grafik hazırlıkları
fig, ax = plt.subplots()
x = np.arange(0, CHUNK) * (1.0 / RATE)  # Zaman ekseni
line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(-32000, 32000)
ax.set_xlim(0, CHUNK * (1.0 / RATE))  # X ekseni için zamansal ölçek

plt.xlabel('Zaman (saniye)')
plt.ylabel('Genlik')
plt.title('Osiloskop')

# Frekans değeri için metin ekleyin
text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

# Dalga boyu sayısı için metin ekleyin
wavelength_text = ax.text(0.05, 0.8, '', transform=ax.transAxes)

def update_frame(frame):
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = np.frombuffer(data, dtype=np.int16)

    # Frekans spektrumunu hesapla
    frekans = np.fft.rfftfreq(len(data_int), 1/RATE)
    spektrum = np.fft.rfft(data_int)
    frekans_peak = frekans[np.argmax(np.abs(spektrum))]

    # Eğer frekans koşulu sağlanıyorsa:
    if 18000.0 < frekans_peak < 19000.0:
        n = 2
        b = [1.0 / n] * n
        a = 1
        yy = lfilter(b, a, data_int)

        line.set_ydata(yy)

        # Frekans değerini güncelle
        text.set_text(f'Frekans: {frekans_peak:.2f} Hz')

        # Dalga boyu sayısını hesapla
        total_time = CHUNK / RATE
        number_of_wavelengths = frekans_peak * total_time
        wavelength_text.set_text(f'Dalga Boyu Sayısı: {number_of_wavelengths:.2f}')
        
    else:
        line.set_ydata(np.repeat(0, CHUNK))
        text.set_text('Frekans: Dışı')
        wavelength_text.set_text('Dalga Boyu Sayısı: -')

    return line, text, wavelength_text

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=5, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
