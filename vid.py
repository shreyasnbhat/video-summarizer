# PyQt5 Video player

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoFrame, QVideoProbe
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QGridLayout,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QLineEdit)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction, QStackedWidget
from PyQt5.QtGui import QIcon, QPixmap, QImage, QGuiApplication
from PyQt5.QtCore import pyqtSlot, QRect
import sys
from metadata import *

METADATA = []
CLUSTERS = 40
META_FILE_PATH = "meta.csv"
CLUSTER_PATH = "clusters.txt"


def loadMetData():
    f = open(META_FILE_PATH, "r")
    lines = f.readlines()
    f.close()

    global CLUSTERS

    f = open(CLUSTER_PATH, "r")
    line = f.readlines()
    CLUSTERS = int(line[0])

    print(CLUSTERS)
    f.close()

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

    def __init__(self, parent=None, summaryImgPath=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Video Summarizer")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()
        videoWidget.setFixedSize(880, 720)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        # Position slider
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Create the Image Widget
        self.sumImage = QImage(summaryImgPath)

        imgW = self.sumImage.width()
        imgH = self.sumImage.height()

        self.sumImage = self.sumImage.scaledToHeight(min(imgH, 175))
        self.imageWidget = QPixmap.fromImage(self.sumImage)

        print(self.imageWidget.height())

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
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.imageLabel)
        hLayout.setAlignment(Qt.AlignCenter)

        self.stackWidget = QStackedWidget(self)

        self.imgLabel = QLabel()
        self.stackImageWidget = QPixmap('')
        self.imgLabel.setPixmap(self.stackImageWidget)

        self.stackWidget.addWidget(videoWidget)
        self.stackWidget.addWidget(self.imgLabel)

        layout.addWidget(self.stackWidget)
        layout.addLayout(controlLayout)
        layout.addLayout(hLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.setWindowTitle("CS576 Video Summarizer")

    def getPos(self, event):
        print("Mouse Click")
        x = event.pos().x()
        y = event.pos().y()

        labelW = self.imageLabel.width()
        labelH = self.imageLabel.height()

        print(labelW, labelH)

        smallImgW = labelW / (CLUSTERS / 2)
        smallImgH = labelH / 2

        imgIdxX = int(x // smallImgW)
        imgIdxY = int(y // smallImgH)

        idx = (CLUSTERS // 2) * imgIdxY + imgIdxX

        metaFile = METADATA[idx]

        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(metaFile.path)))

        if type(metaFile) == VideoMetaData:
            self.stackWidget.setCurrentIndex(0)
            self.mediaPlayer.setPosition(int(metaFile.timeStamp))
            self.playButton.setEnabled(True)
            self.play()
        else:
            self.stackWidget.setCurrentIndex(1)
            pixmap = QPixmap(metaFile.path)
            pixmap = pixmap.scaled(880, 720)
            self.imgLabel.setPixmap(pixmap)

        self.setWindowTitle(metaFile.path)

        print("Image Pointer:", idx)

    def resizeEvent(self, event):
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

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


if __name__ == '__main__':
    summaryImgPath = sys.argv[1]

    loadMetData()
    app = QApplication(sys.argv)
    player = VideoWindow(None, summaryImgPath)
    player.show()
    sys.exit(app.exec_())
