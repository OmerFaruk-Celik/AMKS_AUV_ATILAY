import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, TextBox, CheckButtons
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
DEFAULT_LOWCUT = 5000
DEFAULT_HIGHCUT = 20000
DEFAULT_NOISE_THRESHOLD = 0.1
DEFAULT_SMOOTHING = 51
DEFAULT_FREQ_NOISE_THRESHOLD = 0.1  # FFT için gürültü eşiği

# Veri kuyruğu
audio_queue = []
stream = None
show_filtered = True  # Zaman domain filtresi kontrolü
show_freq_filtered = True  # Frekans domain filtresi kontrolü

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

def apply_smoothing(data, window_length):
    if window_length % 2 == 0:
        window_length += 1
    return signal.savgol_filter(data, window_length, 3)

def apply_freq_filter(freqs, amplitudes, threshold):
    mask = amplitudes > (threshold * np.max(amplitudes))
    filtered_amps = amplitudes.copy()
    filtered_amps[~mask] = 0
    return filtered_amps

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

# Grafik ayarları - Zaman Domain
line1, = ax1.plot([], [], '#2196F3', label='Orijinal Sinyal', linewidth=1.5)
line_filtered, = ax1.plot([], [], '#FF4081', label='Filtrelenmiş Sinyal', alpha=0.7, linewidth=1.5)
freq_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('Zaman (saniye)', fontsize=10)
ax1.set_ylabel('Genlik', fontsize=10)
ax1.set_title('Zaman Domain Analizi', fontsize=12, pad=10)
ax1.legend(loc='upper right', framealpha=0.9)

# Grafik ayarları - Frekans Domain
line2, = ax2.plot([], [], '#4CAF50', label='Orijinal FFT', linewidth=1.5)
line2_filtered, = ax2.plot([], [], '#FF9800', label='Filtrelenmiş FFT', alpha=0.7, linewidth=1.5)
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('Frekans (Hz)', fontsize=10)
ax2.set_ylabel('Genlik', fontsize=10)
ax2.set_title('Frekans Domain Analizi', fontsize=12, pad=10)
ax2.legend(loc='upper right', framealpha=0.9)

# Slider ve kontrolcü stil ayarları
slider_color = '#f8f9fa'
text_box_style = {'boxstyle': 'round,pad=0.5', 
                 'facecolor': slider_color,
                 'edgecolor': '#dee2e6'}

# Zaman domain kontrolleri
ax_xlim = plt.axes([0.05, 0.7, 0.03, 0.2], facecolor=slider_color)
ax_ylim = plt.axes([0.12, 0.7, 0.03, 0.2], facecolor=slider_color)
ax_lowcut = plt.axes([0.05, 0.45, 0.1, 0.03], facecolor=slider_color)
ax_highcut = plt.axes([0.05, 0.4, 0.1, 0.03], facecolor=slider_color)
ax_noise = plt.axes([0.05, 0.35, 0.1, 0.03], facecolor=slider_color)
ax_smooth = plt.axes([0.05, 0.3, 0.1, 0.03], facecolor=slider_color)
ax_toggle = plt.axes([0.05, 0.25, 0.1, 0.03])

# Frekans domain kontrolleri
ax_freq_noise = plt.axes([0.05, 0.15, 0.1, 0.03], facecolor='#e3f2fd')  # Farklı renk
ax_freq_toggle = plt.axes([0.05, 0.1, 0.1, 0.03])

# Alt kontrol sliderları
ax_duration = plt.axes([0.25, 0.05, 0.5, 0.02], facecolor=slider_color)
ax_sample_rate = plt.axes([0.25, 0.09, 0.5, 0.02], facecolor=slider_color)

# Kontrol elemanları - Zaman Domain
s_xlim = Slider(ax_xlim, 'X Lim', 0.001, 0.5, valinit=XLIM, orientation='vertical',
                color='#4CAF50')
s_ylim = Slider(ax_ylim, 'Y Lim', 0.001, 0.05, valinit=YLIM, orientation='vertical',
                color='#4CAF50')
s_duration = Slider(ax_duration, 'Duration', 0.0001, 0.1, valinit=DURATION,
                   color='#2196F3')
