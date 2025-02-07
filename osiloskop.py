import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# Başlangıç örnekleme frekansı ve pencere süresi
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
plt.subplots_adjust(left=0.1, bottom=0.25)
xdata, ydata = [], []
ln, = plt.plot([], [], 'b-')
plt.xlabel('Zaman (saniye)')
plt.ylabel('Ses Amplitüdü')
plt.title('Gerçek Zamanlı Ses Verisi')
plt.grid(True)

# Sliderlar için eksenler
axcolor = 'lightgoldenrodyellow'
ax_duration = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_sample_rate = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axcolor)

# Sliderlar
s_duration = Slider(ax_duration, 'Duration', 0.0001, 0.1, valinit=DURATION, valstep=0.0001)
s_sample_rate = Slider(ax_sample_rate, 'Sample Rate', 20000, 200000, valinit=SAMPLE_RATE, valstep=1000)

def init():
    ax.set_xlim(0, DURATION)
    ax.set_ylim(-1, 1)
    return ln,

def update(frame):
    global SAMPLE_RATE, DURATION
    SAMPLE_RATE = int(s_sample_rate.val)
    DURATION = s_duration.val
    if not audio_queue:
        return ln,
    ydata = audio_queue.pop(0)
    xdata = np.linspace(0, DURATION, len(ydata))
    ln.set_data(xdata, ydata)
    ax.set_xlim(0, DURATION)
    return ln,

# Slider güncelleme fonksiyonları
def update_duration(val):
    global DURATION
    DURATION = val

def update_sample_rate(val):
    global SAMPLE_RATE
    SAMPLE_RATE = int(val)

s_duration.on_changed(update_duration)
s_sample_rate.on_changed(update_sample_rate)

# Mikrofonu başlat
try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE):
        ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=50)
        plt.show()

except KeyboardInterrupt:
    print("Ses verisi alımı durduruldu.")
except Exception as e:
    print(f"Bir hata oluştu: {e}")
