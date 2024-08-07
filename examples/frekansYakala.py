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
    for line, fd in zip(lines, np.array_split(filtered_data, 5)):
        line.set_ydata(fd)
    return lines

# Set up figure and animation
fig, ax = plt.subplots(5, 1, figsize=(10, 10))
lines = []

for i in range(5):
    line, = ax[i].plot(np.arange(CHUNK//5), np.zeros(CHUNK//5))
    lines.append(line)
    ax[i].set_ylim(-32768, 32767)

ani = animation.FuncAnimation(fig, update_frame, interval=10, blit=True)

plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
