import os
from video_compressor.adapters.ffmpeg import ffmpegVideoCompressorAdapter, ffmpegProbeVideoInfoAdapter
import video_compressor.functions as vfunctions

class VideoInfo():

    @classmethod
    def defaultInfoAdapter(cls):
        return ffmpegProbeVideoInfoAdapter

    def __init__(self, path, adapter=None, **options):
        self.path = path
        self.adapter = adapter or VideoInfo.defaultInfoAdapter()(input=path, **options)
        self.adapter.check_video_integrity(path)

    def volumedetect(self):
        return self.adapter.volumedetect()

    def getVideoBitrate(self):
        return self.adapter.getVideoBitrate()

    def getAudioBitrate(self):
        return self.adapter.getAudioBitrate()

    def getResolution(self):
        return self.adapter.getResolution()

    def getDurationInMicroseconds(self):
        return self.adapter.getDurationInMicroseconds()

    def getDurationInMilliseconds(self):
        microseconds = self.getDurationInMicroseconds()
        return round(microseconds/1000)

    def getDurationInSeconds(self):
        milliseconds = self.getDurationInMilliseconds()
        return round(milliseconds/1000)

    def getSize(self):
        return self.adapter.getSize()

    def getFramePerSeconds(self):
        return self.adapter.getFramePerSeconds()

    def isFragmented(self):
        return self.adapter.isFragmented()
class VideoInfoCollection():

    def __init__(self, videos=None):
        self._videos = [VideoInfo(video) for video in (videos or [])]

    def __len__(self):
        return len(self._videos)

    def append(self, video, adapter_options={}):
        self._videos.append(VideoInfo(video, **adapter_options))

    def getDurationInMicroseconds(self):
        return sum(map(lambda s: s.getDurationInMicroseconds(), self._videos))


class VideoCompressor():

    WebSettings = [
        {'scale':[480, -1], 'bitrate': '200k', 'fps': 24, 'suffix':'@sm'},
        {'scale':[640, -1], 'bitrate': '1M', 'fps': 24, 'suffix':'@md'},
        {'scale':[960, -1], 'bitrate': '2M', 'fps': 24, 'suffix':'@lg'},
        {'scale':[1280, -1], 'bitrate': '3M', 'fps': 24, 'suffix':'@xl'},
    ]

    @classmethod
    def defaultCompressorAdapter(cls):
        return ffmpegVideoCompressorAdapter

    def __init__(
        self,
        input=None,
        mute=None,
        scale=None,
        bitrate=None,
        crop_origin=None,
        crop_size=None,
        fps=None,
        codec_preset=None,
        quality=None,
        suffix="",
        adapter=None,
        **adapter_options,
    ):
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate
        self._crop_origin = crop_origin
        self._crop_size = crop_size
        self._fps = fps
        self._codec_preset = codec_preset
        self._quality = quality
        self._suffix = suffix
        self._adapter_options = adapter_options

        self.VideoCompressorAdapter = adapter or VideoCompressor.defaultCompressorAdapter()

    @property
    def compressor_adapter(self):
        return self.VideoCompressorAdapter(
            input=self._input,
            mute=self._mute,
            scale=self._scale,
            bitrate=self._bitrate,
            crop_origin=self._crop_origin,
            crop_size=self._crop_size,
            codec_preset=self._codec_preset,
            quality=self._quality,
            fps=self._fps,
            **self._adapter_options
        )

    @property
    def info(self):
        return VideoInfo(self._input, **self._adapter_options)

    def options(self):
        return {
            'input': self._input,
            'mute': self._mute,
            'scale': self._scale,
            'bitrate': self._bitrate,
            'crop_origin': self._crop_origin,
            'crop_size': self._crop_size,
            'codec_preset': self._codec_preset,
            'quality': self._quality,
            'fps': self._fps,
        }

    def update(self, **updates):
        options = self.options()
        options.update(updates)
        video = VideoCompressor(**options, **self._adapter_options)
        video.VideoCompressorAdapter = self.VideoCompressorAdapter
        return video

    def mute(self, mute):
        return self.update(mute=mute)

    def scale(self, *scale):
        if len(scale) == 1:
            return self.update(scale=(scale[0], -1))
        return self.update(scale=scale)

    def bitrate(self, bitrate):
        return self.update(bitrate=bitrate)

    def crop(self, origin, size):
        return self.update(crop_origin=origin, crop_size=size)

    def fps(self, fps):
        return self.update(fps=fps)

    def codecPreset(self, codec_preset):
        return self.update(codec_preset=codec_preset)

    def quality(self, quality):
        return self.update(quality=quality)

    def export(self, output):
        filename, ext = os.path.splitext(output)
        return self.compressor_adapter.export(f'{filename}{self._suffix}{ext}')

    def fragment(self, output):
        return self.compressor_adapter.fragment(output)

    def slice(self, output, stepInMilliseconds=1000):
        
        videos = VideoInfoCollection()
        path, ext = os.path.splitext(output)
        durationInMilliseconds = self.info.getDurationInMilliseconds()

        steps = vfunctions.rangeSliceBySteps(
            0, 
            durationInMilliseconds, 
            stepInMilliseconds
        )

        for i, step in enumerate(steps):
            start, duration = step
            step_path = f'{path}-{i}{ext}'
            self.compressor_adapter.slice(step_path, start, duration)
            videos.append(step_path, self._adapter_options)

        return videos

    def exportCollection(self, output, settings):
        for setting in settings:
            video = self.update(**setting)
            video.export(output)
            yield video
