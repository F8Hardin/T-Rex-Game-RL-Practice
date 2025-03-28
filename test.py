import pyautogui
import threading
import time
import sys
import pygetwindow
import keyboard
from obstacleDetection import ObjectDetectionWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def detectionLoop():
    browser_windows = pygetwindow.getWindowsWithTitle('Firefox')
    if browser_windows:
        browser_window = browser_windows[0]
        browser_window.activate()
        print("Browser window activated.")
    else:
        print("Browser window not found. Please ensure it is open.")

    while True:
        if keyboard.is_pressed('q'):
            print("Detected 'q' press, quitting.")
            QApplication.quit()
            break
        pyautogui.press('space')
        print("Pressed space in the browser window.")
        time.sleep(1)

if __name__ == "__main__":
    #start the QT app
    app = QApplication(sys.argv)
    window = ObjectDetectionWindow()
    window.show()

    #testing space bar with window attention
    thread = threading.Thread(target=detectionLoop, daemon=True)
    thread.start()

    #Testing detection drawing performance
    counter = 0
    def update_detection():
        global counter
        window.clear_detections()
        rect = (counter, 100, 50, 50)
        window.add_detection(rect)
        counter += 1
    timer = QTimer()
    timer.timeout.connect(update_detection)
    timer.start(10)

    sys.exit(app.exec_())
