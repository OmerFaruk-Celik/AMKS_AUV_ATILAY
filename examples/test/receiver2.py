import pyaudio
import numpy as np
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Mikrofon ayarları
RATE = 44100  # Örnekleme frekansı
CHUNK = 1024  # Her seferinde alınan veri miktarı

# Pyaudio nesnesi oluştur
p = pyaudio.PyAudio()

# Mikrofon girişi başlat
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

fig, ax = plt.subplots()
x = np.linspace(15000, 18000, CHUNK//2)
line, = ax.plot(x, np.random.rand(CHUNK//2))
ax.set_ylim(0, 255)
ax.set_xlim(15000, 18000)
ax.set_xlabel('Frekans (Hz)')
ax.set_ylabel('Amplitüd')
ax.set_title('15kHz - 18kHz Frekans Aralığı')

def update(frame):
    data = stream.read(CHUNK)
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    data_np = np.array(data_int, dtype='b')[::2] + 128
    
    fft_data = np.fft.fft(data_np)
    freqs = np.fft.fftfreq(len(fft_data)) * RATE
    
    idx = np.where((freqs >= 15000) & (freqs <= 18000))
    filtered_freqs = freqs[idx]
    filtered_fft = np.abs(fft_data[idx])
    
    line.set_ydata(filtered_fft)
    return line,

ani = FuncAnimation(fig, update, blit=True, interval=50)

plt.show()

# Dinlemeyi durdurmak için Ctrl+C kullanın.
try:
    plt.show()
except KeyboardInterrupt:
    print("Dinleme durduruldu")
    stream.stop_stream()
    stream.close()
    p.terminate()
