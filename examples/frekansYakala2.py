import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, lfilter

# Set up audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 10

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
lowcut = 17600.0
highcut = 18800.0

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

    # Calculate and update the two-wavelength plot
    wavelength = RATE / dominant_freq if dominant_freq != 0 else 0
    num_samples = int(2 * wavelength)
    two_wavelength_data = filtered_data[:num_samples] if num_samples < len(filtered_data) else filtered_data
    line_wavelength.set_ydata(two_wavelength_data)
    line_wavelength.set_xdata(np.arange(len(two_wavelength_data)))

    return line, freq_text, line_wavelength

# Set up figure and animation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# Time domain plot
line, = ax1.plot(np.arange(CHUNK), np.zeros(CHUNK))
ax1.set_ylim(-32768, 32767)
ax1.set_xlim(40, CHUNK/100)
ax1.set_title("Time Domain")
ax1.set_xlabel("Samples")
ax1.set_ylabel("Amplitude")

# Frequency text
freq_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=14, verticalalignment='top')

# Two-wavelength plot
line_wavelength, = ax2.plot(np.arange(CHUNK), np.zeros(CHUNK))
ax2.set_ylim(-32768, 32767)
ax2.set_xlim(0, CHUNK)
ax2.set_title("Two Wavelengths")
ax2.set_xlabel("Samples")
ax2.set_ylabel("Amplitude")

ani = animation.FuncAnimation(fig, update_frame, interval=50, blit=True)

plt.tight_layout()
plt.show()

# Close audio stream
stream.stop_stream()
stream.close()
p.terminate()
