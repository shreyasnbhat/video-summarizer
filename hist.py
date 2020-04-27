import cv2
import numpy as np
import os
import sys
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from scenesfromvideo import runSceneDetection
from metadata import *

METAPATH = "meta.csv"
CLUSTERS = 34


def genScenes(videoPath, outputScenePath):
    runSceneDetection(videoPath, outputScenePath)


# basedir holds all summary video frames
def summaryFromHistogram(basedir, summaryImageOutputPath, vidInputPath, sceneMetaPath):
    histData = []
    paths = []
    metadata = []

    extensions = [".jpg", ".png"]

    for path in os.listdir(basedir):
        ext = os.path.splitext(path)[-1].lower()
        if ext in extensions:
            fpath = os.path.join(basedir, path)

            #print("Getting metadata for", fpath)
            vidMeta = getSceneMetaDataFromImage(sceneMetaPath, vidInputPath, fpath)

            img = cv2.imread(fpath, 0)
            hist = cv2.calcHist([img], [0], None, [256], [0, 256]).ravel()
            hist = hist.transpose()
            histData.append(hist)
            paths.append(fpath)
            metadata.append(vidMeta)

    histData = np.array(histData)

    print("Clustering...")
    km = KMeans(n_clusters=CLUSTERS).fit(histData)

    closest, _ = pairwise_distances_argmin_min(km.cluster_centers_, histData)

    respaths = []
    resmeta = []
    for i in closest:
        respaths.append(paths[i])
        resmeta.append(metadata[i])

    respaths, resmeta = (list(t) for t in zip(*sorted(zip(respaths, resmeta))))

    for i in resmeta:
        i.write(METAPATH)

    finalImage = None
    for i in range(CLUSTERS // 2):
        img1 = cv2.imread(respaths[i])
        img2 = cv2.imread(respaths[CLUSTERS//2 + i])

        width = 352
        height = 288
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


def summaryFromHistogramFolder(inputPath, outputPath):
    extensions = [".avi", ".mkv"]

    # mkdir summary image output path
    summaryOutputDir = os.path.join(outputPath, "images")
    if not os.path.exists(summaryOutputDir):
        os.mkdir(summaryOutputDir)

    for path in os.listdir(inputPath):
        ext = os.path.splitext(path)[-1].lower()
        vidTitle = os.path.splitext(path)[0]

        if ext in extensions:
            videoOutputSceneDir = os.path.join(outputPath, vidTitle)
            if not os.path.exists(videoOutputSceneDir):
                os.mkdir(videoOutputSceneDir)

            resultImageName = vidTitle + "_summary.jpg"
            resultImagePath = summaryOutputDir + "/" + resultImageName

            vidInputPath = os.path.join(os.getcwd(), inputPath, path)
            #genScenes(vidInputPath, videoOutputSceneDir)

            sceneMetaFile = vidTitle + "-Scenes.csv"
            sceneMetaPath = os.path.join(videoOutputSceneDir, sceneMetaFile)

            summaryFromHistogram(videoOutputSceneDir, resultImagePath, vidInputPath, sceneMetaPath)


if __name__ == '__main__':
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    # Creat processing directories
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    summaryFromHistogramFolder(inputPath, outputPath)
