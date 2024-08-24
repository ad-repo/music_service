# music_service
dockerized flac and mp3 tools for managing large music libraries. tested with M1 Mac and Synology 923+ NAS

swagger interface provided

## split_flac
walk a source folder and split an image flac/cue pair into individual flac tracks, retains metadata, unpacks in 
same dir

## flac2mp3
walk a source folder and convert flac files to 320kbps mp3 files. retains original folder structure and metadata