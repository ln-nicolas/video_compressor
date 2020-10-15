A simple python helper to compress video. 

## Installation

Please install [ffmpeg bin](https://ffmpeg.org/)
then install video_compressor

```
pip install video_compressor
```

## Usage

```python
# import VideoCompressor
from video_compressor import VideoCompressor, VideoInfo

# add your options
VideoCompressor(input='./example.mp4')
    .mute(True)
    .crop((0, 0), (100, 100))
    .scale(640, -1)
    .bitrate('1M')
    .fps(24)
    .codec_presect('h264WebVBR')
    .quality('low')
    .export('./export.mp4') # then export !

# read video metrics
info = VideoInfo('./export.mp4')
w, h = info.getResolution()
ismute = info.volumedetect()
video_bitrate = info.getVideoBitrate()
audio_bitrate = info.getAudioBitrate()
duration = info.getDurationInMilliseconds()
size = info.getSize()
fps = info.getFramePerSeconds()
```

## Export Options

|option|value|description|
|------|-----|-----------|
|mute| ```boolean``` |Mute the video|
|scale| ```width, height``` | Scale video to given width and height. If ```width = -1``` or ```height = -1``` scale video keeping ration.|
|crop|```(origin_x, origin_y), (width, height)```| Crop the video from origin point (origin_x, orign_y) with given size (width, height)| 
|bitrate| ```string like 1000000,1000k or 1M```| The average bit/seconds|
|fps| ```integer```| Number of frame per seconds |
|codec_presect|```string 'h264WebVBR'```| Specify a codec preset used to encode video |
|quality|```string 'low' or 'max'```| Specify a video quality |


## Export a collection

For responsive video, you would export your video to different resolutions.

```python
settings = [
    {'codec_preset': 'h264WebVBR', 'scale':[480, -1], 'suffix':'@sm'},
    {'codec_preset': 'h264WebVBR', 'scale':[480, -1], 'quality':'low', 'suffix':'@sm+low'},
    {'scale':[640, -1], 'suffix':'@md'},
    {'scale':[960, -1], 'suffix':'@lg'},
    {'scale':[1280, -1], 'suffix':'@xl'},
]
video = VideoCompressor('video.mp4')
video.exportCollection(temp('export.mp4'), settings)

# ls ./
# video.mp4
# export@sm.mp4
# export@sm+low.mp4
# export@md.mp4
# export@lg.mp4
# export@xl.m4
```
