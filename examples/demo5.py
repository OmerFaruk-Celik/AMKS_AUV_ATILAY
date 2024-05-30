import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import sounddevice as sd
import time
import os

# Parametreleri belirle
fs = 44100  # Ses kartı için yaygın kullanılan örnekleme frekansı
fc = 2000  # Taşıyıcı frekansı
phasedev = np.pi / 2

def pmdemod(y, fc, fs):
    analytic_signal = hilbert(y)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    instantaneous_frequency = np.diff(instantaneous_phase) / (2.0 * np.pi * (1.0 / fs))
    return instantaneous_frequency - fc

while True:
    # Modüle edilmiş sinyal dosyasını kontrol et
    if os.path.exists("modulated_signal.npy"):
        # Modüle edilmiş sinyali yükle
        y = np.load("modulated_signal.npy")

        t = np.arange(0, len(y)) / fs

        # Modüle edilmiş sinyali çiz
        plt.subplot(2, 1, 1)
        plt.plot(t, y)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('PM Signal')
        plt.grid(True)

        # Demodüle edilmiş sinyali oluştur ve çiz
        z = pmdemod(y, fc, fs)
        t_z = t[:-1]  # Z'nin uzunluğu t'den bir eksik olacak, bu yüzden t'yi ayarlamamız gerekiyor

        plt.subplot(2, 1, 2)
        plt.plot(t_z, z)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('PM Demodulated Signal')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        # Demodüle edilmiş sinyali hoparlörden çal
        sd.play(z, fs)
        sd.wait()  # Çalma işlemi bitene kadar bekle

        # Modüle edilmiş sinyal dosyasını sil
        os.remove("modulated_signal.npy")

    # Kısa bir süre bekle ve tekrar kontrol et
    time.sleep(1)
