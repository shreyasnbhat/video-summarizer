import sys
import os


def runSceneDetection(inputPath, outputPath="scenes/"):
    print("Running Scene Detect for", inputPath)
    os.system(
        "scenedetect --input " + inputPath + " --output " + outputPath + " detect-content list-scenes save-images -n 1 > /dev/null 2>&1")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        runSceneDetection(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        runSceneDetection(sys.argv[1])
    else:
        print("Please provide file path to the input video")
