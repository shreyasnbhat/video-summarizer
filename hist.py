import cv2
import numpy as np
import os
import sys
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from scenesfromvideo import runSceneDetection
from metadata import *

METAPATH = "meta.csv"
CLUSTERS = 40


def genScenes(videoPath, outputScenePath):
    runSceneDetection(videoPath, outputScenePath)


def generateSummary(respaths, resmeta, summaryImageOutputPath):
    for i in resmeta:
        i.write(METAPATH)

    finalImage = None
    for i in range(CLUSTERS // 2):
        img1 = cv2.imread(respaths[i])
        img2 = cv2.imread(respaths[CLUSTERS // 2 + i])

        scale = 0.4

        width = int(352 * scale)
        height = int(288 * scale)
        dim = (width, height)

        # resize image
        resized1 = cv2.resize(img1, dim, interpolation=cv2.INTER_AREA)
        resized2 = cv2.resize(img2, dim, interpolation=cv2.INTER_AREA)

        if finalImage is None:
            finalImage = resized1
            finalImage = np.vstack((finalImage, resized2))
        else:
            tempImage = resized1
            tempImage = np.vstack((tempImage, resized2))
            finalImage = np.hstack((finalImage, tempImage))

    print("Generating final image in", summaryImageOutputPath)
    cv2.imwrite(summaryImageOutputPath, finalImage)


# basedir holds all summary video frames
def summaryFromHistogram(basedir, summaryImageOutputPath, vidInputPath, sceneMetaPath):
    histData = []
    paths = []
    metadata = []

    extensions = [".jpg", ".png"]

    dataPoints = 0

    print(basedir, summaryImageOutputPath, vidInputPath, sceneMetaPath)

    for path in os.listdir(basedir):
        ext = os.path.splitext(path)[-1].lower()
        if ext in extensions:
            fpath = os.path.join(basedir, path)

            vidMeta = getSceneMetaDataFromImage(sceneMetaPath, vidInputPath, fpath)

            img = cv2.imread(fpath, 0)
            hist = cv2.calcHist([img], [0], None, [256], [0, 256]).ravel()
            hist = hist.transpose()
            histData.append(hist)
            paths.append(fpath)
            metadata.append(vidMeta)

            dataPoints += 1

    histData = np.array(histData)

    global CLUSTERS

    if dataPoints < CLUSTERS:
        CLUSTERS = (dataPoints // 2) * 2

    # write CLUSTERS to cluster file
    f = open("clusters.txt", "w")
    f.write(str(CLUSTERS))
    f.close()

    print("Clustering...")
    print(histData.shape)
    km = KMeans(n_clusters=CLUSTERS).fit(histData)

    closest, _ = pairwise_distances_argmin_min(km.cluster_centers_, histData)

    respaths = []
    resmeta = []
    for i in closest:
        respaths.append(paths[i])
        resmeta.append(metadata[i])

    respaths, resmeta = (list(t) for t in zip(*sorted(zip(respaths, resmeta))))
    generateSummary(respaths, resmeta, summaryImageOutputPath)


def summaryFromHistogramFolder(inputPath, outputPath):
    # mkdir summary image output path
    summaryOutputDir = os.path.join(outputPath, "images")
    if not os.path.exists(summaryOutputDir):
        os.mkdir(summaryOutputDir)

    # stores video names, as directory name is video name
    dirs = [i for i in os.listdir(inputPath) if os.path.isdir(os.path.join(inputPath, i))]

    for dir in dirs:
        # all input paths
        vidTitle = dir
        metaPath = os.path.join(os.getcwd(), inputPath, vidTitle + "-Scenes.csv")
        inputVideoPath = os.path.join(os.getcwd(), inputPath, vidTitle + ".mp4")
        videoSmoothFrameDir = os.path.join(os.getcwd(), inputPath, vidTitle)

        print(metaPath, inputVideoPath, videoSmoothFrameDir)

        # all output paths
        resultImageName = vidTitle + "_summary.jpg"
        resultImagePath = os.path.join(os.getcwd(), summaryOutputDir, resultImageName)

        summaryFromHistogram(videoSmoothFrameDir, resultImagePath, inputVideoPath, metaPath)


if __name__ == '__main__':
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    # delete metadata file

    if os.path.exists("meta.csv"):
        os.remove("meta.csv")

    if os.path.exists("clusters.txt"):
        os.remove("clusters.txt")


    # Creat processing directories
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    summaryFromHistogramFolder(inputPath, outputPath)
