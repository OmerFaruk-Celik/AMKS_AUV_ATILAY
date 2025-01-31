import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 3D veriler oluşturma
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
x, y = np.meshgrid(x, y)
z = np.sin(np.sqrt(x**2 + y**2))

# 3D grafik oluşturma
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 3D yüzey çizimi
ax.plot_surface(x, y, z, cmap='viridis')

# Eksen etiketleri
ax.set_xlabel('X Eksen')
ax.set_ylabel('Y Eksen')
ax.set_zlabel('Z Eksen')
ax.set_title('3D Grafik Örneği')

# Grafik gösterimi
plt.show()
