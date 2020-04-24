import pandas as pd 
import cv2
import numpy as np
from pyCAIR import cropByColumn
import sys
import os
from scenesfromvideo import runSceneDetection
from rgb import readRGBFromDirectory
from generateImage import genImageFromVideo
from generateImage import mergeImages
from generateImage import reshapeFinalImage

def genImageFromFolder(inputFolder,outputFolder='Processing/'):
	cwd = os.getcwd()
	path = os.path.join(cwd, outputFolder)
	if not os.path.isdir(path):
		os.mkdir(path)
	rootdir = inputFolder
	extensions = ('.avi')
	videoFilePath = []
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			ext = os.path.splitext(file)[-1].lower()
			if ext in extensions:
				filePath = os.path.abspath(os.path.join(subdir, file))
				fileName = os.path.splitext(file)[-2]
				outputVideoPath = os.path.join(path,fileName)
				videoFilePath.append(outputVideoPath)
				if not os.path.isdir(outputVideoPath):
					os.mkdir(outputVideoPath)
				runSceneDetection(filePath, outputVideoPath)

	readRGBFromDirectory(inputFolder,path+'/images')

	for file in videoFilePath:
		videoPath = path+'images/finalimage'+file.split('/')[-1]+'.jpg'
		genImageFromVideo(file,videoPath)

	mergeImages(path+'/images/')

	# reshapeFinalImage(path+'/images/finalImage.png')


if __name__ == '__main__':
	if len(sys.argv)==3:
		genImageFromFolder(sys.argv[1],sys.argv[2])
	elif len(sys.argv)==2:
		genImageFromFolder(sys.argv[1])
	else:
		print("Please provide file path to the input folder")
