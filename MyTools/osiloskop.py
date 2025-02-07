import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import scipy.signal as signal
import numpy.fft as fft

class Osiloskop:
    def __init__(self, sample_rate=44100, duration=0.1, max_queue_size=10):
        self.SAMPLE_RATE = sample_rate
        self.DURATION = duration
        self.MAX_QUEUE_SIZE = max_queue_size
        
        self.audio_queue = []
        self.stream = None
        self.fig = None
        self.ani = None
        
        self._initialize_plot()
        
    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        if len(self.audio_queue) > self.MAX_QUEUE_SIZE:
            self.audio_queue.pop(0)
        self.audio_queue.append(indata[:, 0])
    
    def _initialize_plot(self):
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.25, bottom=0.25, right=0.85)
        self.ln, = plt.plot([], [], 'b-')
        plt.xlabel('Zaman (saniye)')
        plt.ylabel('Ses Amplitüdü')
        plt.title('Gerçek Zamanlı Ses Verisi')
        plt.grid(True)
        
    def start_stream(self, sample_rate=None, duration=None):
        if sample_rate:
            self.SAMPLE_RATE = sample_rate
        if duration:
            self.DURATION = duration
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        self.audio_queue.clear()
        
        try:
            self.stream = sd.InputStream(
                callback=self._audio_callback, 
                channels=1, 
                samplerate=self.SAMPLE_RATE,
                blocksize=int(self.SAMPLE_RATE * self.DURATION)
            )
            self.stream.start()
        except Exception as e:
            print(f"Stream error: {e}")
    
    def visualize(self, interval=50):
        def init():
            self.ax.set_xlim(0, self.DURATION)
            self.ax.set_ylim(-1, 1)
            return self.ln,

        def update(frame):
            if not self.audio_queue:
                return self.ln,
            
            try:
                ydata = self.audio_queue[-1]
                xdata = np.linspace(0, self.DURATION, len(ydata))
                self.ln.set_data(xdata, ydata)
                self.ax.set_xlim(0, self.DURATION)
                self.ax.set_ylim(-1, 1)
            except Exception as e:
                print(f"Update error: {e}")
            
            return self.ln,

        self.ani = FuncAnimation(
            self.fig, 
            update, 
            init_func=init, 
            blit=True, 
            interval=interval,
            cache_frame_data=False
        )
        
        plt.ion()  # Interactive mode
        plt.show(block=False)
    
    def get_data(self):
        return self.audio_queue[-1] if self.audio_queue else None
    
    def apply_bandpass_filter(self, data, lowcut, highcut, order=5):
        """Apply bandpass filter to audio data"""
        # Ensure data is a 1D numpy array
        data = np.asarray(data).flatten()
        
        nyq = 0.5 * self.SAMPLE_RATE
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        return signal.lfilter(b, a, data)
    
    def reduce_noise(self, data, noise_threshold=0.1):
        """Simple noise reduction using amplitude thresholding"""
        data = np.asarray(data).flatten()
        return np.where(np.abs(data) > noise_threshold, data, 0)
    
    def estimate_dominant_frequency(self, data):
        """Estimate dominant frequency using FFT"""
        # Ensure data is a 1D numpy array
        data = np.asarray(data).flatten()
        
        fft_data = fft.fft(data)
        freqs = fft.fftfreq(len(data), 1/self.SAMPLE_RATE)
        
        positive_freqs = freqs[:len(freqs)//2]
        positive_amplitudes = np.abs(fft_data[:len(fft_data)//2])
        
        dominant_index = np.argmax(positive_amplitudes)
        return positive_freqs[dominant_index]
    
    def spectral_density(self, data):
        """Compute power spectral density"""
        # Ensure data is a 1D numpy array
        data = np.asarray(data).flatten()
        f, Pxx = signal.welch(data, self.SAMPLE_RATE)
        return f, Pxx
