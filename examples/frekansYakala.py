import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, lfilter

# Set up audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 5

# Initialize audio stream
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Bandpass filter design
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Filter parameters
lowcut = 16000.0
highcut = 17000.0

# Function to update frame
def update_frame(i):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    filtered_data = bandpass_filter(data, lowcut, highcut, RATE)

    # Update time domain plot
    line.set_ydata(filtered_data)

    # Compute FFT and update frequency domain plot
    fft_data = np.fft.fft(filtered_data)
    fft_freq = np.fft.fftfreq(len(filtered_data), 1/RATE)
    line_fft.set_ydata(np.abs(fft_data)[:CHUNK // 2])
    
    return line, line_fft

# Set up figure and animation
fig, (ax_time, ax_freq) = plt.subplots(2, 1, figsize=(10, 10))

# Time domain plot
line, = ax_time.plot(np.arange(CHUNK), np.zeros(CHUNK))
ax_time.set_ylim(-32768, 32767)
ax_time.set_xlim(0, CHUNK)
ax_time.set_title("Time Domain")
ax_time.set_xlabel("Samples")
ax_time.set_ylabel("Amplitude")

# Frequency domain plot
line_fft, = ax_freq.plot(np.linspace(0, RATE / 2, CHUNK // 2), np.zeros(CHUNK // 2))
ax_freq.set_ylim(0, 1000)
ax_freq.set_xlim(0, RATE / 2)
ax_freq.set_title("Frequency Domain")
ax_freq.set_xlabel("Frequency (Hz)")
ax_freq.set_ylabel("Amplitude")

ani = animation.FuncAnimation(fig, update_frame, interval=50, blit=True)

plt.tight_layout()
plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
