VID=1
rm -rvf Intermediary Results Final

mkdir Intermediary
mkdir Results
mkdir Results/images

# Just for a video
python3 createvideo.py Data/576RGBVideo$VID Intermediary/576RGBVideo$VID Data/video_$VID.wav Results/
python3 scenesfromvideo.py Results/576RGBVideo$VID.mp4 Intermediary/scenes
python3 frame_extractor.py Intermediary/scenes/576RGBVideo$VID-Scenes.csv Intermediary/576RGBVideo$VID/ Results/576RGBVideo$VID/
mv Results/576RGBVideo$VID/576RGBVideo$VID-Scenes.csv Results/576RGBVideo$VID-Scenes.csv

python3 hist.py Results Final
python3 vid.py Final/images/576RGBVideo"$VID"_summary.jpg