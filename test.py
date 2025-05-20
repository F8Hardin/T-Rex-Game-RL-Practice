import sys
import time
import pyautogui
import keyboard
import threading
import pygetwindow
from ultralytics import YOLO
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from obstacleDetection import ObjectDetectionWindow

# Persistence timeout (if used later)
PERSISTENCE_TIMEOUT = 0.3

class DetectionThread(QThread):
    # Emit a dictionary mapping label -> (x, y, w, h)
    detections_updated = pyqtSignal(dict)

    def __init__(self, model, window):
        super().__init__()
        self.model = model
        self.window = window
        self.running = True
        self.frame_count = 0  # Count frames processed in this thread

    def run(self):
        # Optionally, activate the browser window if needed.
        browser_windows = pygetwindow.getWindowsWithTitle('Firefox')
        if browser_windows:
            browser_windows[0].activate()
            print("Browser window activated.")
        else:
            print("Browser window not found. Please ensure it is open.")

        while self.running:
            if keyboard.is_pressed('q'):
                print("Detected 'q' press, quitting.")
                self.running = False
                QApplication.quit()
                break

            # Capture the screenshot from the region defined by the PyQt window.
            region = self.window.getCoordinates()  # returns (x, y, w, h)
            screenshot = pyautogui.screenshot(region=region)
            # Convert the region dimensions.
            x, y, w, h = region
            # Use the window's height as the square size.
            square_size = h

            # If the width is less than 2*square_size, resize the image so that width = 2*square_size.
            if w < 2 * square_size:
                screenshot = screenshot.resize((2 * square_size, square_size))
            else:
                # Crop the screenshot to have width = 2*square_size.
                screenshot = screenshot.crop((0, 0, 2 * square_size, square_size))

            # Split the screenshot into two square halves.
            left_square = screenshot.crop((0, 0, square_size, square_size))
            right_square = screenshot.crop((square_size, 0, 2 * square_size, square_size))

            # Run YOLO inference separately on each square.
            try:
                left_results = self.model.predict(left_square, conf=0.5, device='cuda')
                right_results = self.model.predict(right_square, conf=0.5, device='cuda')
            except Exception as e:
                print("Error during model prediction:", e)
                continue

            updated_detections = {}

            # Process left square detections.
            if left_results:
                try:
                    boxes = left_results[0].boxes.xyxy.cpu().numpy()  # Format: x1, y1, x2, y2
                    classes = left_results[0].boxes.cls.cpu().numpy()
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, box[:4])
                        class_idx = int(classes[i])
                        label = self.model.names[class_idx] if hasattr(self.model, 'names') else str(class_idx)
                        updated_detections[label] = (x1, y1, x2 - x1, y2 - y1)
                except Exception as e:
                    print("Error processing left side detection results:", e)

            # Process right square detections (adjust x coordinates).
            if right_results:
                try:
                    boxes = right_results[0].boxes.xyxy.cpu().numpy()
                    classes = right_results[0].boxes.cls.cpu().numpy()
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, box[:4])
                        # Adjust x-coordinates by adding the square size.
                        x1_adj = x1 + square_size
                        x2_adj = x2 + square_size
                        class_idx = int(classes[i])
                        label = self.model.names[class_idx] if hasattr(self.model, 'names') else str(class_idx)
                        updated_detections[label] = (x1_adj, y1, x2_adj - x1_adj, y2 - y1)
                except Exception as e:
                    print("Error processing right side detection results:", e)

            self.detections_updated.emit(updated_detections)
            self.frame_count += 1

def update_detections(detections_dict, window):
    # Clear old indicators and update with new ones.
    window.clear_detections()
    for label, rect_tuple in detections_dict.items():
        window.update_detection(label, rect_tuple)

def main():
    app = QApplication(sys.argv)
    window = ObjectDetectionWindow()
    window.show()

    # Load the trained YOLO model (update path as needed).
    model_path = r"F:\Documents\GitHub\T-Rex Game RL\runs\detect\train2\weights\best.pt"
    model = YOLO(model_path)

    # Create and start the detection thread.
    detection_thread = DetectionThread(model, window)
    detection_thread.detections_updated.connect(lambda det: update_detections(det, window))
    detection_thread.start()

    # Set up a QTimer to update the FPS counter every second.
    fps_timer = QTimer()
    def update_fps():
        window.fps = detection_thread.frame_count
        detection_thread.frame_count = 0
        window.update()
    fps_timer.timeout.connect(update_fps)
    fps_timer.start(1000)

    def press_space_loop():
        while True:
            pyautogui.press('space')
            print("Pressed space")
            time.sleep(5)

    # Start the thread
    space_thread = threading.Thread(target=press_space_loop, daemon=True)
    space_thread.start()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
