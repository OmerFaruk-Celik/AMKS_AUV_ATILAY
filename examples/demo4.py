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
fig, (ax1, ax2) = plt.subplots(2, 1)

# Zaman aralığını hesapla
x = np.arange(0, CHUNK) * (1.0 / RATE)  # Zaman ekseni
line1, = ax1.plot(x, np.random.rand(CHUNK))
line2, = ax2.plot([], [])  # İkinci grafik için boş başlangıç

ax1.set_ylim(-32000, 32000)
ax1.set_xlim(0, CHUNK * (1.0 / RATE))  # X ekseni için zamansal ölçek
ax1.set_xlabel('Zaman (saniye)')
ax1.set_ylabel('Genlik')
ax1.set_title('Osiloskop')

ax2.set_ylim(-32000, 32000)
ax2.set_xlim(0, 10 * (1.0 / RATE))  # İkinci grafik için X eksenini ayarlayın (10 dalga boyu)
ax2.set_xlabel('Zaman (saniye)')
ax2.set_ylabel('Genlik')
ax2.set_title('10 Dalga Boyu')

# Frekans değeri için metin ekleyin
text = ax1.text(0.05, 0.9, '', transform=ax1.transAxes)

# Dalga boyu sayısı için metin ekleyin
wavelength_text = ax1.text(0.05, 0.8, '', transform=ax1.transAxes)

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

        line1.set_ydata(yy)

        # Frekans değerini güncelle
        text.set_text(f'Frekans: {frekans_peak:.2f} Hz')

        # Dalga boyu sayısını hesapla
        total_time = CHUNK / RATE
        number_of_wavelengths = frekans_peak * total_time
        wavelength_text.set_text(f'Dalga Boyu Sayısı: {number_of_wavelengths:.2f}')
        
        # 10 Dalga Boyunu Hesapla
        samples_per_wave = RATE / frekans_peak  # Bir dalga boyu için örnek sayısı
        total_samples = int(10 * samples_per_wave)  # 10 dalga boyu için toplam örnek sayısı

        if total_samples <= len(yy):
            wave_data = yy[:total_samples]
            wave_x = np.arange(0, total_samples) * (1.0 / RATE)
            line2.set_data(wave_x, wave_data)
            ax2.set_xlim(0, wave_x[-1])

    else:
        line1.set_ydata(np.repeat(0, CHUNK))
        text.set_text('Frekans: Dışı')
        wavelength_text.set_text('Dalga Boyu Sayısı: -')

    return line1, line2, text, wavelength_text

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=5, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
