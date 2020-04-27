import cv2

VIDEO_PATH = "B99/b99.mkv"
OUTPUT_PATH = "temp/"

vidcap = cv2.VideoCapture(VIDEO_PATH)
success, image = vidcap.read()
count = 0

while success:

    cv2.imwrite(OUTPUT_PATH + "frame%d.jpg" % count, image)  # save frame as JPEG file
    print('Read frame: ', count)
    count += 1
    success, image = vidcap.read()

    if count == 1000:
        break