### Video Summarizer
A toolkit to generate a summary tapestry for a video.

##### RGB to JPG Converter
- Run `python3 rgb.py directoryPath` to convert all rgb files inside `directoryPath` to jpg. 
- All images saved inside directory `images`

##### Video to Scenes using 
- Requires the scenedetect package to make this work. 
- Installation instruction - `pip3 install scenedetect`
- Run `python3 scenesfromvideo.py inputVideoPath outputDirectoryPath` takes video as input and runs the scenedetect code on it to generate a list of scenes as images and a csv file containing metadata related to the scenes.
- All output is stored in the directory specified in outputDirectoryPath or in `scenes` folder by default.