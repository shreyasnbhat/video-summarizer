import numpy as np
import sys
import cv2
import os


def readRGBImageFromPath(path, writeDir):
    f = open(path, "rb")
    imageArr = f.read()

    height = 288
    width = 352
    channels = 3

    data = np.zeros((height, width, channels))

    offset = height * width

    R = imageArr[0:offset]
    G = imageArr[offset: 2 * offset]
    B = imageArr[2 * offset:]

    for i in range(offset):
        x = int(i / width)
        y = int(i % width)

        data[x][y][0] = B[i]
        data[x][y][1] = G[i]
        data[x][y][2] = R[i]

    data = np.array(data).astype("uint8")

    new_p = path.split('/')

    if not os.path.exists(writeDir):
        os.mkdir(writeDir)

    writePath = writeDir + "/" + new_p[-1][:-3] + "jpg"
    print("Converted", path, "to", writePath)
    cv2.imwrite(writePath, data)


def readRGBFromDirectory(dirpath):
    for filename in os.listdir(dirpath):
        if filename.endswith(".rgb"):
            imgPath = os.path.join(dirpath, filename)
            readRGBImageFromPath(imgPath, "images")


if __name__ == '__main__':
    readRGBFromDirectory(sys.argv[1])
