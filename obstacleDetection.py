import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect

class ObjectDetectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture Window")
        self.setGeometry(300, 400, 700, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.detections = []

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.green, 10) 
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        detection_pen = QPen(Qt.red, 3)
        painter.setPen(detection_pen)
        for rect in self.detections:
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def getCoordinates(self):
        return self.geometry().getRect()
    
    def add_detection(self, rect):
        if not isinstance(rect, QRect):
            rect = QRect(*rect)
        self.detections.append(rect)
        self.update()

    def remove_detection(self, index):
        if 0 <= index < len(self.detections):
            self.detections.pop(index)
            self.update()

    def clear_detections(self):
        self.detections.clear()
        self.update()