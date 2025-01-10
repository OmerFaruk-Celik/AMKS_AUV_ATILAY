import pygame
import sys
import math

# Pygame'i başlat
pygame.init()

# Ekran boyutları
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("P Noktası Çizimi")

# Renkler (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Çizgi ve nokta ayarları
LINE_LENGTH = 300
LINE_THICKNESS = 5
LINE_START = (SCREEN_WIDTH//2, SCREEN_HEIGHT // 2)
LINE_END = (LINE_START[0] + LINE_LENGTH, LINE_START[1])
LINE_END2 = (SCREEN_WIDTH//2, LINE_START[1]+LINE_LENGTH)


P_X, P_Y = 1, 200
p_point = (P_X, P_Y)  # P noktasının başlangıç koordinatları

# Yazı tipi
font = pygame.font.Font(None, 36)

# Fonksiyon: İki nokta arasındaki uzaklığı hesapla
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

# Fonksiyon: Hesaplama işlemi
def calculate_coordinates(r0, r1,r2 ,line_length,P_Y):
    x = round((line_length / 2) + (r0**2 - r1**2) / (2 * line_length))
    
    y=round((line_length / 2) + (r0**2 - r2**2) / (2 * line_length))
    
    """
    if r0 >= x:
        y = round(math.sqrt(max(0, r0**2 - x**2)))
    else:
        y = round(math.sqrt(max(0, x**2 - r0**2)))
    """

    y += SCREEN_HEIGHT// 2
    x += SCREEN_WIDTH // 2
    return (x, y)

# Ana döngü
running = True
x_velocity = 0.05  # P noktasının hareket hızı
y_velocity = 0.08  # P noktasının hareket hızı

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # R0 ve R1 hesaplama
    r0 = calculate_distance(LINE_START, p_point)
    r1 = calculate_distance(LINE_END, p_point)
    r2=calculate_distance(LINE_END2, p_point)

    # P tahmini koordinatları hesapla
    estimated_x, estimated_y = calculate_coordinates(r0, r1,r2, LINE_LENGTH,P_Y)

    # Ekranı temizle
    screen.fill(WHITE)

    # X ve Y eksenlerini çiz
    pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 2)
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

    # X eksenine paralel çizgi
    pygame.draw.line(screen, RED, LINE_START, LINE_END, LINE_THICKNESS)
    
    # Y eksenine paralel çizgi
    pygame.draw.line(screen, RED, LINE_START, LINE_END2, LINE_THICKNESS)

    # P noktasını çiz
    pygame.draw.circle(screen, RED, p_point, 5)

    # P noktası etrafına artı işareti çiz
    pygame.draw.line(screen, BLACK, (p_point[0] - 10, p_point[1]), (p_point[0] + 10, p_point[1]), 1)
    pygame.draw.line(screen, BLACK, (p_point[0], p_point[1] - 10), (p_point[0], p_point[1] + 10), 1)

    # R0 ve R1 , R2 çizgilerini çiz
    pygame.draw.line(screen, BLACK, LINE_START, p_point, 1)
    pygame.draw.line(screen, BLACK, LINE_END, p_point, 1)

    pygame.draw.line(screen, BLACK, LINE_END2, p_point, 1)

    # Yazılar
    p_text = font.render(f"X: {round(P_X)}, Y: {round(P_Y)}", True, BLACK)
    screen.blit(p_text, (p_point[0] + 10, p_point[1] - 20))

    estimated_text = font.render(f"Tahmini X: {estimated_x}, Tahmini Y: {estimated_y}", True, BLACK)
    screen.blit(estimated_text, (50, 50))

    r0_text = font.render(f"R0: {round(r0)}", True, BLACK)
    r1_text = font.render(f"R1: {round(r1)}", True, BLACK)
    r2_text = font.render(f"R2: {round(r2)}", True, BLACK)

    r0_text_position = (LINE_START[0] + (p_point[0] - LINE_START[0]) // 2, 
                        LINE_START[1] + (p_point[1] - LINE_START[1]) // 2)
    r1_text_position = (LINE_END[0] + (p_point[0] - LINE_END[0]) // 2, 
                        LINE_END[1] + (p_point[1] - LINE_END[1]) // 2)
    r2_text_position = (LINE_END2[0] + (p_point[0] - LINE_END2[0]) // 2, 
                        LINE_END2[1] + (p_point[1] - LINE_END2[1]) // 2)

    screen.blit(r0_text, r0_text_position)
    screen.blit(r1_text, r1_text_position)
    screen.blit(r1_text, r2_text_position)

    # P noktasını hareket ettir
    if P_X >= SCREEN_WIDTH or P_X <= 0:
        x_velocity = -x_velocity
    # P noktasını hareket ettir
    if P_Y >= SCREEN_HEIGHT or P_Y <= 0:
        y_velocity = -y_velocity
        
    P_Y +=y_velocity   
    P_X += x_velocity
    p_point = (P_X, P_Y)

    # Ekranı güncelle
    pygame.display.flip()

# Pygame'i kapat
pygame.quit()
sys.exit()
