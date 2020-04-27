import pandas as pd
import cv2
import numpy as np
from pyCAIR import cropByColumn
import sys
import os
from scenesfromvideo import runSceneDetection
from rgb import readRGBFromDirectory
from generateImage import genImageFromVideo, mergeImages, reshapeFinalImage


def genImageFromFolder(inputFolder, outputFolder='Processing'):
    cwd = os.getcwd()
    path = os.path.join(cwd, outputFolder)

    if not os.path.isdir(path):
        os.mkdir(path)

    rootdir = inputFolder
    extensions = ('.avi')

    vidSourcePaths = []
    videoSDOutputPaths = []

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()

            if ext in extensions:
                filePath = os.path.abspath(os.path.join(subdir, file))
                fileName = os.path.splitext(file)
                outputVideoPath = os.path.join(path, fileName[-2])

                # Store Video Source Paths
                vidSourcePaths.append(filePath)

                # Stores Scene Detect Video Output directory paths
                videoSDOutputPaths.append(outputVideoPath)

                if not os.path.isdir(outputVideoPath):
                    os.mkdir(outputVideoPath)

                print(filePath)
                print(outputVideoPath)

                runSceneDetection(filePath, outputVideoPath)

    readRGBFromDirectory(inputFolder, path + '/images')

    for file, ofile in zip(videoSDOutputPaths, vidSourcePaths):
        videoTitle = file.split('/')[-1]
        videoImageSummaryPath = path + '/images/finalimage' + str(videoTitle) + '.jpg'
        print("Generating Image File for", file, videoImageSummaryPath)
        genImageFromVideo(file, videoImageSummaryPath, ofile)

    mergeImages(path + '/images/')


# reshapeFinalImage(path+'/images/finalImage.png')


if __name__ == '__main__':
    os.remove("metadata.csv")

    if len(sys.argv) == 3:
        genImageFromFolder(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        genImageFromFolder(sys.argv[1])
    else:
        print("Please provide file path to the input folder")
