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
lowcut = 15000.0
highcut = 18000.0

# Function to update frame
def update_frame(i):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    filtered_data = bandpass_filter(data, lowcut, highcut, RATE)
    line.set_ydata(filtered_data * 100)  # Zoomed in by a factor of 100
    return line,

# Set up figure and animation
fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot(np.arange(CHUNK), np.zeros(CHUNK))
ax.set_ylim(-32768 * 100, 32767 * 100)

ani = animation.FuncAnimation(fig, update_frame, interval=10, blit=True)

plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
