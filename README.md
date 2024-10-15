# music_service
Dockerized  tools for managing large music libraries. Supports flac,ape,wv,mp4,mp3 tested with M1 Mac and Synology 923+ NAS

Swagger interface

## split_image.py
Walk a source folder and split an image (flac,ape,wv)/cue pair into individual flac tracks, retains metadata, unpacks in 
same dir

## lossless2mp3.py
Walk a source folder and convert flac files to 320kbps mp3 files. retains original folder structure and metadata


## set_video_lang.py 
Remove language audio and/or subtitle tracks from mkv files
