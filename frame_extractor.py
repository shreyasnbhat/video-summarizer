import cv2
import os
from skimage.measure import compare_ssim
import pandas as pd
import sys
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def getTime(frameNumber):
    seconds = frameNumber / 30
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = int(seconds / 60)
    seconds = seconds % 60
    hours = int(seconds / 60)
    minutes = minutes % 60
    totalTime = str("{0:02}".format(hours)) + ":" + str("{0:02}".format(minutes)) + ":" + str(
        "{0:02}".format(seconds)) + "." + str(milliseconds)
    return totalTime


def findSmoothFramesInVideo(csvFilePath, frameFolder, outputFolder):
    file = open(csvFilePath, "r")
    df = file.readlines()
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)
    listOfFrames = os.listdir(frameFolder)
    listOfFrames.sort(key=natural_keys)
    numOfScenes = len(df)
    finalData = pd.DataFrame(columns=["frame", "time", "timeinseconds"])
    for j in range(2, numOfScenes):
        min_score = -2
        min_file = ""
        min_i = -1
        start = int(df[j].split(',')[1])
        end = int(df[j].split(',')[4])
        for i in range(start + 5, end - 5):
            print(i)
            img = cv2.imread(frameFolder + "/" + listOfFrames[i])
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            score = 0
            for j in range(-5, 5, 1):
                if j != 0:
                    imgToCompare = cv2.imread(frameFolder + "/" + listOfFrames[i + j])
                    grayToCompare = cv2.cvtColor(imgToCompare, cv2.COLOR_BGR2GRAY)
                    score += compare_ssim(gray, grayToCompare, full=True)[0]
            score /= 10
            if score > min_score+0.1:
                min_score = score
                min_file = listOfFrames[i]
                min_i = i
        min_i += 1
        img = cv2.imread(frameFolder + '/' + min_file)
        cv2.imwrite(outputFolder + '/' + min_file, img)
        t = getTime(min_i)
        print(min_i, t)
        finalData = finalData.append(pd.DataFrame([[min_i, t, min_i / 30]], columns=["frame", "time", "timeinseconds"]),
                                     ignore_index=True)
    finalData.to_csv(outputFolder + '/' + csvFilePath.split('/')[-1])


if __name__ == '__main__':
    findSmoothFramesInVideo(sys.argv[1], sys.argv[2], sys.argv[3])
