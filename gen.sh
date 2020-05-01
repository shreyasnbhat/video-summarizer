MAXVID=$1

echo $MAXVID

rm -rvf Intermediary Results Final

mkdir Intermediary
mkdir Results
mkdir Results/images

python3 rgb.py Data/image Results/images

for (( VID=1; VID<=$MAXVID; VID++ ))
do
echo "Video: video$VID"
VIDNAME=video$VID
python3 createvideo.py Data/$VIDNAME Intermediary/$VIDNAME Data/$VIDNAME/audio.wav Results/
python3 scenesfromvideo.py Results/$VIDNAME.mp4 Intermediary/scenes
python3 frame_extractor.py Intermediary/scenes/$VIDNAME-Scenes.csv Intermediary/$VIDNAME/ Results/$VIDNAME/
mv Results/$VIDNAME/$VIDNAME-Scenes.csv Results/$VIDNAME-Scenes.csv
done

python3 hist.py Results Final
python3 vid.py Final/images/summary.jpg