import numpy as np
import sounddevice as sd
import queue
import threading
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from time import sleep
# Sabitler
sampling_rate = 12500  # Örnekleme frekansı (Hz)
block_duration = 0.01  # Blok süresi (saniye)
blocksize = int(sampling_rate * block_duration)  # Blok boyutu (örnek sayısı)
scale_factor = 10  # Genlik ölçekleme faktörü

# Ses verilerini tutmak için bir kuyruk oluşturun
q = queue.Queue()  # Maksimum boyutu belirleyin
dizi=[]
def audio_callback(indata, frames, time, status):
    """Bu fonksiyon mikrofon girişini alır ve verileri kuyrukta saklar."""
    if status:
        print(status)
    try:
        q.put(indata.copy() * scale_factor, block=False)  # Genlik ölçekleme ekle
        #print(q.qsize())
        #sleep(0.5)
        if q.qsize() > 16:
            while q.qsize() > 16:
                q.get()  # Kuyruktan fazladan verileri çıkar
    except queue.Full:
        pass  # Kuyruk doluysa veriyi atla

def update_plot(slider_val):
    """Bu fonksiyon grafiği günceller."""
    global dizi
    plt.ion()  # Interaktif modu etkinleştir
    fig, ax1 = plt.subplots()  # Tek alt grafik oluştur
    
    # Slider eklemek için ikinci bir eksen oluştur
    ax_slider = plt.axes([0.25, 0.01, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Yenileme Hızı', 0.01, 1, valinit=slider_val)
    
    x = np.arange(0, 2000)  # 2000 nokta
    y = np.zeros(2000)
    line1, = ax1.plot(x, y)
    ax1.set_ylim([-1, 1])
    ax1.set_xlim([0, 2000])
    ax1.set_title("Time Domain Signal")
    
    def update(val):
        nonlocal slider_val
        slider_val = slider.val  # Slider değerini güncelle
        
    slider.on_changed(update)
    
    while True:
        if not q.empty():
            
            indata = q.get()
            #print(indata)
            for i in indata:
                dizi.append([i[0]])
   
            indata_length =len(dizi) 
            print(dizi)

            print(indata_length)
            indata=dizi
            
            if indata_length >= 2000:
                dizi=[]
                display_data = indata[:2000, 0]  # İlk 2000 noktayı al
            else:
                # Eski verileri kaydır ve yeni veriyi ekle
                y = np.roll(y, -indata_length)
                y[-indata_length:] = indata[:, 0]
                display_data = y
            
            # Zaman domeni sinyali güncelle
            line1.set_ydata(display_data)
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(slider_val)  # Slider değerine göre grafiği güncelle
            sleep(0.01)

def listen_microphone(slider_val):
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate, blocksize=blocksize):
        print("Mikrofon dinleniyor... 'Ctrl+C' ile çıkış yapabilirsiniz.")
        
        # GUI işlemlerini ana iş parçacığında çalıştır
        update_plot(slider_val)

if __name__ == "__main__":
    slider_val = 0.1  # Başlangıç yenileme hızı
    listen_microphone(slider_val)
