import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, TextBox
from scipy import signal
from scipy.fft import fft, fftfreq

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

# Fourier analizi fonksiyonu
def calculate_dominant_frequency(data, sample_rate):
    if len(data) == 0:
        return 0
    
    yf = fft(data)
    xf = fftfreq(len(data), 1/sample_rate)
    
    # Sadece pozitif frekansları al
    yf = yf[:len(data)//2]
    xf = xf[:len(data)//2]
    
    # En büyük genliğe sahip frekansı bul
    dominant_idx = np.argmax(np.abs(yf))
    return abs(xf[dominant_idx])

# Band geçiren filtre fonksiyonu
def apply_bandpass_filter(data, lowcut, highcut, sample_rate, order=FILTER_ORDER):
    nyquist = sample_rate / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, data)

# Gürültü filtreleme fonksiyonu
def apply_noise_filter(data, threshold):
    mask = np.abs(data) > threshold
    filtered_data = data.copy()
    filtered_data[~mask] = 0
    return filtered_data

# Grafik oluşturma
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.85, hspace=0.3)

# Zaman domain grafiği
line1, = ax1.plot([], [], 'b-', label='Orijinal Sinyal')
line_filtered, = ax1.plot([], [], 'r-', label='Filtrelenmiş Sinyal', alpha=0.7)
freq_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes)
ax1.grid(True)
ax1.set_xlabel('Zaman (saniye)')
ax1.set_ylabel('Genlik')
ax1.set_title('Zaman Domain Analizi')
ax1.legend()

# Frekans domain grafiği
line2, = ax2.plot([], [], 'g-')
ax2.grid(True)
ax2.set_xlabel('Frekans (Hz)')
ax2.set_ylabel('Genlik')
ax2.set_title('Frekans Domain Analizi')

# Kontrol paneli
axcolor = 'lightgoldenrodyellow'
ax_duration = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_sample_rate = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axcolor)

# Filtre kontrolleri
ax_lowcut = plt.axes([0.88, 0.7, 0.1, 0.03], facecolor=axcolor)
ax_highcut = plt.axes([0.88, 0.6, 0.1, 0.03], facecolor=axcolor)
ax_noise = plt.axes([0.88, 0.5, 0.1, 0.03], facecolor=axcolor)

# Sliderlar
s_duration = Slider(ax_duration, 'Duration', 0.0001, 0.1, valinit=DURATION)
s_sample_rate = Slider(ax_sample_rate, 'Sample Rate', 20000, 400000, valinit=SAMPLE_RATE)
s_noise = Slider(ax_noise, 'Noise Threshold', 0, 1, valinit=DEFAULT_NOISE_THRESHOLD)

# Textbox'lar
t_lowcut = TextBox(ax_lowcut, 'Low Cut (Hz)', initial=str(DEFAULT_LOWCUT))
t_highcut = TextBox(ax_highcut, 'High Cut (Hz)', initial=str(DEFAULT_HIGHCUT))

def init():
    ax1.set_xlim(0, XLIM)
    ax1.set_ylim(-YLIM, YLIM)
    ax2.set_xlim(0, SAMPLE_RATE/2)
    ax2.set_ylim(0, 1)
    return line1, line_filtered, line2

def update(frame):
    global SAMPLE_RATE, DURATION
    
    if not audio_queue:
        return line1, line_filtered, line2

    try:
        # Zaman domain verisi
        ydata = audio_queue[-1]
        xdata = np.linspace(0, DURATION, len(ydata))
        
        # Filtreleme
        lowcut = float(t_lowcut.text)
        highcut = float(t_highcut.text)
        noise_threshold = s_noise.val
        
        # Band geçiren filtre uygula
        filtered_data = apply_bandpass_filter(ydata, lowcut, highcut, SAMPLE_RATE)
        
        # Gürültü filtresi uygula
        filtered_data = apply_noise_filter(filtered_data, noise_threshold)
        
        # Dominant frekansı hesapla
        dominant_freq = calculate_dominant_frequency(filtered_data, SAMPLE_RATE)
        freq_text.set_text(f'Dominant Frekans: {dominant_freq:.1f} Hz')
        
        # FFT hesapla
        yf = np.abs(fft(filtered_data))
        xf = fftfreq(len(filtered_data), 1/SAMPLE_RATE)
        
        # Pozitif frekansları al
        positive_freq_mask = xf >= 0
        yf = yf[positive_freq_mask]
        xf = xf[positive_freq_mask]
        
        # Normalize et
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

# Callback fonksiyonları
def update_sample_rate(val):
    global SAMPLE_RATE
    SAMPLE_RATE = int(val)
    restart_stream()

def update_duration(val):
    global DURATION
    DURATION = val
    restart_stream()

# Callback'leri bağla
s_sample_rate.on_changed(update_sample_rate)
s_duration.on_changed(update_duration)

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