s_sample_rate = Slider(ax_sample_rate, 'Sample Rate', 20000, 400000, valinit=SAMPLE_RATE,
                      color='#2196F3')
s_noise = Slider(ax_noise, 'Time Noise', 0, 0.005, valinit=DEFAULT_NOISE_THRESHOLD,
                color='#FF9800')
s_smooth = Slider(ax_smooth, 'Smooth', 3, 99, valinit=DEFAULT_SMOOTHING,
                 color='#9C27B0')

# Kontrol elemanları - Frekans Domain
s_freq_noise = Slider(ax_freq_noise, 'Freq Noise', 0, 0.5, valinit=DEFAULT_FREQ_NOISE_THRESHOLD,
                     color='#2196F3')

# Toggle butonları
check_time = CheckButtons(ax_toggle, ['Time Filter'], [True])
check_freq = CheckButtons(ax_freq_toggle, ['Freq Filter'], [True])

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
    return line1, line_filtered, line2, line2_filtered

def toggle_time_filter(label):
    global show_filtered
    show_filtered = not show_filtered
    plt.draw()

def toggle_freq_filter(label):
    global show_freq_filtered
    show_freq_filtered = not show_freq_filtered
    plt.draw()

def update(frame):
    global SAMPLE_RATE, DURATION
    
    if not audio_queue:
        return line1, line_filtered, line2, line2_filtered

    try:
        ydata = audio_queue[-1]
        xdata = np.linspace(0, DURATION, len(ydata))
        
        # Zaman domain filtreleme
        lowcut = float(t_lowcut.text)
        highcut = float(t_highcut.text)
        noise_threshold = s_noise.val
        smooth_window = int(s_smooth.val)
        if smooth_window % 2 == 0:
            smooth_window += 1
        
        # Frekans domain filtreleme
        freq_noise_threshold = s_freq_noise.val
        
        if show_filtered:
            # Zaman domain filtresi
            filtered_data = apply_bandpass_filter(ydata, lowcut, highcut, SAMPLE_RATE)
            filtered_data = apply_noise_filter(filtered_data, noise_threshold)
            filtered_data = apply_smoothing(filtered_data, smooth_window)
            line_filtered.set_data(xdata, filtered_data)
            data_for_fft = filtered_data
        else:
			# Her zaman orijinal veriyi göster
            line1.set_data(xdata, ydata)
            line_filtered.set_data([], [])
            data_for_fft = ydata
            

            
        # FFT hesaplama
        yf = np.abs(fft(data_for_fft))
        xf = fftfreq(len(data_for_fft), 1/SAMPLE_RATE)
        
        # Pozitif frekansları al
        positive_freq_mask = xf >= 0
        yf = yf[positive_freq_mask]
        xf = xf[positive_freq_mask]
        
        # Normalize et
        yf = yf / np.max(yf) if np.max(yf) > 0 else yf
        
        # Orijinal FFT'yi göster
        line2.set_data(xf, yf)
        
        # Frekans filtresi
        if show_freq_filtered:
            filtered_yf = apply_freq_filter(xf, yf, freq_noise_threshold)
            line2_filtered.set_data(xf, filtered_yf)
            
            # Dominant frekansı filtrelenmiş veriden hesapla
            max_idx = np.argmax(filtered_yf)
            dominant_freq = xf[max_idx] if max_idx < len(xf) else 0
        else:
            line2_filtered.set_data([], [])
            # Dominant frekansı orijinal veriden hesapla
            max_idx = np.argmax(yf)
            dominant_freq = xf[max_idx] if max_idx < len(xf) else 0
            
        freq_text.set_text(f'Dominant Frekans:\n{dominant_freq:.1f} Hz')
        
    except Exception as e:
        print(f"Update error: {e}")
    
    return line1, line_filtered, line2, line2_filtered

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
    global SAMPLE_RATE
    SAMPLE_RATE = int(val)
    highcut = float(t_highcut.text)
    restart_stream()
    ax2.set_xlim(0, highcut)
    plt.draw()

def update_duration(val):
    global DURATION, XLIM
    DURATION = val
    XLIM = val
    
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
check_time.on_clicked(toggle_time_filter)
check_freq.on_clicked(toggle_time_filter)

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
