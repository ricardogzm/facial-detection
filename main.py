import sys
import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap

# from paz.pipelines import DetectMiniXceptionFER
from PySide6.QtCore import Signal, Slot, Qt, QThread, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QMainWindow,
    QLabel,
    QHBoxLayout,
)


class VideoThread(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class CameraWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(640, 480)
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Emotion detection")
        self.setGeometry(300, 300, 1200, 600)

        cameraWidget = CameraWidget()
        testButton = QPushButton("Test")
        testButton.clicked.connect(self.test)

        layout = QHBoxLayout()
        layout.addWidget(cameraWidget)
        layout.addWidget(testButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.show()

    def test(self):
        print("test!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
