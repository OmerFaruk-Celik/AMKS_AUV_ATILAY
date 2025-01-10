import pyautogui
import pywinauto
import subprocess
import time

def is_text_field_active():
    """Aktif pencere bir metin alanı mı kontrol eder."""
    app = pywinauto.Application().connect(active_only=True)
    window = app.active_window()
    
    if window:
        # Bu örnekte yalnızca pencere başlığını kontrol ediyoruz
        # Gerçek uygulamada pencere içeriğini kontrol etmek gerekebilir
        title = window.window_text().lower()
        return any(keyword in title for keyword in ['text', 'input', 'field'])
    return False

def move_keyboard_to_cursor():
    """Klavyeyi imlecin altına taşır."""
    # Klavyenin var olup olmadığını kontrol et
    if not pywinauto.Application().connect(title='Onboard', found_index=0):
        subprocess.Popen(['onboard'])
        time.sleep(2)  # Klavye açılması için kısa bir süre bekle

    # Klavye penceresini al
    keyboard_window = pywinauto.Application().connect(title='Onboard').window(title='Onboard')
    
    # İmleç konumunu al
    cursor_x, cursor_y = pyautogui.position()
    
    # Klavye penceresinin boyutlarını al
    keyboard_width, keyboard_height = keyboard_window.width(), keyboard_window.height()
    
    # Klavyeyi imlecin altına konumlandır
    new_x = cursor_x - (keyboard_width // 2)
    new_y = cursor_y + 10  # İmlecin biraz altına
    
    # Klavye penceresini yeniden konumlandır
    keyboard_window.move_window(x=new_x, y=new_y)

def main():
    while True:
        if is_text_field_active():
            move_keyboard_to_cursor()
        else:
            # Klavye kapalı değilse kapat
            for keyboard in pywinauto.Application().windows(title='Onboard'):
                keyboard.close()
        
        # 1 saniyede bir kontrol et
        time.sleep(1)

if __name__ == "__main__":
    main()
