import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt

class ObjectDetectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture Window")
        self.setGeometry(300, 375, 700, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Dictionary for tracking detections.
        self.tracked_detections = {}
        self.fps = 0  # Optional: frames per second indicator

        # For moving/resizing.
        self.resizing = False
        self.dragPos = None
        self.originalSize = None
        self.resizeMargin = 10  # pixels near bottom right corner to trigger resizing

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw a green border around the window.
        painter.setPen(QPen(QColor("green"), 10))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # Draw each detection as a small dot with its label.
        dot_radius = 5
        painter.setPen(QPen(QColor("blue")))
        painter.setBrush(QColor("blue"))
        painter.setFont(QFont("Arial", 10))
        for label, (x_center, fixed_y) in self.tracked_detections.items():
            painter.drawEllipse(x_center - dot_radius, fixed_y - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawText(x_center + 7, fixed_y + 4, label)
        
        # Draw the FPS counter and coordinates in the top-left corner.
        painter.setPen(QPen(QColor("blue")))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        coords = self.getCoordinates()  # (x, y, width, height)
        text = f"PPS: {self.fps}   Coords: {coords}"
        painter.drawText(10, 30, text)

    def mousePressEvent(self, event):
        margin = self.resizeMargin
        rect = self.rect()
        pos = event.pos()
        # Check if the click is within the resize margin (bottom-right corner).
        if pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
            self.resizing = True
            self.dragPos = event.globalPos()
            self.originalSize = self.size()
        elif event.button() == Qt.LeftButton:
            self.resizing = False
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing:
            diff = event.globalPos() - self.dragPos
            new_width = self.originalSize.width() + diff.x()
            new_height = self.originalSize.height() + diff.y()
            # Set a minimum size to avoid collapsing too small.
            self.resize(max(new_width, 200), max(new_height, 100))
            event.accept()
        elif event.buttons() == Qt.LeftButton and self.dragPos and not self.resizing:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        event.accept()

    def getCoordinates(self):
        # Returns (x, y, width, height) of this widget in screen coordinates.
        geo = self.geometry()
        return geo.getRect()
    
    def update_detection(self, label, rect_tuple):
        x, y, w, h = rect_tuple
        x_center = int(x + w / 2)
        fixed_y = self.height() - 20  # Draw the indicator 20 pixels above the bottom.
        self.tracked_detections[label] = (x_center, fixed_y)
        self.update()

    def remove_detection(self, label):
        if label in self.tracked_detections:
            del self.tracked_detections[label]
            self.update()

    def clear_detections(self):
        self.tracked_detections.clear()
        self.update()
