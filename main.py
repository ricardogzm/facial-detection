import sys
import cv2
import numpy as np
from joke_window import JokeWindow
from video_window import YTVideoWindow
import web_server

from paz.pipelines import DetectMiniXceptionFER
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Signal, Slot, Qt, QThread, QTimer, QMutex
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QMainWindow,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)


class CameraThread(QThread):
    change_pixmap_signal = Signal(np.ndarray)
    emotion_change_signal = Signal(str)
    detect = DetectMiniXceptionFER()
    cap = cv2.VideoCapture(0)
    emotion = None

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self._timer = QTimer(self, timeout=self._on_timeout)
        self._timer.setTimerType(Qt.PreciseTimer)

    @Slot()
    def _on_timeout(self):
        ret, frame = self.cap.read()

        if ret:
            detection = self.detect(frame)
            frame = detection["image"]
            detection_info = detection["boxes2D"]
            if detection_info:
                self.emotion = detection_info[0].class_name
            else:
                self.emotion = None

            # print(f"Emotion: {self.emotion}")

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qImg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = qImg.scaled(640, 480, Qt.KeepAspectRatio)
            self.change_pixmap_signal.emit(QPixmap.fromImage(p))

    def start(self):
        self._timer.start(1000 / 30)

    def stop(self):
        self._timer.stop()
        self.emotion_change_signal.emit(self.emotion)

    def kill(self):
        self._timer.stop()
        self.cap.release()
        self.quit()


class CameraWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(640, 480)
        self.thread = CameraThread()
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
        self.setPixmap(cv_img)

    def deleteLater(self):
        self.thread.kill()
        super().deleteLater()


class VideoAndControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.camera_widget = CameraWidget()

        self.controls = QWidget()
        controlsLayout = QHBoxLayout(self.controls)
        self.pauseButton = QPushButton("Pause")
        self.pauseButton.clicked.connect(self.pauseVideo)
        self.resumeButtom = QPushButton("Resume")
        self.resumeButtom.clicked.connect(self.resumeVideo)
        controlsLayout.addWidget(self.pauseButton)
        controlsLayout.addWidget(self.resumeButtom)

        layout.addWidget(self.camera_widget)
        layout.addWidget(self.controls)

    def pauseVideo(self):
        self.camera_widget.thread.stop()
        print("Pause!")

    def resumeVideo(self):
        self.camera_widget.thread.start()
        print("Resume!")


class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.joke_window = None
        self.video_window = None

        layout = QVBoxLayout(self)

        self.emotion_value = QLabel("Emotion: None")
        self.emotion_value.setStyleSheet("font-size: 20px; border: 1px solid #000000;")
        self.emotion_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.emotion_value)

        self.open_joke_button = QPushButton("Open Joke")
        self.open_joke_button.clicked.connect(self.open_joke)
        self.open_joke_button.setStyleSheet("font-size: 20px;")
        self.open_joke_button.setEnabled(False)
        layout.addWidget(self.open_joke_button)

        self.open_video_button = QPushButton("Open Video")
        self.open_video_button.clicked.connect(self.open_video)
        self.open_video_button.setStyleSheet("font-size: 20px;")
        self.open_video_button.setEnabled(False)
        layout.addWidget(self.open_video_button)

    def open_joke(self):
        print("Open joke!")
        if self.joke_window is None:
            self.joke_window = JokeWindow()
        self.joke_window.show()

    def open_video(self):
        print("Open video!")
        if self.video_window is None:
            self.video_window = YTVideoWindow()
        self.video_window.show()

    def update_emotion(self, emotion):
        emotion_text = f"Emotion: {emotion}"

        if emotion in ("angry", "disgust", "fear", "sad"):
            emotion_text += "\n\nIt seems you are not happy. Let's cheer you up!\nTry to watch a funny video or read a joke."
            self.open_joke_button.setEnabled(True)
            self.open_video_button.setEnabled(True)
        else:
            self.open_joke_button.setEnabled(False)
            self.open_video_button.setEnabled(False)

        self.emotion_value.setText(emotion_text)


# Create a web server thread
class WebServerThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)

    # TODO: Improve this method
    def run(self):
        web_server.run()

    # TODO: Add a stop method to stop the server properly


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Emotion detection")
        self.setGeometry(300, 300, 1200, 600)

        self.videoAndControls = VideoAndControls()
        self.sidePanel = SidePanel()

        # Connect the signal from the camera thread to the update_emotion slot
        self.videoAndControls.camera_widget.thread.emotion_change_signal.connect(
            self.sidePanel.update_emotion
        )

        layout = QHBoxLayout()
        layout.addWidget(self.videoAndControls)
        layout.addWidget(self.sidePanel)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.thread = WebServerThread()
        self.thread.start()

        self.show()

    def closeEvent(self, event):
        self.videoAndControls.camera_widget.deleteLater()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
