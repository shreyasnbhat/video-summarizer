# PyQt5 Video player

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame, QVideoProbe
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QLineEdit)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import pyqtSlot
import sys
from generateImage import VideoMetaData,ImageMetaData

METADATA = []
META_FILE_PATH = "metadata.csv"

def loadMetData():
    f = open(META_FILE_PATH, "r")
    lines = f.readlines()

    for line in lines:
        data = line.split(',')
        if data[0] == "IMG":
            meta = ImageMetaData(data[1][:-1])
        else:
            path = data[1]
            frameNum = int(data[2])
            timeStamp = int(float(data[3][:-1]))
            meta = VideoMetaData(path, frameNum, timeStamp)
        METADATA.append(meta)

class FrameCounterWidget(QLabel):

    def __init__(self, parent=None):
        super(FrameCounterWidget, self).__init__(parent)
        self.frame_cnt = 0
        self.setText('0')

    @pyqtSlot(QVideoFrame)
    def processFrame(self, frame):
        self.frame_cnt = self.frame_cnt + 1
        self.setText(str(self.frame_cnt))


class VideoWindow(QMainWindow):
    filePath = None

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Video Summarizer")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        # To get frame number!
        self.frameCounter = FrameCounterWidget()

        self.probe = QVideoProbe()
        self.probe.videoFrameProbed.connect(self.frameCounter.processFrame)
        self.probe.setSource(self.mediaPlayer)

        # Frame input Text Box
        self.frameTextWidget = QLineEdit()
        self.frameTextWidget.setMaxLength(10)
        self.frameTextWidget.setPlaceholderText("Enter your text")
        self.frameTextWidget.returnPressed.connect(self.return_pressed)

        # Position slider
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Create the Image Widget
        self.sumImage = QImage("./Processing/images/finalImage.png")
        self.sumImage = self.sumImage.scaled(700, 300, aspectRatioMode=Qt.KeepAspectRatio,
                                             transformMode=Qt.SmoothTransformation)
        self.imageWidget = QPixmap.fromImage(self.sumImage)
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(self.imageWidget)
        self.imageLabel.mousePressEvent = self.getPos

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.frameCounter)
        controlLayout.addWidget(self.frameTextWidget)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def getPos(self, event):
        print("Mouse Click")
        x = event.pos().x()
        y = event.pos().y()

        labelW = self.imageLabel.width()
        labelH = self.imageLabel.height()

        smallImgW = labelW / 27
        imgIndex = int(x // smallImgW)

        metaFile = METADATA[imgIndex]

        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(metaFile.path)))
        self.playButton.setEnabled(True)

        if type(metaFile) == VideoMetaData:
            self.mediaPlayer.setPosition(int(metaFile.timeStamp))
        self.play()

        print("Image Pointer:", imgIndex)

    def resizeEvent(self, event):
        self.sumImage = self.sumImage = self.sumImage.scaled(1600, 900, aspectRatioMode=Qt.KeepAspectRatio)
        self.imageWidget = QPixmap(self.sumImage)
        self.imageLabel.setPixmap(self.imageWidget)
        QMainWindow.resizeEvent(self, event)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        print(fileName)
        if fileName != '':
            fileURL = QUrl.fromLocalFile(fileName)
            self.mediaPlayer.setMedia(
                QMediaContent(fileURL))
            self.filePath = fileURL.path()
            self.playButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        print(duration / 1000 / 60, "minutes")
        self.positionSlider.setRange(0, duration)

    def return_pressed(self):
        print("Return pressed!")
        frameToSeek = self.frameTextWidget.text()
        print(self.mediaPlayer.duration())
        print(self.mediaPlayer.metaData('VideoFrameRate'))
        self.positionSlider.setValue(int(frameToSeek))
        self.mediaPlayer.setPosition(int(frameToSeek))
        self.mediaPlayer.play()

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


if __name__ == '__main__':
    loadMetData()
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
