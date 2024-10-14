# music_service
dockerized  tools for managing large music libraries. Supports flac,ape,wv,mp4,mp3 tested with M1 Mac and Synology 923+ NAS

swagger interface provided

## split_lossles
walk a source folder and split an image flac/cue pair into individual flac tracks, retains metadata, unpacks in 
same dir

## lossless2mp3
walk a source folder and convert flac files to 320kbps mp3 files. retains original folder structure and metadata


## set video to language/remove subtitles, audiotracks