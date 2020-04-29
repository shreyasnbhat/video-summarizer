import moviepy.editor as mpe
import cv2
import numpy as np
import os
import sys
import re
from rgb import readRGBFromDirectory

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def createVideoFromImages(imageFolder,audioFile,outputVideoPath):
    print(imageFolder)
    videoName = imageFolder.split('/')[-1]
    print(videoName)
    fileList = os.listdir(imageFolder)
    fileList.sort(key=natural_keys)
     
    img_array = []
    for filename in fileList:
        print(filename)
        img = cv2.imread(imageFolder+'/'+filename)
        print(img.shape)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
     
     
    out = cv2.VideoWriter(outputVideoPath + '/' + videoName + '.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
     
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    videoClip = mpe.VideoFileClip(outputVideoPath + '/' + videoName + '.avi')
    audioClip = mpe.AudioFileClip(audioFile)
    newVideoClip = videoClip.set_audio(audioClip)
    newVideoClip.write_videofile(outputVideoPath + '/' + videoName + '.mp4',fps=30)

if __name__ == '__main__':
    # readRGBFromDirectory(sys.argv[1], sys.argv[2])
    createVideoFromImages(sys.argv[2],sys.argv[3],sys.argv[4])