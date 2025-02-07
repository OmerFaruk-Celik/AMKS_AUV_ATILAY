from osiloskop import start_stream, get

# Grafiği başlat
start_stream()

# Bir süre sonra ses verilerini almak için
import time
#time.sleep(5)  # 5 saniye bekleyin
data = get()
print(data)
