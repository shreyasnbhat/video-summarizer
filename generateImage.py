import pandas as pd 
import cv2
import numpy as np
from pyCAIR import cropByColumn
import sys
import os

def genImageFromVideo(folderName, outputPath):
	fileName = folderName.split('/')[-1]
	df = pd.read_csv(folderName+'/'+fileName+'-Scenes.csv')
	numberOfScenes = df.shape[0]-1
	finalImage = []

	for i in range(1,numberOfScenes+1):
		num = "{0:03}".format(i)
		img = cv2.imread(folderName+'/'+fileName+'-Scene-'+str(num)+'-01.jpg')
		if i==1:
			finalImage = img
		else:
			finalImage = np.hstack((finalImage,img))
	print(finalImage.shape)
	print(outputPath)
	cv2.imwrite(outputPath,finalImage)

def mergeImages(pathImage):
	finalImage = None
	for filename in os.listdir(pathImage):
		if filename.endswith(".jpg"):
			imgPath = os.path.join(pathImage, filename)
			img = cv2.imread(imgPath)
			if finalImage is None:
				finalImage = img
			else :
				finalImage = np.hstack((finalImage,img))
	cv2.imwrite(pathImage+'finalImage.png',finalImage)

def reshapeFinalImage(fileName):
	finalImage = cv2.imread(fileName)
	height = finalImage.shape[0]
	if finalImage.shape[1]>1080:
		finalImage = cv2.resize(finalImage,(1080,height))
	cv2.imwrite(fileName,finalImage)

def seamcarveFinalImage(fileName):
	finalImage = cv2.imread(fileName)
	height = finalImage.shape[0]
	if finalImage.shape[1]>1080:
		ratio = 1080/finalImage.shape[1]
		print(ratio)
		seam_img, finalImage = cropByColumn(finalImage, 1, 0, ['trial','png'], 0.95, 0)
	cv2.imwrite('badaimage2.png',finalImage)


if __name__ == '__main__':
	if len(sys.argv)==3:
		genImageFromVideo(sys.argv[1],sys.argv[2])
	elif len(sys.argv)==2:
		genImageFromVideo(sys.argv[1])
	else:
		print("Please provide file path to the input video")
	reshapeFinalImage(sys.argv[2])
