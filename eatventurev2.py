import cv2
import numpy as np
import subprocess
import time
import os

# Ścieżki do rysunków
image_paths = {
    'rysunek1': 'C:',
    'rysunek2': 'C:',
    'rysunek3': 'C:',
    'rysunek4': 'C:',
    'rysunek5': 'C:',
    'rysunek6': 'C:',
    'rysunek7': 'C:',
    'rysunek8': 'C:',
    'rysunek9': 'C:',
    'rysunek10': 'C:',
    'rysunek11': 'C:',
    'rysunek12': 'C:'
}

# Zmienna globalna do śledzenia bieżącego kroku
current_step = 1

def capture_screen():
    print("Próba wykonania zrzutu ekranu...")
    subprocess.run("adb exec-out screencap -p > screen.png", shell=True)
    screen = cv2.imread("screen.png")
    if screen is None:
        print("Nie udało się załadować zrzutu ekranu.")
    else:
        print("Zrzut ekranu załadowany pomyślnie.")
    return screen

def is_position_excluded(pattern_name, x, y):
    file_path = f"{pattern_name}_bledy.txt"
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r") as file:
        for line in file:
            bx, by = map(int, line.strip().split(","))
            if (bx, by) == (x, y):
                print(f"Współrzędne ({x},{y}) dla {pattern_name} są wykluczone.")
                return True
    return False

def save_position_error(pattern_name, x, y):
    file_path = f"{pattern_name}_bledy.txt"
    with open(file_path, "a") as file:
        file.write(f"{x},{y}\n")
    print(f"Zapisano błąd dla {pattern_name} w pozycji ({x},{y}).")

def find_pattern(screen, pattern_path, pattern_name, threshold=0.4):
    print(f"Próba znalezienia wzorca {pattern_name} na ekranie.")
    pattern = cv2.imread(pattern_path, cv2.IMREAD_COLOR)

    # Skala od 80% do 120%
    for scale in np.linspace(0.8, 1.2, 5):
        resized_pattern = cv2.resize(pattern, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(screen, resized_pattern, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            x, y = max_loc
            if not is_position_excluded(pattern_name, x, y):
                print(f"Znaleziono {pattern_name} na pozycji ({x}, {y}) przy skali {scale}")
                return x, y
            else:
                print(f"{pattern_name} na pozycji ({x}, {y}) jest wykluczony.")
        else:
            print(f"{pattern_name} nie znaleziono przy skali {scale}.")
    return None

def verified_tap(x, y, pattern_name):
    tap(x, y)
    response = input(f"Czy kliknięcie na {pattern_name} w punkcie ({x},{y}) było poprawne? (tak/nie): ").strip().lower()
    if response == "tak":
        return True
    else:
        save_position_error(pattern_name, x, y)
        return False

def tap(x, y, times=1, delay=0.05):
    print(f"Wykonywanie {times} kliknięć w pozycji ({x},{y})")
    for _ in range(times):
        subprocess.run(f"adb shell input tap {x} {y}", shell=True)
        time.sleep(delay)

def main():
    global current_step  # Użycie globalnej zmiennej
    while True:
        screen = capture_screen()
        
        if current_step == 1:
            if (loc := find_pattern(screen, image_paths['rysunek1'], 'rysunek1')) is not None:
                x, y = loc
                z = x
                z -= 600
                if verified_tap(z, y, 'rysunek1'):
                    print("KROK 1: Naciśnięcie na rysunek 1 zakończone sukcesem.")
                    current_step = 2  # Przechodzimy do następnego kroku

        if current_step == 2:
            if (loc := find_pattern(screen, image_paths['rysunek2'], 'rysunek2')) is not None:
                x, y = loc
                if verified_tap(x, y, 'rysunek2'):
                    print("KROK 2: Naciśnięcie na rysunek 2 zakończone sukcesem.")
                    current_step = 3

        if current_step == 3:
            if (loc := find_pattern(screen, image_paths['rysunek3'], 'rysunek3')) is not None:
                x, y = loc
                a = x - 650
                b = y + 650

                if verified_tap(a, b, 'rysunek3'):
                    tap(a, b, times=2)
                    print("KROK 3: Podwójne kliknięcie na rysunek 3 zakończone sukcesem.")
                    current_step = 4

        # Kolejne kroki z logiką podobną do powyższej
        # ...

        time.sleep(1)

if __name__ == "__main__":
    main()
