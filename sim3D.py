import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 3D veriler oluşturma
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
x, y = np.meshgrid(x, y)
z = np.sin(np.sqrt(x**2 + y**2))

# Büyük boyutlu 3D grafik oluşturma
fig = plt.figure(figsize=(16, 9))  # Figür boyutlarını ayarlama (inch cinsinden)
ax = fig.add_subplot(111, projection='3d')

# 3D yüzey çizimi
ax.plot_surface(x, y, z, cmap='viridis')

# Eksen etiketleri ve başlık
ax.set_xlabel('X Eksen')
ax.set_ylabel('Y Eksen')
ax.set_zlabel('Z Eksen')
ax.set_title('Tüm Ekranı Kaplayan 3D Grafik Örneği')

# Eksen sınırlarını genişletme
ax.set_xlim([-20, 20])
ax.set_ylim([-20, 20])
ax.set_zlim([-2, 2])

# Grafik gösterimi
plt.show()
