import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Örnekleme frekansı ve pencere süresi
SAMPLE_RATE = 44100  # 44.1 kHz, CD kalitesinde ses
DURATION = 0.1  # 100 ms

# Ses verisi için bir kuyruk
audio_queue = []

# Ses verisini işlemek için bir geri çağırma fonksiyonu
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    # Alınan ses verisini kuyruğa ekle
    audio_queue.append(indata[:, 0])

# Grafik oluşturma
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'b-')
plt.xlabel('Zaman (saniye)')
plt.ylabel('Ses Amplitüdü')
plt.title('Gerçek Zamanlı Ses Verisi')
plt.grid(True)

def init():
    ax.set_xlim(0, DURATION)
    ax.set_ylim(-1, 1)
    return ln,

def update(frame):
    if not audio_queue:
        return ln,
    ydata = audio_queue.pop(0)
    xdata = np.linspace(0, DURATION, len(ydata))
    ln.set_data(xdata, ydata)
    return ln,

# Mikrofonu başlat
try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE):
        ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=50)
        plt.show()

except KeyboardInterrupt:
    print("Ses verisi alımı durduruldu.")
except Exception as e:
    print(f"Bir hata oluştu: {e}")
