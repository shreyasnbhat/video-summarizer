import math

class VideoMetaData:
    def __init__(self, path, frameNumber, timeStamp):
        self.path = path
        self.frameNumber = frameNumber
        self.timeStamp = timeStamp

    def write(self, path):
        f = open(path, "a+")
        content = "VID," + self.path + "," + self.frameNumber + "," + str(float(self.timeStamp) * 1000) + "\n"
        f.write(content)
        f.close()


class ImageMetaData:
    def __init__(self, path):
        self.path = path


    # Ideally a csv
    def write(self, path):
        f = open(path, "a+")
        content = "IMG," + self.path + "\n"
        f.write(content)
        f.close()


# metapath : Path to scene detect metadata
# vidSrcPath : Path to video source
# imagePath : Path to scene jpg
def getSceneMetaDataFromImage(metapath, vidSrcPath, imagePath):
    f = open(metapath, "r")
    res = f.readlines()

    temp = imagePath.split('.')[-2].split('-')
    frameNumber = int(temp[-1])

    vidMeta = None

    for i in range(1, len(res)):
        sceneContent = res[i].split(',')
        frameNo = int(sceneContent[1])

        if frameNumber == frameNo:
            fTime = float(sceneContent[3])
            path = vidSrcPath
            vidMeta = VideoMetaData(path, str(frameNumber), fTime)

    f.close()

    if vidMeta is not None:
        print("Metadata for", imagePath, "was generated!")

    return vidMeta
