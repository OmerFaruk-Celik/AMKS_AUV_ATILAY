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
ax.set_xlim([-10, 10])
ax.set_ylim([-10, 10])
ax.set_zlim([-1, 1])

# 3D eksende bir nokta ekleme
point_x, point_y, point_z = 0, 0, 0  # Noktanın koordinatları
ax.scatter(point_x, point_y, point_z, color='red', s=100)  # Nokta ekleme (s: boyut)

# Küre verilerini oluşturma
phi = np.linspace(0, 2 * np.pi, 100)
theta = np.linspace(0, np.pi, 100)
phi, theta = np.meshgrid(phi, theta)
r = 1  # Kürenin yarıçapı
sphere_x = r * np.sin(theta) * np.cos(phi)
sphere_y = r * np.sin(theta) * np.sin(phi)
sphere_z = r * np.cos(theta)

# 3D eksende bir küre ekleme
ax.plot_surface(sphere_x + 3, sphere_y + 3, sphere_z, color='blue', alpha=0.6)  # Küre ekleme (alpha: saydamlık)

# Grafik gösterimi
plt.show()
