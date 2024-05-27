import numpy as np
from scipy.signal import butter, lfilter
from scipy.fftpack import fft
import scipy.signal as signal # signal modülünü import et

def butter_lowpass(cutoff, fs, order=5):
    """
    Belirtilen kesme frekansına sahip bir Butterworth düşük geçiş filtresi tasarlar.

    Args:
        cutoff (float): Kesme frekansı (Hz)
        fs (float): Örnekleme hızı (Hz)
        order (int): Filtre mertebesi

    Returns:
        tuple: Filtre katsayıları (b, a)
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    Verileri bir Butterworth düşük geçiş filtresi ile filtreler.

    Args:
        data (array_like): Filtrelenecek veriler
        cutoff (float): Kesme frekansı (Hz)
        fs (float): Örnekleme hızı (Hz)
        order (int): Filtre mertebesi

    Returns:
        array_like: Filtrelenmiş veriler
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def noise_reduction_fft(signal, threshold=0.1):
    """
    Hızlı Fourier Dönüşümü (FFT) kullanarak gürültüyü azaltır.

    Args:
        signal (array_like): Giriş sinyali
        threshold (float): Gürültü için eşik değeri (0 ile 1 arasında)

    Returns:
        array_like: Gürültüsü azaltılmış sinyal
    """
    fft_signal = fft(signal)
    frequencies = np.fft.fftfreq(signal.size, d=1/44100)  # Örnekleme hızı 44100 Hz olarak varsayılıyor
    filtered_fft = fft_signal * (np.abs(fft_signal) > threshold * np.max(np.abs(fft_signal)))
    filtered_signal = np.real(np.fft.ifft(filtered_fft))
    return filtered_signal

def moving_average(data, window_size):
    """
    Verileri bir hareketli ortalama filtresiyle filtreler.

    Args:
        data (array_like): Filtrelenecek veriler
        window_size (int): Pencere boyutu

    Returns:
        array_like: Filtrelenmiş veriler
    """
    cumulative_sum = np.cumsum(data)
    cumulative_sum[window_size:] = cumulative_sum[window_size:] - cumulative_sum[:-window_size]
    return cumulative_sum[window_size - 1:] / window_size
    
    
def aralik_filtrele(sinyal, fs, alt, ust, order):
  """
  Verilen alt ve üst frekanslar arasında bir bant geçiren filtre uygulayan fonksiyon.

  Args:
    sinyal: Filtrelenecek sinyal.
    fs: Örnekleme frekansı.
    alt: Alt kesme frekansı (Hz).
    ust: Üst kesme frekansı (Hz).
    order: Filtre sırası.

  Returns:
    Filtrelenmiş sinyal.
  """

  kesme_frekans_alt = alt
  kesme_frekans_ust = ust

  # Bant geçiren filtre oluştur
  nyquist_frekansı = 0.5 * fs
  normal_kesme_frekans_alt = kesme_frekans_alt / nyquist_frekansı
  normal_kesme_frekans_ust = kesme_frekans_ust / nyquist_frekansı
  b, a = signal.butter(order, [normal_kesme_frekans_alt, normal_kesme_frekans_ust], btype='band')

  # Sinyalı filtrele
  filtrelenmis_sinyal = signal.lfilter(b, a, sinyal)


  return filtrelenmis_sinyal
  
  
# Genlik filtreleme fonksiyonu
def genlik_filtrele(sinyal, esik):
  """
  Belirtilen eşik değerinden düşük genlikli sinyalleri sıfırlayan fonksiyon.

  Args:
    sinyal: Filtrelenecek sinyal.
    esik: Genlik eşik değeri.

  Returns:
    Filtrelenmiş sinyal.
  """
  sinyal[np.abs(sinyal) < esik] = 0

  return sinyal

