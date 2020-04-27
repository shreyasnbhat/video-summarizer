import pandas as pd
import cv2
import numpy as np
from pyCAIR import cropByColumn
import sys
import os
from collections import defaultdict
from .metadata import *

METADATA_FILE = "metadata.csv"

META_MAP = defaultdict(list)

# Stores Metadata of First Frame of each scene
def processVideoMetaData(metapath, videoSourcePath):
    f = open(metapath, "r")
    res = f.readlines()

    for i in range(2, len(res)):
        path = videoSourcePath
        contents = res[i].split(',')
        vidMeta = VideoMetaData(path, contents[1], contents[3])
        videoTitle = path.split('/')[-1].split('.')[0]
        META_MAP[videoTitle].append(vidMeta)

    f.close()


def genImageFromVideo(folderName, outputPath, videoSourcePath=""):
    fileName = folderName.split('/')[-1]

    metapath = folderName + '/' + fileName + '-Scenes.csv'
    df = pd.read_csv(metapath)

    processVideoMetaData(metapath, videoSourcePath)

    numberOfScenes = df.shape[0] - 1
    finalImage = []

    for i in range(1, numberOfScenes + 1):
        num = "{0:03}".format(i)
        imgPath = folderName + '/' + fileName + '-Scene-' + str(num) + '-01.jpg'

        img = cv2.imread(imgPath)
        if i == 1:
            finalImage = img
        else:
            finalImage = np.hstack((finalImage, img))

    cv2.imwrite(outputPath, finalImage)


def isVideo(path):
    return ("finalimage" in path)


def mergeImages(pathImage):
    finalImage = None

    for filename in os.listdir(pathImage):
        if filename.endswith(".jpg"):
            imgPath = os.path.join(pathImage, filename)

            # Write image metadata if not a video summary
            if not isVideo(imgPath):
                imageMetaData = ImageMetaData(imgPath)
                imageMetaData.write(METADATA_FILE)
            else:
                videoTitle = imgPath.split('/')[-1][10:].split('.')[0]
                for i in META_MAP[videoTitle]:
                    i.write(METADATA_FILE)

            img = cv2.imread(imgPath)
            if finalImage is None:
                finalImage = img
            else:
                finalImage = np.hstack((finalImage, img))

    cv2.imwrite(pathImage + 'finalImage.png', finalImage)


def reshapeFinalImage(fileName):
    finalImage = cv2.imread(fileName)
    height = finalImage.shape[0]
    if finalImage.shape[1] > 1080:
        finalImage = cv2.resize(finalImage, (1080, height))
    cv2.imwrite(fileName, finalImage)


def seamCarveFinalImage(fileName):
    finalImage = cv2.imread(fileName)
    height = finalImage.shape[0]
    if finalImage.shape[1] > 1080:
        ratio = 1080 / finalImage.shape[1]
        print(ratio)
        seam_img, finalImage = cropByColumn(finalImage, 1, 0, ['trial', 'png'], 0.95, 0)
    cv2.imwrite('badaimage2.png', finalImage)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        genImageFromVideo(sys.argv[1], sys.argv[2], sys.argv[1])
    elif len(sys.argv) == 2:
        genImageFromVideo(sys.argv[1], "Processing", sys.argv[1])
    else:
        print("Please provide file path to the input video")
    reshapeFinalImage(sys.argv[2])
