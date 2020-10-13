A simple helper to compress video. 

## Installation 

Please install [ffmpeg](https://ffmpeg.org/)
Then install video_compressor 
```
pip install video_compressor
```

## Usage 

```python

from video_compressor import VideoCompressor, VideoInfo

VideoCompressor(input='./example.mp4')
    .bitrate(1000000)
    .scale(640, -1)
    .export('./export.mp4')

VideoInfo('./export.mp4').getResolution() 
# 640, 300
```

*work in progress..*