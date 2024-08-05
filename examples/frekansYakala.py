import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

# Function to update frame
def update_frame(i):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    line.set_ydata(data)
    return line,

# Set up figure and animation
fig, ax = plt.subplots(5, 1, figsize=(10, 10))
lines = []

for i in range(5):
    line, = ax[i].plot(np.arange(CHUNK), np.zeros(CHUNK))
    lines.append(line)
    ax[i].set_ylim(-32768, 32767)

ani = animation.FuncAnimation(fig, update_frame, interval=50, blit=True)

plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
