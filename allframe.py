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


def findAllFramesInVideo(frameFolder, outputFolder):
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)
    listOfFrames = os.listdir(frameFolder)
    listOfFrames.sort(key=natural_keys)
    finalData = pd.DataFrame(columns=["frame", "time", "timeinseconds"])
    i=0
    while i<len(listOfFrames):
        if i%10==0:
            print(i)
        file = listOfFrames[i]
        img = cv2.imread(frameFolder + '/' + file)
        cv2.imwrite(outputFolder + '/' + file, img)
        t = getTime(i+1)
        finalData = finalData.append(pd.DataFrame([[i+1, t, (i+1) / 30]], columns=["frame", "time", "timeinseconds"]),
                             ignore_index=True)
        i+=1        
    finalData.to_csv(outputFolder + '/' + outputFolder.split('/')[-1]+'-Scenes.csv')


if __name__ == '__main__':
    findAllFramesInVideo(sys.argv[1], sys.argv[2])
