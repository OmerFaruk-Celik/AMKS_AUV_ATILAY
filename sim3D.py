import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
from matplotlib.animation import FuncAnimation

# Ekran boyutları
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 960

# Çizgi ve nokta ayarları
LINE_LENGTH = 300
LINE_START = np.array([SCREEN_WIDTH//2, SCREEN_HEIGHT // 2, 0])
LINE_END = np.array([LINE_START[0] + LINE_LENGTH, LINE_START[1], 0])
LINE_END2 = np.array([SCREEN_WIDTH//2, LINE_START[1] + LINE_LENGTH, 0])
LINE_END3 = np.array([SCREEN_WIDTH//2, SCREEN_HEIGHT // 2, LINE_LENGTH])

P_X, P_Y, P_Z = 1, 200, 100
p_point = np.array([P_X, P_Y, P_Z])  # P noktasının başlangıç koordinatları

# Fonksiyon: İki nokta arasındaki uzaklığı hesapla
def calculate_distance(point1, point2):
    return np.linalg.norm(point2 - point1)

# Fonksiyon: Hesaplama işlemi
def calculate_coordinates(r0, r1, r2, r3, line_length):
    x = round((line_length / 2) + (r0**2 - r1**2) / (2 * line_length))
    y = round((line_length / 2) + (r0**2 - r2**2) / (2 * line_length))
    z = round((line_length / 2) + (r0**2 - r3**2) / (2 * line_length))
    return np.array([x, y, z]) + np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 0])

# Animasyon fonksiyonu
def update(num):
    global p_point, P_X, P_Y, P_Z, x_velocity, y_velocity, z_velocity

    r0 = calculate_distance(LINE_START, p_point)
    r1 = calculate_distance(LINE_END, p_point)
    r2 = calculate_distance(LINE_END2, p_point)
    r3 = calculate_distance(LINE_END3, p_point)

    estimated_point = calculate_coordinates(r0, r1, r2, r3, LINE_LENGTH)

    ax.clear()
    
    ax.set_xlim([0, SCREEN_WIDTH])
    ax.set_ylim([0, SCREEN_HEIGHT])
    ax.set_zlim([0, LINE_LENGTH * 2])
    
    ax.plot([LINE_START[0], LINE_END[0]], [LINE_START[1], LINE_END[1]], [LINE_START[2], LINE_END[2]], color='red', linewidth=5)
    ax.plot([LINE_START[0], LINE_END2[0]], [LINE_START[1], LINE_END2[1]], [LINE_START[2], LINE_END2[2]], color='red', linewidth=5)
    ax.plot([LINE_START[0], LINE_END3[0]], [LINE_START[1], LINE_END3[1]], [LINE_START[2], LINE_END3[2]], color='red', linewidth=5)

    ax.scatter(p_point[0], p_point[1], p_point[2], color='red', s=100)

    ax.text(p_point[0], p_point[1], p_point[2], f"X: {round(P_X)}, Y: {round(P_Y)}, Z: {round(P_Z)}", color='black')
    
    ax.text(50, 50, 50, f"Tahmini X: {estimated_point[0]}, Tahmini Y: {estimated_point[1]}, Tahmini Z: {estimated_point[2]}", color='black')

    ax.plot([LINE_START[0], p_point[0]], [LINE_START[1], p_point[1]], [LINE_START[2], p_point[2]], color='black', linestyle='dashed')
    ax.plot([LINE_END[0], p_point[0]], [LINE_END[1], p_point[1]], [LINE_END[2], p_point[2]], color='black', linestyle='dashed')
    ax.plot([LINE_END2[0], p_point[0]], [LINE_END2[1], p_point[1]], [LINE_END2[2], p_point[2]], color='black', linestyle='dashed')
    ax.plot([LINE_END3[0], p_point[0]], [LINE_END3[1], p_point[1]], [LINE_END3[2], p_point[2]], color='black', linestyle='dashed')

    if P_X >= SCREEN_WIDTH or P_X <= 0:
        x_velocity = -x_velocity
    if P_Y >= SCREEN_HEIGHT or P_Y <= 0:
        y_velocity = -y_velocity
    if P_Z >= LINE_LENGTH * 2 or P_Z <= 0:
        z_velocity = -z_velocity

    P_X += x_velocity
    P_Y += y_velocity
    P_Z += z_velocity
    p_point = np.array([P_X, P_Y, P_Z])

# Ana döngü parametreleri
x_velocity = 0.5  # P noktasının hareket hızı
y_velocity = 0.8  # P noktasının hareket hızı
z_velocity = 0.3  # P noktasının hareket hızı

fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111, projection='3d')

ani = FuncAnimation(fig, update, frames=100, interval=50)
plt.show()
