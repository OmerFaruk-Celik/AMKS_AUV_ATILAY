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
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        if len(data) < CHUNK * 2:
            return line,

        data_int = struct.unpack(str(len(data) // 2) + 'h', data)
        data_np = np.array(data_int, dtype='int16')

        fft_data = np.fft.fft(data_np)
        freqs = np.fft.fftfreq(len(fft_data)) * RATE
        
        idx = np.where((freqs >= 15000) & (freqs <= 18000))
        filtered_freqs = freqs[idx]
        filtered_fft = np.abs(fft_data[idx])
        
        # Boyutları eşitlemek için interpolasyon kullan
        if len(filtered_fft) > 0:
            line.set_ydata(np.interp(x, filtered_freqs, filtered_fft))
        
    except IOError as e:
        print(f"IOError: {e}")
    
    return line,

ani = FuncAnimation(fig, update, interval=50, cache_frame_data=False)

plt.show()

# Dinlemeyi durdurmak için Ctrl+C kullanın.
try:
    plt.show()
except KeyboardInterrupt:
    print("Dinleme durduruldu")
    stream.stop_stream()
    stream.close()
    p.terminate()
