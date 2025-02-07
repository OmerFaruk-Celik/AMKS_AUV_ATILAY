import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, TextBox
from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.style as style
from matplotlib.gridspec import GridSpec

# Modern stil ayarları
plt.style.use('default')
plt.rcParams.update({
    'font.family': 'serif',
    'font.sans-serif': ['Arial'],
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.facecolor': '#f0f0f0',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#cccccc',
    'grid.color': '#cccccc'
})

# Başlangıç parametreleri
SAMPLE_RATE = 44100
DURATION = 0.1
XLIM = DURATION
YLIM = 1
INTERVAL = 50
MAX_FRAMES = 1000

# Filtre parametreleri
FILTER_ORDER = 4
DEFAULT_LOWCUT = 500
DEFAULT_HIGHCUT = 2000
DEFAULT_NOISE_THRESHOLD = 0.1

# Veri kuyruğu
audio_queue = []
stream = None

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    if len(audio_queue) > 10:
        audio_queue.pop(0)
    audio_queue.append(indata[:, 0])

def calculate_dominant_frequency(data, sample_rate):
    if len(data) == 0:
        return 0
    
    yf = fft(data)
    xf = fftfreq(len(data), 1/sample_rate)
    
    yf = yf[:len(data)//2]
    xf = xf[:len(data)//2]
    
    dominant_idx = np.argmax(np.abs(yf))
    return abs(xf[dominant_idx])

def apply_bandpass_filter(data, lowcut, highcut, sample_rate, order=FILTER_ORDER):
    nyquist = sample_rate / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, data)

def apply_noise_filter(data, threshold):
    mask = np.abs(data) > threshold
    filtered_data = data.copy()
    filtered_data[~mask] = 0
    return filtered_data

# Grafik oluşturma
fig = plt.figure(figsize=(12, 8))
gs = GridSpec(2, 2, width_ratios=[0.2, 1], height_ratios=[1, 1])
plt.subplots_adjust(left=0.25, bottom=0.12, right=0.95, top=0.95, hspace=0.3)

# Sol kontrol paneli için axes
ax_controls = plt.subplot(gs[:, 0])
ax_controls.set_visible(False)

# Ana grafikler
ax1 = plt.subplot(gs[0, 1])
ax2 = plt.subplot(gs[1, 1])

# Grafik ayarları
line1, = ax1.plot([], [], '#2196F3', label='Orijinal Sinyal', linewidth=1.5)
line_filtered, = ax1.plot([], [], '#FF4081', label='Filtrelenmiş Sinyal', alpha=0.7, linewidth=1.5)
freq_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('Zaman (saniye)', fontsize=10)
ax1.set_ylabel('Genlik', fontsize=10)
ax1.set_title('Zaman Domain Analizi', fontsize=12, pad=10)
ax1.legend(loc='upper right', framealpha=0.9)

line2, = ax2.plot([], [], '#4CAF50', linewidth=1.5)
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('Frekans (Hz)', fontsize=10)
ax2.set_ylabel('Genlik', fontsize=10)
ax2.set_title('Frekans Domain Analizi', fontsize=12, pad=10)

# Slider ve textbox stil ayarları
slider_color = '#f8f9fa'
text_box_style = {'boxstyle': 'round,pad=0.5', 
                 'facecolor': slider_color,
                 'edgecolor': '#dee2e6'}

# Sol taraftaki kontroller için yeni konumlar
ax_xlim = plt.axes([0.05, 0.7, 0.03, 0.2], facecolor=slider_color)
ax_ylim = plt.axes([0.12, 0.7, 0.03, 0.2], facecolor=slider_color)
ax_lowcut = plt.axes([0.05, 0.45, 0.1, 0.03], facecolor=slider_color)
ax_highcut = plt.axes([0.05, 0.4, 0.1, 0.03], facecolor=slider_color)
ax_noise = plt.axes([0.05, 0.35, 0.1, 0.03], facecolor=slider_color)

# Alt kısımdaki kontrol sliderları
ax_duration = plt.axes([0.25, 0.05, 0.5, 0.02], facecolor=slider_color)
ax_sample_rate = plt.axes([0.25, 0.09, 0.5, 0.02], facecolor=slider_color)

# Kontrol elemanları
s_xlim = Slider(ax_xlim, 'X Lim', 0.001, 0.5, valinit=XLIM, orientation='vertical',
                color='#4CAF50')
s_ylim = Slider(ax_ylim, 'Y Lim', 0.1, 2.0, valinit=YLIM, orientation='vertical',
                color='#4CAF50')
s_duration = Slider(ax_duration, 'Duration', 0.0001, 0.1, valinit=DURATION,
                   color='#2196F3')
s_sample_rate = Slider(ax_sample_rate, 'Sample Rate', 20000, 400000, valinit=SAMPLE_RATE,
                      color='#2196F3')
s_noise = Slider(ax_noise, 'Noise', 0, 1, valinit=DEFAULT_NOISE_THRESHOLD,
                color='#FF9800')

# Text boxlar
t_lowcut = TextBox(ax_lowcut, 'Low Cut Hz', initial=str(DEFAULT_LOWCUT),
                  textalignment="center", label_pad=0.1)
t_highcut = TextBox(ax_highcut, 'High Cut Hz', initial=str(DEFAULT_HIGHCUT),
                   textalignment="center", label_pad=0.1)

# Text box stilleri
for tb in [t_lowcut, t_highcut]:
    tb.label.set_color('#333333')
    tb.label.set_fontsize(9)
    tb.text_disp.set_fontsize(9)

def init():
    ax1.set_xlim(0, s_xlim.val)
    ax1.set_ylim(-s_ylim.val, s_ylim.val)
    ax2.set_xlim(0, SAMPLE_RATE/2)
    ax2.set_ylim(0, 1)
    return line1, line_filtered, line2

def update(frame):
    global SAMPLE_RATE, DURATION
    
    if not audio_queue:
        return line1, line_filtered, line2

    try:
        ydata = audio_queue[-1]
        xdata = np.linspace(0, DURATION, len(ydata))
        
        # Filtreleme
        lowcut = float(t_lowcut.text)
        highcut = float(t_highcut.text)
        noise_threshold = s_noise.val
        
        filtered_data = apply_bandpass_filter(ydata, lowcut, highcut, SAMPLE_RATE)
        filtered_data = apply_noise_filter(filtered_data, noise_threshold)
        
        # Dominant frekans
        dominant_freq = calculate_dominant_frequency(filtered_data, SAMPLE_RATE)
        freq_text.set_text(f'Dominant Frekans:\n{dominant_freq:.1f} Hz')
        
        # FFT
        yf = np.abs(fft(filtered_data))
        xf = fftfreq(len(filtered_data), 1/SAMPLE_RATE)
        
        positive_freq_mask = xf >= 0
        yf = yf[positive_freq_mask]
        xf = xf[positive_freq_mask]
        
        yf = yf / np.max(yf) if np.max(yf) > 0 else yf
        
        # Grafikleri güncelle
        line1.set_data(xdata, ydata)
        line_filtered.set_data(xdata, filtered_data)
        line2.set_data(xf, yf)
        
    except Exception as e:
        print(f"Update error: {e}")
    
    return line1, line_filtered, line2

def restart_stream():
    global stream, audio_queue
    if stream is not None:
        stream.stop()
        stream.close()
    audio_queue.clear()
    
    try:
        stream = sd.InputStream(callback=audio_callback,
                              channels=1,
                              samplerate=SAMPLE_RATE,
                              blocksize=int(SAMPLE_RATE * DURATION))
        stream.start()
    except Exception as e:
        print(f"Stream error: {e}")

def update_sample_rate(val):
    global SAMPLE_RATE,DURATION
    SAMPLE_RATE = int(val)
    highcut = float(t_highcut.text)
    restart_stream()
    #ax2.set_xlim(0, highcut)
    ax1.set_xlim(0, SAMPLE_RATE*DURATION)
    plt.draw()

def update_duration(val):
    global DURATION, XLIM
    DURATION = val
    XLIM = val
    
    # xlim slider'ını güncelle
    if s_xlim.val > DURATION:
        s_xlim.set_val(DURATION)
    
    s_xlim.valmax = DURATION
    ax_xlim.set_ylim(s_xlim.valmin, DURATION)
    
    restart_stream()
    plt.draw()

def update_xlim(val):
    ax1.set_xlim(0, val)
    plt.draw()

def update_ylim(val):
    ax1.set_ylim(-val, val)
    plt.draw()

# Callback'leri bağla
s_sample_rate.on_changed(update_sample_rate)
s_duration.on_changed(update_duration)
s_xlim.on_changed(update_xlim)
s_ylim.on_changed(update_ylim)

def baslat():
    global ani
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

# Programı başlat
baslat()
