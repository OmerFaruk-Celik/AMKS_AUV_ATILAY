import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, AxesWidget

class Bar(AxesWidget):
    """
    A bar widget for matplotlib.
    """
    def __init__(self, ax, label, valmin, valmax, valinit=0.5, orientation='horizontal', **kwargs):
        AxesWidget.__init__(self, ax)

        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.orientation = orientation
        self.poly = ax.barh if orientation == 'horizontal' else ax.bar

        self.bar = self.poly([label], [valinit], **kwargs)
        ax.set_xlim(valmin, valmax) if orientation == 'horizontal' else ax.set_ylim(valmin, valmax)
        self.connect_event('button_press_event', self._update)
        self.connect_event('motion_notify_event', self._update)
        self.connect_event('button_release_event', self._release)
        self.callbacks = {}

    def _update(self, event):
        if self.ignore(event):
            return
        if not self.ax.contains(event)[0]:
            return

        value = event.xdata if self.orientation == 'horizontal' else event.ydata
        self.set_val(value)

    def _release(self, event):
        if not self.eventson:
            return
        self._update(event)

    def set_val(self, val):
        val = max(self.valmin, min(self.valmax, val))
        self.val = val
        if self.orientation == 'vertical':
            self.bar[0].set_height(val)
        else:
            self.bar[0].set_width(val)
        self.ax.figure.canvas.draw_idle()  # Çubuğun yeniden çizilmesini sağlar
        if not self.eventson:
            return
        if 'change' in self.callbacks:
            for callback in self.callbacks['change']:
                callback(self.val)

    def on_changed(self, callback):
        if 'change' not in self.callbacks:
            self.callbacks['change'] = []
        self.callbacks['change'].append(callback)

# Başlangıç örnekleme frekansı ve pencere süresi
SAMPLE_RATE = 44100# 44.1 kHz, CD kalitesinde ses
DURATION = 0.1  # 100 ms
XLIM = DURATION  # Başlangıç xlim
YLIM = 1  # Başlangıç ylim
INTERVAL = 50  # Başlangıç interval değeri (ms)

# Ses verisi için bir kuyruk
audio_queue = []

# Ses verisini işlemek için bir geri çağırma fonksiyonu
def audio_callback(indata, frames, time, status):
    global INTERVAL
    print(INTERVAL)
    if status:
        print(status)
    # Alınan ses verisini kuyruğa ekle
    audio_queue.append(indata[:, 0])

# Grafik oluşturma
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.85)
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
ax_xlim = plt.axes([0.88, 0.25, 0.03, 0.63], facecolor=axcolor)
ax_ylim = plt.axes([0.93, 0.25, 0.03, 0.63], facecolor=axcolor)
ax_interval = plt.axes([0.05, 0.25, 0.03, 0.63], facecolor=axcolor)

# Sliderlar
s_duration = Slider(ax_duration, 'Duration', 0.0001, 0.1, valinit=DURATION, valstep=0.0001)
s_sample_rate = Slider(ax_sample_rate, 'Sample Rate', 20000, 200000, valinit=SAMPLE_RATE, valstep=1000)
s_xlim = Slider(ax_xlim, 'X Lim', 0.001, 0.1, valinit=XLIM, valstep=0.001, orientation='vertical')
s_ylim = Slider(ax_ylim, 'Y Lim', 0.001, 1, valinit=YLIM, valstep=0.01, orientation='vertical')

# Bar
b_interval = Bar(ax_interval, 'Interval', 10, 200, valinit=INTERVAL, orientation='vertical', color='blue')

def init():
    ax.set_xlim(0, XLIM)
    ax.set_ylim(-YLIM, YLIM)
    return ln,

def update(frame):
    global SAMPLE_RATE, DURATION, XLIM, YLIM, INTERVAL
    SAMPLE_RATE = int(s_sample_rate.val)
    DURATION = s_duration.val
    XLIM = s_xlim.val
    YLIM = s_ylim.val
    INTERVAL = int(b_interval.val)
    if not audio_queue:
        return ln,
    ydata = audio_queue.pop(0)
    xdata = np.linspace(0, DURATION, len(ydata))
    ln.set_data(xdata, ydata)
    ax.set_xlim(0, XLIM)
    ax.set_ylim(-YLIM, YLIM)
    return ln,

# Bar güncelleme fonksiyonu
def update_interval(val):
    global INTERVAL
    INTERVAL = int(val)
   
    if 'ani' in globals() and ani:
        ani.event_source.interval = INTERVAL

b_interval.on_changed(update_interval)

# Mikrofonu başlat
def baslat():
    global ani
    try:
        print(INTERVAL)
        ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=INTERVAL)
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE) as listen:
            plt.show()

        
    except KeyboardInterrupt:
        print("Ses verisi alımı durduruldu.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")


# Başlat ve durdur fonksiyonlarını test etmek için
baslat()
# stop() fonksiyonunu çağırmak için bir yol ekleyebilirsiniz
# Örneğin, bir tuşa basıldığında stop() fonksiyonunu çağırabilirsiniz
