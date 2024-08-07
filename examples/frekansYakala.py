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
lowcut = 18000.0
highcut = 18200.0

# Function to update frame
def update_frame(i):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    filtered_data = bandpass_filter(data, lowcut, highcut, RATE)

    # Update time domain plot
    line.set_ydata(filtered_data)

    # Compute FFT and find the dominant frequency
    fft_data = np.fft.fft(filtered_data)
    fft_freq = np.fft.fftfreq(len(filtered_data), 1/RATE)
    dominant_freq = np.abs(fft_freq[np.argmax(np.abs(fft_data))])

    # Update frequency text
    freq_text.set_text(f'Dominant Frequency: {dominant_freq:.2f} Hz')

    return line, freq_text

# Set up figure and animation
fig, ax = plt.subplots(figsize=(10, 5))

# Time domain plot
line, = ax.plot(np.arange(CHUNK), np.zeros(CHUNK))
ax.set_ylim(-32768, 32767)
ax.set_xlim(0, CHUNK)
ax.set_title("Time Domain")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")

# Frequency text
freq_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=14, verticalalignment='top')

ani = animation.FuncAnimation(fig, update_frame, interval=50, blit=True)

plt.tight_layout()
plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
