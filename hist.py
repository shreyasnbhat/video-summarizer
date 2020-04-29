import cv2
import numpy as np
import os
import sys
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from metadata import *
from collections import defaultdict
from math import ceil

METAPATH = "meta.csv"

TARGET_CLUSTERS = 40


def generateSummary(respaths, resmeta, summaryImageOutputPath):
    for i in resmeta:
        i.write(METAPATH)

    finalImage = None

    CLUSTERS = len(respaths)

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


def cluster(histData, paths, metadata, targetClusters):
    print("Clustering...")
    km = KMeans(n_clusters=targetClusters).fit(histData)

    closest, _ = pairwise_distances_argmin_min(km.cluster_centers_, histData)

    respaths = []
    resmeta = []
    for i in closest:
        respaths.append(paths[i])
        resmeta.append(metadata[i])

    respaths, resmeta = (list(t) for t in zip(*sorted(zip(respaths, resmeta))))

    return respaths, resmeta


def getImagesFromDir(basedir, vidInputPath, sceneMetaPath):
    histData = []
    paths = []
    metadata = []

    extensions = [".jpg", ".png"]

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

    return histData, paths, metadata


# basedir holds all summary video frames
def summaryFromHistogram(basedir, summaryImageOutputPath, vidInputPath, sceneMetaPath):
    histData, paths, metadata = getImagesFromDir(basedir, vidInputPath, sceneMetaPath)
    histData = np.array(histData)

    targetClusters = min(histData.shape[0], TARGET_CLUSTERS)

    respaths, resmeta = cluster(histData, paths, metadata, targetClusters)
    generateSummary(respaths, resmeta, summaryImageOutputPath)


def summaryHistogramPerFolder(inputPath, outputPath):
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


def summaryHistogramAllFolder(inputPath, outputPath):
    # mkdir summary image output path
    summaryOutputDir = os.path.join(outputPath, "images")
    if not os.path.exists(summaryOutputDir):
        os.mkdir(summaryOutputDir)

    # stores video names, as directory name is video name
    dirs = [i for i in os.listdir(inputPath) if os.path.isdir(os.path.join(inputPath, i)) and i != "images"]

    # all output paths
    summaryImageName = "summary.jpg"
    summaryImageOutputPath = os.path.join(os.getcwd(), summaryOutputDir, summaryImageName)

    histData = []
    paths = []
    metaData = []

    # iterate over video folders
    for dir in dirs:
        # all input paths
        vidTitle = dir
        metaPath = os.path.join(os.getcwd(), inputPath, vidTitle + "-Scenes.csv")
        inputVideoPath = os.path.join(os.getcwd(), inputPath, vidTitle + ".mp4")
        videoSmoothFrameDir = os.path.join(os.getcwd(), inputPath, vidTitle)

        h, p, m = getImagesFromDir(videoSmoothFrameDir, inputVideoPath, metaPath)

        histData += h
        paths += p
        metaData += m

    # iterate over images
    imagePath = os.path.join(os.getcwd(), inputPath, "images")
    h, p, m = getImagesFromDir(imagePath, None, None)
    if len(h) is not 0:
        histData += h
        paths += p
        metaData += m
    else:
        print("No images found!")

    histData = np.array(histData)

    print(histData.shape)

    # cluster everything!
    targetClusters = min(histData.shape[0], TARGET_CLUSTERS)
    _, resMeta = cluster(histData, paths, metaData, targetClusters)

    vidExtensions = ["mp4", "avi"]
    vidClusterCnt = defaultdict(int)

    # find cluster weight of each video/image
    # images given a lower preference! Half the weight.
    for i in resMeta:
        vidTitle, extension = i.path.split('/')[-1].split('.')
        if extension in vidExtensions:
            vidClusterCnt[vidTitle] += 1
        else:
            # potentially alter this, to reduce image importance.
            vidClusterCnt["img"] += 1

    # compute target cluster count
    summation = 0
    maxi = -1
    maxIdx = None
    for i in vidClusterCnt:
        vidClusterCnt[i] = min(ceil(vidClusterCnt[i]), int(vidClusterCnt[i] / (len(resMeta)) * TARGET_CLUSTERS))

        if maxi < vidClusterCnt[i]:
            maxi = vidClusterCnt[i]
            maxIdx = i

        summation += vidClusterCnt[i]

    # make cluster counts even
    # remove one from maximum cluster count group
    if summation % 2 == 1:
        vidClusterCnt[maxIdx] -= 1

    # recluster based on file importance
    resPaths = []
    resMeta = []

    for dir in dirs:
        # all input paths
        vidTitle = dir
        metaPath = os.path.join(os.getcwd(), inputPath, vidTitle + "-Scenes.csv")
        inputVideoPath = os.path.join(os.getcwd(), inputPath, vidTitle + ".mp4")
        videoSmoothFrameDir = os.path.join(os.getcwd(), inputPath, vidTitle)

        h, p, m = getImagesFromDir(videoSmoothFrameDir, inputVideoPath, metaPath)

        if vidClusterCnt[vidTitle] > 0:
            print("Target Cluster Count for", videoSmoothFrameDir, "is", vidClusterCnt[vidTitle])
            rp, rm = cluster(h, p, m, vidClusterCnt[vidTitle])

            resPaths += rp
            resMeta += rm
        else:
            print("Video", vidTitle, "not in final result!")

    # iterate over images
    imagePath = os.path.join(os.getcwd(), inputPath, "images")
    h, p, m = getImagesFromDir(imagePath, None, None)
    if len(h) is not 0:
        print("Target Cluster Count for", imagePath, "is", vidClusterCnt["img"])
        rp, rm = cluster(h, p, m, vidClusterCnt["img"])
        resPaths += rp
        resMeta += rm
    else:
        print("No images found!")

    assert (len(resPaths) % 2 == 0)

    # finally generate the summary image!
    generateSummary(resPaths, resMeta, summaryImageOutputPath)

    # write total cluster count!
    f = open("clusters.txt", "w")
    f.write(str(len(resPaths)))
    f.close()


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

    summaryHistogramAllFolder(inputPath, outputPath)
