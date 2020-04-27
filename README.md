### Video Summarizer
A toolkit to generate a summary tapestry for a video.

##### RGB to JPG Converter
- Run `python3 rgb.py directoryPath` to convert all rgb files inside `directoryPath` to jpg. 
- All images saved inside directory `images`

##### Video to Scenes with pyscenedetect 
- Requires the scenedetect package to make this work. 
- Installation instruction - `pip3 install scenedetect`
- Run `python3 scenesfromvideo.py inputVideoPath outputDirectoryPath` takes video as input and runs the scenedetect code on it to generate a list of scenes as images and a csv file containing metadata related to the scenes.
- All output is stored in the directory specified in outputDirectoryPath or in `scenes` folder by default.

##### Image Summary Format
- Total images for summary capped at 34.
- 2 Layers of 17 Images, images arranged chronologically.

##### Image Clustering based on Histograms
- `python3 hist.py inputDir outputDir` takes in an input directory of videos and output a summary image for each video under the output directory.
- We resize all frames to 352 x 288

##### Video Player
- `python3 vid.py` runs the video player which can be used to explore the summary image.
- It assumes the above described summary image format.

##### Frame Generator
- `python3 frameGen.py` outputs all frames of a video.
