mkdir Intermediary
mkdir Results
python3 createvideo.py Data/576RGBVideo4 Intermediary/576RGBVideo4 Data/video_4.wav Results/
python3 scenesfromvideo.py Results/576RGBVideo4.mp4 Intermediary/scenes
python3 frame_extractor.py Intermediary/scenes/576RGBVideo4-Scenes.csv Intermediary/576RGBVideo4/ Results/576RGBVideo4/
mv Results/576RGBVideo4/576RGBVideo4-Scenes.csv Results/576RGBVideo4-Scenes.csv
