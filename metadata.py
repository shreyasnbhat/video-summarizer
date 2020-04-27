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
    sceneNumber = int(temp[-2])
    sceneFrameNumber = int(temp[-1])

    vidMeta = None

    for i in range(2, len(res)):
        sceneContent = res[i].split(',')

        sceneNo = int(sceneContent[0])

        if sceneNo == sceneNumber:
            sFrame = int(sceneContent[1])
            sTime = float(sceneContent[3])

            eFrame = int(sceneContent[4])
            eTime = float(sceneContent[6])

            fps = (eFrame - sFrame) / (eTime - sTime)

            mFrame = (sFrame + eFrame) // 2
            midFrameCnt = math.ceil((eFrame - sFrame) / 2)
            mTime = sTime + (midFrameCnt - 5) / fps

            print(sTime, mTime, (sTime + eTime) / 2, eTime)

            path = vidSrcPath

            if sceneFrameNumber == 1:
                vidMeta = VideoMetaData(path, str(sFrame), sTime)
            elif sceneFrameNumber == 2:
                vidMeta = VideoMetaData(path, str(mFrame), mTime)
            elif sceneFrameNumber == 3:
                vidMeta = VideoMetaData(path, str(eFrame), eTime)

    f.close()
    return vidMeta
