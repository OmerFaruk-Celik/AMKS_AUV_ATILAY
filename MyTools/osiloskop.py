import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

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
        
        # Stop existing stream if any
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        # Clear previous data
        self.audio_queue.clear()
        
        # Start new input stream
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
    
    def get_data(self):
        # Return the most recent audio data or None
        return self.audio_queue[-1] if self.audio_queue else None
    
    def send_data(self, data=None):
        # If no data provided, use microphone data
        print(data)
        if data is None:
           
            data = self.get_data()
        
        if data is not None:
            # Example: you could implement data sending logic here
            # For now, just return the data
            return data
        return None
    
    def visualize(self, interval=50, max_frames=1000):
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
            cache_frame_data=False, 
            save_count=max_frames
        )
        plt.show()

# Example usage
def main():
    osc = Osiloskop()
    osc.start_stream()
    osc.visualize()

if __name__ == "__main__":
    main()
