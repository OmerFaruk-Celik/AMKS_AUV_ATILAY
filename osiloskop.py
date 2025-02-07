import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# Başlangıç örnekleme frekansı ve pencere süresi
SAMPLE_RATE = 44100  # 44.1 kHz, CD kalitesinde ses
DURATION = 0.1  # 100 ms
XLIM = DURATION  # Başlangıç xlim
YLIM = 1  # Başlangıç ylim
INTERVAL = 50  # Başlangıç interval değeri (ms)
MAX_FRAMES = 1000  # Maksimum frame sayısı

# Ses verisi için bir kuyruk
audio_queue = []

# Ses stream nesnesi için global değişken
stream = None

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    # Kuyruğu sınırla
    if len(audio_queue) > 10:  # Maksimum 10 veri paketi tut
        audio_queue.pop(0)
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
s_interval = Slider(ax_interval, 'Interval', 10, 200, valinit=INTERVAL, orientation='vertical')

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
    INTERVAL = int(s_interval.val)
    
    if not audio_queue:
        return ln,
        
    try:
        ydata = audio_queue[-1]  # En son veriyi al
        xdata = np.linspace(0, DURATION, len(ydata))
        ln.set_data(xdata, ydata)
        ax.set_xlim(0, XLIM)
        ax.set_ylim(-YLIM, YLIM)
    except Exception as e:
        print(f"Update error: {e}")
        
    return ln,

def update_interval(val):
    global INTERVAL, ani
    INTERVAL = int(val)
    if hasattr(ani, 'event_source'):
        ani.event_source.interval = INTERVAL

def restart_stream():
    global stream, audio_queue
    # Mevcut stream'i temizle
    if stream is not None:
        stream.stop()
        stream.close()
    
    # Kuyruğu temizle
    audio_queue.clear()
    
    # Yeni stream başlat
    try:
        stream = sd.InputStream(callback=audio_callback, 
                              channels=1, 
                              samplerate=SAMPLE_RATE,
                              blocksize=int(SAMPLE_RATE * DURATION))
        stream.start()
    except Exception as e:
        print(f"Stream error: {e}")

def update_sample_rate(val):
    global SAMPLE_RATE
    SAMPLE_RATE = int(val)
    print(f"New sample rate: {SAMPLE_RATE}")
    restart_stream()

def update_duration(val):
    global DURATION
    DURATION = val
    print(f"New duration: {DURATION}")
    
    # xlim slider'ını güncelle
    s_xlim.valmax = DURATION  # Maximum değeri güncelle
    if s_xlim.val > DURATION:  # Eğer mevcut değer yeni maximum'dan büyükse
        s_xlim.set_val(DURATION)  # xlim değerini yeni duration'a eşitle
    
    # Slider'ın görsel sınırlarını güncelle
    ax_xlim.set_ylim(s_xlim.valmin, DURATION)
    
    # Grafik eksenini güncelle
    ax.set_xlim(0, s_xlim.val)
    
    restart_stream()
# Slider callback'leri
s_interval.on_changed(update_interval)
s_sample_rate.on_changed(update_sample_rate)
s_duration.on_changed(update_duration)

# Mikrofonu başlat
def baslat():
    global ani, stream
    try:
        restart_stream()
        ani = FuncAnimation(fig, update, init_func=init, 
                          blit=True, interval=INTERVAL,
                          cache_frame_data=False, save_count=MAX_FRAMES)
        plt.show()
    except KeyboardInterrupt:
        print("Ses verisi alımı durduruldu.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        if stream:
            stream.stop()
            stream.close()

# Başlat
baslat()
